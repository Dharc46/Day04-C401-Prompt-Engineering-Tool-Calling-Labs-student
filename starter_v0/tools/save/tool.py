from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


SAVE_DIR = ROOT / "saved"


def save_to_file(content: str = "", filename: str = "", format: str = "md") -> dict[str, Any]:
    try:
        if not content.strip():
            raise ValueError("content is required")
        format = format if format in {"txt", "md", "json"} else "md"
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_{timestamp}.{format}"
        elif not filename.endswith(f".{format}"):
            filename = f"{filename}.{format}"
        filepath = SAVE_DIR / filename
        filepath.write_text(content, encoding="utf-8")
        return {
            "tool": "save",
            "filename": filename,
            "path": str(filepath),
            "format": format,
            "size_bytes": filepath.stat().st_size,
            "message": f"Saved to {filepath}",
        }
    except Exception as exc:
        return err("save", exc)
