"""Put transcribed text into the focused window as EDITABLE text (never auto-submit).

Default = clipboard-paste: copy text, simulate Ctrl+V, then restore the prior clipboard.
The text lands at the cursor in whatever has focus; the user reviews and presses Enter
themselves.
"""
from __future__ import annotations

import time


def paste_text(text: str, restore_clipboard: bool = True, settle: float = 0.08) -> None:
    if not text:
        return
    import keyboard
    import pyperclip

    previous = None
    if restore_clipboard:
        try:
            previous = pyperclip.paste()
        except Exception:
            previous = None

    pyperclip.copy(text)
    time.sleep(settle)
    keyboard.send("ctrl+v")

    if restore_clipboard and previous is not None:
        time.sleep(settle)
        try:
            pyperclip.copy(previous)
        except Exception:
            pass
