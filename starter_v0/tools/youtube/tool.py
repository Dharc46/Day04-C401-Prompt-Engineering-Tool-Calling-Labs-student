from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def youtube_search(query: str = "", limit: int = 5, sort_by: str = "relevance") -> dict[str, Any]:
    try:
        if not query.strip():
            raise ValueError("query is required")
        key = os.getenv("RAPIDAPI_KEY")
        host = os.getenv("RAPIDAPI_YOUTUBE_HOST", "youtube138.p.rapidapi.com")
        if not key:
            raise RuntimeError("Missing RAPIDAPI_KEY env var")
        params: dict[str, Any] = {"q": query, "sort": sort_by}
        response = requests.get(
            f"https://{host}/search/",
            params=params,
            headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        raw_items = data.get("contents") or data.get("items") or data.get("results") or []
        items = []
        for item in raw_items[:int(limit or 5)]:
            video = item.get("video") or item
            video_id = video.get("videoId") or video.get("id") or ""
            items.append({
                "title": video.get("title") or "",
                "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
                "channel": (video.get("channelName") or video.get("author") or
                            (video.get("channel") or {}).get("name") or ""),
                "views": video.get("viewCountText") or video.get("views"),
                "published": video.get("publishedTimeText") or video.get("publishedAt"),
                "duration": video.get("lengthText") or video.get("duration"),
                "source": "youtube.com",
            })
        return {"tool": "youtube_search", "query": query, "sort_by": sort_by, "items": items}
    except Exception as exc:
        return err("youtube_search", exc)
