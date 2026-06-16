"""Speech-to-text seam. Default impl = faster-whisper (CTranslate2), GPU or CPU."""
from __future__ import annotations

from typing import Protocol

import numpy as np

from .text import clean_transcript


class Transcriber(Protocol):
    def transcribe(self, audio: np.ndarray) -> str: ...


def _resolve_device(device: str) -> str:
    """'auto' -> 'cuda' if an NVIDIA GPU is usable, else 'cpu'."""
    if device and device != "auto":
        return device
    try:
        import ctranslate2

        return "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    except Exception:
        return "cpu"


def _resolve_compute_type(compute_type: str, device: str) -> str:
    """'auto' -> 'float16' on CUDA, 'int8' on CPU."""
    if compute_type and compute_type != "auto":
        return compute_type
    return "float16" if device == "cuda" else "int8"


class FasterWhisperTranscriber:
    """Wraps a faster-whisper model. Loads eagerly so the hotkey path is fast.

    On CUDA, cuda_paths.add_cuda_to_path() must have run before constructing this.
    """

    def __init__(
        self,
        model: str = "small",
        device: str = "auto",
        compute_type: str = "auto",
        language: str | None = "en",
        vad_filter: bool = True,
        condition_on_previous_text: bool = False,
        beam_size: int = 5,
        initial_prompt: str | None = None,
    ) -> None:
        from faster_whisper import WhisperModel

        self.device = _resolve_device(device)
        self.compute_type = _resolve_compute_type(compute_type, self.device)
        self.language = language
        self.vad_filter = vad_filter
        self.condition_on_previous_text = condition_on_previous_text
        self.beam_size = beam_size
        self.initial_prompt = initial_prompt
        self._model = WhisperModel(model, device=self.device, compute_type=self.compute_type)

    def transcribe(self, audio: np.ndarray) -> str:
        if audio is None or len(audio) == 0:
            return ""
        segments, _info = self._model.transcribe(
            audio,
            language=self.language,
            vad_filter=self.vad_filter,
            condition_on_previous_text=self.condition_on_previous_text,
            beam_size=self.beam_size,
            initial_prompt=self.initial_prompt,
        )
        return clean_transcript("".join(seg.text for seg in segments))
