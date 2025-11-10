from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from loguru import logger
import os
import argparse
import time
import sys

load_dotenv()

# Configure loguru
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}")

def resolve_channel_id(youtube, handle_or_id: str) -> str:
    """
    Accepts either a channel handle (e.g. @GoogleDevelopers) or a channel ID (UCxxxx).
    Returns the canonical channelId.
    """
    try:
        if handle_or_id.startswith("@"):
            logger.debug(f"Resolving channel handle: {handle_or_id}")
            ch = youtube.channels().list(part="id", forHandle=handle_or_id).execute()
            if not ch.get("items"):
                raise ValueError(f"Handle not found: {handle_or_id}")
            return ch["items"][0]["id"]

        # Try direct channel ID
        logger.debug(f"Resolving channel ID: {handle_or_id}")
        ch = youtube.channels().list(part="id", id=handle_or_id).execute()
        if not ch.get("items"):
            raise ValueError(f"Channel ID not found: {handle_or_id}")
        return ch["items"][0]["id"]

    except Exception as e:
        logger.error(f"Error resolving channel '{handle_or_id}': {e}")
        raise


def month_window_iso(month: str = None, days: int = None):
    """
    Returns (publishedAfter, publishedBefore) in RFC3339.
    - If month like '2025-10' is provided, use that calendar month.
    - Else use the last N days (default 30).
    """
    try:
        if month:
            start = datetime.fromisoformat(month + "-01").replace(tzinfo=timezone.utc)
            end = start + relativedelta(months=1)
        else:
            if not days:
                days = 30
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
        logger.debug(f"Date window: {start.isoformat()} → {end.isoformat()}")
        return start.isoformat(), end.isoformat()
    except Exception as e:
        logger.error(f"Failed to compute month window: {e}")
        raise


def list_recent_video_ids(youtube, channel_id: str, published_after: str, published_before: str):
    """
    Use the Search API to list video IDs published in the date window.
    """
    ids = []
    token = None
    try:
        while True:
            resp = (
                youtube.search()
                .list(
                    part="id",
                    channelId=channel_id,
                    publishedAfter=published_after,
                    publishedBefore=published_before,
                    type="video",
                    order="date",
                    maxResults=50,
                    pageToken=token,
                )
                .execute()
            )
            for it in resp.get("items", []):
                vid = it["id"].get("videoId")
                if vid:
                    ids.append(vid)
            token = resp.get("nextPageToken")
            if not token:
                break
        logger.info(f"Found {len(ids)} videos for channel {channel_id}")
    except Exception as e:
        logger.error(f"Error listing recent videos for channel {channel_id}: {e}")
    return ids


def fetch_video_metadata(youtube, video_ids: list[str]):
    """
    Batch fetch snippet + statistics for given IDs.
    Returns list of dicts with views, title, url, publishedAt.
    """
    rows = []
    try:
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            vi = (
                youtube.videos()
                .list(part="snippet,statistics", id=",".join(chunk), maxResults=50)
                .execute()
            )
            for v in vi.get("items", []):
                vid = v["id"]
                sn = v.get("snippet", {})
                st = v.get("statistics", {})
                title = sn.get("title", "")
                url = f"https://www.youtube.com/watch?v={vid}"
                views = int(st.get("viewCount", 0))
                published = sn.get("publishedAt", "")
                rows.append(
                    {
                        "views": views,
                        "title": title,
                        "url": url,
                        "publishedAt": published,
                        "id": vid,
                    }
                )
        logger.info(f"Fetched metadata for {len(rows)} videos")
    except Exception as e:
        logger.error(f"Error fetching video metadata: {e}")
    return rows


def update_database(db=None, analytics=None):
    logger.debug("update_database() placeholder called.")
    pass


def pull_analytics(args):
    try:
        youtube = build("youtube", "v3", developerKey=args.google_api_key)
    except Exception as e:
        logger.critical(f"Failed to initialize YouTube API client: {e}")
        return

    for channel in args.channels:
        try:
            logger.info(f"Processing channel: {channel}")
            channel_id = resolve_channel_id(youtube, channel)
            published_after, published_before = month_window_iso(args.month, args.days)

            video_ids = list_recent_video_ids(youtube, channel_id, published_after, published_before)
            if not video_ids:
                logger.warning(f"No videos found for {channel} in the specified window.")
                continue

            rows = fetch_video_metadata(youtube, video_ids)
            rows.sort(key=lambda r: r["views"], reverse=True)
            limit = args.top if args.top and args.top > 0 else len(rows)

            update_database(None, None)  # Placeholder

            for r in rows[:limit]:
                logger.info(f'{r["views"]:>10} | {r["publishedAt"]} | {r["title"]} | {r["url"]}')

        except Exception as e:
            logger.error(f"Failed to process channel {channel}: {e}")
            continue


def parse_arguments():
    ap = argparse.ArgumentParser(
        description="List a channel’s videos within a month, sorted by views desc."
    )
    ap.add_argument(
        "--channels",
        nargs="+",
        required=True,
        help="Channel handle (@foo) or channel ID (UCxxxx)",
    )
    ap.add_argument(
        "--google-api-key",
        type=str,
        default=os.getenv("GOOGLE_API_KEY"),
        help="Google API Key to access youtube metadata.",
    )
    ap.add_argument(
        "--database-host",
        type=str,
        default="localhost",
        help="Database hostname (default is localhost).",
    )
    ap.add_argument(
        "--database-port",
        type=str,
        default="8080",
        help="Database port (default is 8080).",
    )
    ap.add_argument(
        "--month",
        help="Calendar month YYYY-MM (e.g., 2025-10). If omitted, uses last --days.",
    )
    ap.add_argument(
        "--days",
        type=int,
        default=30,
        help="Days back if --month not provided (default 30).",
    )
    ap.add_argument(
        "--sleep",
        type=int,
        default=12 * 60 * 60,
        help="Sleep interval between analytics pulls (default 12h).",
    )
    ap.add_argument("--top", type=int, default=0, help="If >0, only print top N.")
    return ap.parse_args()


def main():
    args = parse_arguments()

    # Log runtime configuration (safe, no secrets)
    sleep_hours = args.sleep / 3600 if args.sleep > 3600 else args.sleep
    sleep_unit = "hours" if args.sleep > 3600 else "seconds"
    channels_str = ", ".join(args.channels) if isinstance(args.channels, list) else args.channels

    logger.info("Starting YouTube Analytics container with configuration:")
    logger.info(f"  Channels: {channels_str}")
    logger.info(f"  Days: {args.days}")
    logger.info(f"  Top: {args.top}")
    logger.info(f"  Sleep interval: {sleep_hours:.1f} {sleep_unit}")

    # Sanity check for API key
    if not args.google_api_key or args.google_api_key.strip() == "":
        logger.critical("Missing Google API key. Please set GOOGLE_API_KEY in your environment or .env file.")
        sys.exit(1)

    while True:
        try:
            pull_analytics(args)
            logger.info(f"Sleeping for {args.sleep / 3600:.1f} hours...")
            time.sleep(args.sleep)
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
