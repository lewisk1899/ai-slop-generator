import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.analytics import Base
from src.crud import channel, video


class TestVideoIntegration(unittest.TestCase):
    """Integration tests for src/client/video.py CRUD operations."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()
        # Each test starts with one channel
        channel.create(self.db, "LTT")

    def tearDown(self):
        for table in reversed(Base.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()
        self.db.close()

    # -----------------------------
    # CREATE
    # -----------------------------
    def test_create_video(self):
        vid = video.create(
            db=self.db,
            handle="LTT",
            title="GPU Review",
            views=1000,
            published_at=datetime(2025, 1, 1),
            url="http://youtube.com/ltt",
        )
        self.assertEqual(vid.title, "GPU Review")
        self.assertEqual(vid.views, 1000)

    def test_create_many_videos(self):
        videos = [
            {"title": "GPU Review", "views": 10, "published_at": datetime(2025, 1, 1), "url": "url1"},
            {"title": "CPU Review", "views": 20, "published_at": datetime(2025, 2, 1), "url": "url2"},
        ]
        created = video.create_many(self.db, "LTT", videos)
        self.assertEqual(len(created), 2)
        self.assertEqual(created[1].title, "CPU Review")

    # -----------------------------
    # READ
    # -----------------------------
    def test_get_video(self):
        created = video.create(
            self.db, "LTT", "TestVid", 10, datetime(2025, 1, 1), "url"
        )
        fetched = video.get(self.db, created.id)
        self.assertEqual(fetched.id, created.id)

    def test_get_multi_videos(self):
        video.create(self.db, "LTT", "Vid1", 10, datetime(2025, 1, 1), "url1")
        video.create(self.db, "LTT", "Vid2", 20, datetime(2025, 2, 1), "url2")
        all_videos = video.get_multi(self.db, "LTT")
        self.assertEqual(len(all_videos), 2)
        titles = [v.title for v in all_videos]
        self.assertIn("Vid1", titles)

    # -----------------------------
    # UPDATE
    # -----------------------------
    def test_update_video(self):
        vid = video.create(self.db, "LTT", "Old", 10, datetime(2025, 1, 1), "url")
        updated = video.update(self.db, vid.id, title="New", views=123)
        self.assertEqual(updated.title, "New")
        self.assertEqual(updated.views, 123)

    def test_update_many_videos(self):
        video.create(self.db, "LTT", "A", 5, datetime(2025, 1, 1), "urlA")
        video.create(self.db, "LTT", "B", 10, datetime(2025, 2, 1), "urlB")
        count = video.update_many(self.db, "LTT", 10)
        self.assertEqual(count, 2)
        vids = video.get_multi(self.db, "LTT")
        self.assertTrue(all(v.views >= 15 for v in vids))

    # -----------------------------
    # DELETE
    # -----------------------------
    def test_delete_video(self):
        vid = video.create(self.db, "LTT", "DeleteMe", 10, datetime(2025, 1, 1), "url")
        deleted = video.delete(self.db, vid.id)
        self.assertTrue(deleted)
        vids = video.get_multi(self.db, "LTT")
        self.assertEqual(len(vids), 0)

    def test_delete_many_videos(self):
        video.create(self.db, "LTT", "V1", 10, datetime(2025, 1, 1), "url1")
        video.create(self.db, "LTT", "V2", 20, datetime(2025, 2, 1), "url2")
        count = video.delete_many(self.db, "LTT")
        self.assertEqual(count, 2)
        vids = video.get_multi(self.db, "LTT")
        self.assertEqual(len(vids), 0)
