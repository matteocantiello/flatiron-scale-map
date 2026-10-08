"""Register the bundled Instrument Sans / Instrument Serif fonts with Matplotlib.

The fonts live in ``<repo>/fonts`` under the SIL Open Font License (see the
OFL-*.txt files there). If they are missing, Matplotlib falls back to its
default sans-serif and a warning is issued.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from matplotlib import font_manager

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SANS = "Instrument Sans"
SERIF = "Instrument Serif"
_FILES = ("InstrumentSans-Regular.ttf", "InstrumentSans-Bold.ttf",
          "InstrumentSerif-Regular.ttf", "InstrumentSerif-Italic.ttf")
_registered = False


def register() -> bool:
    """Add the bundled fonts to Matplotlib's font manager (idempotent)."""
    global _registered
    if _registered:
        return True
    missing = [f for f in _FILES if not (FONT_DIR / f).exists()]
    if missing:
        warnings.warn(f"bundled fonts missing ({', '.join(missing)}); falling back to defaults")
        return False
    for f in _FILES:
        font_manager.fontManager.addfont(str(FONT_DIR / f))
    _registered = True
    return True
