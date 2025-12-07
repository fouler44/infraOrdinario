from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from config.db import Base

class AppUser(Base):
    __tablename__ = "app_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    puuid = Column(String(78))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def data(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "puuid": self.puuid,
            "created_at": self.created_at
        }
    
