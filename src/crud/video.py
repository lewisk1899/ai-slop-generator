from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.models.analytics import Channel, Video


# ======================================
# CREATE
# ======================================

def create(
    db: Session,
    handle: str,
    title: str,
    views: int,
    published_at: datetime,
    url: str,
) -> Video:
    """Create a video under a given channel."""
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


def create_many(db: Session, handle: str, videos: List[Dict[str, Any]]) -> List[Video]:
    """Create multiple videos for a given channel."""
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        raise ValueError(f"Channel '{handle}' not found")

    objs = [
        Video(
            title=v["title"],
            views=v["views"],
            published_at=v["published_at"],
            url=v["url"],
            channel_id=channel.id,
        )
        for v in videos
    ]
    db.add_all(objs)
    db.commit()
    for v in objs:
        db.refresh(v)
    return objs


# ======================================
# READ
# ======================================

def get(db: Session, video_id: int) -> Optional[Video]:
    """Get a single video by ID."""
    return db.query(Video).filter_by(id=video_id).first()


def get_multi(db: Session, handle: Optional[str] = None) -> List[Video]:
    """Get all videos, or all videos for a channel if handle is provided."""
    query = db.query(Video)
    if handle:
        channel = db.query(Channel).filter_by(handle=handle).first()
        if not channel:
            return []
        query = query.filter_by(channel_id=channel.id)
    return query.all()


# ======================================
# UPDATE
# ======================================

def update(db: Session, video_id: int, **kwargs) -> Video:
    """Update a single video's fields."""
    video = db.query(Video).filter_by(id=video_id).first()
    if not video:
        raise ValueError(f"Video ID '{video_id}' not found")

    for key, val in kwargs.items():
        if hasattr(video, key):
            setattr(video, key, val)
    db.commit()
    db.refresh(video)
    return video


def update_many(db: Session, handle: str, views_delta: int) -> int:
    """Increment views for all videos in a given channel."""
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        raise ValueError(f"Channel '{handle}' not found")

    count = (
        db.query(Video)
        .filter(Video.channel_id == channel.id)
        .update({Video.views: Video.views + views_delta})
    )
    db.commit()
    return count


# ======================================
# DELETE
# ======================================

def delete(db: Session, video_id: int) -> bool:
    """Delete a single video by ID."""
    deleted = db.query(Video).filter_by(id=video_id).delete()
    db.commit()
    return bool(deleted)


def delete_many(db: Session, handle: str) -> int:
    """Delete all videos for a given channel."""
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        raise ValueError(f"Channel '{handle}' not found")

    deleted = db.query(Video).filter_by(channel_id=channel.id).delete()
    db.commit()
    return deleted

