import requests
from config.config import RIOT_API_KEY

def get_puuid_by_gametag(game_name, tag, platform):
    platform = platform.upper()
    if platform in ('LAN', 'LAS', 'NA', 'BR'):
        region = 'americas'
    elif platform in ('EUW', 'EUNE', 'TR', 'RU'):
        region = 'europe'
    elif platform in ('KR', 'JP', 'OCE'):
        region = 'asia'
    else:
        raise ValueError(f"Plataforma no soportada: {platform}")

    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["puuid"]


def get_summoner(puuid, platform):
    platform_mapping = {
        'lan': 'la1',
        'las': 'la2',
        'na': 'na1',
        'br': 'br1',
        'euw': 'euw1',
        'eune': 'eun1',
        'tr': 'tr1',
        'ru': 'ru',
        'kr': 'kr',
        'jp': 'jp1',
        'oce': 'oc1',
    }

    platform_code = platform_mapping.get(platform.lower(), platform.lower())
    url = f"https://{platform_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    return {
        "level": data["summonerLevel"],
        "icon": data["profileIconId"]
    }


def get_match_ids_by_puuid(puuid, platform, count=20, start=0):
    platform = platform.upper()
    if platform in ('LAN', 'LAS', 'NA', 'BR'):
        region = 'americas'
    elif platform in ('EUW', 'EUNE', 'TR', 'RU'):
        region = 'europe'
    elif platform in ('KR', 'JP', 'OCE'):
        region = 'asia'
    else:
        raise ValueError(f"Plataforma no soportada: {platform}")

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    params = {
        "start": start,
        "count": min(count, 100)
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_match_details(match_id: str, platform: str) -> dict:
    platform = platform.upper()
    if platform in ('LAN', 'LAS', 'NA', 'BR'):
        region = 'americas'
    elif platform in ('EUW', 'EUNE', 'TR', 'RU'):
        region = 'europe'
    elif platform in ('KR', 'JP', 'OCE'):
        region = 'asia'
    else:
        raise ValueError(f"Plataforma no soportada: {platform}")

    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
