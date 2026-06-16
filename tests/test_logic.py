"""Pure-logic unit tests — no GPU, no mic, no whisper, no network."""
from src.voice_cli.config import DEFAULTS, _deep_merge, load_config
from src.voice_cli.recorder import State, ToggleRecorder
from src.voice_cli.text import clean_transcript


# --- recorder state machine ---
def test_recorder_starts_idle():
    assert ToggleRecorder().state is State.IDLE


def test_recorder_toggles_start_then_stop():
    r = ToggleRecorder()
    assert r.toggle() == "start"
    assert r.is_recording is True
    assert r.toggle() == "stop"
    assert r.is_recording is False


def test_recorder_alternates():
    r = ToggleRecorder()
    assert [r.toggle() for _ in range(4)] == ["start", "stop", "start", "stop"]


# --- transcript cleaning ---
def test_clean_collapses_and_trims():
    assert clean_transcript("  hello   there\n world ") == "hello there world"


def test_clean_empty():
    assert clean_transcript("") == ""
    assert clean_transcript("   ") == ""


# --- config ---
def test_config_defaults_when_no_file():
    cfg = load_config(None)
    assert cfg["hotkey"]["toggle"] == "f9"
    assert cfg["transcriber"]["device"] == "auto"
    assert cfg["injector"]["auto_submit"] is False


def test_deep_merge_overrides_nested_only():
    merged = _deep_merge(DEFAULTS, {"transcriber": {"model": "large-v3"}})
    assert merged["transcriber"]["model"] == "large-v3"
    # untouched siblings survive
    assert merged["transcriber"]["device"] == "auto"
    assert merged["hotkey"]["toggle"] == "f9"


def test_load_config_from_file(tmp_path):
    p = tmp_path / "settings.yaml"
    p.write_text("hotkey:\n  toggle: f8\ntranscriber:\n  device: cpu\n", encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg["hotkey"]["toggle"] == "f8"
    assert cfg["transcriber"]["device"] == "cpu"
    assert cfg["transcriber"]["model"] == "small"  # default preserved
