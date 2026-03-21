import os

# === API Keys ===
# Option 1 : créer un fichier config_local.py (ignoré par git) avec :
#   GROQ_API_KEY = "gsk_ta_cle_ici"
# Option 2 : variable d'environnement GROQ_API_KEY
try:
    from config_local import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "ta-cle-groq-ici")

# === Modèles ===
STT_MODEL = "whisper-large-v3"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# === TTS ===
TTS_VOICE = "fr-FR-DeniseNeural"  # Voix féminine française, claire

# === Détection ===
YOLO_MODEL = "yolov8n.pt"  # 3.2 MB, CPU
OBSTACLE_CONFIDENCE = 0.4
PROXIMITY_THRESHOLD = 0.15  # % de l'image occupé = "proche"

# === Serveur ===
HOST = "0.0.0.0"
PORT = 8000