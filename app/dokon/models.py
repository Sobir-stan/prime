from sqlalchemy import Column, Integer, String, JSON
from app.db.database import Base


class Progress(Base):
    __tablename__ = "progress"

    user_id = Column(Integer, primary_key=True)
    cookies = Column(Integer, default=0)

    active_skin = Column(String, default="cookie.png")
    unlocked_skins = Column(JSON, default=["cookie.png"])