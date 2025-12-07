# tests/test_crud_channel.py
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.analytics import Base, Channel 
from crud.crud import channel_crud, video_crud

class ChannelCRUDTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One in-memory DB for the whole test class
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
        # Fresh tables for each test
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    # --- tests ---

    def test_create_and_get_channel(self):
        created = channel_crud.create(self.db, {"handle": "test-handle"})

        self.assertIsNotNone(created.id)
        self.assertEqual(created.handle, "test-handle")

        fetched = channel_crud.get(self.db, created.id)
        self.assertIsInstance(fetched, Channel)
        self.assertEqual(fetched.handle, "test-handle")

    def test_get_multi_and_create_many(self):
        channel_crud.create_many(
            self.db,
            [{"handle": "c1"}, {"handle": "c2"}, {"handle": "c3"}],
        )

        channels = channel_crud.get_multi(self.db)
        self.assertEqual(len(channels), 3)
        handles = {c.handle for c in channels}
        self.assertEqual(handles, {"c1", "c2", "c3"})

    def test_get_by_and_get_by_handle(self):
        channel_crud.create_many(
            self.db,
            [{"handle": "same"}, {"handle": "other1"}, {"handle": "other"}],
        )

        one = channel_crud.get_by(self.db, handle="same")
        self.assertIsNotNone(one)
        self.assertEqual(one.handle, "same")

        by_handle = channel_crud.get_by_handle(self.db, "same")
        self.assertIsNotNone(by_handle)
        self.assertEqual(by_handle.handle, "same")

    def test_update_and_update_many(self):
        c1 = channel_crud.create(self.db, {"handle": "old1"})
        c2 = channel_crud.create(self.db, {"handle": "old2"})

        updated_one = channel_crud.update(self.db, c1, {"handle": "new1"})
        self.assertEqual(updated_one.handle, "new1")

        updated_many = channel_crud.update_many(
            self.db,
            [
                (c1, {"handle": "new1b"}),
                (c2, {"handle": "new2b"}),
            ],
        )
        handles = {c.handle for c in updated_many}
        self.assertEqual(handles, {"new1b", "new2b"})

    def test_delete_and_delete_many(self):
        c1 = channel_crud.create(self.db, {"handle": "d1"})
        c2 = channel_crud.create(self.db, {"handle": "d2"})
        c3 = channel_crud.create(self.db, {"handle": "d3"})

        channel_crud.delete(self.db, c1.id)
        self.assertIsNone(channel_crud.get(self.db, c1.id))

        deleted_count = channel_crud.delete_many(self.db, [c2.id, c3.id])
        self.assertEqual(deleted_count, 2)
        self.assertIsNone(channel_crud.get(self.db, c2.id))
        self.assertIsNone(channel_crud.get(self.db, c3.id))


