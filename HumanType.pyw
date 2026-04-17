#!/usr/bin/env python3
"""
HumanType v2 — Full-featured human typing simulator with GUI.
Double-click to launch. No terminal needed.

Requirements:
    pip install pyautogui pynput
    (macOS: also pip install pyobjc-framework-Quartz)
    (Linux: sudo apt install python3-tk python3-dev)
"""

import threading
import time
import random
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import math

# ── Dependency checks ─────────────────────────────────────────────
try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Missing Dependency",
        "pyautogui is not installed.\n\n"
        "Open a terminal and run:\n"
        "pip install pyautogui\n\n"
        "Then re-launch this app."
    )
    sys.exit(1)

HAS_PYNPUT = False
try:
    from pynput import keyboard as pynput_keyboard
    HAS_PYNPUT = True
except ImportError:
    pass

# ── Config path ───────────────────────────────────────────────────
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".humantype")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
os.makedirs(CONFIG_DIR, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────
ADJACENT = {
    'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx', 'e': 'wrsdf',
    'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb', 'i': 'uojk', 'j': 'huiknm',
    'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'ipkl',
    'p': 'ol', 'q': 'wa', 'r': 'etdf', 's': 'awedxz', 't': 'ryfg',
    'u': 'yihj', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tughj',
    'z': 'asx',
}

COMMON_LETTERS = set('etaoinshrdlu ')
RARE_LETTERS = set('zxqjkvbp')

WORD_TYPOS = {
    'the': ['teh', 'hte'], 'and': ['adn', 'nad'], 'that': ['taht', 'ttha'],
    'have': ['ahve', 'hvae'], 'with': ['wiht', 'wtih'], 'this': ['tihs', 'thsi'],
    'from': ['form', 'fomr'], 'they': ['tehy', 'thye'], 'been': ['eben', 'bene'],
    'their': ['thier', 'tehir'], 'which': ['whcih', 'wihch'], 'would': ['woudl', 'wuold'],
    'there': ['tehre', 'theer'], 'about': ['abuot', 'abotu'], 'could': ['coudl', 'cuold'],
    'people': ['poeple', 'peopel'], 'because': ['becuase', 'becasue'],
    'your': ['yuor', 'yoru'], 'some': ['soem', 'smoe'], 'just': ['jsut', 'juts'],
    'also': ['aslo', 'alsi'], 'into': ['inot', 'itno'], 'what': ['waht', 'whta'],
}

THEMES = {
    "dark": {
        "bg": "#111214", "surface": "#1a1b1f", "surface2": "#222328",
        "border": "#2e3035", "text": "#e4e4e9", "dim": "#7d7f88",
        "muted": "#53555c", "accent": "#22c55e", "accent_dark": "#166534",
        "danger": "#ef4444", "warning": "#eab308", "input_bg": "#16171b",
        "button_bg": "#27282d", "button_hover": "#333438",
    },
    "light": {
        "bg": "#f4f5f7", "surface": "#ffffff", "surface2": "#f0f1f3",
        "border": "#d8dae0", "text": "#1a1b1e", "dim": "#6b6d75",
        "muted": "#9b9da5", "accent": "#16a34a", "accent_dark": "#15803d",
        "danger": "#dc2626", "warning": "#ca8a04", "input_bg": "#f8f9fb",
        "button_bg": "#e8e9ed", "button_hover": "#dcdde2",
    }
}


class TypingEngine:
    def __init__(self):
        self.stop_flag = False
        self.paused = False
        self.chars_typed = 0
        self.total_chars = 0
        self.start_time = 0
        self.on_progress = None
        self.on_done = None

    def type_text(self, text, wpm, variation, typo_rate, pauses_on,
                  burst_typing, word_typos, fatigue, variable_speed):
        self.stop_flag = False
        self.paused = False
        self.chars_typed = 0
        self.total_chars = len(text)
        self.start_time = time.time()

        words = self._split_into_words(text)

        try:
            for word in words:
                if self.stop_flag:
                    break

                if (word_typos and word.lower().strip() in WORD_TYPOS
                        and random.random() < 0.03):
                    if self._do_word_typo(word, wpm):
                        continue

                in_burst = burst_typing and random.random() < 0.08
                burst_mult = random.uniform(0.5, 0.7) if in_burst else 1.0

                for ch in word:
                    while self.paused and not self.stop_flag:
                        time.sleep(0.08)
                    if self.stop_flag:
                        break

                    fatigue_mult = 1.0
                    if fatigue and self.total_chars > 0:
                        progress = self.chars_typed / self.total_chars
                        fatigue_mult = 1.0 + (progress * 0.35)

                    char_mult = 1.0
                    if variable_speed:
                        low = ch.lower()
                        if low in COMMON_LETTERS:
                            char_mult = random.uniform(0.75, 0.9)
                        elif low in RARE_LETTERS:
                            char_mult = random.uniform(1.1, 1.4)

                    typo = self._maybe_typo(ch, typo_rate)
                    if typo is not None:
                        self._type_char(typo)
                        time.sleep(self._delay(wpm, variation) * burst_mult)
                        time.sleep(random.uniform(0.15, 0.4))
                        if self.stop_flag: break
                        pyautogui.press('backspace')
                        time.sleep(random.uniform(0.06, 0.15))
                        if self.stop_flag: break

                    self._type_char(ch)
                    time.sleep(self._delay(wpm, variation) * burst_mult * fatigue_mult * char_mult)

                    p = self._pause(ch, pauses_on)
                    if p > 0:
                        time.sleep(p)

                    self.chars_typed += 1
                    if self.on_progress and self.chars_typed % 3 == 0:
                        self.on_progress(self.chars_typed, self.total_chars,
                                         time.time() - self.start_time)

                if in_burst and random.random() < 0.5:
                    time.sleep(random.uniform(0.4, 1.2))

        except pyautogui.FailSafeException:
            if self.on_done: self.on_done(True)
            return
        except Exception:
            if self.on_done: self.on_done(True)
            return

        if self.on_progress:
            self.on_progress(self.chars_typed, self.total_chars, time.time() - self.start_time)
        if self.on_done:
            self.on_done(self.stop_flag)

    def _do_word_typo(self, word, wpm):
        stripped = word.lower().strip()
        if stripped not in WORD_TYPOS:
            return False
        wrong = random.choice(WORD_TYPOS[stripped])
        suffix = word[len(word.rstrip()):]

        for ch in wrong:
            if self.stop_flag: return False
            self._type_char(ch)
            time.sleep(self._delay(wpm, 0.3))
        for ch in suffix:
            if self.stop_flag: return False
            self._type_char(ch)
            time.sleep(self._delay(wpm, 0.3))

        time.sleep(random.uniform(0.3, 0.8))

        for _ in range(len(wrong) + len(suffix)):
            if self.stop_flag: return False
            pyautogui.press('backspace')
            time.sleep(random.uniform(0.03, 0.07))

        time.sleep(random.uniform(0.1, 0.25))

        for ch in word:
            if self.stop_flag: return False
            self._type_char(ch)
            time.sleep(self._delay(wpm, 0.25))
            self.chars_typed += 1
        return True

    @staticmethod
    def _split_into_words(text):
        words, current = [], []
        for ch in text:
            if ch == ' ':
                current.append(ch)
                words.append(''.join(current))
                current = []
            else:
                current.append(ch)
        if current:
            words.append(''.join(current))
        return words

    @staticmethod
    def _type_char(ch):
        if ch == '\n': pyautogui.press('enter')
        elif ch == '\t': pyautogui.press('tab')
        else: pyautogui.write(ch, interval=0)

    @staticmethod
    def _delay(wpm, variation):
        base = 60.0 / (wpm * 5)
        jitter = base * variation
        return max(0.008, base + random.uniform(-jitter, jitter))

    @staticmethod
    def _pause(ch, enabled):
        if not enabled: return 0
        if ch in '.!?': return random.uniform(0.35, 0.75)
        if ch in ',;:': return random.uniform(0.15, 0.35)
        if ch == '\n': return random.uniform(0.25, 0.55)
        if ch == ' ' and random.random() < 0.04: return random.uniform(0.25, 0.6)
        return 0

    @staticmethod
    def _maybe_typo(ch, rate):
        if random.random() > rate: return None
        lower = ch.lower()
        if lower not in ADJACENT: return None
        wrong = random.choice(ADJACENT[lower])
        return wrong.upper() if ch.isupper() and ch != lower else wrong


class HumanTypeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HumanType")
        self.root.minsize(700, 760)
        self.root.geometry("720x800")

        self.engine = TypingEngine()
        self.engine.on_progress = self._on_progress
        self.engine.on_done = self._on_done

        self.theme_name = "dark"
        self.t = THEMES["dark"]
        self.typing_active = False
        self.test_mode = False
        self.thread = None
        self.clipboard_mode = False
        self.clipboard_last = ""
        self.clipboard_poll_id = None
        self.hotkey_listener = None
        self.queue_items = []

        self.wpm_var = tk.IntVar(value=60)
        self.var_var = tk.IntVar(value=40)
        self.typo_var = tk.IntVar(value=2)
        self.delay_var = tk.IntVar(value=5)
        self.pauses_var = tk.BooleanVar(value=True)
        self.burst_var = tk.BooleanVar(value=True)
        self.word_typo_var = tk.BooleanVar(value=True)
        self.fatigue_var = tk.BooleanVar(value=False)
        self.variable_speed_var = tk.BooleanVar(value=True)
        self.sound_var = tk.BooleanVar(value=False)

        self._load_settings()
        self._build_ui()
        self._setup_hotkeys()

    def _build_ui(self):
        self.root.configure(bg=self.t["bg"])
        self.container = tk.Frame(self.root, bg=self.t["bg"])
        self.container.pack(fill="both", expand=True, padx=22, pady=14)

        # Header
        hdr = tk.Frame(self.container, bg=self.t["bg"])
        hdr.pack(fill="x", pady=(0, 12))

        logo = tk.Frame(hdr, bg=self.t["accent"], width=36, height=36)
        logo.pack_propagate(False)
        logo.pack(side="left", padx=(0, 10))
        tk.Label(logo, text="H", bg=self.t["accent"], fg="#000",
                 font=("Segoe UI", 14, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        tf = tk.Frame(hdr, bg=self.t["bg"])
        tf.pack(side="left")
        tk.Label(tf, text="HumanType", bg=self.t["bg"], fg=self.t["text"],
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(tf, text="Natural typing simulator", bg=self.t["bg"],
                 fg=self.t["dim"], font=("Segoe UI", 9)).pack(anchor="w")

        hdr_r = tk.Frame(hdr, bg=self.t["bg"])
        hdr_r.pack(side="right")
        self.theme_btn = tk.Button(hdr_r, text="☀" if self.theme_name == "dark" else "🌙",
            command=self._toggle_theme, bg=self.t["button_bg"], fg=self.t["dim"],
            font=("Segoe UI", 12), bd=0, padx=8, pady=2, cursor="hand2")
        self.theme_btn.pack(side="left", padx=(0, 6))
        self.status_label = tk.Label(hdr_r, text="● Idle", bg=self.t["bg"],
                                     fg=self.t["dim"], font=("Segoe UI", 10))
        self.status_label.pack(side="left")

        # Tabs
        self.tab_bar = tk.Frame(self.container, bg=self.t["bg"])
        self.tab_bar.pack(fill="x", pady=(0, 8))
        self.tabs = {}
        self.tab_buttons = {}
        self.active_tab = "type"

        for tid, label in [("type","⌨  Type"), ("settings","⚙  Settings"),
                           ("queue","📋  Queue"), ("tools","🔧  Tools")]:
            btn = tk.Button(self.tab_bar, text=label, command=lambda t=tid: self._switch_tab(t),
                bg=self.t["surface"], fg=self.t["dim"], font=("Segoe UI", 10, "bold"),
                bd=0, padx=16, pady=8, cursor="hand2")
            btn.pack(side="left", padx=(0, 2))
            self.tab_buttons[tid] = btn

        self.tab_container = tk.Frame(self.container, bg=self.t["bg"])
        self.tab_container.pack(fill="both", expand=True)

        self._build_type_tab()
        self._build_settings_tab()
        self._build_queue_tab()
        self._build_tools_tab()
        self._switch_tab("type")

    # ── TYPE TAB ──

    def _build_type_tab(self):
        self.tabs["type"] = tab = tk.Frame(self.tab_container, bg=self.t["bg"])

        # Text input card
        ic = self._card(tab)
        ic.pack(fill="both", expand=True, pady=(0, 8))

        ih = tk.Frame(ic, bg=self.t["surface"])
        ih.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(ih, text="TEXT TO TYPE", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.char_label = tk.Label(ih, text="0 chars  ·  ~0s", bg=self.t["surface"],
                                    fg=self.t["muted"], font=("Segoe UI", 9))
        self.char_label.pack(side="right")

        self.text_box = tk.Text(ic, height=8, wrap="word", bg=self.t["input_bg"],
            fg=self.t["text"], insertbackground=self.t["accent"],
            font=("Consolas", 11), bd=0, padx=14, pady=10,
            highlightthickness=0, relief="flat", undo=True)
        self.text_box.pack(fill="both", expand=True, padx=2, pady=2)
        self.text_box.bind("<KeyRelease>", lambda e: self._update_info())

        self.drop_hint = tk.Label(self.text_box,
            text="📂  Drop a .txt file here, paste text, or use buttons below",
            bg=self.t["input_bg"], fg=self.t["muted"], font=("Segoe UI", 10))
        self.drop_hint.place(relx=0.5, rely=0.5, anchor="center")
        self.text_box.bind("<FocusIn>", lambda e: self.drop_hint.place_forget())
        self.text_box.bind("<<Modified>>", self._on_text_mod)

        br = tk.Frame(ic, bg=self.t["surface"])
        br.pack(fill="x", padx=14, pady=(0, 10))
        self._sbtn(br, "📂 Load file", self._load_file).pack(side="left", padx=(0,6))
        self._sbtn(br, "📋 Paste", self._paste_clip).pack(side="left", padx=(0,6))
        self._sbtn(br, "✕ Clear", self._clear_text).pack(side="left")
        self._sbtn(br, "+ Add to queue", self._add_to_queue).pack(side="right")

        # Quick settings
        qs = self._card(tab)
        qs.pack(fill="x", pady=(0, 8))
        tk.Label(qs, text="QUICK SETTINGS", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 6))

        sf = tk.Frame(qs, bg=self.t["surface"])
        sf.pack(fill="x", padx=14, pady=(0, 12))
        for i in range(4): sf.columnconfigure(i, weight=1)

        self._slider(sf, "Speed", "WPM", self.wpm_var, 20, 120, 0)
        self._slider(sf, "Variation", "%", self.var_var, 0, 80, 1)
        self._slider(sf, "Typos", "%", self.typo_var, 0, 10, 2)
        self._slider(sf, "Delay", "s", self.delay_var, 3, 15, 3)

        # Progress + stats
        sc = self._card(tab)
        sc.pack(fill="x", pady=(0, 8))
        self.progress_canvas = tk.Canvas(sc, height=6, bg=self.t["border"],
                                          highlightthickness=0, bd=0)
        self.progress_canvas.pack(fill="x", padx=14, pady=(12, 8))

        sr = tk.Frame(sc, bg=self.t["surface"])
        sr.pack(fill="x", padx=14, pady=(0, 12))
        self.stat_typed = self._statbox(sr, "Typed", "0 / 0")
        self.stat_typed.pack(side="left", expand=True, fill="x", padx=(0,4))
        self.stat_wpm = self._statbox(sr, "Live WPM", "—")
        self.stat_wpm.pack(side="left", expand=True, fill="x", padx=(2,4))
        self.stat_eta = self._statbox(sr, "ETA", "—")
        self.stat_eta.pack(side="left", expand=True, fill="x", padx=(2,0))

        # Buttons
        af = tk.Frame(tab, bg=self.t["bg"])
        af.pack(fill="x", pady=(0, 4))

        self.start_btn = tk.Button(af, text="▶  Start Typing", command=self._on_start,
            bg=self.t["accent"], fg="#000", font=("Segoe UI Semibold", 12),
            bd=0, padx=28, pady=12, cursor="hand2",
            activebackground=self.t["accent_dark"], activeforeground="#000")
        self.start_btn.pack(side="left", padx=(0, 8))

        self.pause_btn = tk.Button(af, text="⏸  Pause", command=self._on_pause,
            bg=self.t["button_bg"], fg=self.t["dim"], font=("Segoe UI", 10),
            bd=0, padx=16, pady=12, cursor="hand2", state="disabled")
        self.pause_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(af, text="■  Stop", command=self._on_stop,
            bg=self.t["button_bg"], fg=self.t["danger"], font=("Segoe UI", 10),
            bd=0, padx=16, pady=12, cursor="hand2", state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        self.test_btn = tk.Button(af, text="🧪 Test", command=self._on_test,
            bg=self.t["button_bg"], fg=self.t["dim"], font=("Segoe UI", 10),
            bd=0, padx=16, pady=12, cursor="hand2")
        self.test_btn.pack(side="left")

        hint = "F6: Start/Stop  ·  F7: Pause  ·  Mouse corner: Emergency stop"
        if not HAS_PYNPUT:
            hint = "pip install pynput for hotkeys  ·  Mouse corner: Emergency stop"
        tk.Label(af, text=hint, bg=self.t["bg"], fg=self.t["muted"],
                 font=("Segoe UI", 8)).pack(side="right")

    # ── SETTINGS TAB ──

    def _build_settings_tab(self):
        self.tabs["settings"] = tab = tk.Frame(self.tab_container, bg=self.t["bg"])

        rc = self._card(tab)
        rc.pack(fill="x", pady=(0, 8))
        tk.Label(rc, text="REALISM", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 8))

        self._trow(rc, "Burst typing", "Fast bursts followed by thinking pauses", self.burst_var)
        self._trow(rc, "Whole-word typos", "Misspell words like 'teh', backspace, retype", self.word_typo_var)
        self._trow(rc, "Fatigue simulation", "Gradually slow down over long texts", self.fatigue_var)
        self._trow(rc, "Variable letter speed", "Common letters faster, rare letters slower", self.variable_speed_var)
        self._trow(rc, "Punctuation pauses", "Longer pauses at periods, commas, newlines", self.pauses_var)
        tk.Frame(rc, bg=self.t["surface"], height=8).pack()

        ec = self._card(tab)
        ec.pack(fill="x", pady=(0, 8))
        tk.Label(ec, text="EXTRAS", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 8))
        self._trow(ec, "Keyboard sounds", "Click sounds for screen recordings (Windows only)", self.sound_var)
        tk.Frame(ec, bg=self.t["surface"], height=8).pack()

        pc = self._card(tab)
        pc.pack(fill="x", pady=(0, 8))
        tk.Label(pc, text="PRESETS", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 8))
        pr = tk.Frame(pc, bg=self.t["surface"])
        pr.pack(fill="x", padx=14, pady=(0, 14))
        self._sbtn(pr, "💾 Save settings", self._save_settings).pack(side="left", padx=(0,8))
        self._sbtn(pr, "📂 Load settings", lambda: [self._load_settings(), messagebox.showinfo("Loaded", "Settings reloaded.")]).pack(side="left", padx=(0,8))
        self._sbtn(pr, "↺ Reset defaults", self._reset_defaults).pack(side="left")

    # ── QUEUE TAB ──

    def _build_queue_tab(self):
        self.tabs["queue"] = tab = tk.Frame(self.tab_container, bg=self.t["bg"])

        qc = self._card(tab)
        qc.pack(fill="both", expand=True, pady=(0, 8))

        qh = tk.Frame(qc, bg=self.t["surface"])
        qh.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(qh, text="TEXT QUEUE", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.q_count = tk.Label(qh, text="0 items", bg=self.t["surface"],
                                 fg=self.t["muted"], font=("Segoe UI", 9))
        self.q_count.pack(side="right")

        self.q_list = tk.Listbox(qc, bg=self.t["input_bg"], fg=self.t["text"],
            font=("Consolas", 10), bd=0, highlightthickness=0,
            selectbackground=self.t["accent_dark"], selectforeground=self.t["text"],
            activestyle="none", height=12)
        self.q_list.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        qb = tk.Frame(qc, bg=self.t["surface"])
        qb.pack(fill="x", padx=14, pady=(0, 14))
        self._sbtn(qb, "▶ Type all", self._type_queue).pack(side="left", padx=(0,6))
        self._sbtn(qb, "▲ Up", self._q_up).pack(side="left", padx=(0,6))
        self._sbtn(qb, "▼ Down", self._q_down).pack(side="left", padx=(0,6))
        self._sbtn(qb, "✕ Remove", self._q_remove).pack(side="left", padx=(0,6))
        self._sbtn(qb, "🗑 Clear all", self._q_clear).pack(side="right")

    # ── TOOLS TAB ──

    def _build_tools_tab(self):
        self.tabs["tools"] = tab = tk.Frame(self.tab_container, bg=self.t["bg"])

        # Find & Replace
        fc = self._card(tab)
        fc.pack(fill="x", pady=(0, 8))
        tk.Label(fc, text="FIND & REPLACE", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 8))

        fg = tk.Frame(fc, bg=self.t["surface"])
        fg.pack(fill="x", padx=14, pady=(0, 8))
        fg.columnconfigure(1, weight=1)

        tk.Label(fg, text="Find:", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.find_e = tk.Entry(fg, bg=self.t["input_bg"], fg=self.t["text"],
            font=("Consolas", 10), bd=0, highlightthickness=1,
            highlightcolor=self.t["border"], highlightbackground=self.t["border"],
            insertbackground=self.t["accent"])
        self.find_e.grid(row=0, column=1, sticky="ew", padx=(8,0), pady=2)

        tk.Label(fg, text="Replace:", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=2)
        self.replace_e = tk.Entry(fg, bg=self.t["input_bg"], fg=self.t["text"],
            font=("Consolas", 10), bd=0, highlightthickness=1,
            highlightcolor=self.t["border"], highlightbackground=self.t["border"],
            insertbackground=self.t["accent"])
        self.replace_e.grid(row=1, column=1, sticky="ew", padx=(8,0), pady=2)

        fr = tk.Frame(fc, bg=self.t["surface"])
        fr.pack(fill="x", padx=14, pady=(0, 14))
        self._sbtn(fr, "Replace all", self._do_replace).pack(side="left")

        # Clipboard mode
        cc = self._card(tab)
        cc.pack(fill="x", pady=(0, 8))
        tk.Label(cc, text="CLIPBOARD MODE", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(cc, text="When active, anything you copy is automatically typed into the focused window.",
                 bg=self.t["surface"], fg=self.t["muted"], font=("Segoe UI", 9),
                 wraplength=500, justify="left").pack(anchor="w", padx=14, pady=(0, 8))

        cr = tk.Frame(cc, bg=self.t["surface"])
        cr.pack(fill="x", padx=14, pady=(0, 14))
        self.clip_btn = tk.Button(cr, text="📋 Enable clipboard mode",
            command=self._toggle_clipboard, bg=self.t["button_bg"], fg=self.t["dim"],
            font=("Segoe UI", 10), bd=0, padx=14, pady=8, cursor="hand2")
        self.clip_btn.pack(side="left")
        self.clip_status = tk.Label(cr, text="", bg=self.t["surface"],
                                     fg=self.t["muted"], font=("Segoe UI", 9))
        self.clip_status.pack(side="left", padx=(10, 0))

        # Test preview
        tc = self._card(tab)
        tc.pack(fill="both", expand=True, pady=(0, 8))
        tk.Label(tc, text="TEST PREVIEW", bg=self.t["surface"], fg=self.t["dim"],
                 font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(tc, text="Click 🧪 Test on the Type tab to preview typing here.",
                 bg=self.t["surface"], fg=self.t["muted"], font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(0, 8))
        self.test_out = tk.Text(tc, height=8, wrap="word", bg=self.t["input_bg"],
            fg=self.t["text"], font=("Consolas", 11), bd=0, padx=14, pady=10,
            highlightthickness=0, relief="flat", state="disabled")
        self.test_out.pack(fill="both", expand=True, padx=2, pady=(0, 2))

    # ═══ HELPERS ═══

    def _card(self, parent):
        return tk.Frame(parent, bg=self.t["surface"], highlightbackground=self.t["border"],
                        highlightthickness=1)

    def _sbtn(self, parent, text, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=self.t["button_bg"],
            fg=self.t["dim"], font=("Segoe UI", 9), bd=0, padx=10, pady=5,
            cursor="hand2", activebackground=self.t["button_hover"],
            activeforeground=self.t["text"])

    def _slider(self, parent, label, unit, var, lo, hi, col):
        f = tk.Frame(parent, bg=self.t["surface"])
        f.grid(row=0, column=col, sticky="ew", padx=4)
        tk.Label(f, text=label, bg=self.t["surface"], fg=self.t["muted"],
                 font=("Segoe UI", 8)).pack(anchor="w")
        vl = tk.Label(f, text=f"{var.get()} {unit}", bg=self.t["surface"],
                      fg=self.t["accent"], font=("Consolas", 11, "bold"))
        vl.pack(anchor="w")
        tk.Scale(f, from_=lo, to=hi, orient="horizontal", variable=var,
            bg=self.t["surface"], fg=self.t["dim"], troughcolor=self.t["border"],
            highlightthickness=0, bd=0, sliderrelief="flat", showvalue=False,
            command=lambda v, l=vl, u=unit: l.config(text=f"{int(float(v))} {u}")
        ).pack(fill="x")

    def _trow(self, parent, label, desc, var):
        r = tk.Frame(parent, bg=self.t["surface"])
        r.pack(fill="x", padx=14, pady=3)
        lf = tk.Frame(r, bg=self.t["surface"])
        lf.pack(side="left", fill="x", expand=True)
        tk.Label(lf, text=label, bg=self.t["surface"], fg=self.t["text"],
                 font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(lf, text=desc, bg=self.t["surface"], fg=self.t["muted"],
                 font=("Segoe UI", 8), wraplength=400, justify="left").pack(anchor="w")
        tk.Checkbutton(r, variable=var, bg=self.t["surface"], fg=self.t["text"],
            selectcolor=self.t["input_bg"], activebackground=self.t["surface"],
            bd=0, highlightthickness=0).pack(side="right")

    def _statbox(self, parent, label, value):
        f = tk.Frame(parent, bg=self.t["surface2"], highlightbackground=self.t["border"],
                     highlightthickness=1)
        tk.Label(f, text=label, bg=self.t["surface2"], fg=self.t["muted"],
                 font=("Segoe UI", 8)).pack(anchor="w", padx=8, pady=(6, 0))
        vl = tk.Label(f, text=value, bg=self.t["surface2"], fg=self.t["text"],
                      font=("Consolas", 13, "bold"))
        vl.pack(anchor="w", padx=8, pady=(0, 6))
        f._vl = vl
        return f

    # ═══ TAB SWITCHING ═══

    def _switch_tab(self, tid):
        self.active_tab = tid
        for t, f in self.tabs.items():
            f.pack_forget()
        self.tabs[tid].pack(fill="both", expand=True)
        for t, b in self.tab_buttons.items():
            b.config(bg=self.t["accent"] if t == tid else self.t["surface"],
                     fg="#000" if t == tid else self.t["dim"])

    # ═══ TEXT ACTIONS ═══

    def _on_text_mod(self, e=None):
        if self.text_box.get("1.0", "end-1c").strip():
            self.drop_hint.place_forget()
        self.text_box.edit_modified(False)
        self._update_info()

    def _update_info(self):
        n = len(self.text_box.get("1.0", "end-1c"))
        wpm = self.wpm_var.get()
        est = (n / (wpm * 5)) * 60 if wpm > 0 else 0
        ts = f"~{int(est)}s" if est < 60 else f"~{int(est//60)}m {int(est%60)}s"
        self.char_label.config(text=f"{n} chars  ·  {ts}")

    def _load_file(self):
        p = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if p:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    self.text_box.delete("1.0", "end")
                    self.text_box.insert("1.0", f.read())
                    self.drop_hint.place_forget()
                    self._update_info()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _paste_clip(self):
        try:
            t = self.root.clipboard_get()
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", t)
            self.drop_hint.place_forget()
            self._update_info()
        except tk.TclError:
            messagebox.showinfo("Empty", "Clipboard is empty.")

    def _clear_text(self):
        self.text_box.delete("1.0", "end")
        self._update_info()

    def _set_status(self, text, color=None):
        self.status_label.config(text=text, fg=color or self.t["dim"])

    # ═══ TYPING ═══

    def _on_start(self):
        text = self.text_box.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("No text", "Paste or type some text first.")
            return
        self._begin(text, False)

    def _on_test(self):
        text = self.text_box.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("No text", "Paste or type some text first.")
            return
        self._switch_tab("tools")
        self.test_out.config(state="normal")
        self.test_out.delete("1.0", "end")
        self.test_out.config(state="disabled")
        self._begin(text, True)

    def _begin(self, text, test):
        self.typing_active = True
        self.test_mode = test
        self.start_btn.config(state="disabled")
        self.test_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self._reset_stats()
        self.engine.stop_flag = False
        self.engine.paused = False
        self.thread = threading.Thread(target=self._type_thread, args=(text, test), daemon=True)
        self.thread.start()

    def _type_thread(self, text, test):
        if not test:
            delay = self.delay_var.get()
            for i in range(delay, 0, -1):
                if self.engine.stop_flag:
                    self.root.after(0, self._finish)
                    return
                self.root.after(0, lambda s=i: self._set_status(
                    f"⏳ {s}s — click your target window!", self.t["warning"]))
                time.sleep(1)
            self.root.after(0, self.root.iconify)

        self.root.after(0, lambda: self._set_status("● Typing...", self.t["accent"]))

        if test:
            self._run_test(text)
        else:
            self.engine.type_text(
                text, wpm=self.wpm_var.get(), variation=self.var_var.get()/100,
                typo_rate=self.typo_var.get()/100, pauses_on=self.pauses_var.get(),
                burst_typing=self.burst_var.get(), word_typos=self.word_typo_var.get(),
                fatigue=self.fatigue_var.get(), variable_speed=self.variable_speed_var.get())

    def _run_test(self, text):
        wpm = self.wpm_var.get()
        var = self.var_var.get() / 100
        tr = self.typo_var.get() / 100
        e = self.engine
        e.total_chars = len(text)
        e.chars_typed = 0
        e.start_time = time.time()

        try:
            for ch in text:
                while e.paused and not e.stop_flag:
                    time.sleep(0.08)
                if e.stop_flag: break

                typo = TypingEngine._maybe_typo(ch, tr)
                if typo:
                    self.root.after(0, lambda c=typo: self._tins(c))
                    time.sleep(TypingEngine._delay(wpm, var))
                    time.sleep(random.uniform(0.12, 0.3))
                    if e.stop_flag: break
                    self.root.after(0, self._tdel)
                    time.sleep(random.uniform(0.05, 0.1))
                    if e.stop_flag: break

                self.root.after(0, lambda c=ch: self._tins(c))
                time.sleep(TypingEngine._delay(wpm, var))

                p = TypingEngine._pause(ch, self.pauses_var.get())
                if p > 0: time.sleep(p)

                e.chars_typed += 1
                if e.chars_typed % 3 == 0:
                    self._on_progress(e.chars_typed, e.total_chars, time.time() - e.start_time)
        except Exception:
            pass
        self._on_done(e.stop_flag)

    def _tins(self, ch):
        self.test_out.config(state="normal")
        self.test_out.insert("end", ch)
        self.test_out.see("end")
        self.test_out.config(state="disabled")

    def _tdel(self):
        self.test_out.config(state="normal")
        self.test_out.delete("end-2c", "end-1c")
        self.test_out.config(state="disabled")

    def _on_pause(self):
        if not self.typing_active: return
        if self.engine.paused:
            self.engine.paused = False
            self.pause_btn.config(text="⏸  Pause")
            self._set_status("● Typing...", self.t["accent"])
        else:
            self.engine.paused = True
            self.pause_btn.config(text="▶  Resume")
            self._set_status("● Paused", self.t["warning"])

    def _on_stop(self):
        self.engine.stop_flag = True
        self.engine.paused = False

    def _on_progress(self, chars, total, elapsed):
        def u():
            pct = (chars / total * 100) if total else 0
            self._draw_prog(pct)
            self.stat_typed._vl.config(text=f"{chars} / {total}")
            if elapsed > 0:
                self.stat_wpm._vl.config(text=str(int((chars/5)/(elapsed/60))))
            rem = total - chars
            if chars > 0 and elapsed > 0:
                eta = rem / (chars / elapsed)
                self.stat_eta._vl.config(text=f"{int(eta)}s" if eta < 60 else f"{int(eta//60)}m {int(eta%60)}s")
            if self.sound_var.get() and chars % 2 == 0 and sys.platform == 'win32':
                try:
                    import winsound
                    winsound.Beep(800 + random.randint(-100, 100), 12)
                except Exception: pass
        self.root.after(0, u)

    def _on_done(self, aborted):
        def f():
            self.root.deiconify()
            self.root.lift()
            self._finish()
            if aborted:
                self._set_status("■ Stopped", self.t["danger"])
            else:
                self._set_status("✓ Done!", self.t["accent"])
                self._draw_prog(100)
        self.root.after(0, f)

    def _finish(self):
        self.typing_active = False
        self.start_btn.config(state="normal")
        self.test_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="⏸  Pause")
        self.stop_btn.config(state="disabled")

    def _reset_stats(self):
        self._draw_prog(0)
        self.stat_typed._vl.config(text="0 / 0")
        self.stat_wpm._vl.config(text="—")
        self.stat_eta._vl.config(text="—")

    def _draw_prog(self, pct):
        c = self.progress_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w > 1:
            c.create_rectangle(0, 0, int(pct/100*w), h, fill=self.t["accent"], outline="")

    # ═══ QUEUE ═══

    def _add_to_queue(self):
        t = self.text_box.get("1.0", "end-1c").strip()
        if not t: return
        self.queue_items.append(t)
        prev = t[:80].replace("\n", " ") + ("..." if len(t) > 80 else "")
        self.q_list.insert("end", f"[{len(self.queue_items)}] {prev}")
        self.q_count.config(text=f"{len(self.queue_items)} items")
        self._switch_tab("queue")

    def _q_remove(self):
        s = self.q_list.curselection()
        if not s: return
        self.queue_items.pop(s[0])
        self._q_refresh()

    def _q_up(self):
        s = self.q_list.curselection()
        if not s or s[0] == 0: return
        i = s[0]
        self.queue_items[i], self.queue_items[i-1] = self.queue_items[i-1], self.queue_items[i]
        self._q_refresh()
        self.q_list.selection_set(i-1)

    def _q_down(self):
        s = self.q_list.curselection()
        if not s or s[0] >= len(self.queue_items)-1: return
        i = s[0]
        self.queue_items[i], self.queue_items[i+1] = self.queue_items[i+1], self.queue_items[i]
        self._q_refresh()
        self.q_list.selection_set(i+1)

    def _q_clear(self):
        self.queue_items.clear()
        self.q_list.delete(0, "end")
        self.q_count.config(text="0 items")

    def _q_refresh(self):
        self.q_list.delete(0, "end")
        for i, t in enumerate(self.queue_items):
            prev = t[:80].replace("\n", " ") + ("..." if len(t) > 80 else "")
            self.q_list.insert("end", f"[{i+1}] {prev}")
        self.q_count.config(text=f"{len(self.queue_items)} items")

    def _type_queue(self):
        if not self.queue_items:
            messagebox.showinfo("Empty", "Add texts to the queue first.")
            return
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", "\n\n".join(self.queue_items))
        self._update_info()
        self._switch_tab("type")
        self._on_start()

    # ═══ TOOLS ═══

    def _do_replace(self):
        find = self.find_e.get()
        repl = self.replace_e.get()
        if not find: return
        t = self.text_box.get("1.0", "end-1c")
        c = t.count(find)
        if c == 0:
            messagebox.showinfo("Not found", f'"{find}" not found.')
            return
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", t.replace(find, repl))
        self._update_info()
        messagebox.showinfo("Done", f"Replaced {c} occurrence(s).")

    def _toggle_clipboard(self):
        if self.clipboard_mode:
            self.clipboard_mode = False
            self.clip_btn.config(text="📋 Enable clipboard mode")
            self.clip_status.config(text="Disabled", fg=self.t["muted"])
            if self.clipboard_poll_id:
                self.root.after_cancel(self.clipboard_poll_id)
        else:
            self.clipboard_mode = True
            self.clip_btn.config(text="■ Disable clipboard mode")
            self.clip_status.config(text="Listening...", fg=self.t["accent"])
            try: self.clipboard_last = self.root.clipboard_get()
            except: self.clipboard_last = ""
            self._poll_clip()

    def _poll_clip(self):
        if not self.clipboard_mode: return
        try:
            cur = self.root.clipboard_get()
            if cur != self.clipboard_last and cur.strip():
                self.clipboard_last = cur
                if not self.typing_active:
                    self.text_box.delete("1.0", "end")
                    self.text_box.insert("1.0", cur)
                    self._update_info()
                    self._switch_tab("type")
                    self._on_start()
        except: pass
        self.clipboard_poll_id = self.root.after(500, self._poll_clip)

    # ═══ SETTINGS ═══

    def _get_cfg(self):
        return {"wpm": self.wpm_var.get(), "variation": self.var_var.get(),
            "typo_rate": self.typo_var.get(), "delay": self.delay_var.get(),
            "pauses": self.pauses_var.get(), "burst": self.burst_var.get(),
            "word_typos": self.word_typo_var.get(), "fatigue": self.fatigue_var.get(),
            "variable_speed": self.variable_speed_var.get(), "sound": self.sound_var.get(),
            "theme": self.theme_name}

    def _set_cfg(self, d):
        self.wpm_var.set(d.get("wpm", 60))
        self.var_var.set(d.get("variation", 40))
        self.typo_var.set(d.get("typo_rate", 2))
        self.delay_var.set(d.get("delay", 5))
        self.pauses_var.set(d.get("pauses", True))
        self.burst_var.set(d.get("burst", True))
        self.word_typo_var.set(d.get("word_typos", True))
        self.fatigue_var.set(d.get("fatigue", False))
        self.variable_speed_var.set(d.get("variable_speed", True))
        self.sound_var.set(d.get("sound", False))
        if d.get("theme"): self.theme_name = d["theme"]

    def _save_settings(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._get_cfg(), f, indent=2)
            messagebox.showinfo("Saved", f"Settings saved.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    self._set_cfg(json.load(f))
            except: pass

    def _reset_defaults(self):
        self._set_cfg({})
        messagebox.showinfo("Reset", "Defaults restored.")

    # ═══ THEME ═══

    def _toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.t = THEMES[self.theme_name]
        for w in self.root.winfo_children(): w.destroy()
        self._build_ui()

    # ═══ HOTKEYS ═══

    def _setup_hotkeys(self):
        if not HAS_PYNPUT: return
        try:
            def on_press(key):
                try:
                    if key == pynput_keyboard.Key.f6:
                        self.root.after(0, self._on_stop if self.typing_active else self._on_start)
                    elif key == pynput_keyboard.Key.f7:
                        self.root.after(0, self._on_pause)
                except: pass
            self.hotkey_listener = pynput_keyboard.Listener(on_press=on_press)
            self.hotkey_listener.daemon = True
            self.hotkey_listener.start()
        except: pass


if __name__ == '__main__':
    root = tk.Tk()
    try:
        from ctypes import windll, byref, c_int
        root.update()
        hwnd = windll.user32.GetParent(root.winfo_id())
        windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(c_int(2)), 4)
    except: pass
    app = HumanTypeApp(root)
    root.mainloop()
