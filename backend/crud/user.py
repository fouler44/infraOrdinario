from sqlalchemy.orm import Session
from models.user import AppUser

def update_user_puuid(db: Session, user_id: int, puuid: str):
    """
    Actualiza el puuid de un usuario
    """
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise ValueError(f"Usuario {user_id} no encontrado")
    
    user.puuid = puuid
    return user

def get_user_by_id(db: Session, user_id: int):
    """Obtiene un usuario por ID"""
    return db.query(AppUser).filter(AppUser.user_id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Obtiene un usuario por username"""
    return db.query(AppUser).filter(AppUser.username == username).first()

def get_user_by_puuid(db: Session, puuid: str):
    """Obtiene un usuario por PUUID"""
    return db.query(AppUser).filter(AppUser.puuid == puuid).first()