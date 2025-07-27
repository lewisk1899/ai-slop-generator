import os
import argparse
from yt_dlp import YoutubeDL

def download_youtube_video(url: str, output_dir: str = "downloads") -> None:
    """Download a YouTube video to the specified directory."""
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a YouTube video using yt-dlp")
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output-dir', default='downloads', help='Directory to save the video')
    args = parser.parse_args()

    download_youtube_video(args.url, args.output_dir)
