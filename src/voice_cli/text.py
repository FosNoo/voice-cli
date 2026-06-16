"""Transcript post-processing. Pure functions — unit tested."""
from __future__ import annotations

import re


def clean_transcript(text: str) -> str:
    """Trim and collapse whitespace from raw whisper output into a single tidy line."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()
