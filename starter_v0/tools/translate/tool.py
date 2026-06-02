from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def translate_text(text: str = "", source_lang: str = "en", target_lang: str = "vi") -> dict[str, Any]:
    try:
        if not text.strip():
            raise ValueError("text is required")
        langpair = f"{source_lang}|{target_lang}"
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": langpair},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        translated = data.get("responseData", {}).get("translatedText", "")
        match_quality = data.get("responseData", {}).get("match")
        alternatives = [
            {"text": m.get("translation", ""), "quality": m.get("quality"), "source": m.get("created-by")}
            for m in (data.get("matches") or [])[:3]
        ]
        return {
            "tool": "translate",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "original": text,
            "translated": translated,
            "match_quality": match_quality,
            "alternatives": alternatives,
        }
    except Exception as exc:
        return err("translate", exc)
