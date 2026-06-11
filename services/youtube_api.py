"""
YouTube Data API v3 Service Layer
Handles all API interactions with caching and quota management.
"""

import os
import re
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import isodate
from datetime import datetime

load_dotenv()


def get_api_key():
    """Return YouTube API key.

    Priority order:
    1. Streamlit secrets: `st.secrets["YOUTUBE_API_KEY"]` (recommended on Streamlit Cloud)
    2. Environment variable `YOUTUBE_API_KEY` (useful for local dev or CI)
    3. `.env` file via `load_dotenv()` (local development only)

    Do NOT commit API keys into source control. Add the key in Streamlit Cloud
    as a secret named `YOUTUBE_API_KEY`.
    """
    # 1) Streamlit-managed secrets (Streamlit Cloud)
    try:
        secret_key = st.secrets.get("YOUTUBE_API_KEY") if hasattr(st, "secrets") else None
    except Exception:
        secret_key = None

    if secret_key:
        return secret_key

    # 2) Environment variable / .env
    key = os.getenv("YOUTUBE_API_KEY")
    if key:
        return key

    # Not found — show user-friendly error in the app
    st.error("❌ YouTube API key not found. Add `YOUTUBE_API_KEY` to Streamlit Secrets or your environment.")
    st.stop()
    return None


@st.cache_resource(show_spinner=False)
def get_youtube_client():
    api_key = get_api_key()
    return build("youtube", "v3", developerKey=api_key)


def detect_input_type(user_input: str) -> tuple[str, str]:
    """Auto-detect input type and return (type, identifier)."""
    user_input = user_input.strip()

    # Channel ID
    if re.match(r'^UC[a-zA-Z0-9_-]{22}$', user_input):
        return "channel_id", user_input

    # @Handle
    if user_input.startswith("@"):
        return "handle", user_input.lstrip("@")

    # Full URL patterns
    url_patterns = [
        r'youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})',
        r'youtube\.com/@([a-zA-Z0-9_.-]+)',
        r'youtube\.com/user/([a-zA-Z0-9_.-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_.-]+)',
    ]
    for pattern in url_patterns:
        m = re.search(pattern, user_input)
        if m:
            val = m.group(1)
            if val.startswith("UC") and len(val) == 24:
                return "channel_id", val
            return "handle", val

    # Plain text = treat as handle
    return "handle", user_input


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_channel_data(identifier: str) -> dict | None:
    """Fetch full channel data by ID or handle."""
    yt = get_youtube_client()
    try:
        # Try as channel ID first
        if identifier.startswith("UC") and len(identifier) == 24:
            resp = yt.channels().list(
                part="snippet,statistics,brandingSettings,contentDetails",
                id=identifier
            ).execute()
        else:
            resp = yt.channels().list(
                part="snippet,statistics,brandingSettings,contentDetails",
                forHandle=identifier if not identifier.startswith("UC") else None,
                id=identifier if identifier.startswith("UC") else None
            ).execute()

        if not resp.get("items"):
            # Fallback: try forHandle
            resp = yt.channels().list(
                part="snippet,statistics,brandingSettings,contentDetails",
                forHandle=identifier
            ).execute()

        if not resp.get("items"):
            return None

        item = resp["items"][0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        branding = item.get("brandingSettings", {}).get("image", {})
        channel_branding = item.get("brandingSettings", {}).get("channel", {})

        return {
            "channel_id": item["id"],
            "title": snippet.get("title", "N/A"),
            "description": snippet.get("description", ""),
            "custom_url": snippet.get("customUrl", "N/A"),
            "published_at": snippet.get("publishedAt", ""),
            "country": snippet.get("country", "N/A"),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "banner": branding.get("bannerExternalUrl", ""),
            "subscribers": int(stats.get("subscriberCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "uploads_playlist": item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads", ""),
            "keywords": channel_branding.get("keywords", ""),
            "trailer": channel_branding.get("unsubscribedTrailer", ""),
        }
    except HttpError as e:
        st.error(f"YouTube API Error: {e.reason}")
        return None


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_videos(uploads_playlist_id: str, max_results: int = 100) -> list[dict]:
    """Fetch up to max_results videos from a channel's uploads playlist."""
    yt = get_youtube_client()
    videos = []
    next_page_token = None

    try:
        while len(videos) < max_results:
            batch = min(50, max_results - len(videos))
            resp = yt.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=batch,
                pageToken=next_page_token
            ).execute()

            items = resp.get("items", [])
            video_ids = [item["contentDetails"]["videoId"] for item in items]

            if video_ids:
                stats_resp = yt.videos().list(
                    part="statistics,contentDetails,snippet",
                    id=",".join(video_ids)
                ).execute()

                for v in stats_resp.get("items", []):
                    snippet = v.get("snippet", {})
                    stats = v.get("statistics", {})
                    content = v.get("contentDetails", {})

                    duration_sec = 0
                    try:
                        duration_sec = int(isodate.parse_duration(content.get("duration", "PT0S")).total_seconds())
                    except Exception:
                        pass

                    pub_date = snippet.get("publishedAt", "")
                    dt = None
                    try:
                        dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    except Exception:
                        pass

                    videos.append({
                        "video_id": v["id"],
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "published_at": pub_date,
                        "published_dt": dt,
                        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                        "duration_sec": duration_sec,
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                        "tags": snippet.get("tags", []),
                        "category_id": snippet.get("categoryId", ""),
                    })

            next_page_token = resp.get("nextPageToken")
            if not next_page_token or len(items) == 0:
                break

    except HttpError as e:
        st.error(f"YouTube API Error fetching videos: {e.reason}")

    return videos
