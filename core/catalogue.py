import json
import re
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent / "catalogue"
CLES_ECHANTILLONNAGE = {"temperature", "top_p", "top_k", "min_p", "presence_penalty", "repetition_penalty"}
FOURNISSEURS_CLOUD = {"anthropic", "openai", "claude_cli"}
CHAMPS_LOCAL = {"id", "nom", "depot_hf", "quantification", "echantillonnage", "source_echantillonnage"}
CHAMPS_ETALON = {"id", "nom", "fournisseur", "modele_api", "echantillonnage", "reglages_api",
                 "source_echantillonnage", "prix_mtok"}


def categorie(entree: dict) -> str:
    return entree.get("categorie", "local")


def est_etalon(entree: dict) -> bool:
    return categorie(entree) == "etalon_cloud"


def lister(dossier: Path = DOSSIER) -> list:
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(dossier.glob("*.json"))]


def charger(id_: str, dossier: Path = DOSSIER) -> dict:
    for entree in lister(dossier):
        if entree["id"] == id_:
            return entree
    raise KeyError(f"modele {id_!r} absent du catalogue")


def cout_usd(entree: dict, tokens_entree, tokens_sortie):
    prix = entree.get("prix_mtok")
    if not prix or tokens_entree is None or tokens_sortie is None:
        return None
    return (tokens_entree * prix["entree"] + tokens_sortie * prix["sortie"]) / 1e6


def verifier(dossier: Path = DOSSIER) -> list:
    erreurs, vus = [], set()
    for f in sorted(dossier.glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        etalon = est_etalon(e)
        manquants = (CHAMPS_ETALON if etalon else CHAMPS_LOCAL) - set(e)
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
        if etalon:
            if e["fournisseur"] not in FOURNISSEURS_CLOUD:
                erreurs.append(f"{f.name} : fournisseur {e['fournisseur']!r} inconnu")
            p = e["prix_mtok"]
            if not {"entree", "sortie", "source", "releve"} <= set(p) or p["entree"] <= 0 or p["sortie"] <= 0:
                erreurs.append(f"{f.name} : prix_mtok doit donner entree, sortie, source et date de releve")
        else:
            if e["quantification"] != "NVFP4" and not e.get("exception_format"):
                erreurs.append(f"{f.name} : un modele local du catalogue publie est en NVFP4 uniquement, sauf exception_format motivee")
            if "max_tokens" in e and not (isinstance(e["max_tokens"], int) and e["max_tokens"] >= 1024):
                erreurs.append(f"{f.name} : max_tokens doit etre un entier d'au moins 1024")
            if not re.fullmatch(r"[0-9a-f]{40}", str(e.get("revision_hf", ""))):
                erreurs.append(f"{f.name} : revision_hf doit etre le SHA complet (40 caracteres) du depot servi")
            if not e.get("licence"):
                erreurs.append(f"{f.name} : licence manquante")
            if not 12 <= e.get("parametres_milliards", 0) <= 35:
                erreurs.append(f"{f.name} : le perimetre du projet est de 12 a 35 milliards de parametres")
            if e.get("parseur_outils_vllm") is None and "a_determiner_au_premier_chargement" not in e:
                erreurs.append(f"{f.name} : un parseur d'outils inconnu doit etre declare dans a_determiner_au_premier_chargement")
    return erreurs
