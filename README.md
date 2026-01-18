# 🎙️ Jarvis - Audio Automation for macOS

> **"Just say it, double clap, and it's done."**  
> A privacy-first, sci-fi inspired voice assistant for macOS.

![macOS Verified](https://img.shields.io/badge/Platform-macOS-000000?style=flat-square&logo=apple)
![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-34C759?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-007AFF?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)

---

## 🌌 Overview

**Jarvis** is a background utility that listens for a wake word ("Jarvis") and then waits for a **Clap Pattern** to trigger actions. Unlike Siri or Alexa, Jarvis runs **locally** on your device using Picovoice Porcupine, ensuring zero latency and zero data leaks.

### ✨ Key Features

*   **🗣️ Sonic Identity**: Jarvis speaks back ("Yes, Sir") using the 'Daniel' British voice.
*   **👁️ Sci-Fi HUD**: A floating, futuristic "Orb" that pulses when listening and reacts to volume levels.
*   **🔒 True Privacy Mode**: The microphone is **physically disconnected** when paused. No "Orange Dot" surveillance.
*   **🎚️ Advanced Controls**: Settings Dashboard to adjust clap sensitivity (down to whisper levels), manage keys, and view logs.
*   **🚀 Smart Launch**: Double-Clap to launch your workspace (VS Code, Chrome). Triple-Clap for media/secondary actions.

---

## 🛠️ Usage

### 🚀 Quick Start
1.  **Launch the App**: Open usage `Jarvis.app` or run `start_gui.sh`.
2.  **Say "Jarvis"**: You will hear a *Hero* chime and "Yes, Sir".
3.  **Clap Twice (👏👏)**: Launches your configured Development workspace.

### 🎛️ Settings Dashboard
Click the **Gear Icon** in the System Tray (Menu Bar) to open the Command Center:
*   **Microphone Toggle**: Instantly cut mic access (Green = Live, Red = Off).
*   **Sensitivity**: Adjust `100 - 5000` to tune clap detection.
*   **System Log**: View real-time diagnostics ("Claps Detected: 2").

---

## ⚙️ Configuration

Jarvis uses `config.py` for core settings.

### 🔑 Setup (First Run)
1.  **Get AccessKey**: Sign up for free at [Picovoice Console](https://console.picovoice.ai/).
2.  **Clone Repo**:
    ```bash
    git clone https://github.com/yourusername/audio-automation.git
    cd audio-automation
    ```
3.  **Install Dependencies**:
    ```bash
    brew install portaudio # Required for PyAudio
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  **Configure**:
    Create `config.py` (see `config_example.py`) and paste your API Key.

### 🎵 Custom Sounds
You can customize the sound effects in `config.py`:
```python
"sounds": {
    "startup": "/System/Library/Sounds/Blow.aiff",
    "wake": "/System/Library/Sounds/Hero.aiff", # Or set WAKE_RESPONSE to text
    "success": "/System/Library/Sounds/Glass.aiff"
}
```

---

## 🧩 Action Roadmap (Brick by Brick)

We are building Jarvis incrementally:
- [x] **Core Engine**: Wake Word + Clap Detection.
- [x] **Privacy**: Physical Mic Disconnect.
- [x] **Sonic Identity**: TTS Feedback.
- [ ] **Media Control**: "Jarvis, Next Song".
- [ ] **Smart Home**: "Jarvis, Lights On".

---

## ⚠️ Troubleshooting

**"The Orange Dot is still on!"**  
Wait 5 seconds. macOS takes a moment to update the status bar after we terminate the driver.

**"It ignores my claps!"**  
Open Settings and lower the **Sensitivity Slider** to ~200. Ensure you aren't clapping too fast (0.5s interval is best).

**"VS Code isn't opening!"**  
Check the System Log. If you see `[Errno 2]`, it means the path is wrong. Use the "Test Action" button in Settings to debug.

---

built with 💙 by **pranavgawai**
