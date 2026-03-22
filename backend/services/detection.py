from ultralytics import YOLO
from PIL import Image
import io

# Charger le modèle une seule fois au démarrage (6 MB)
model = YOLO("yolov8n.pt")

# ============================================================
# CLASSIFICATION DES OBJETS PAR NIVEAU DE DANGER
# ============================================================

# CRITIQUE — véhicules, peut blesser gravement
CRITICAL = {
    2: "voiture", 3: "moto", 5: "bus", 7: "camion",
    1: "vélo",
}

# HAUT — gros obstacles sur lesquels on se cogne / trébuche
HIGH = {
    0: "personne", 13: "banc", 56: "chaise", 57: "canapé",
    59: "lit", 60: "table", 62: "télévision", 72: "réfrigérateur",
    73: "valise",
}

# MOYEN — obstacles au sol, animaux
MEDIUM = {
    16: "chien", 17: "cheval", 15: "chat",
    58: "plante en pot", 24: "sac à dos", 25: "parapluie",
    26: "sac à main", 27: "valise", 28: "frisbee",
    36: "skateboard",
}

# BAS — petits objets, moins dangereux mais à signaler
LOW = {
    39: "bouteille", 41: "tasse", 44: "bouteille",
    63: "ordinateur portable", 67: "téléphone",
    74: "horloge", 75: "vase",
}

ALL_OBJECTS = {**CRITICAL, **HIGH, **MEDIUM, **LOW}
DANGER_LEVELS = {}
for d, obj_dict in [(4, CRITICAL), (3, HIGH), (2, MEDIUM), (1, LOW)]:
    for cls_id in obj_dict:
        DANGER_LEVELS[cls_id] = d

# ============================================================
# SEUILS
# ============================================================
CONF_THRESHOLD = 0.40       # Confiance minimale
MIN_SIZE_RATIO = 0.015      # Ignorer les objets trop petits (< 1.5% de l'image)
CLOSE_RATIO = 0.06          # > 6% de l'image = proche
VERY_CLOSE_RATIO = 0.15     # > 15% de l'image = très proche
BOTTOM_CLOSE = 0.75         # Bas de la boîte > 75% de l'image = proche
BOTTOM_VERY_CLOSE = 0.88    # Bas de la boîte > 88% = très proche


# ============================================================
# DÉTECTION
# ============================================================
def detect_obstacles(image_bytes: bytes) -> list:
    """
    Détecte les obstacles dans une image.
    Retourne une liste triée par danger décroissant.
    """
    image = Image.open(io.BytesIO(image_bytes))
    img_w, img_h = image.size
    img_area = img_w * img_h

    results = model(image, conf=CONF_THRESHOLD, verbose=False)[0]

    obstacles = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id not in ALL_OBJECTS:
            continue

        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        box_area = (x2 - x1) * (y2 - y1)
        ratio = box_area / img_area

        # Ignorer les objets trop petits
        if ratio < MIN_SIZE_RATIO:
            continue

        # === Position horizontale ===
        center_x = (x1 + x2) / 2
        if center_x < img_w * 0.30:
            position = "à gauche"
            zone = "left"
        elif center_x > img_w * 0.70:
            position = "à droite"
            zone = "right"
        else:
            position = "devant vous"
            zone = "center"

        # === Proximité (taille + position verticale) ===
        bottom_y = y2 / img_h  # Plus le bas de la boîte est en bas, plus l'objet est proche

        if ratio > VERY_CLOSE_RATIO or bottom_y > BOTTOM_VERY_CLOSE:
            proximite = "très proche"
            prox_score = 3
        elif ratio > CLOSE_RATIO or bottom_y > BOTTOM_CLOSE:
            proximite = "proche"
            prox_score = 2
        else:
            proximite = "à quelques mètres"
            prox_score = 1

        # === Score de danger ===
        base_danger = DANGER_LEVELS.get(cls_id, 1)
        # Véhicules proches = danger maximal
        if cls_id in CRITICAL and prox_score >= 2:
            danger = 5
        else:
            danger = base_danger + prox_score

        obstacles.append({
            "objet": ALL_OBJECTS[cls_id],
            "position": position,
            "zone": zone,
            "proximite": proximite,
            "danger": danger,
            "confiance": round(conf, 2),
            "taille": round(ratio, 3),
            "prox_score": prox_score
        })

    # Trier : danger max en premier, puis par taille
    obstacles.sort(key=lambda x: (-x["danger"], -x["taille"]))

    # Limiter à 6 obstacles max
    return obstacles[:6]


# ============================================================
# ANALYSE DE LA VOIE LIBRE
# ============================================================
def _find_free_path(obstacles, img_zones=("left", "center", "right")):
    """Détermine quelle zone est la plus libre pour passer."""
    zone_danger = {"left": 0, "center": 0, "right": 0}

    for obs in obstacles:
        z = obs["zone"]
        zone_danger[z] += obs["danger"]

    # Zone avec le moins de danger
    safest = min(zone_danger, key=zone_danger.get)
    total_danger = sum(zone_danger.values())

    if total_danger == 0:
        return None  # Tout est libre

    labels = {"left": "à gauche", "center": "tout droit", "right": "à droite"}
    return labels[safest]


# ============================================================
# FORMATAGE DU TEXTE
# ============================================================
def format_obstacles_text(obstacles: list) -> str:
    """Formate la détection en texte naturel pour le TTS."""
    if not obstacles:
        return "La voie semble libre."

    # Séparer par proximité
    tres_proches = [o for o in obstacles if o["proximite"] == "très proche"]
    proches = [o for o in obstacles if o["proximite"] == "proche"]
    loin = [o for o in obstacles if o["proximite"] == "à quelques mètres"]

    parts = []

    # Alertes critiques d'abord
    vehicules = [o for o in tres_proches + proches if o["objet"] in CRITICAL.values()]
    if vehicules:
        v = vehicules[0]
        parts.append(f"Attention, {v['objet']} {v['position']}, {v['proximite']}")

    # Obstacles très proches (hors véhicules déjà mentionnés)
    autres_proches = [o for o in tres_proches if o["objet"] not in CRITICAL.values()]
    if autres_proches:
        parts.append(f"{_group(autres_proches)}, très proche")

    # Obstacles proches
    autres_moyens = [o for o in proches if o["objet"] not in CRITICAL.values()]
    if autres_moyens:
        parts.append(f"{_group(autres_moyens)}, proche")

    # Loin — mentionner brièvement
    if loin and len(parts) < 3:
        parts.append(f"{_group(loin)}, à quelques mètres")

    # Recommandation de direction
    free_path = _find_free_path(obstacles)
    if free_path:
        parts.append(f"Passage possible {free_path}")

    text = ". ".join(parts) + "."

    # Préfixe d'alerte si danger élevé
    max_danger = max(o["danger"] for o in obstacles) if obstacles else 0
    if max_danger >= 5:
        text = "Danger! " + text
    elif max_danger >= 3:
        text = "Attention. " + text

    return text


def _group(obstacles: list) -> str:
    """Regroupe les obstacles identiques : '2 chaises à gauche et un banc devant vous'."""
    counts = {}
    positions = {}
    for o in obstacles:
        n = o["objet"]
        counts[n] = counts.get(n, 0) + 1
        if n not in positions:
            positions[n] = o["position"]

    parts = []
    for name, count in counts.items():
        pos = positions[name]
        if count == 1:
            parts.append(f"un {name} {pos}")
        else:
            # Pluriel simple
            plural = name + "s" if not name.endswith("s") else name
            parts.append(f"{count} {plural} {pos}")

    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} et {parts[1]}"
    else:
        return ", ".join(parts[:-1]) + f" et {parts[-1]}"