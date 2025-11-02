import unittest
import ffmpeg
import os
from src.trimmer import trim


class TrimTest(unittest.TestCase):

    # Tests:
    # 1. Gets the video clip length
    # 2. Gets the amount of clips that were specified
    # 3. Ensures the naming of the clips are done correctly

    def test_get_video_length(self):

        file_path = "downloads/Nek Minute - Original.mp4"
        VIDEO_LENGTH = 47.438356

        probe_result = ffmpeg.probe(file_path)
        duration = probe_result.get("format", {}).get("duration", None)

        self.assertAlmostEqual(VIDEO_LENGTH, float(duration))

    def test_get_num_clips(self):
        file_path = "downloads/Nek Minute - Original.mp4"
        out_path = "clips"
        time_stamps = [(4, 10), (15, 18)]

        current_dir = os.getcwd() + "/clips"

        # clear the directory
        for filename in os.listdir(current_dir):
            clip_path = os.path.join(current_dir, filename)
            if os.path.isfile(clip_path):
                os.remove(clip_path)

        trim(file_path, out_path, time_stamps)

        num_clips = len(
            [
                entry
                for entry in os.listdir(current_dir)
                if os.path.isfile(os.path.join(current_dir, entry))
            ]
        )

        self.assertEqual(num_clips, 2)

        # clear the directory
        for filename in os.listdir(current_dir):
            clip_path = os.path.join(current_dir, filename)
            if os.path.isfile(clip_path):
                os.remove(clip_path)

    def test_clip_names(self):
        file_path = "downloads/Nek Minute - Original.mp4"
        out_path = "clips"
        time_stamps = [(4, 10)]
        expected_name = "Nek Minute - Original_clip_1.mp4"

        current_dir = os.getcwd() + "/clips"

        # clear the directory
        for filename in os.listdir(current_dir):
            clip_path = os.path.join(current_dir, filename)
            if os.path.isfile(clip_path):
                os.remove(clip_path)

        trim(file_path, out_path, time_stamps)

        clips = [f for f in os.listdir(current_dir) if f.endswith(".mp4")]

        self.assertEqual(len(clips), 1)

        clip_name = clips[0]

        self.assertEqual(clip_name, expected_name)
