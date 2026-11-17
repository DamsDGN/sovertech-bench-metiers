import hashlib
import json
from pathlib import Path

VERSION = "v0"
RACINE = Path(__file__).resolve().parent.parent


def charger(metier: str, racine: Path = RACINE) -> dict:
    """Consignes systeme d'un metier (<metier>/prompts.json) : chat_systeme et rag_systeme."""
    donnees = json.loads((racine / metier / "prompts.json").read_text(encoding="utf-8"))
    manquants = {"chat_systeme", "rag_systeme"} - set(donnees)
    if manquants:
        raise ValueError(f"{metier}/prompts.json : cles manquantes {sorted(manquants)}")
    return donnees


def chat_utilisateur(consigne: str, passages: list) -> str:
    if not passages:
        return consigne
    return "Documents fournis :\n\n" + "\n\n".join(passages) + "\n\n---\n\n" + consigne


def rag_utilisateur(question: str, passages: list) -> str:
    return "Extraits :\n\n" + "\n\n".join(passages) + "\n\n---\n\nQuestion : " + question


def empreinte(consignes: dict, systeme_agent: str) -> str:
    texte = "\n".join([VERSION, consignes["chat_systeme"], consignes["rag_systeme"], systeme_agent])
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]
