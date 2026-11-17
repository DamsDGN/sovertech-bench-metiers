import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent / "catalogue"
CHAMPS = {"id", "nom", "depot_hf", "quantification", "echantillonnage", "source_echantillonnage"}
CLES_ECHANTILLONNAGE = {"temperature", "top_p", "top_k", "min_p", "presence_penalty", "repetition_penalty"}


def lister(dossier: Path = DOSSIER) -> list:
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(dossier.glob("*.json"))]


def charger(id_: str, dossier: Path = DOSSIER) -> dict:
    for entree in lister(dossier):
        if entree["id"] == id_:
            return entree
    raise KeyError(f"modele {id_!r} absent du catalogue")


def verifier(dossier: Path = DOSSIER) -> list:
    erreurs, vus = [], set()
    for f in sorted(dossier.glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        manquants = CHAMPS - set(e)
        if manquants:
            erreurs.append(f"{f.name} : champs manquants {sorted(manquants)}")
            continue
        if e["id"] != f.stem:
            erreurs.append(f"{f.name} : id different du nom de fichier")
        if e["id"] in vus:
            erreurs.append(f"{f.name} : id en double")
        vus.add(e["id"])
        inconnues = set(e["echantillonnage"]) - CLES_ECHANTILLONNAGE
        if inconnues:
            erreurs.append(f"{f.name} : reglages inconnus {sorted(inconnues)}")
        if e["quantification"] != "NVFP4":
            erreurs.append(f"{f.name} : le catalogue publie est en NVFP4 uniquement")
    return erreurs
