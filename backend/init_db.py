from config.db import engine, Base
from models import AppUser, Player, LolMatch, MatchParticipation

def init_database():
    """Crea todas las tablas en la base de datos"""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente")

if __name__ == "__main__":
    init_database()