# voice-cli

**Local push-to-talk dictation for your terminal and any text field.** Press a hotkey, speak,
press again — your words are transcribed **on your own machine** and pasted as **editable text**
wherever your cursor is. Nothing is auto-submitted and no audio ever leaves your computer.

```
press hotkey  →  speak  →  press hotkey  →  [faster-whisper, local]  →  editable text at the cursor  →  review  →  Enter
```

Built to make dictating long, detailed instructions (e.g. to an AI coding CLI) faster than
typing — while keeping you in control of every line before it's sent.

> 🛠️ A free, open-source tool by **[FosNoo](https://fosnoo.com)** — the developer directory where your real work speaks.

## Features
- 🎙️ **Press-to-toggle dictation** with a single global hotkey (default `F9`).
- 🔒 **100% local** — speech-to-text runs on-device with [faster-whisper](https://github.com/SYSTRAN/faster-whisper); audio never leaves your machine.
- ✏️ **You stay in control** — text is inserted as *editable* text and never auto-submitted. Fix a word, then press Enter.
- ⚡ **GPU or CPU** — uses an NVIDIA GPU automatically if present, otherwise runs on CPU.
- 🌍 **Multilingual** — Whisper supports ~99 languages. Defaults to English; set `language` for another (or `null` to auto-detect).
- 🧩 **Swappable seams** — audio, transcriber, hotkey, and text-injection are separate modules.
- 🔇 No telemetry, no accounts, no cloud.

## Requirements
- **Windows 10/11** (primary target — uses a global hotkey, clipboard paste, and a beep cue).
  The core is mostly cross-platform; minor tweaks may be needed on Linux/macOS.
- **Python 3.10+**
- *(Optional)* an **NVIDIA GPU** for fast, high-accuracy transcription with larger models.

## Install

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

**For NVIDIA GPU acceleration (optional):**
```bash
pip install -r requirements-gpu.txt
```
This installs the CUDA 12 runtime libraries as pip wheels — no system CUDA toolkit needed.

Then create your config:
```bash
cp config/settings.example.yaml config/settings.yaml   # Windows: copy config\settings.example.yaml config\settings.yaml
```

## Usage
Start the helper (leave it running):
```bash
python -m src.voice_cli
```
It prints the device it loaded on (`CPU` or `CUDA`) and then `ready - press [f9]...`.

Then, in **any** window with a text field (a terminal, an editor, a chat box):
1. Click into the text field so it has focus.
2. Press **F9** → wait for the beep → **speak**.
3. Press **F9** again → your words are transcribed and pasted at the cursor, editable.
4. Review, fix anything, and press Enter.

**Tips for best accuracy**
- Wait for the beep, *then* speak; pause a beat before pressing stop.
- Speak at a natural, even pace — rushed, run-together phrases are where any ASR slips.
- On a GPU, set `model: large-v3` in `settings.yaml` for the best accuracy.
- Set `initial_prompt` to bias recognition toward your jargon, names, or domain terms.

## Configuration
All settings live in `config/settings.yaml` (see `settings.example.yaml` for the full list):

| Key | What it does |
|---|---|
| `hotkey.toggle` | The global push-to-talk key (default `f9`). |
| `transcriber.model` | Whisper model size: `tiny`→`large-v3`. Bigger = more accurate, slower. |
| `transcriber.device` | `auto` (GPU if present, else CPU), or force `cuda`/`cpu`. |
| `transcriber.language` | Language code, e.g. `en`, `el`, `es`, `de`. `null` = auto-detect. |
| `transcriber.initial_prompt` | Prime the model with vocabulary it should expect. |
| `audio.warmup_seconds` / `tail_seconds` | Lead-in / trailing capture so edge words aren't clipped. |
| `injector.mode` | `clipboard` (paste) or `type` (keystrokes). |
| `recordings.save` | Save WAVs for debugging (off by default). |

### Languages
Whisper is multilingual (~99 languages). Set `transcriber.language` to your language code
(`en`, `el`, `es`, `fr`, `de`, ...) or `null` to auto-detect. **For non-English, use a
multilingual model** — `tiny`, `base`, `small`, `medium`, or `large-v3`. The English-only
variants (`*.en`, and `distil-large-v3`) will not work for other languages.

## How it works
```
src/voice_cli/
├── app.py          orchestrates: hotkey -> record -> transcribe -> paste
├── audio.py        microphone capture (sounddevice)
├── transcriber.py  faster-whisper, with GPU/CPU auto-detection
├── injector.py     clipboard-paste (or keystroke) text insertion
├── recorder.py     press-to-toggle state machine (pure)
├── text.py         transcript cleanup (pure)
├── config.py       settings loader (pure)
└── cuda_paths.py   puts the pip CUDA DLLs on PATH for CTranslate2 (Windows GPU)
```

Run the tests (dev deps only — not needed to use the tool):
```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Limitations (honest)
- It's a **dictation aid**, not perfect transcription. Fast, run-together speech will miss the
  occasional word — that's exactly why the text is editable before you send it.
- Larger models on **CPU** are slow; use `small`/`base` on CPU, `large-v3` on a GPU.
- Currently focused on **Windows**.

## About FosNoo
voice-cli is a free tool from **[FosNoo](https://fosnoo.com)** — a developer directory done
differently. FosNoo brings your real work — public activity, package downloads, live products —
into one page you own, straight from the source. Every number links to where it came from.

**Launching soon.** Only the first 500 claim a numbered *Genesis* mark — first in, first numbered.
**[Join the waitlist →](https://fosnoo.com)**

## License
[MIT](LICENSE) — do what you like, no warranty.

---
*Speech-to-text by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2). Models by OpenAI Whisper / SYSTRAN.*
