"""Foreground-window capture/restore (Windows).

Dictation should land in the window that was focused when you STARTED recording —
not wherever focus happens to be when transcription finishes. We snapshot the
foreground window on start and re-focus it just before pasting.
"""
from __future__ import annotations


def get_foreground_window():
    """Return a handle to the currently focused window (or None if unavailable)."""
    try:
        import ctypes

        return ctypes.windll.user32.GetForegroundWindow()
    except Exception:
        return None


def focus_window(hwnd) -> bool:
    """Bring `hwnd` to the foreground. Returns True on a best-effort success.

    Uses AttachThreadInput to bypass Windows' foreground-lock, which otherwise
    makes a bare SetForegroundWindow fail (and only flash the taskbar).
    """
    if not hwnd:
        return False
    try:
        import ctypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        current = user32.GetForegroundWindow()
        if current == hwnd:
            return True

        cur_thread = kernel32.GetCurrentThreadId()
        fg_thread = user32.GetWindowThreadProcessId(current, None)
        tgt_thread = user32.GetWindowThreadProcessId(hwnd, None)

        user32.AttachThreadInput(cur_thread, fg_thread, True)
        user32.AttachThreadInput(cur_thread, tgt_thread, True)
        try:
            user32.SetForegroundWindow(hwnd)
        finally:
            user32.AttachThreadInput(cur_thread, fg_thread, False)
            user32.AttachThreadInput(cur_thread, tgt_thread, False)
        return user32.GetForegroundWindow() == hwnd
    except Exception:
        return False
