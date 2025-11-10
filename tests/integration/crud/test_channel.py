import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.analytics import Base
from src.crud import channel


class TestChannelIntegration(unittest.TestCase):
    """Integration tests for src/client/channel.py CRUD operations."""

    @classmethod
    def setUpClass(cls):
        # In-memory SQLite DB
        cls.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()

    def tearDown(self):
        # Clean up all tables between tests
        for table in reversed(Base.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()
        self.db.close()

    # -----------------------------
    # CREATE
    # -----------------------------
    def test_create_channel(self):
        ch = channel.create(self.db, "LTT")
        self.assertEqual(ch.handle, "LTT")

    def test_create_many_channels(self):
        created = channel.create_many(self.db, ["A", "B", "C"])
        self.assertEqual(len(created), 3)
        handles = [c.handle for c in created]
        self.assertIn("A", handles)
        self.assertIn("C", handles)

    # -----------------------------
    # READ
    # -----------------------------
    def test_get_channel(self):
        channel.create(self.db, "TechTips")
        ch = channel.get(self.db, "TechTips")
        self.assertIsNotNone(ch)
        self.assertEqual(ch.handle, "TechTips")

    def test_get_multi_channels(self):
        channel.create_many(self.db, ["One", "Two"])
        all_channels = channel.get_multi(self.db)
        self.assertEqual(len(all_channels), 2)

    # -----------------------------
    # UPDATE
    # -----------------------------
    def test_update_channel(self):
        channel.create(self.db, "OldName")
        updated = channel.update(self.db, "OldName", new_handle="NewName")
        self.assertEqual(updated.handle, "NewName")

    def test_update_many_channels(self):
        channel.create_many(self.db, ["X", "Y"])
        updates = [{"old_handle": "X", "new_handle": "X1"}, {"old_handle": "Y", "new_handle": "Y1"}]
        updated = channel.update_many(self.db, updates)
        self.assertEqual(len(updated), 2)
        names = [c.handle for c in channel.get_multi(self.db)]
        self.assertIn("X1", names)
        self.assertIn("Y1", names)

    # -----------------------------
    # DELETE
    # -----------------------------
    def test_delete_channel(self):
        channel.create(self.db, "DeleteMe")
        deleted = channel.delete(self.db, "DeleteMe")
        self.assertTrue(deleted)
        remaining = channel.get_multi(self.db)
        self.assertEqual(len(remaining), 0)

    def test_delete_many_channels(self):
        channel.create_many(self.db, ["A", "B", "C"])
        deleted_count = channel.delete_many(self.db, ["A", "B"])
        self.assertEqual(deleted_count, 2)
        remaining = [c.handle for c in channel.get_multi(self.db)]
        self.assertEqual(remaining, ["C"])
