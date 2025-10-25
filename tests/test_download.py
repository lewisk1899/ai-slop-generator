import unittest
import tempfile
from download import download_youtube_video


class TestDownload(unittest.TestCase):
    def test_download_nekk_minut(self):
        # Arrange
        nekk_minutt_url = "https://www.youtube.com/watch?v=CTZyorJVeqI"
        with tempfile.TemporaryDirectory() as tempdir:
            # Act
            video_path = download_youtube_video(nekk_minutt_url, tempdir)
            # Assert
            self.assertEqual(video_path, "downloads/'Nek Minute - Original.mp4'")



