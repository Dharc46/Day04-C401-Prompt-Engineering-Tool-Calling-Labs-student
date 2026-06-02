from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def search_github(query: str = "", sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    try:
        if not query.strip():
            raise ValueError("query is required")
        sort = sort if sort in {"stars", "updated", "forks"} else "stars"
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": query, "sort": sort, "order": "desc", "per_page": int(limit or 5)},
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = []
        for repo in data.get("items", []):
            items.append({
                "name": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "description": repo.get("description", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language"),
                "updated": repo.get("updated_at"),
                "source": "github.com",
            })
        return {
            "tool": "github_search",
            "query": query,
            "sort": sort,
            "total_count": data.get("total_count", 0),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)
