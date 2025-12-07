# app/crud.py
from sqlalchemy.orm import Session

from crud.crud_base import CRUDBase, ModelType
from models.analytics import Channel, Video


class ChannelCRUD(CRUDBase[Channel]):
    def get_by_handle(self, db: Session, handle: str) -> Channel | None:
        return self.get_by(db, handle=handle)


class VideoCRUD(CRUDBase[Video]):
    def get_by_channel(self, db: Session, channel_id: int) -> list[Video]:
        return self.get_multi_by(db, channel_id=channel_id)


channel_crud = ChannelCRUD(Channel)
video_crud = VideoCRUD(Video)
