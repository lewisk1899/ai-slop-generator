import os
import subprocess
from typing import List
from src.models.clip import Clips, Clip  # import your Pydantic models


def generate_clips(video_path: str, clips: Clips, output_dir: str = "clips") -> List[str]:
    """
    Generate video clips using ffmpeg.
    Accepts a Pydantic Clips object (list of Clip instances).

    Each Clip defines:
        - start_time: float
        - end_time: float
        - title: str
    """
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.abspath(video_path)
    output_dir = os.path.abspath(output_dir)

    clip_paths = []

    for idx, clip in enumerate(clips.clips):
        start = float(clip.start_time)
        end = float(clip.end_time)
        duration = end - start

        if duration <= 0:
            print(f"Skipping invalid clip {idx}: start={start}, end={end}")
            continue

        title = clip.title or f"clip_{idx}"
        # Sanitize title for filesystem (remove illegal characters)
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in title)
        clip_path = os.path.join(output_dir, f"{safe_title}.mp4")

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
            print(f"[ERROR] ffmpeg failed for clip {idx}:\n{result.stderr.decode()}")
        elif os.path.getsize(clip_path) < 1000:
            print(f"[WARN] Empty/short output for {clip_path}")
        else:
            clip_paths.append(clip_path)

    return clip_paths
