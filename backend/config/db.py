from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from config.config import DB_CONFIG

def _build_url(cfg: dict) -> str:
    user = cfg["user"]
    pwd = quote_plus(cfg["password"])
    host = cfg["host"]
    port = cfg["port"]
    db   = cfg["dbname"]

    sslmode = cfg.get("sslmode", "disable")
    query = f"?sslmode={sslmode}" if sslmode else ""

    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

DATABASE_URL = _build_url(DB_CONFIG)

engine = create_engine(
    DATABASE_URL,
    echo=False,           
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

Base = declarative_base()

from contextlib import contextmanager
@contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
