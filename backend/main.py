from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import base64
import uuid
import os
from pathlib import Path
from config import HOST, PORT
from services import stt, tts, vision, detection

# Dossier pour stocker les fichiers audio temporaires
AUDIO_CACHE = Path(__file__).parent / "audio_cache"
AUDIO_CACHE.mkdir(exist_ok=True)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

app = FastAPI(title="BasiRA", description="Assistant IA pour personnes malvoyantes")

# CORS pour que la PWA puisse communiquer avec le backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "BasiRA est en ligne"}


# ============================================================
# ÉTAPE 2 : STT + TTS
# ============================================================

@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Reçoit un fichier audio, retourne la transcription texte."""
    audio_bytes = await audio.read()
    text = await stt.transcribe(audio_bytes, filename=audio.filename)
    return {"text": text}


@app.post("/tts")
async def text_to_speech(request: dict):
    """Reçoit du texte, retourne un fichier audio MP3."""
    text = request.get("text", "")
    if not text:
        return {"error": "Aucun texte fourni"}

    audio_bytes = tts.synthesize(text)

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=response.mp3"}
    )


@app.post("/tts-base64")
async def text_to_speech_base64(request: dict):
    """Reçoit du texte, retourne l'audio en base64 (pour le frontend)."""
    text = request.get("text", "")
    if not text:
        return {"error": "Aucun texte fourni"}

    audio_bytes = tts.synthesize(text)
    audio_b64 = base64.b64encode(audio_bytes).decode()

    return {"audio": audio_b64}


def save_audio_cache(audio_bytes: bytes) -> str:
    """Sauvegarde l'audio dans le cache et retourne l'ID."""
    # Nettoyer les vieux fichiers (garder max 20)
    cached = sorted(AUDIO_CACHE.glob("*.mp3"), key=os.path.getmtime)
    while len(cached) > 20:
        cached.pop(0).unlink()

    audio_id = str(uuid.uuid4())[:8]
    path = AUDIO_CACHE / f"{audio_id}.mp3"
    path.write_bytes(audio_bytes)
    return audio_id


@app.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Sert un fichier audio depuis le cache — compatible mobile."""
    path = AUDIO_CACHE / f"{audio_id}.mp3"
    if not path.exists():
        return Response(status_code=404)
    return Response(
        content=path.read_bytes(),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache",
            "Accept-Ranges": "bytes"
        }
    )


@app.post("/tts-url")
async def tts_to_url(request: dict):
    """Génère l'audio TTS et retourne une URL pour le lire."""
    text = request.get("text", "")
    if not text:
        return {"error": "Aucun texte fourni"}
    audio_bytes = tts.synthesize(text)
    audio_id = save_audio_cache(audio_bytes)
    return {"audio_id": audio_id}


# ============================================================
# ÉTAPE 3 : Vision (description, lecture, Q&A)
# ============================================================

@app.post("/describe")
async def describe_scene(image: UploadFile = File(...)):
    """Reçoit une image, retourne une description de scène pour malvoyant."""
    image_bytes = await image.read()
    description = await vision.describe_scene(image_bytes)
    return {"description": description}


@app.post("/read")
async def read_document(image: UploadFile = File(...)):
    """Reçoit une image de document, retourne le texte extrait et structuré."""
    image_bytes = await image.read()
    text = await vision.read_document(image_bytes)
    return {"text": text}


@app.post("/ask")
async def visual_qa(image: UploadFile = File(...), question: str = "Que vois-tu ?"):
    """Reçoit une image + une question, retourne une réponse."""
    image_bytes = await image.read()
    answer = await vision.visual_qa(image_bytes, question)
    return {"answer": answer}


@app.post("/money")
async def detect_money(image: UploadFile = File(...)):
    """Reçoit une image, identifie les billets/pièces MAD."""
    image_bytes = await image.read()
    result = await vision.detect_money(image_bytes)
    return {"result": result}


@app.post("/detect")
async def detect_obstacles_endpoint(image: UploadFile = File(...)):
    """Détection complète d'obstacles via Vision IA (murs, portes, escaliers, etc.)."""
    image_bytes = await image.read()
    text = await vision.detect_obstacles_ai(image_bytes)
    return {"text": text}


@app.post("/detect-fast")
async def detect_obstacles_fast(image: UploadFile = File(...)):
    """Détection rapide d'obstacles via YOLOv8 (objets courants seulement)."""
    image_bytes = await image.read()
    obstacles = detection.detect_obstacles(image_bytes)
    text = detection.format_obstacles_text(obstacles)
    return {"obstacles": obstacles, "text": text}


# ============================================================
# ÉTAPE 4 : Orchestrateur — endpoint unique /process
# ============================================================

# Mots-clés pour détecter la commande dans la transcription
COMMANDS = {
    "describe": ["décris", "decris", "décrit", "describe", "qu'est-ce qu'il y a", "devant moi", "autour de moi", "où suis-je", "ou suis-je", "que vois"],
    "read":     ["lis", "lire", "lecture", "document", "texte", "panneau", "affiche", "ordonnance"],
    "money":    ["billet", "monnaie", "argent", "dirham", "combien", "pièce", "piece", "sous"],
    "detect":   ["obstacle", "danger", "attention", "chemin", "passage", "route", "trottoir", "marche"],
    "ask":      []  # fallback — toute question libre
}


def classify_command(text: str) -> tuple:
    """
    Analyse la transcription vocale et retourne (action, question_restante).
    """
    text_lower = text.lower().strip()

    for action, keywords in COMMANDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return action, text_lower

    # Par défaut → question libre (VQA)
    return "ask", text_lower


@app.post("/process")
async def process(
    audio: UploadFile = File(...),
    image: UploadFile = File(...)
):
    """
    Endpoint principal de BasiRA.
    Reçoit : audio (commande vocale) + image (capture caméra)
    Retourne : texte de réponse + URL audio
    """
    # 1. Transcrire la commande vocale
    audio_bytes = await audio.read()
    transcription = await stt.transcribe(audio_bytes, filename=audio.filename or "audio.webm")

    # 2. Classifier la commande
    action, question = classify_command(transcription)

    # 3. Traiter l'image selon l'action
    image_bytes = await image.read()

    if action == "describe":
        result_text = await vision.describe_scene(image_bytes)
    elif action == "read":
        result_text = await vision.read_document(image_bytes)
    elif action == "money":
        result_text = await vision.detect_money(image_bytes)
    elif action == "detect":
        result_text = await vision.detect_obstacles_ai(image_bytes)
    else:  # "ask"
        result_text = await vision.visual_qa(image_bytes, question)

    # 4. Convertir la réponse en audio et sauvegarder
    audio_response = tts.synthesize(result_text)
    audio_id = save_audio_cache(audio_response)

    return {
        "transcription": transcription,
        "action": action,
        "text": result_text,
        "audio_id": audio_id
    }


# ============================================================
# Servir le frontend
# ============================================================

@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


# Servir les fichiers statiques du frontend (manifest.json, etc.)
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")


if __name__ == "__main__":
    import glob

    # Chercher automatiquement les certificats SSL (générés par mkcert)
    pem_files = glob.glob("*.pem")
    cert_file = next((f for f in pem_files if "key" not in f), None)
    key_file = next((f for f in pem_files if "key" in f), None)

    if cert_file and key_file:
        print(f"HTTPS activé avec {cert_file} + {key_file}")
        print(f"Ouvrir https://localhost:{PORT} ou https://<ton-ip>:{PORT}")
        uvicorn.run(app, host=HOST, port=PORT, ssl_certfile=cert_file, ssl_keyfile=key_file)
    else:
        print("HTTP uniquement (pas de certificats SSL trouvés)")
        print(f"Ouvrir http://localhost:{PORT}")
        print("Pour HTTPS : mkcert localhost 127.0.0.1 <ton-ip>")
        uvicorn.run(app, host=HOST, port=PORT)