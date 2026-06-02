from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET
import requests


def rss_summary(url: str, limit: int = 5) -> dict[str, Any]:
    """Fetch an RSS/Atom feed and return a short summary list.

    Returns dict with either `items` (list) or `error`.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        return {"error": "fetch_failed", "message": str(exc)}

    try:
        root = ET.fromstring(resp.content)
    except Exception as exc:
        return {"error": "parse_failed", "message": str(exc)}

    items = []
    # RSS: channel/item ; Atom: entry
    # search for item or entry tags
    for elem in root.findall('.//item')[:limit]:
        title = elem.findtext('title') or ''
        link = elem.findtext('link') or ''
        desc = elem.findtext('description') or ''
        items.append({"title": title.strip(), "url": link.strip(), "summary": desc.strip()})

    if not items:
        for elem in root.findall('.//{http://www.w3.org/2005/Atom}entry')[:limit]:
            title = elem.findtext('{http://www.w3.org/2005/Atom}title') or ''
            link_elem = elem.find('{http://www.w3.org/2005/Atom}link')
            link = link_elem.get('href') if link_elem is not None else ''
            summary = elem.findtext('{http://www.w3.org/2005/Atom}summary') or elem.findtext('{http://www.w3.org/2005/Atom}content') or ''
            items.append({"title": title.strip(), "url": link.strip(), "summary": summary.strip()})

    return {"items": items[:limit]}
