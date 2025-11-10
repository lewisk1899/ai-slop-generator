import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.client.graphql_client import GraphQLClient


class TestGraphQLClientUnit(unittest.TestCase):
    """Unit tests for GraphQLClient (mocked HTTP)."""

    def setUp(self):
        self.client = GraphQLClient("http://fake/graphql")

    @patch("src.client.graphql_client.requests.post")
    def test_add_channel(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"addChannel": {"id": 1, "handle": "LTT"}}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.add_channel("LTT")
        mock_post.assert_called_once()
        self.assertEqual(result["handle"], "LTT")

    @patch("src.client.graphql_client.requests.post")
    def test_add_video(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"addVideo": {"id": 5, "title": "GPU Review"}}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = self.client.add_video(
            handle="LTT",
            title="GPU Review",
            views=9999,
            published_at=datetime(2025, 1, 1),
            url="http://youtube.com/ltt",
        )
        mock_post.assert_called_once()
        self.assertEqual(res["title"], "GPU Review")

    @patch("src.client.graphql_client.requests.post")
    def test_get_channels(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"channels": [{"handle": "LTT"}]}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_channels()
        self.assertEqual(result[0]["handle"], "LTT")

    @patch("src.client.graphql_client.requests.post")
    def test_delete_channel(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"deleteChannel": True}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.delete_channel("LTT")
        self.assertTrue(result)

    @patch("src.client.graphql_client.requests.post")
    def test_error_raises_exception(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Something went wrong"}]}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            self.client.add_channel("BadChannel")
