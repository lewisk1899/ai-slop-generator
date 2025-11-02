from typing import List, Dict
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os


def generate_clips(
    video_path: str, segments: List[Dict[str, float]], output_dir: str = "clips"
) -> List[str]:
    """Generate video clips based on the provided segments."""
    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []
    for idx, segment in enumerate(segments):
        start = float(segment["start_time"])
        end = float(segment["end_time"])
        clip_path = os.path.join(output_dir, f"{segment["title"]}.mp4")
        ffmpeg_extract_subclip(video_path, start, end)
        clip_paths.append(clip_path)
    return clip_paths
