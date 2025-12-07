from sqlalchemy.orm import Session
from clients.riot import get_match_ids_by_puuid, get_match_details
from crud.match import upsert_match, insert_participation, match_exists
from utils.data_transformer import transform_match_data

def fetch_and_save_matches(db: Session, puuid: str, platform: str, count: int = 20):
    """
    Obtiene y guarda las últimas partidas de un jugador
    
    Returns:
        dict con estadísticas del proceso
    """
    # Obtener IDs de partidas
    match_ids = get_match_ids_by_puuid(puuid, platform, count=count)
    
    stats = {
        "total_fetched": len(match_ids),
        "new_matches": 0,
        "skipped_existing": 0,
        "errors": []
    }
    
    for match_id in match_ids:
        try:
            # Verificar si ya existe
            if match_exists(db, match_id):
                stats["skipped_existing"] += 1
                continue
            
            # Obtener detalles de la partida
            match_data = get_match_details(match_id, platform)
            
            # Transformar datos
            match_info, participations = transform_match_data(match_data)
            
            if not match_info:
                stats["errors"].append(f"Match {match_id}: datos inválidos")
                continue
            
            # Guardar en DB
            upsert_match(db, **match_info)
            
            for part in participations:
                insert_participation(db, **part)
            
            db.commit()
            stats["new_matches"] += 1
            
        except Exception as e:
            db.rollback()
            stats["errors"].append(f"Match {match_id}: {str(e)}")
            continue
    
    return stats


def get_player_match_history(db: Session, puuid: str, limit: int = 20, offset: int = 0):
    """Obtiene el historial de partidas con paginación"""
    from crud.match import get_participations_by_puuid, get_match_by_id
    
    participations = get_participations_by_puuid(db, puuid, limit, offset)
    
    result = []
    for part in participations:
        match = get_match_by_id(db, part.match_id)
        result.append({
            "match": {
                "match_id": match.match_id,
                "duration_seconds": match.duration_seconds,
                "game_mode": match.game_mode,
                "game_status": match.game_status,
                "patch_version": match.patch_version,
                "game_start_ts": match.game_start_ts
            },
            "performance": {
                "champion_id": part.champion_id,
                "kills": part.kills,
                "deaths": part.deaths,
                "assists": part.assists,
                "kda": float(part.kda),
                "kp": float(part.kp),
                "total_damage": float(part.total_damage),
                "damage_per_min": part.damage_per_min,
                "lane": part.lane,
                "champion_level": part.champion_level,
                "items": part.item_slots,
                "trinket": part.trinket,
                "cs": part.total_minions,
                "vision_score": part.vision_score,
                "win": part.win,
            }
        })
    
    return result