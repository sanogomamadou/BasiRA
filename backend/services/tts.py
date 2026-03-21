from gtts import gTTS
import io


def synthesize(text: str) -> bytes:
    """
    Convertit du texte en audio MP3 via Google Text-to-Speech.
    Gratuit, stable, sans clé API.
    Note: gTTS est synchrone, pas de async nécessaire.
    """
    tts = gTTS(text=text, lang="fr", slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()