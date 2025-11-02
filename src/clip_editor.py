from typing import List, Dict
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import subprocess

def generate_clips(
    video_path: str, segments: List[Dict[str, float]], output_dir: str = "clips"
) -> List[str]:
    """
    Generate video clips using ffmpeg via subprocess.
    Each segment dict should contain:
        - "start_time": float
        - "end_time": float
        - optional "title": str
    """
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.abspath(video_path)
    output_dir = os.path.abspath(output_dir)

    clip_paths = []

    for idx, segment in enumerate(segments):
        start = float(segment["start_time"])
        end = float(segment["end_time"])
        duration = end - start

        if duration <= 0:
            print(f"Skipping invalid segment {idx}: start={start}, end={end}")
            continue

        title = segment.get("title", f"clip_{idx}")
        clip_path = os.path.join(output_dir, f"{title}.mp4")

        cmd = [
            "ffmpeg",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(duration),
            "-c", "copy",   # no re-encoding; fast
            "-y",           # overwrite if exists
            clip_path,
        ]

        print(f"Extracting {start:.2f}–{end:.2f} sec → {clip_path}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print(f"ffmpeg failed for segment {idx}:\n{result.stderr.decode()}")
        elif os.path.getsize(clip_path) < 1000:
            print(f" Empty/short output for {clip_path}")
        else:
            clip_paths.append(clip_path)

    return clip_paths
