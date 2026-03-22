import httpx
import base64
from config import GROQ_API_KEY, VISION_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


async def _call_vision(image_bytes: bytes, prompt: str, max_tokens: int = 300) -> str:
    """Appel générique à Groq Vision avec une image + un prompt."""
    b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            raise Exception(f"Groq Vision error {response.status_code}: {response.text}")

        return response.json()["choices"][0]["message"]["content"]


async def describe_scene(image_bytes: bytes) -> str:
    """Décrit une scène pour une personne malvoyante."""
    prompt = (
        "Tu es un assistant pour une personne aveugle. "
        "Décris cette scène de manière concise et utile pour la navigation. "
        "Mentionne : les obstacles, les personnes, les panneaux lisibles, "
        "les portes, les directions possibles. "
        "Réponds en français, 2-3 phrases maximum."
    )
    return await _call_vision(image_bytes, prompt, max_tokens=200)


async def read_document(image_bytes: bytes) -> str:
    """Lit et structure le contenu d'un document photographié."""
    prompt = (
        "Tu es un assistant pour une personne aveugle. "
        "Extrais et lis tout le texte visible dans cette image. "
        "Si c'est un formulaire, indique les champs et leurs valeurs. "
        "Si c'est une ordonnance, lis les médicaments et posologies. "
        "Si c'est un panneau ou une affiche, lis le contenu. "
        "Structure ta réponse clairement. Réponds en français."
    )
    return await _call_vision(image_bytes, prompt, max_tokens=500)


async def visual_qa(image_bytes: bytes, question: str) -> str:
    """Répond à une question libre sur une image."""
    prompt = (
        "Tu es un assistant pour une personne aveugle. "
        f"Réponds à cette question de manière concise et utile : {question} "
        "Réponds en français."
    )
    return await _call_vision(image_bytes, prompt, max_tokens=200)


async def detect_money(image_bytes: bytes) -> str:
    """Identifie les billets et pièces de monnaie marocaine (MAD)."""
    prompt = (
        "Tu es un assistant pour une personne aveugle au Maroc. "
        "Regarde cette image et identifie les billets ou pièces de monnaie marocaine (dirham, MAD). "
        "Les billets marocains existants sont : 20 DH (bleu), 50 DH (vert), 100 DH (marron/orange), 200 DH (jaune/doré). "
        "Pour chaque billet ou pièce visible, indique : "
        "- La valeur (ex: 100 dirhams) "
        "- Le nombre si plusieurs billets "
        "- Le total si plusieurs billets ou pièces "
        "Si ce n'est pas de la monnaie, dis-le clairement. "
        "Réponds en français, de manière concise."
    )
    return await _call_vision(image_bytes, prompt, max_tokens=200)


async def detect_obstacles_ai(image_bytes: bytes) -> str:
    """Détection d'obstacles complète pour navigation indoor/outdoor."""
    prompt = (
        "Tu es un assistant de navigation pour une personne aveugle. "
        "Analyse cette image et signale TOUS les obstacles et éléments importants pour se déplacer en sécurité. "
        "Signale en priorité :\n"
        "- Obstacles au sol : marches, escaliers (montants ou descendants), trottoir, bordure, trou, câble, objet au sol\n"
        "- Obstacles à hauteur du corps : murs, portes (ouvertes ou fermées), poteaux, piliers, barrières, meubles\n"
        "- Obstacles suspendus : panneaux, branches, étagères basses\n"
        "- Personnes et animaux sur le chemin\n"
        "- Véhicules en mouvement ou stationnés\n"
        "- Éléments de navigation : porte de sortie, couloir, passage libre, direction possible\n"
        "Pour chaque élément, indique :\n"
        "1. Quoi (ex: porte fermée, escalier descendant, chaise)\n"
        "2. Où (à gauche, à droite, devant, au centre)\n"
        "3. Distance approximative (très proche, proche, loin)\n"
        "Termine par une recommandation de direction : où aller pour avancer en sécurité.\n"
        "Réponds en français, phrases courtes, style alerte. Maximum 4-5 phrases."
    )
    return await _call_vision(image_bytes, prompt, max_tokens=250)