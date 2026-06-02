from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.append(str(ROOT / "starter_v0"))

from ui import main

if __name__ == "__main__":
    main()
