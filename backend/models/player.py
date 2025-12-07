from sqlalchemy import Column, String, Text, Integer, DateTime, CheckConstraint
from sqlalchemy.sql import func
from config.db import Base

class Player(Base):
    __tablename__ = "player"

    puuid = Column(String(78), primary_key=True)
    game_name = Column(Text, nullable=False)
    tagline = Column(Text, nullable=False)
    platform = Column(String(5), nullable=False)
    player_level = Column(Integer, nullable=False)
    player_icon = Column(Integer)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("player_level >= 0"),
        CheckConstraint("platform IN ('LAN','LAS','NA','BR','EUW','EUNE','TR','RU','KR','JP','OCE')"),
    )
