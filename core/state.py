"""
Gestion de l'état de session et persistance des territoires
"""

import streamlit as st
import json
from pathlib import Path

# Fichier de persistance des territoires (dans le dossier de l'app)
TERRITOIRES_FILE = Path(__file__).parent.parent / "data" / "territoires.json"


def init_state():
    """Initialise les variables de session si absentes."""
    defaults = {
        "page": "accueil",
        "territoire_actif": None,
        "generation_log": [],
        "generation_en_cours": False,
        "couches_disponibles": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def charger_territoires() -> list:
    """Charge la liste des territoires depuis le fichier JSON."""
    if not TERRITOIRES_FILE.exists():
        return []
    try:
        with open(TERRITOIRES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def sauvegarder_territoire(territoire: dict):
    """Ajoute ou met à jour un territoire dans le fichier JSON."""
    TERRITOIRES_FILE.parent.mkdir(parents=True, exist_ok=True)
    territoires = charger_territoires()

    # Mise à jour si existe déjà, sinon ajout
    existant = next((i for i, t in enumerate(territoires) if t["id"] == territoire["id"]), None)
    if existant is not None:
        territoires[existant] = territoire
    else:
        territoires.append(territoire)

    with open(TERRITOIRES_FILE, "w", encoding="utf-8") as f:
        json.dump(territoires, f, ensure_ascii=False, indent=2)


def supprimer_territoire(territoire_id: str):
    """Supprime un territoire par son ID."""
    territoires = charger_territoires()
    territoires = [t for t in territoires if t["id"] != territoire_id]
    with open(TERRITOIRES_FILE, "w", encoding="utf-8") as f:
        json.dump(territoires, f, ensure_ascii=False, indent=2)


def get_territoire_actif() -> dict | None:
    """Retourne le territoire actuellement sélectionné."""
    tid = st.session_state.get("territoire_actif")
    if not tid:
        return None
    territoires = charger_territoires()
    return next((t for t in territoires if t["id"] == tid), None)
