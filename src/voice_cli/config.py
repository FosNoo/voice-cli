"""Load settings.yaml over built-in defaults. Pure + testable (no I/O beyond an optional path)."""
from __future__ import annotations

import copy
import os
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "hotkey": {"toggle": "f9"},
    "audio": {
        "device": None,
        "sample_rate": 16000,
        "warmup_seconds": 0.4,
        "tail_seconds": 0.4,
    },
    "transcriber": {
        "engine": "faster-whisper",
        "model": "small",        # cross-platform default; use large-v3 on a GPU for best accuracy
        "device": "auto",        # auto -> CUDA if available, else CPU
        "compute_type": "auto",  # auto -> float16 on CUDA, int8 on CPU
        "language": "en",
        "vad_filter": True,
        "condition_on_previous_text": False,
        "beam_size": 5,
        "initial_prompt": None,
    },
    "injector": {"mode": "clipboard", "auto_submit": False, "refocus_target": True},
    "recordings": {"save": False, "dir": "recordings"},
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge `override` into a copy of `base`."""
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: str | None = None) -> dict[str, Any]:
    """Return DEFAULTS, deep-merged with the YAML at `path` if it exists."""
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
        return _deep_merge(DEFAULTS, user)
    return copy.deepcopy(DEFAULTS)
