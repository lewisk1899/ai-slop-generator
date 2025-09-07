import argparse
from download import download_youtube_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a YouTube video using yt-dlp")
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output-dir', default='downloads', help='Directory to save the video')
    args = parser.parse_args()

    download_youtube_video(args.url, args.output_dir)
