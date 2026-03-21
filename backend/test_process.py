"""
Test de l'orchestrateur /process.
Simule ce que le frontend fera : envoie un audio + une image, reçoit la réponse vocale.

Usage : python test_process.py image.jpg audio.webm
   ou : python test_process.py image.jpg  (utilise un audio de test généré automatiquement)
"""
import requests
import sys
import os
import base64


def create_test_audio():
    """Crée un fichier audio de test avec gTTS (simule une commande vocale)."""
    from gtts import gTTS
    test_text = "Décris ce qui est devant moi"
    tts = gTTS(text=test_text, lang="fr", slow=False)
    tts.save("test_command.mp3")
    print(f"Audio de test créé : 'Décris ce qui est devant moi'")
    return "test_command.mp3"


def test_process(image_path, audio_path):
    print(f"=== Test /process ===")
    print(f"Image : {image_path}")
    print(f"Audio : {audio_path}")
    print()

    with open(image_path, "rb") as img, open(audio_path, "rb") as aud:
        response = requests.post(
            "http://localhost:8000/process",
            files={
                "image": (os.path.basename(image_path), img, "image/jpeg"),
                "audio": (os.path.basename(audio_path), aud, "audio/mpeg")
            }
        )

    if response.status_code != 200:
        print(f"Erreur {response.status_code} : {response.text}")
        return

    result = response.json()
    print(f"Transcription : {result['transcription']}")
    print(f"Action détectée : {result['action']}")
    print(f"Réponse texte : {result['text']}")
    print()

    # Sauvegarder et jouer l'audio de réponse
    if result.get("audio"):
        audio_data = base64.b64decode(result["audio"])
        with open("test_process_response.mp3", "wb") as f:
            f.write(audio_data)
        print(f"Audio réponse sauvegardé : test_process_response.mp3 ({len(audio_data)} octets)")
        os.startfile("test_process_response.mp3")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python test_process.py image.jpg [audio.webm]")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Image introuvable : {image_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        audio_path = sys.argv[2]
    else:
        print("Pas d'audio fourni, création d'un audio de test...")
        audio_path = create_test_audio()

    test_process(image_path, audio_path)