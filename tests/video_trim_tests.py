import unittest
import ffmpeg
from trimmer import trim


class TrimTest(unittest.TestCase):

    # Tests:
    # 1. Gets the video clip length
    # 2. Gets the amount of clips that were specified
    # 3. Ensures the naming of the clips are done correctly

    def test_get_video_length(self):

        file_path = "../downloads/Nek Minute - Original.mp4"
        VIDEO_LENGTH = 47.438356

        probe_result = ffmpeg.probe(file_path)
        duration = probe_result.get("format", {}).get("duration", None)

        self.assertAlmostEquals(video_length, duration)

    def test_get_num_clips(self):
        file_path = "../downloads/Nek Minute - Original.mp4"
        out_path = "../clips"
        time_stamps = [(4, 10), (15, 18)]
        trim(file_path, out_path, time_stamps)
        pass


if __name__ == "__main__":
    unittest.main()
