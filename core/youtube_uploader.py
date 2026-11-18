#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
core/youtube_uploader.py — Automated YouTube Video & Thumbnail Upload Client.
Designed for headless execution in GitHub Actions CI/CD and local pipelines.
"""

import os
import sys
import time
import random
import argparse
from datetime import datetime
from dotenv import load_dotenv

# UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

CATEGORY_MAPPING = {
    "film & animation": "1",
    "autos & vehicles": "2",
    "music": "10",
    "pets & animals": "15",
    "sports": "17",
    "travel & events": "19",
    "gaming": "20",
    "people & blogs": "22",
    "comedy": "23",
    "entertainment": "24",
    "news & politics": "25",
    "howto & style": "26",
    "education": "27",
    "science & technology": "28",
    "nonprofits & activism": "29",
}

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 10


def get_youtube_client(client_id: str = None, client_secret: str = None, refresh_token: str = None):
    """Builds an authenticated YouTube Data API v3 client using OAuth2 refresh token."""
    cid = client_id or os.environ.get("YOUTUBE_CLIENT_ID")
    csec = client_secret or os.environ.get("YOUTUBE_CLIENT_SECRET")
    rtoken = refresh_token or os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if cid:
        cid = cid.strip().lstrip("\ufeff")
    if csec:
        csec = csec.strip().lstrip("\ufeff")
    if rtoken:
        rtoken = rtoken.strip().lstrip("\ufeff")

    if not (cid and csec and rtoken):
        raise ValueError(
            "Missing YouTube credentials! Ensure YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, "
            "and YOUTUBE_REFRESH_TOKEN are set in .env or GitHub Secrets."
        )

    creds = Credentials(
        token=None,
        refresh_token=rtoken,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cid,
        client_secret=csec,
        scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"],
    )

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_thumbnail(youtube, video_id: str, thumbnail_path: str) -> bool:
    """Uploads a custom thumbnail to an uploaded YouTube video."""
    if not os.path.exists(thumbnail_path):
        print(f"⚠️ Thumbnail file not found: {thumbnail_path}")
        return False

    print(f"🖼️ Uploading custom thumbnail: {thumbnail_path}")
    try:
        media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg", resumable=True)
        request = youtube.thumbnails().set(videoId=video_id, media_body=media)
        request.execute()
        print("✅ Custom thumbnail uploaded successfully!")
        return True
    except Exception as e:
        print(f"⚠️ Failed to upload thumbnail: {e}")
        return False


def upload_video(
    video_path: str,
    title: str = None,
    description: str = None,
    tags: list = None,
    category: str = "Entertainment",
    privacy_status: str = "unlisted",
    thumbnail_path: str = None,
    contains_synthetic_media: bool = True,
    client_id: str = None,
    client_secret: str = None,
    refresh_token: str = None,
) -> dict:
    """
    Uploads a video to YouTube with resumable chunked upload and synthetic media disclosure.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"\n📤 Starting YouTube upload:")
    print(f"   Video: {video_path} ({file_size_mb:.2f} MB)")
    print(f"   Privacy: {privacy_status}")

    youtube = get_youtube_client(client_id, client_secret, refresh_token)

    # Title cleanup
    if not title:
        title = os.path.splitext(os.path.basename(video_path))[0].replace("_", " ").title()
    clean_title = title[:100]

    # Category ID
    category_id = CATEGORY_MAPPING.get(category.lower(), "24")

    # Tags
    if not tags:
        tags = ["StoryFlow", "Animation", "Documentary", "AIStory"]

    body = {
        "snippet": {
            "title": clean_title,
            "description": description or f"{clean_title}\n\nGenerated with StoryFlow AI.",
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": contains_synthetic_media,
        },
    }

    media = MediaFileUpload(
        video_path,
        chunksize=10 * 1024 * 1024,
        resumable=True,
        mimetype="video/mp4",
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    retry_count = 0

    print("🚀 Uploading chunks...")
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"   Progress: {int(status.progress() * 100)}%")
        except googleapiclient.errors.HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    raise Exception(f"Upload failed after {MAX_RETRIES} retries: {e}")
                sleep_sec = (2 ** retry_count) + random.random()
                print(f"⚠️ Network error ({e}), retrying in {sleep_sec:.1f}s...")
                time.sleep(sleep_sec)
            else:
                raise
        except Exception as e:
            retry_count += 1
            if retry_count > MAX_RETRIES:
                raise Exception(f"Upload failed after {MAX_RETRIES} retries: {e}")
            sleep_sec = (2 ** retry_count) + random.random()
            print(f"⚠️ Retry error: {e}, waiting {sleep_sec:.1f}s...")
            time.sleep(sleep_sec)

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n🎉 Video successfully uploaded to YouTube!")
    print(f"🆔 Video ID:  {video_id}")
    print(f"🔗 Watch URL: {video_url}")

    if thumbnail_path:
        upload_thumbnail(youtube, video_id, thumbnail_path)

    # Append to GitHub Actions summary if available
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path and os.path.exists(os.path.dirname(summary_path)):
        try:
            with open(summary_path, "a", encoding="utf-8") as f:
                f.write(f"\n## 🎬 YouTube Video Uploaded!\n")
                f.write(f"- **Title:** {clean_title}\n")
                f.write(f"- **Privacy:** `{privacy_status}`\n")
                f.write(f"- **Watch URL:** [{video_url}]({video_url})\n\n")
        except Exception as ex:
            print(f"Notice: Failed to write summary: {ex}")

    return {
        "status": "success",
        "video_id": video_id,
        "video_url": video_url,
        "title": clean_title,
        "privacy": privacy_status,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="YouTube Uploader for StoryFlow.")
    parser.add_argument("--video", type=str, required=True, help="Path to MP4 video.")
    parser.add_argument("--title", type=str, default=None, help="Video title.")
    parser.add_argument("--desc", type=str, default="", help="Video description.")
    parser.add_argument("--tags", type=str, default=None, help="Comma-separated tags.")
    parser.add_argument("--category", type=str, default="Entertainment", help="Category.")
    parser.add_argument("--privacy", type=str, choices=["private", "unlisted", "public"], default="unlisted", help="Privacy.")
    parser.add_argument("--thumbnail", type=str, default=None, help="Custom thumbnail JPEG/PNG.")
    args = parser.parse_args()

    tags_list = [t.strip() for t in args.tags.split(",")] if args.tags else None

    result = upload_video(
        video_path=args.video,
        title=args.title,
        description=args.desc,
        tags=tags_list,
        category=args.category,
        privacy_status=args.privacy,
        thumbnail_path=args.thumbnail,
    )
    print(f"\n✅ Result: {result['video_url']}")


if __name__ == "__main__":
    main()
