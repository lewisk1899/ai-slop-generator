import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
import sys

from crud.crud import video_crud, channel_crud
from process_video import run_pipeline_from_url   # your DI-driven pipeline

from datetime import datetime


# -----------------------------
# Pipeline Runner (DI)
# -----------------------------
class PipelineRunner:
    def run(self, url: str):
        return run_pipeline_from_url(url)


# -----------------------------
# Video Processing Service 
# -----------------------------
class VideoProcessingService:
    def __init__(self, pipeline_runner: PipelineRunner):
        self.pipeline_runner = pipeline_runner

    def process_next_for_channel(self, db, channel_handle: str):
        channel = channel_crud.get_by_handle(db, channel_handle)
        if not channel:
            print(f"Channel not found: {channel_handle}")
            return None

        # USE CRUD METHOD (DI not applied to CRUD)
        video = video_crud.get_top_unprocessed_from_channel(db, channel.id)
        if video is None:
            print(f"No unprocessed videos for channel {channel_handle}")
            return None

        print(f"Processing video: {video.title}")

        self.pipeline_runner.run(video.url)

        video_crud.mark_processed(db, video.id)

        print(f"Finished video: {video.title}")
        return video

# -----------------------------
# Scheduler Loop
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the environment")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

PROCESS_INTERVAL_HOURS = float(os.getenv("PROCESS_INTERVAL_HOURS", 6))

# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Process top unprocessed video for a channel"
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="Channel handle (e.g. @GoogleDevelopers)"
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run forever every X hours"
    )
    args = parser.parse_args()

    runner = PipelineRunner()
    service = VideoProcessingService(runner)

    if not args.loop:
        # one-shot processing
        with SessionLocal() as db:
            service.process_next_for_channel(db, args.channel)
        return

    # scheduled loop
    while True:
        with SessionLocal() as db:
            service.process_next_for_channel(db, args.channel)

        print(f"Sleeping {PROCESS_INTERVAL_HOURS} hours...")
        time.sleep(PROCESS_INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    main()
