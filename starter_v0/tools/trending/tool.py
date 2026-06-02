from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def get_trending(country: str = "vietnam", limit: int = 10) -> dict[str, Any]:
    try:
        key = os.getenv("RAPIDAPI_KEY")
        host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
        if not key:
            raise RuntimeError("Missing RAPIDAPI_KEY env var")
        response = requests.get(
            f"https://{host}/trending.php",
            params={"country": country},
            headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        raw_trends = data if isinstance(data, list) else data.get("trends") or data.get("timeline") or []
        items = []
        for trend in raw_trends[:int(limit or 10)]:
            if isinstance(trend, dict):
                items.append({
                    "name": trend.get("name") or trend.get("trend") or "",
                    "url": trend.get("url") or "",
                    "tweet_volume": trend.get("tweet_volume") or trend.get("volume"),
                    "category": trend.get("category") or trend.get("domain_label"),
                })
            elif isinstance(trend, str):
                items.append({"name": trend, "url": "", "tweet_volume": None, "category": None})
        return {"tool": "trending", "country": country, "items": items}
    except Exception as exc:
        return err("trending", exc)
