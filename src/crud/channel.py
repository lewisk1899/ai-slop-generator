from typing import List, Optional
from sqlalchemy.orm import Session
from src.models.analytics import Channel


# ======================================
# CREATE
# ======================================

def create(db: Session, handle: str) -> Channel:
    """Create a new channel."""
    channel = Channel(handle=handle)
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return channel


def create_many(db: Session, handles: List[str]) -> List[Channel]:
    """Create multiple channels at once."""
    channels = [Channel(handle=h) for h in handles]
    db.add_all(channels)
    db.commit()
    for c in channels:
        db.refresh(c)
    return channels


# ======================================
# READ
# ======================================

def get(db: Session, handle: str) -> Optional[Channel]:
    """Get a single channel by handle."""
    return db.query(Channel).filter_by(handle=handle).first()


def get_multi(db: Session) -> List[Channel]:
    """Get all channels."""
    return db.query(Channel).all()


# ======================================
# UPDATE
# ======================================

def update(db: Session, handle: str, new_handle: Optional[str] = None) -> Channel:
    """Update a single channel's handle."""
    channel = db.query(Channel).filter_by(handle=handle).first()
    if not channel:
        raise ValueError(f"Channel '{handle}' not found")

    if new_handle:
        channel.handle = new_handle
    db.commit()
    db.refresh(channel)
    return channel


def update_many(db: Session, updates: List[dict]) -> List[Channel]:
    """Batch update multiple channels.
    Each item in `updates` should be {'old_handle': str, 'new_handle': str}.
    """
    updated_channels = []
    for u in updates:
        ch = db.query(Channel).filter_by(handle=u["old_handle"]).first()
        if ch:
            ch.handle = u["new_handle"]
            db.commit()
            db.refresh(ch)
            updated_channels.append(ch)
    return updated_channels


# ======================================
# DELETE
# ======================================

def delete(db: Session, handle: str) -> bool:
    """Delete a single channel."""
    deleted = db.query(Channel).filter_by(handle=handle).delete()
    db.commit()
    return bool(deleted)


def delete_many(db: Session, handles: List[str]) -> int:
    """Delete multiple channels by handle."""
    deleted = db.query(Channel).filter(Channel.handle.in_(handles)).delete(synchronize_session=False)
    db.commit()
    return deleted

