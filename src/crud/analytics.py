from datetime import datetime
from sqlalchemy.orm import Session
from src.models.analytics import Channel, Video

def add_channel(db: Session, handle: str) -> Channel:
    channel = Channel(handle=handle)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel

def add_video(db: Session, handle: str, title: str, views: int, published_at: datetime, url: str) -> Video:
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        raise ValueError(f"Channel '{handle}' not found")
    video = Video(
        title=title,
        views=views,
        published_at=published_at,
        url=url,
        channel_id=channel.id,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

def get_channels(db: Session):
    return db.query(Channel).all()

def get_videos(db: Session, handle: str):
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        return []
    return db.query(Video).filter_by(channel_id=channel.id).all()

def delete_channel(db: Session, handle: str):
    deleted = db.query(Channel).filter_by(handle=handle).delete()
    db.commit()
    return bool(deleted)


