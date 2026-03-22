<div align="center">

# BasiRA — بصيرة

### Assistant IA de Perception Augmentée pour Personnes Malvoyantes

![Python](https://img.shields.io/badge/Python-3.12+-3776ab?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_4_Scout-f55036?logo=meta&logoColor=white)
![Whisper](https://img.shields.io/badge/Whisper-STT-74aa9c?logo=openai&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Detection-purple)
![Gratuit](https://img.shields.io/badge/Cout-100%25_Gratuit-00e4b8)

*BasiRA transforme un smartphone en assistant visuel intelligent : il décrit l'environnement, lit les documents, identifie la monnaie, détecte les obstacles — le tout par interface 100% vocale, conçu pour les personnes en situation de handicap visuel.*

</div>

---

## 📋 Table des matières

- [🎯 Présentation](#-présentation)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🎮 Interactions accessibles](#-interactions-accessibles)
- [🏗 Architecture technique](#-architecture-technique)
- [🛠 Stack technologique](#-stack-technologique)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [📱 Accès mobile HTTPS](#-accès-mobile-https)
- [🚀 Utilisation](#-utilisation)
- [🗂 Structure du projet](#-structure-du-projet)
- [🔌 Endpoints API](#-endpoints-api)
- [♿ Accessibilité](#-accessibilité)
- [🏛 Contexte du projet](#-contexte-du-projet)

---

## 🎯 Présentation

**BasiRA** (بصيرة — "clairvoyance" en arabe) est une application web progressive (PWA) qui utilise l'intelligence artificielle pour aider les personnes malvoyantes à percevoir et comprendre leur environnement.

L'application fonctionne via un smartphone porté au cou avec un écouteur. L'utilisateur interagit **exclusivement par la voix et des gestes simples** — aucune interaction visuelle avec l'écran n'est nécessaire.

### Pourquoi BasiRA ?

**Le problème :**
- 2,2 milliards de personnes dans le monde souffrent de déficience visuelle (OMS, 2023)
- 1 703 424 personnes en situation de handicap au Maroc, taux de prévalence de 5,1% (RGPH 2014, HCP)
- 28,8% présentent des déficiences visuelles
- Taux d'analphabétisme de 71% chez les personnes handicapées contre 42% dans la population générale

**La solution :**
- Une application mobile gratuite qui utilise la caméra du smartphone et l'IA pour "voir" à la place de l'utilisateur
- Interface 100% vocale et gestuelle
- Adaptée au contexte marocain (monnaie MAD, documents locaux)
- Coût de fonctionnement : **0 DH** — toutes les APIs sont gratuites

**Différenciation :**
- Contrairement à Seeing AI (Microsoft) et Be My Eyes (GPT-4V), BasiRA est 100% gratuit, open source, fonctionne en français, et intègre la détection de monnaie marocaine

---

## ✨ Fonctionnalités

### 🔊 Modules IA

| Module | Description | Commande vocale |
|--------|-------------|-----------------|
| **Description de scène** | Décrit l'environnement : obstacles, personnes, objets, directions | *"Décris ce qui est devant moi"* |
| **Lecture de documents** | Extrait et lit le texte de documents, ordonnances, formulaires, panneaux | *"Lis ce document"* |
| **Questions visuelles** | Répond à toute question libre sur ce que la caméra voit | *"C'est quoi la couleur de ce médicament ?"* |
| **Identification monnaie** | Reconnaît les billets marocains 20, 50, 100, 200 DH | *"C'est quel billet ?"* / *"C'est combien ?"* |
| **Scan d'obstacles** | Détection continue en temps réel avec YOLOv8 + recommandation de direction | *Triple-tap ou "obstacle"* |
| **Mode urgence** | Appui 5 secondes n'importe où pour appel d'urgence automatique | *Appui long 5s* |

---

## 🎮 Interactions accessibles

Aucune interaction visuelle requise. Tout se fait par gestes simples et voix.

### Gestes tactiles

| Geste | Action |
|-------|--------|
| **Double tap** (n'importe où) | Démarre l'enregistrement vocal |
| **Triple tap** (n'importe où) | Active / désactive le scan d'obstacles continu |
| **Tap simple** (pendant enregistrement) | Arrête et envoie la commande |
| **Secouer le téléphone** | Bascule caméra avant/arrière + annonce vocale |
| **Appui long 5 secondes** | Déclenche un appel d'urgence avec bips progressifs |

### Retours sensoriels

| Son | Signification |
|-----|---------------|
| Bip aigu (880 Hz) | Enregistrement démarré |
| Bip grave (440 Hz) | Enregistrement terminé, envoi en cours |
| Double bip montant | Scan d'obstacles activé |
| Double bip descendant | Scan d'obstacles désactivé |
| Bips progressifs (1s à 4s) | Compte à rebours urgence |
| Bip strident (1200 Hz) | Appel d'urgence déclenché |
| Annonce vocale | Confirmation basculement caméra |
| Silence 2,5s | Fin automatique de l'enregistrement |

---

## 🏗 Architecture technique

```
UTILISATEUR (smartphone au cou + écouteur)
        |
        | audio + image (HTTPS)
        v
   PWA FRONTEND (HTML/CSS/JS vanilla)
   - Capture caméra (getUserMedia)
   - Enregistrement micro (MediaRecorder)
   - Double-tap / triple-tap / shake / appui long
   - Détection de silence (AudioAnalyser)
   - Lecture audio (balise <audio> native)
        |
        | REST API
        v
   BACKEND FASTAPI (Python 3.12)
   - /process    --> Orchestrateur principal
   - /describe   --> Description de scène
   - /read       --> Lecture de document
   - /ask        --> Question visuelle libre
   - /money      --> Identification monnaie
   - /detect     --> Obstacles (Vision IA)
   - /detect-fast --> Obstacles (YOLOv8 rapide)
   - /stt, /tts  --> Speech-to-Text, Text-to-Speech
   - /audio/:id  --> Streaming audio MP3
        |
        | API calls (gratuit)
        v
   GROQ CLOUD --- Whisper STT + Llama 4 Scout Vision
   gTTS --------- Google Text-to-Speech
   YOLOv8-nano -- Détection d'objets locale (CPU)
```

### Flux de traitement

1. Double-tap → bip aigu → enregistrement démarre
2. Utilisateur parle : "Décris ce qui est devant moi"
3. Silence 2.5s détecté → bip grave → enregistrement s'arrête
4. Frontend envoie audio + frame caméra → POST /process
5. Backend : audio → Whisper STT → transcription
6. Backend : classify_command() → action = "describe"
7. Backend : frame → Llama 4 Scout Vision → description
8. Backend : description → gTTS → MP3 sauvegardé dans cache
9. Backend retourne : { text, action, audio_id }
10. Frontend : affiche le texte + joue l'audio via GET /audio/{id}

---

## 🛠 Stack technologique

| Composant | Technologie | Coût | Détails |
|-----------|-------------|------|---------|
| **STT** | Whisper large-v3 via Groq | Gratuit | 14 400 req/jour, ~0.3s latence |
| **Vision / OCR / VQA** | Llama 4 Scout 17B via Groq | Gratuit | Multimodal, 12 langues, 128K contexte |
| **TTS** | gTTS (Google Text-to-Speech) | Gratuit | Voix française, aucune clé API requise |
| **Détection obstacles** | YOLOv8-nano (6 MB) | Gratuit | Temps réel sur CPU, 35+ classes |
| **Backend** | FastAPI + Python 3.12 | — | Async, auto-documentation Swagger |
| **Frontend** | HTML/CSS/JS vanilla (PWA) | — | Zéro dépendance, installable |
| **HTTPS** | mkcert (certificats locaux) | — | Requis pour caméra/micro sur mobile |

**Coût total de fonctionnement : 0 DH**

---

## 📦 Installation

### Prérequis

- Python 3.10+
- Chrome (desktop ou mobile)
- Compte Groq gratuit → [console.groq.com](https://console.groq.com)

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/sanogomamadou/BasiRA.git
cd BasiRA

# 2. Installer les dépendances
cd backend
pip install -r requirements.txt

# 3. Configurer la clé API Groq
# Créer backend/config_local.py (ignoré par git) :
echo 'GROQ_API_KEY = "gsk_votre_cle_ici"' > config_local.py

# 4. Lancer le serveur
python main.py

# 5. Ouvrir http://localhost:8000 dans Chrome
```

---

## ⚙️ Configuration

### config.py

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| GROQ_API_KEY | via config_local.py ou env | Clé API Groq |
| STT_MODEL | whisper-large-v3 | Modèle de transcription |
| VISION_MODEL | meta-llama/llama-4-scout-17b-16e-instruct | Modèle de vision |
| HOST | 0.0.0.0 | Adresse du serveur |
| PORT | 8000 | Port du serveur |

### Numéro d'urgence

Dans `frontend/index.html`, modifier la constante :

```javascript
const EMERGENCY_NUMBER = 'tel:+212XXXXXXXXX';
```

---

## 📱 Accès mobile HTTPS

Les navigateurs mobiles exigent HTTPS pour accéder à la caméra et au micro.

```bash
# 1. Télécharger mkcert depuis github.com/FiloSottile/mkcert/releases
# 2. Installer l'autorité de certification
mkcert -install

# 3. Trouver votre IP locale
ipconfig  # Windows - chercher IPv4 Address

# 4. Générer les certificats (remplacer par votre IP)
cd backend
mkcert localhost 127.0.0.1 192.168.x.x

# 5. Relancer le serveur
python main.py
# --> Affiche : HTTPS activé
```

Sur le téléphone (même WiFi) : ouvrir `https://192.168.x.x:8000` dans Chrome, accepter l'avertissement, autoriser caméra + micro.

---

## 🚀 Utilisation

### Premier lancement

Un écran d'onboarding présente les gestes clés. Le bouton "Commencer" initialise la caméra, le micro, et la détection de mouvement (shake).

### Mode vocal (principal)

1. **Double-tap** n'importe où sur l'écran
2. Un **bip aigu** confirme le début d'enregistrement
3. Parler sa commande
4. Le silence (2,5s) arrête automatiquement l'enregistrement
5. Un **bip grave** confirme l'envoi
6. La réponse s'affiche en texte ET se lit en audio

### Scan d'obstacles continu

1. **Triple-tap** n'importe où → double bip montant → scan activé
2. L'app envoie une frame toutes les 3,5 secondes à YOLOv8
3. Annonce vocale uniquement quand la scène change
4. Indique position (gauche/droite/devant) et proximité
5. Recommande la direction de passage libre
6. **Triple-tap** à nouveau → double bip descendant → scan désactivé

### Boutons rapides (fallback visuel)

Décrire, Lire, Monnaie, Scan continu, Couleurs, Personnes

### Usage recommandé

- Smartphone en tour de cou (pochette ou clip)
- Un seul écouteur (garder une oreille pour l'environnement)
- Caméra arrière orientée vers l'avant
- Secouer pour basculer en caméra avant si besoin

---

## 🗂 Structure du projet

```
BasiRA/
├── backend/
│   ├── config.py                # Configuration (modèles, ports)
│   ├── config_local.py          # Clé API Groq (ignoré par git)
│   ├── main.py                  # FastAPI + orchestrateur + routes
│   ├── requirements.txt         # Dépendances Python
│   ├── audio_cache/             # Cache audio TTS (auto-généré)
│   └── services/
│       ├── __init__.py
│       ├── stt.py               # Speech-to-Text (Groq Whisper)
│       ├── tts.py               # Text-to-Speech (gTTS)
│       ├── vision.py            # Vision IA (Groq Llama 4 Scout)
│       └── detection.py         # Détection d'obstacles (YOLOv8-nano)
├── frontend/
│   ├── index.html               # PWA complète (HTML/CSS/JS)
│   └── manifest.json            # Manifeste PWA
├── .gitignore
└── README.md
```

---

## 🔌 Endpoints API

Documentation Swagger interactive : `http://localhost:8000/docs`

| Méthode | Endpoint | Description | Entrée | Sortie |
|---------|----------|-------------|--------|--------|
| GET | /health | Status du serveur | — | {status, message} |
| POST | /process | Orchestrateur principal | audio + image | {transcription, action, text, audio_id} |
| POST | /describe | Description de scène | image | {description} |
| POST | /read | Lecture de document | image | {text} |
| POST | /ask?question= | Question visuelle | image + query | {answer} |
| POST | /money | Identification monnaie | image | {result} |
| POST | /detect | Obstacles (Vision IA) | image | {text} |
| POST | /detect-fast | Obstacles (YOLOv8) | image | {obstacles, text} |
| POST | /stt | Speech-to-Text | audio | {text} |
| POST | /tts | Text-to-Speech | {text} | audio/mpeg |
| POST | /tts-url | TTS vers URL | {text} | {audio_id} |
| GET | /audio/{id} | Servir fichier audio | id | audio/mpeg |

### Commandes vocales reconnues

| Action | Mots-clés déclencheurs |
|--------|----------------------|
| describe | décris, décrit, devant moi, autour de moi, où suis-je, que vois |
| read | lis, lire, lecture, document, texte, panneau, affiche, ordonnance |
| money | billet, monnaie, argent, dirham, combien, pièce, sous |
| detect | obstacle, danger, attention, chemin, passage, route, trottoir, marche |
| ask | *(tout le reste — question libre par défaut)* |

---

## ♿ Accessibilité

BasiRA est conçu dès le départ pour être utilisable **sans aucune capacité visuelle** :

| Principe | Implémentation |
|----------|---------------|
| Zéro interaction visuelle | Double-tap, triple-tap, shake, appui long |
| Retours audio systématiques | Bips, annonces vocales, réponses TTS |
| Détection de silence auto | Fin d'enregistrement sans cliquer |
| Urgence sans ciblage | Appui 5s n'importe où, bips progressifs |
| Pas de popups parasites | Sélection texte et menu contextuel désactivés |
| Onboarding intégré | Permissions demandées en un seul geste |
| PWA installable | Ajout à l'écran d'accueil comme app native |
| Scan continu | Triple-tap active la surveillance en arrière-plan |

---

## 🏛 Contexte du projet

Projet réalisé dans le cadre du **17e Forum National du Handicap**, organisé par le **Centre National Mohammed VI des Handicapés**, sous le thème :

> *« Accessibilité numérique et intelligence artificielle : un levier pour la promotion des droits des personnes en situation de handicap »*

**Date** : 31 mars — 3 avril 2026
**Lieu** : Centre National Mohammed VI des Handicapés, Salé Al Jadida

### Alignement avec les axes du forum

| Axe du forum | Application dans BasiRA |
|-------------|------------------------|
| IA et accès aux services de santé, éducation, réhabilitation | Lecture d'ordonnances, documents administratifs, panneaux |
| Technologies d'assistance pour l'autonomie | Coeur du projet — perception augmentée par IA |
| Éthique de l'IA et protection des données | Aucune image stockée, open source, traitement éphémère |
| Bonnes pratiques internationales | Inspiré de Seeing AI / Be My Eyes, adapté au Maroc |

---

<div align="center">

**Université Internationale de Rabat (UIR)** — École d'Ingénierie Informatique — Big Data & Intelligence Artificielle

**BasiRA — بصيرة**

*Parce que l'intelligence artificielle doit servir ceux qui en ont le plus besoin.*

</div>