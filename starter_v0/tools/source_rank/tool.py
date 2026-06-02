from __future__ import annotations

from typing import Any

from tools._shared import domain, terms


PRIMARY_DOMAIN_HINTS = (
    ".gov",
    ".edu",
    "arxiv.org",
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "microsoft.com",
    "meta.com",
    "nvidia.com",
)


def _source_key(item: dict[str, Any]) -> str:
    url = str(item.get("url") or "").strip().lower()
    if url:
        return url.rstrip("/")
    title = str(item.get("title") or "").strip().lower()
    source = str(item.get("source") or "").strip().lower()
    return f"{source}:{title}"


def _primary_boost(item: dict[str, Any]) -> float:
    source = str(item.get("source") or domain(str(item.get("url") or ""))).lower()
    url = str(item.get("url") or "").lower()
    combined = f"{source} {url}"
    return 0.2 if any(hint in combined for hint in PRIMARY_DOMAIN_HINTS) else 0.0


def _score_item(item: dict[str, Any], query_terms: set[str], prefer_primary: bool) -> float:
    text = " ".join(str(item.get(key) or "") for key in ("title", "source", "summary", "url"))
    item_terms = terms(text)
    overlap = len(query_terms & item_terms)
    relevance = overlap / max(len(query_terms), 1)
    upstream_score = item.get("score")
    try:
        upstream = min(max(float(upstream_score), 0.0), 1.0) * 0.25
    except (TypeError, ValueError):
        upstream = 0.0
    primary = _primary_boost(item) if prefer_primary else 0.0
    has_url = 0.1 if item.get("url") else 0.0
    return round(relevance + upstream + primary + has_url, 4)


def rank_sources(
    items: list[dict[str, Any]] | None = None,
    query: str = "",
    top_k: int = 5,
    prefer_primary: bool = True,
) -> dict[str, Any]:
    query_terms = terms(query)
    seen: set[str] = set()
    ranked: list[dict[str, Any]] = []

    for item in items or []:
        if not isinstance(item, dict):
            continue
        key = _source_key(item)
        if key in seen:
            continue
        seen.add(key)
        scored = dict(item)
        scored["rank_score"] = _score_item(scored, query_terms, bool(prefer_primary))
        scored["source"] = scored.get("source") or domain(str(scored.get("url") or ""))
        ranked.append(scored)

    ranked.sort(key=lambda item: item.get("rank_score", 0), reverse=True)
    limit = max(int(top_k or 5), 0)
    return {
        "tool": "source_rank",
        "query": query,
        "item_count": len(ranked[:limit]),
        "items": ranked[:limit],
    }
