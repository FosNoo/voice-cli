"""Make the pip-installed CUDA-12 runtime DLLs loadable by CTranslate2 (Windows + NVIDIA GPU).

CTranslate2's loader searches the process PATH (NOT os.add_dll_directory), so we prepend the
nvidia-*-cu12 wheels' bin/ directories to PATH. This must run before `faster_whisper` is
imported, or GPU inference fails with:
    RuntimeError: Library cublas64_12.dll is not found or cannot be loaded

On CPU-only installs (no nvidia wheels) this is a harmless no-op.
"""
from __future__ import annotations

import glob
import os
import sys


def add_cuda_to_path() -> list[str]:
    """Prepend the venv's nvidia/*/bin dirs to PATH. Returns the dirs added (empty on CPU)."""
    base = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia")
    dirs = sorted(glob.glob(os.path.join(base, "*", "bin")))
    if dirs:
        os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ.get("PATH", "")
    return dirs
