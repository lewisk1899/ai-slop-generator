from sqlalchemy.orm import Session
from datetime import datetime

from crud.crud_base import CRUDBase, ModelType
from models.analytics import Channel, Video

class ChannelCRUD(CRUDBase[Channel]):
    def get_by_handle(self, db: Session, handle: str) -> Channel | None:
        return self.get_by(db, handle=handle)

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from crud.crud_base import CRUDBase
from models.analytics import Channel, Video


class ChannelCRUD(CRUDBase[Channel]):
    def get_by_handle(self, db: Session, handle: str) -> Channel | None:
        return self.get_by(db, handle=handle)


class VideoCRUD(CRUDBase[Video]):
    def get_by_channel(self, db: Session, channel_id: int) -> list[Video]:
        return self.get_multi_by(db, channel_id=channel_id)

    def get_top_unprocessed_from_channel(
        self,
        db: Session,
        channel_id: int
    ) -> ModelType | None:

        videos = self.get_multi_by(
            db,
            channel_id=channel_id,
            processed_at=None,
        )

        if not videos:
            return None

        videos.sort(key=lambda v: v.views, reverse=True)

        return videos[0]

    def mark_processed(self, db: Session, video_id: int) -> Video:
        video = self.get(db, video_id)
        video.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(video)
        return video


channel_crud = ChannelCRUD(Channel)
video_crud = VideoCRUD(Video)
