"""Wire the pieces into the running helper: hotkey toggles record -> transcribe -> paste."""
from __future__ import annotations

import logging
import os
import sys
import time

# Quiet noisy Hugging Face Hub warnings before anything imports huggingface_hub.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

# CUDA DLLs must be on PATH before faster_whisper is imported (no-op on CPU).
from .cuda_paths import add_cuda_to_path

CONFIG_PATH = "config/settings.yaml"


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def main() -> None:
    add_cuda_to_path()

    from . import injector
    from .audio import MicRecorder, save_wav
    from .config import load_config
    from .recorder import ToggleRecorder
    from .transcriber import FasterWhisperTranscriber
    from .window import focus_window, get_foreground_window

    cfg = load_config(CONFIG_PATH)
    tcfg, acfg, rcfg = cfg["transcriber"], cfg["audio"], cfg["recordings"]

    _log(f"loading model '{tcfg['model']}' (first run downloads it)...")
    transcriber = FasterWhisperTranscriber(
        model=tcfg["model"],
        device=tcfg["device"],
        compute_type=tcfg["compute_type"],
        language=tcfg["language"],
        vad_filter=tcfg.get("vad_filter", True),
        condition_on_previous_text=tcfg.get("condition_on_previous_text", False),
        beam_size=tcfg.get("beam_size", 5),
        initial_prompt=tcfg.get("initial_prompt"),
    )
    _log(f"model loaded on {transcriber.device.upper()} ({transcriber.compute_type})")

    mic = MicRecorder(sample_rate=acfg["sample_rate"], device=acfg["device"])
    warmup = float(acfg.get("warmup_seconds", 0.4))
    tail = float(acfg.get("tail_seconds", 0.4))
    rec = ToggleRecorder()
    restore = cfg["injector"].get("mode", "clipboard") == "clipboard"
    refocus = cfg["injector"].get("refocus_target", True)
    target = {"hwnd": None}  # window focused when recording started

    def _beep(freq: int, ms: int = 130) -> None:
        try:
            import winsound

            winsound.Beep(freq, ms)
        except Exception:
            pass  # non-Windows or no audio device: skip the cue

    def on_hotkey() -> None:
        try:
            if rec.toggle() == "start":
                if refocus:
                    target["hwnd"] = get_foreground_window()  # remember where to paste
                mic.start()  # open the mic FIRST so anything said during the cue is captured
                time.sleep(warmup)  # warm the stream before cueing
                _beep(1000)  # "go" cue — recorded as a harmless leading tone, ignored by ASR
                _log("[REC] recording... speak now (press hotkey again to stop)")
            else:
                time.sleep(tail)  # capture trailing speech before closing the stream
                audio = mic.stop()
                _beep(600)  # "stopped" cue
                if rcfg.get("save"):
                    os.makedirs(rcfg.get("dir", "recordings"), exist_ok=True)
                    p = os.path.join(rcfg.get("dir", "recordings"), time.strftime("rec_%Y%m%d_%H%M%S.wav"))
                    save_wav(p, audio, acfg["sample_rate"])
                    _log(f"saved {p} ({len(audio) / acfg['sample_rate']:.1f}s)")
                _log("... transcribing")
                text = transcriber.transcribe(audio)
                if text:
                    if refocus and target["hwnd"]:
                        focus_window(target["hwnd"])  # bring the target window back to front
                        time.sleep(0.12)  # let focus settle before pasting
                    injector.paste_text(text, restore_clipboard=restore)
                    _log(f"-> inserted: {text}")
                else:
                    _log("(no speech detected)")
        except Exception as e:  # never let a bad turn kill the listener
            _log(f"!! error: {type(e).__name__}: {e}")

    import keyboard

    key = cfg["hotkey"]["toggle"]
    keyboard.add_hotkey(key, on_hotkey)
    _log(f"ready - press [{key}] to start/stop dictation. Ctrl+C to quit.")
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        _log("bye")


if __name__ == "__main__":
    main()
