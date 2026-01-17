import os

# ==============================================================================
# 1. API CONFIGURATION
# ==============================================================================
# Get your AccessKey for free at https://console.picovoice.ai/
# This is REQUIRED for the wake word detection to work.
PORCUPINE_ACCESS_KEY = ""


# ==============================================================================
# 2. AUDIO SETTINGS
# ==============================================================================
# Audio sample rate required by Porcupine. Do not change.
SAMPLE_RATE = 16000

# Audio chunk size. 1024 is standard for low latency.
CHUNK_SIZE = 1024

# Amplitude threshold for clap detection (0-32767 for 16-bit audio).
# - Increase if the system triggers on background noise.
# - Decrease if it misses your claps.
CLAP_THRESHOLD = 1500

# Maximum time (in seconds) allowed between claps to consider them a sequence.
CLAP_INTERVAL = 1.0


# ==============================================================================
# 3. SYSTEM SETTINGS
# ==============================================================================
# How long the system listens for claps after the wake word is detected (seconds).
ACTIVE_DURATION = 30

# The wake word to listen for.
# Must be one of the AVAILABLE_WAKE_WORDS below unless you have a custom file.
DEFAULT_WAKE_WORD = "jarvis"

# Debug mode prints detailed logs to the console.
DEBUG_MODE = True


# ==============================================================================
# 4. PATH SETTINGS
# ==============================================================================
# Default development directory. Converted to absolute path.
DEFAULT_PROJECT_PATH = os.path.expanduser("~/Downloads/Development")


# ==============================================================================
# 5. APP CONFIGURATIONS
# ==============================================================================
# List of apps/commands to launch on DOUBLE CLAP.
APPS_TO_LAUNCH = [
    {
        "command": "code",
        "args": [os.path.expanduser("~/Downloads/Devlopment/GitHub Repository/go-url-shortener")],
        "type_msg": "Opening Go URL Shortener Project"
    }
]

# Action to trigger on TRIPLE CLAP.
SECONDARY_ACTION = {
    "command": "open",
    "args": ["-a", "Google Chrome", "https://youtu.be/syFZfO_wfMQ"],
    "type_msg": "Playing YouTube Video"
}


# ==============================================================================
# 6. AVAILABLE WAKE WORDS
# ==============================================================================
# Standard wake words available in Porcupine.
AVAILABLE_WAKE_WORDS = [
    "jarvis",
    "computer",
    "alexa",
    "hey google",
    "terminator",
    "porcupine",
    "bumblebee"
]
