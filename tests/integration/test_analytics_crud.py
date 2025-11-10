import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.analytics import Base
from src.client import graphql_client


class TestGraphQLClientIntegration(unittest.TestCase):
    """Integration tests for direct DB CRUD operations (graphql_client)."""

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()

    def tearDown(self):
        # Clean all data between tests
        for table in reversed(Base.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()
        self.db.close()

    def test_add_and_get_channel(self):
        ch = graphql_client.add_channel(self.db, "LinusTechTips")
        self.assertEqual(ch.handle, "LinusTechTips")

        channels = graphql_client.get_channels(self.db)
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].handle, "LinusTechTips")

    def test_add_video_for_existing_channel(self):
        graphql_client.add_channel(self.db, "LTT")
        vid = graphql_client.add_video(
            db=self.db,
            handle="LTT",
            title="GPU Review",
            views=50000,
            published_at=datetime(2025, 1, 1),
            url="http://youtube.com/ltt",
        )
        self.assertEqual(vid.title, "GPU Review")
        self.assertEqual(vid.views, 50000)

        videos = graphql_client.get_videos(self.db, "LTT")
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0].title, "GPU Review")

    def test_delete_channel(self):
        graphql_client.add_channel(self.db, "DeleteMe")
        deleted = graphql_client.delete_channel(self.db, "DeleteMe")
        self.assertTrue(deleted)

        remaining = graphql_client.get_channels(self.db)
        self.assertEqual(len(remaining), 0)

    def test_add_video_fails_if_channel_missing(self):
        with self.assertRaises(ValueError):
            graphql_client.add_video(
                db=self.db,
                handle="Unknown",
                title="Orphan Video",
                views=100,
                published_at=datetime.utcnow(),
                url="http://youtube.com/test",
            )

