from sqlalchemy.orm import Session
from crud.player import upsert_player
from crud.user import update_user_puuid, get_user_by_username
from clients.riot import get_puuid_by_gametag, get_summoner 

def link_account(db: Session, username, game_name, tag, platform):
    
    user = get_user_by_username(db, username)
    if not user:
        raise ValueError(f"Usuario '{username}' no encontrado")
    
    puuid = get_puuid_by_gametag(game_name, tag, platform)
    
    profile = get_summoner(puuid, platform)
    
    upsert_player(
        db,
        puuid=puuid,
        game_name=game_name,
        tagline=tag,
        platform=platform,
        player_level=profile["level"],
        player_icon=profile["icon"],
    )
    
    update_user_puuid(db, user.user_id, puuid)
    
    return puuid