# tests/test_crud_video.py
import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.analytics import Base, Video
from crud.crud import channel_crud, video_crud


class VideoCRUDTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            echo=False,
            future=True,
        )
        cls.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=cls.engine,
            future=True,
        )

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    # --- tests ---

    def test_create_and_get_video(self):
        channel = channel_crud.create(self.db, {"handle": "owner"})

        video = video_crud.create(
            self.db,
            {
                "channel_id": channel.id,
                "title": "My Video",
                "views": 123,
                "published_at": datetime.utcnow(),
                "url": "https://example.com/video",
            },
        )

        self.assertIsNotNone(video.id)
        self.assertEqual(video.channel_id, channel.id)

        fetched = video_crud.get(self.db, video.id)
        self.assertIsInstance(fetched, Video)
        self.assertEqual(fetched.title, "My Video")
        self.assertEqual(fetched.channel_id, channel.id)

    def test_get_by_channel(self):
        channel = channel_crud.create(self.db, {"handle": "owner2"})

        v1 = video_crud.create(
            self.db,
            {
                "channel_id": channel.id,
                "title": "V1",
                "views": 10,
                "published_at": datetime.utcnow(),
                "url": "https://example.com/v1",
            },
        )
        v2 = video_crud.create(
            self.db,
            {
                "channel_id": channel.id,
                "title": "V2",
                "views": 20,
                "published_at": datetime.utcnow(),
                "url": "https://example.com/v2",
            },
        )

        videos = video_crud.get_by_channel(self.db, channel.id)
        ids = {v.id for v in videos}
        self.assertEqual(ids, {v1.id, v2.id})


