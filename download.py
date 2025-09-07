from yt_dlp import YoutubeDL
import os

def download_youtube_video(url: str, output_dir: str = "downloads") -> str:
    """Download a YouTube video to the specified directory."""
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)

    return video_path
