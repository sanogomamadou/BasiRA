import httpx
from config import GROQ_API_KEY, STT_MODEL


async def transcribe(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcrit un fichier audio en texte français via Groq Whisper.
    Gratuit, rapide (~0.3s), excellent en français.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": (filename, audio_bytes, "audio/webm")},
            data={
                "model": STT_MODEL,
                "language": "fr",
                "response_format": "json"
            }
        )

        if response.status_code != 200:
            raise Exception(f"Groq STT error {response.status_code}: {response.text}")

        return response.json()["text"]