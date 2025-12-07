from sqlalchemy.orm import Session
from models.player import Player

def upsert_player(db: Session, **kwargs):
    """
    Inserta o actualiza un jugador.
    """
    player = db.query(Player).filter(Player.puuid == kwargs["puuid"]).first()
    
    if player:
        for k, v in kwargs.items():
            setattr(player, k, v)
    else:
        player = Player(**kwargs)
        db.add(player)
    
    return player


def get_player_by_puuid(db: Session, puuid: str):
    return db.query(Player).filter(Player.puuid == puuid).first()