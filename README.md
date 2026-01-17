# 🎤 Audio Automation - Voice & Clap Controlled App Launcher

> **Control your Mac with just your voice and claps!**

Manage your workflow hands-free. This Python based tool listens for a wake word and then detects clap patterns to launch applications or trigger custom actions.

---

## ✨ Features

- 🗣️ **Wake Word Activation**: Starts listening when you say "jarvis" (configurable).
- 👏👏 **Double Clap**: Quickly launch a set of configured applications (e.g., VS Code, Chrome).
- 👏👏👏 **Triple Clap**: Trigger a secondary action (e.g., play a music playlist, open a specific URL).
- 🔒 **100% Private**: All audio processing happens locally on your device. No cloud recording.
- ⚡ **Fast & Lightweight**: Built with `pvporcupine` for instant wake word detection.
- 🎯 **Customizable**: Easily edit `config.py` to change apps, sensitivity, and timing.
- 🆓 **Free to Use**: Runs on the free tier of the Picovoice Porcupine API.

---

## 📋 Requirements

- **Operating System**: macOS (Recommended) / Windows (Compatible but may require extra setup).
- **Python**: Version 3.8 or higher.
- **Hardware**: A working microphone.
- **API Key**: A free AccessKey from [Picovoice Console](https://console.picovoice.ai/).

---

## 🚀 Installation (macOS)

### 1. Clone the project
```bash
git clone https://github.com/yourusername/audio-automation.git
cd audio-automation
```

### 2. Set up the environment
Ideally, create a virtual environment to keep dependencies clean:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Audio Drivers
Required for `pyaudio` on macOS:
```bash
brew install portaudio
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Before running the app, you **MUST** configure it.

1.  **Get your Access Key**:
    *   Sign up at [console.picovoice.ai](https://console.picovoice.ai/).
    *   Copy your `AccessKey`.

2.  **Edit `config.py`**:
    *   Open `config.py` in your text editor.
    *   Paste your key into the `PORCUPINE_ACCESS_KEY` variable:
        ```python
        PORCUPINE_ACCESS_KEY = "your_long_key_string_here"
        ```

3.  **Customize Apps**:
    *   Modify the `APPS_TO_LAUNCH` list in `config.py` to add your favorite apps.
    *   Example:
        ```python
        APPS_TO_LAUNCH = [
            {"command": "open", "args": ["-a", "Spotify"], "type_msg": "Opening Spotify"},
            {"command": "code", "args": ["~/MyProject"], "type_msg": "Opening VS Code"}
        ]
        ```

---

## 🚦 Usage

1.  **Run the script**:
    ```bash
    python3 audio_launcher.py
    ```

2.  **Wait for initialization**:
    You will see:
    ```
    ============================================================
    System Online. Wake word: 'jarvis'
    Waiting for wake word...
    ============================================================
    ```

3.  **Commands**:
    *   **Says "Jarvis"**: The system wakes up and listens for claps (default: 30 seconds).
    *   **Clap Twice (👏👏)**: Launches your primary apps (VS Code, Chrome, etc.).
    *   **Clap Three Times (👏👏👏)**: Triggers the secondary action (e.g., opens YouTube).

4.  **Exit**:
    Press `Ctrl+C` in the terminal to stop the program.

---

## 🛠️ Customization

All settings are adjustable in `config.py`:

*   **`CLAP_THRESHOLD`**: Adjust microphone sensitivity. Lower this value if it doesn't hear your claps; raise it if it triggers on background noise.
*   **`ACTIVE_DURATION`**: How long the system listens for claps after hearing the wake word.
*   **`DEFAULT_WAKE_WORD`**: Change "jarvis" to "computer", "alexa", or other supported words.
*   **`CLAP_INTERVAL`**: Adjust how fast you need to clap.

---

## 📂 Project Structure

*   `audio_launcher.py`: Main script handling audio input and logic.
*   `config.py`: Central configuration file for all settings.
*   `app_launcher.py`: Helper module for robust app management.
*   `requirements.txt`: Python package dependencies.

---

**Happy Automating!** 🚀
