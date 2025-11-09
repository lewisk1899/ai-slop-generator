from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os
import argparse
import time

load_dotenv("ai-slop.env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def resolve_channel_id(youtube, handle_or_id: str) -> str:
    """
    Accepts either a channel handle (e.g. @GoogleDevelopers) or a channel ID (UCxxxx).
    Returns the canonical channelId.
    """
    if handle_or_id.startswith("@"):
        ch = youtube.channels().list(part="id", forHandle=handle_or_id).execute()
        if not ch.get("items"):
            raise ValueError(f"Handle not found: {handle_or_id}")
        return ch["items"][0]["id"]
    # Try direct channel ID
    ch = youtube.channels().list(part="id", id=handle_or_id).execute()
    if not ch.get("items"):
        raise ValueError(f"Channel ID not found: {handle_or_id}")
    return ch["items"][0]["id"]


def month_window_iso(month: str = None, days: int = None):
    """
    Returns (publishedAfter, publishedBefore) in RFC3339.
    - If month like '2025-10' is provided, use that calendar month.
    - Else use the last N days (default 30).
    """
    if month:
        start = datetime.fromisoformat(month + "-01").replace(tzinfo=timezone.utc)
        end = start + relativedelta(months=1)
    else:
        if not days:
            days = 30
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def list_recent_video_ids(
    youtube, channel_id: str, published_after: str, published_before: str
):
    """
    Use the Search API to list video IDs published in the date window.
    """
    ids = []
    token = None
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
    return ids


def fetch_video_metadata(youtube, video_ids: list[str]):
    """
    Batch fetch snippet + statistics for given IDs.
    Returns list of dicts with views, title, url, publishedAt.
    """
    rows = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
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
    return rows

def update_database(db = None, analytics = None):
    pass

def pull_analytics(args):
    youtube = build("youtube", "v3", developerKey=GOOGLE_API_KEY)
    for channel in args.channels:
        channel_id = resolve_channel_id(youtube, channel)

        published_after, published_before = month_window_iso(args.month, args.days)
        video_ids = list_recent_video_ids(
            youtube, channel_id, published_after, published_before
        )

        if not video_ids:
            print("No videos found in the specified window.")
            return

        rows = fetch_video_metadata(youtube, video_ids)
        rows.sort(key=lambda r: r["views"], reverse=True)

        limit = args.top if args.top and args.top > 0 else len(rows)
        update_database(None, None) # Placeholder function for updating the database.
        for r in rows[:limit]:
            print(f'{r["views"]:>10} | {r["publishedAt"]} | {r["title"]} | {r["url"]}')


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
        help="Days back if --month not provided (default 30).",
    )

    ap.add_argument("--top", type=int, default=0, help="If >0, only print top N.")
    return ap.parse_args()


def main():
    args = parse_arguments()

    while True:
        pull_analytics(args)
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
