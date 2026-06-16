"""Microphone capture via sounddevice. Thin seam over the OS audio layer."""
from __future__ import annotations

import wave

import numpy as np


def save_wav(path: str, audio: np.ndarray, sample_rate: int) -> None:
    """Write mono float32 audio (-1..1) to a 16-bit PCM WAV for inspection/debug."""
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())


class MicRecorder:
    """Captures mono float32 audio between start() and stop()."""

    def __init__(self, sample_rate: int = 16000, device=None) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self._frames: list[np.ndarray] = []
        self._stream = None

    def start(self) -> None:
        import sounddevice as sd  # imported lazily so tests/config don't need the lib

        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            device=self.device,
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, frames, time_info, status) -> None:  # noqa: ARG002
        self._frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        """Stop capture and return the recorded audio as a 1-D float32 array."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self._frames, axis=0).reshape(-1).astype(np.float32)
