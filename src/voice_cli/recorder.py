"""The press-to-toggle recording state machine. Pure logic — unit tested (no audio)."""
from __future__ import annotations

from enum import Enum


class State(Enum):
    IDLE = "idle"
    RECORDING = "recording"


class ToggleRecorder:
    """Tracks idle<->recording. `toggle()` returns the action to perform."""

    def __init__(self) -> None:
        self.state = State.IDLE

    @property
    def is_recording(self) -> bool:
        return self.state is State.RECORDING

    def toggle(self) -> str:
        """Flip state. Returns 'start' (now recording) or 'stop' (now idle)."""
        if self.state is State.IDLE:
            self.state = State.RECORDING
            return "start"
        self.state = State.IDLE
        return "stop"
