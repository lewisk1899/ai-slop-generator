from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Channel(Base):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String, unique=True, nullable=False)
    videos = relationship("Video", back_populates="channel", cascade="all, delete")

class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)
    title = Column(String, nullable=False)
    views = Column(Integer, nullable=False)
    published_at = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)

    # NEW FIELD
    processed_at = Column(DateTime, nullable=True, default=None)

    channel = relationship("Channel", back_populates="videos")
