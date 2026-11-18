"""
config.py - Configuration for AI Storytelling Video Pipeline
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure required directories exist
for folder in [TEMP_DIR, OUTPUT_DIR, FONTS_DIR, MUSIC_DIR]:
    os.makedirs(folder, exist_ok=True)

# API Keys
AI_HORDE_API_KEY = os.getenv("AI_HORDE_API_KEY", "0000000000")
AI_HORDE_BASE_URL = os.getenv("AI_HORDE_BASE_URL", "https://aihorde.net/api/v2")
AI_HORDE_CLIENT_AGENT = os.getenv("AI_HORDE_CLIENT_AGENT", "StoryFlow:1.0.0:dev@localhost")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Video Presets (16:9 Landscape vs 9:16 Vertical Shorts)
ASPECT_PRESETS = {
    "16:9": {
        "width": 1920,
        "height": 1080,
        "image_width": 768,
        "image_height": 512,
        "subtitle_font_size": 22,
        "subtitle_margin_v": 45,
    },
    "9:16": {
        "width": 1080,
        "height": 1920,
        "image_width": 512,
        "image_height": 768,
        "subtitle_font_size": 30,
        "subtitle_margin_v": 180,
    }
}
DEFAULT_ASPECT = "9:16"
FPS = 30

# High-Quality Storyteller Voices (Edge-TTS)
VALID_VOICES = {
    # English Voices
    "christopher": "en-US-ChristopherNeural",  # Deep, warm, captivating narrator (Default)
    "guy": "en-US-GuyNeural",                  # Clear, engaging storytelling
    "jenny": "en-US-JennyNeural",              # Gentle, expressive female voice
    "ryan": "en-GB-RyanNeural",                # British fantasy / folklore narrator
    "sonia": "en-GB-SoniaNeural",              # Classic British fairy-tale voice
    "eric": "en-US-EricNeural",                # Adventurous, energetic

    # Urdu Voices
    "asad": "ur-PK-AsadNeural",                # Pakistani Urdu Male (Authentic, clear)
    "uzma": "ur-PK-UzmaNeural",                # Pakistani Urdu Female (Expressive)
    "salman": "ur-IN-SalmanNeural",            # Urdu/Hindi Male (Deep, resonant)
    "gul": "ur-IN-GulNeural",                  # Urdu/Hindi Female (Soft narrator)
}
DEFAULT_VOICE = "en-US-ChristopherNeural"

# Preferred AI Horde Models for Cartoon / Storybook Art
CARTOON_IMAGE_MODELS = [
    "Dreamshaper",
    "Deliberate",
    "Rev Animated",
    "Anything v5",
    "Anything Diffusion",
    "stable_diffusion"
]

# Universal Art Style Anchors (appended to every scene prompt for consistent cartoon aesthetic)
CARTOON_STYLE_PREFIX = (
    "charming storybook illustration, warm vibrant cartoon style, expressive characters, "
    "fairytale aesthetic, soft cinematic lighting, highly detailed whimsical background, "
    "sharp colorful outlines, 8k masterpiece"
)

CARTOON_NEGATIVE_PROMPT = (
    "photorealistic, real photograph, 3d render, creepy, deformed eyes, bad anatomy, "
    "mutated hands, extra limbs, ugly, text, watermark, signature, blurry, grainy, dark"
)

# Audio Settings
MUSIC_VOLUME = 0.12  # Ducked under voiceover
VOICE_RATE = "+0%"   # Natural reading speed
