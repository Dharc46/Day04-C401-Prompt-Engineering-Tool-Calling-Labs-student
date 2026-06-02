from __future__ import annotations

from collections import Counter
import re
from typing import Any


def entity_extract(text: str, top_k: int = 10) -> dict[str, Any]:
    """Simple heuristic entity extraction: sequences of Capitalized words.

    Returns {'entities': [{'text': str, 'count': int}, ...]} or {'error':...}
    """
    if not text:
        return {"entities": []}

    # Find sequences of capitalized words (including acronyms)
    matches = re.findall(r"\b(?:[A-Z][a-z0-9]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z0-9]+|[A-Z]{2,}))*\b", text)
    cleaned = [m.strip() for m in matches if len(m.strip()) > 1]
    counts = Counter(cleaned)
    entities = [{"text": ent, "count": cnt} for ent, cnt in counts.most_common(top_k)]
    return {"entities": entities}
