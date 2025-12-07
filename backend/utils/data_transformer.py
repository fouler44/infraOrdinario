def clean_str(val, max_len = 80):
    """Convierte a str, recorta espacios y limita longitud."""
    if val is None:
        return ""
    s = str(val).strip()
    if max_len and len(s) > max_len:
        return s[:max_len]
    return s

def coerce_int(val, default = 0):
    """Convierte a int si es posible, si no devuelve default."""
    try:
        return int(float(val))
    except Exception:
        return default
    
def coerce_float(val, default = 0.0):
    """Convierte a float si es posible, si no devuelve default."""
    try:
        return float(val)
    except Exception:
        return default

def coerce_bool(val, default = False):
    """Convierte a booleano con heurística simple."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1", "yes", "y", "t"):
            return True
        if v in ("false", "0", "no", "n", "f"):
            return False
    if isinstance(val, (int, float)):
        return val != 0
    return default

def safe_get(d, *keys, default=None):
    """Acceso anidado seguro: safe_get(obj, 'a','b','c')."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def transform_match_data(match_data):
    """
    Devuelve:
      - match_info: dict para LolMatch(**match_info)
      - rows: list[dict] para MatchParticipation(**row)
    """
    if not isinstance(match_data, dict):
        print("ERROR: match_data no es un dict")
        return None, []

    info = match_data.get("info") or {}
    meta = match_data.get("metadata") or {}

    # ---- LolMatch ----
    match_id = clean_str(meta.get("matchId"), max_len=50)
    if not match_id:
        print("matchId ausente en metadata")
        return None, []

    duration_seconds = coerce_int(info.get("gameDuration"), 0)
    if duration_seconds <= 0:
        start_ts = coerce_int(info.get("gameStartTimestamp"), 0)
        end_ts   = coerce_int(info.get("gameEndTimestamp"), 0)
        if end_ts > start_ts > 0:
            duration_seconds = (end_ts - start_ts) // 1000  # ms → s

    game_mode    = clean_str(info.get("gameMode") or "UNKNOWN", max_len=25)
    game_status  = clean_str(info.get("endOfGameResult") or "UNKNOWN", max_len=20)
    patch_version= clean_str(info.get("gameVersion") or "UNKNOWN", max_len=30)
    game_start_ts = coerce_int(info.get("gameStartTimestamp"))

    match_info = {
        "match_id": match_id,
        "duration_seconds": duration_seconds,
        "game_mode": game_mode,
        "game_status": game_status,
        "patch_version": patch_version,
        "game_start_ts": game_start_ts
    }

    # ---- Participantes → MatchParticipation ----
    participants = info.get("participants") or []
    if not isinstance(participants, list) or not participants:
        print(f"Partida {match_id}: invalida")
        return match_info, []

    rows = []

    for i, p in enumerate(participants, start=1):
        if not isinstance(p, dict):
            print(f"Partida {match_id}: Participante {i} no es válido")
            continue

        puuid = clean_str(p.get("puuid"), max_len=78)
        if not puuid:
            print(f"Partida {match_id}: participante {i} sin puuid")
            continue

        game_name = clean_str(p.get("riotIdGameName"), max_len=40)
        tag = clean_str(p.get("riotIdTagline"), max_len=5)

        team_id = coerce_int(p.get("teamId"), 100)
        
        champion_id = coerce_int(p.get("championId"), 0)

        kills = coerce_int(p.get("kills", 0))
        deaths = coerce_int(p.get("deaths", 0))
        assists = coerce_int(p.get("assists", 0))

        total_damage = round(coerce_float(p.get("totalDamageDealtToChampions", 0.0)), 1)

        dpm = safe_get(p, "challenges", "damagePerMinute", default=None)
        damage_per_min = coerce_int(dpm, 0)


        lane = clean_str(p.get("lane") or p.get("teamPosition") or "UNKNOWN", max_len=20)
        champion_level = coerce_int(p.get("champLevel", 0))

        item_slots = [
            coerce_int(p.get("item0"), 0),
            coerce_int(p.get("item1"), 0),
            coerce_int(p.get("item2"), 0),
            coerce_int(p.get("item3"), 0),
            coerce_int(p.get("item4"), 0),
            coerce_int(p.get("item5"), 0),
        ]
        trinket = coerce_int(p.get("item6"), 0)

        total_minions = coerce_int(p.get("totalMinionsKilled", 0))
        vision_score  = coerce_int(p.get("visionScore", 0))

        kda = coerce_float(safe_get(p, "challenges", "kda", default=0.0), 0.0)
        kp  = round(coerce_float(safe_get(p, "challenges", "killParticipation", default=0.0), 0.0),2)

        win = coerce_bool(p.get("win"), False)

        participation_dict = {
            "match_id": match_id,
            "puuid": puuid,
            "game_name": game_name,
            "tag": tag,
            "team_id": team_id,
            "champion_id": champion_id,
            "kills": kills,
            "assists": assists,
            "deaths": deaths,
            "total_damage": total_damage,
            "damage_per_min": damage_per_min,
            "lane": lane,
            "champion_level": champion_level,
            "item_slots": item_slots,
            "trinket": trinket,
            "total_minions": total_minions,
            "vision_score": vision_score,
            "kda": round(kda, 1),
            "kp": kp,
            "win": win,
        }

        rows.append(participation_dict)

    if not rows:
        print(f"Partida {match_id}: los participantes no fueron validos")

    return match_info, rows