<div align="center">

# 🤖 HumanType

**A human-like typing simulator for Windows.**

Types into any active window with realistic speed, typos, pauses, and natural variation — just like a real person.

No Python required. Download, run, type.

[![Download](https://img.shields.io/badge/Download-Latest%20Release-22c55e?style=for-the-badge&logo=windows)](../../releases/latest)

---

</div>

## What is HumanType?

HumanType simulates realistic human typing into any application on your computer — Google Docs, Word, Notepad, browsers, anything. Instead of text appearing instantly (like a paste), it types character by character with natural speed variation, occasional typos that get corrected, thinking pauses, and more.

**Built for:**
- 🎥 **Screen recordings & demos** — make tutorials and walkthroughs look natural
- ♿ **Accessibility** — help users with motor difficulties input pre-written text
- 🧪 **QA & testing** — test form inputs and typing-based features
- 🎨 **Creative projects** — animations, interactive fiction, art installations
- 📚 **Practice & learning** — watch code or text appear at a readable pace

## Features

### Realistic Typing Engine
- **Variable speed** — common letters are typed faster, rare letters slower
- **QWERTY-adjacent typos** — hits a neighboring key, pauses, backspaces, corrects (just like you do)
- **Whole-word typos** — occasionally misspells common words like "teh" → backspace → "the"
- **Burst typing** — types fast for a few words, then pauses to "think"
- **Fatigue simulation** — gradually slows down over long texts
- **Punctuation pauses** — longer pauses after periods, commas, and newlines
- **Thinking pauses** — random mid-sentence pauses, like a real person composing thoughts

### Full GUI — No Terminal Needed
- **4-tab interface** — Type, Settings, Queue, and Tools
- **Inline sliders** — adjust WPM, variation, typo rate, and countdown on the fly
- **Live stats** — real-time WPM, characters typed, and ETA while typing
- **Progress bar** — see exactly how far along you are
- **Dark & light theme** — toggle with one click

### Power Features
- **Text queue** — line up multiple texts to type in sequence
- **Find & replace** — swap placeholder names, dates, or variables before typing
- **Clipboard mode** — automatically types anything you copy
- **Test preview** — watch the typing inside the app before committing to an external window
- **Global hotkeys** — F6 to start/stop, F7 to pause (requires `pynput`)
- **Keyboard sounds** — optional click sounds for screen recordings (Windows)
- **Settings persistence** — your preferences are saved between sessions

### Safety
- **5-second countdown** — gives you time to click into your target window
- **Auto-minimize** — the app gets out of the way while typing
- **Emergency stop** — slam your mouse into any screen corner to abort instantly
- **Pause/resume** — pause mid-text and pick up where you left off

## Installation

### Option 1: Download the .exe (recommended)

1. Go to the [**Releases**](../../releases/latest) page
2. Download `HumanType.exe`
3. Double-click to run — no installation or setup needed

> **Note:** Windows SmartScreen may show a warning because the app isn't signed. Click **"More info"** → **"Run anyway"**. This is normal for indie software.

### Option 2: Run from source

Requires Python 3.8+

```bash
# Clone the repo
git clone https://github.com/yourusername/HumanType.git
cd HumanType

# Install dependencies
pip install pyautogui

# Optional: install pynput for global hotkeys (F6/F7)
pip install pynput

# Run
python HumanType.pyw
```

## How to Use

1. **Launch** HumanType
2. **Paste your text** into the text box (or click 📂 Load file)
3. **Adjust settings** — speed, typo rate, variation (or leave defaults)
4. **Click ▶ Start Typing**
5. **Click into your target app** during the countdown (Google Docs, Word, Notepad, etc.)
6. **Watch it type** — the app minimizes and types into whatever window has focus

That's it. When it's done, the app pops back up.

### Quick Settings Guide

| Setting | Default | What it does |
|---------|---------|-------------|
| Speed | 60 WPM | How fast it types (20–120) |
| Variation | 40% | How much the speed fluctuates |
| Typos | 2% | Chance of hitting a wrong key per character |
| Delay | 5s | Countdown before typing starts |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F6 | Start / Stop typing |
| F7 | Pause / Resume |
| Mouse corner | Emergency stop |

## Screenshots

*Coming soon*

## Building from Source

Want to compile your own `.exe`?

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "HumanType" --icon "humantype.ico" HumanType.pyw
```

Your `.exe` will be in the `dist/` folder.

## Requirements

**For the .exe download:** None — everything is bundled.

**For running from source:**
- Python 3.8+
- `pyautogui` (required)
- `pynput` (optional — enables global hotkeys)
- Windows 10 or 11

## FAQ

**Will this get detected by Google Docs / Word edit history?**
HumanType simulates actual keystrokes at the OS level — to the target application, it looks identical to someone physically typing on a keyboard.

**Can I use this on Mac or Linux?**
The source code (`HumanType.pyw`) works on Mac and Linux with Python installed. The `.exe` is Windows-only. Mac users may need to grant Accessibility permissions.

**Why does Windows SmartScreen block it?**
SmartScreen warns about any unsigned executable it hasn't seen before. It's not malicious — you can verify by reading the source code in this repo. Click "More info" → "Run anyway" to proceed.

**How do I stop it mid-typing?**
Three ways: slam your mouse into any screen corner (failsafe), press F6, or press F7 to pause.

## License

MIT License — free to use, modify, and distribute.

## Contributing

Pull requests welcome! If you have ideas for new features or find bugs, open an issue.

---

<div align="center">

**Made with ⌨️ by Kuthab Ibrahim**

</div>
