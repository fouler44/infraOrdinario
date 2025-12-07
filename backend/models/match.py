from sqlalchemy import (
    BigInteger, Column, Index, String, Integer, ForeignKey, Boolean,
    CheckConstraint, Numeric, ARRAY, UniqueConstraint
)
from config.db import Base

class LolMatch(Base):
    __tablename__ = "lol_match"

    match_id = Column(String(50), primary_key=True)
    duration_seconds = Column(Integer, nullable=False)
    game_mode = Column(String(25), nullable=False)
    game_status = Column(String(20), nullable=False)
    patch_version = Column(String(30))
    game_start_ts = Column(BigInteger, nullable=True, index=True)

    __table_args__ = (
        CheckConstraint("duration_seconds > 0"),
    )


class MatchParticipation(Base):
    __tablename__ = "match_participation"

    participation_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String(50), ForeignKey("lol_match.match_id", ondelete="CASCADE"), nullable=False)
    
    puuid = Column(String(78), nullable=False)
    game_name = Column(String(40), nullable=False)
    tag = Column(String(5), nullable=False)
    team_id = Column(Integer, nullable=False)
    champion_id = Column(Integer, nullable=False)
    kills = Column(Integer)
    assists = Column(Integer)
    deaths = Column(Integer)
    total_damage = Column(Numeric(6, 1))
    damage_per_min = Column(Integer)
    lane = Column(String(20))
    champion_level = Column(Integer)
    item_slots = Column(ARRAY(Integer))
    trinket = Column(Integer)
    total_minions = Column(Integer)
    vision_score = Column(Integer)
    kda = Column(Numeric(5, 1))
    kp = Column(Numeric(3, 2))
    win = Column(Boolean, nullable=False)

    __table_args__ = (
        CheckConstraint("kills >= 0"),
        CheckConstraint("assists >= 0"),
        CheckConstraint("deaths >= 0"),
        CheckConstraint("total_damage >= 0"),
        CheckConstraint("champion_level >= 0"),
        CheckConstraint("total_minions >= 0"),
        CheckConstraint("vision_score >= 0"),
        UniqueConstraint("match_id", "puuid"),
    )

Index("idx_mpart_puuid", MatchParticipation.puuid)
Index("idx_match_participation_champion", MatchParticipation.champion_id)