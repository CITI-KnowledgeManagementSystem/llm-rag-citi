import os

# TTS server configuration
TTS_SERVER_URL = os.getenv('TTS_SERVER_URL')

# Default TTS parameters
DEFAULT_VOICE_MODE = "predefined"
DEFAULT_PREDEFINED_VOICE_ID = "default"
DEFAULT_OUTPUT_FORMAT = "wav"
DEFAULT_SPLIT_TEXT = True
DEFAULT_CHUNK_SIZE = 120
DEFAULT_TEMPERATURE = 0.7
DEFAULT_EXAGGERATION = 0.0
DEFAULT_CFG_WEIGHT = 1.0
DEFAULT_SPEED_FACTOR = 1.0
DEFAULT_LANGUAGE = "en"

# OpenAI compatible defaults
OPENAI_MODEL = "tts-1"
OPENAI_VOICE = "alloy"
OPENAI_RESPONSE_FORMAT = "wav"
OPENAI_SPEED = 1.0

# Audio file storage
AUDIO_DIR = os.getenv('AUDIO_DIR', './audio_files')

# Podcast speaker configuration
PODCAST_SPEAKERS = {
    "HOST_A": {
        "voice_id": "host_a_voice",
        "voice_mode": "predefined",
        "predefined_voice_id": "default",
        "temperature": 0.6,
        "speed_factor": 1.0,
        "exaggeration": 0.2
    },
    "HOST_B": {
        "voice_id": "host_b_voice", 
        "voice_mode": "predefined",
        "predefined_voice_id": "default",
        "temperature": 0.8,
        "speed_factor": 1.1,
        "exaggeration": 0.3
    }
}

# Audio processing settings
SILENCE_DURATION = 0.5  # seconds of silence between speakers
AUDIO_FADE_DURATION = 0.1  # seconds for fade in/out effects