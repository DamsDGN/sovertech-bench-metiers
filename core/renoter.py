"""Recalcule les notes d'une mesure deja faite avec le code de notation et les grilles actuels, sans rappeler le modele.

Les reponses, les documents recuperes (RAG) et le journal des appels d'outils (agentique) sont conserves dans
resultats.jsonl : on renote a partir d'eux. L'agentique est rejoue dans un environnement neuf ; si le rejeu ne
redonne pas les tableaux et les brouillons enregistres, l'ancienne note est gardee et le cas est signale.
Une tache dont la consigne vue par le modele a change depuis la mesure n'est pas renotee : sa reponse ne
repond plus a la meme question.
Usage : python3 -m core.renoter DOSSIER [DOSSIER ...]
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from . import agentique as ag
from . import donnees as d
from . import lancer
from . import notation as n
from . import rapport
from .client import Reponse

VUS_PAR_LE_MODELE = {"chat": ("consigne", "contexte", "suite"), "rag": ("question",),
                     "agentique": ("consigne", "pannes", "etapes_max")}
# Une mesure en cours ajoute des lignes a resultats.jsonl : le reecrire en meme temps risque d'en perdre.
# Constate le 18/11/2026 sur une mesure Runpod lancee par une autre session.
DELAI_INACTIVITE = 600


class MesureEnCours(Exception):
    pass


FICHIERS = {"chat": "chat/taches.jsonl", "rag": "rag/questions.jsonl", "agentique": "agentique/taches.jsonl"}


def taches_au_commit(metier: str, commit: str, racine: Path = d.RACINE):
    """Taches telles qu'elles etaient au commit de la mesure, ou None si Git ne peut pas les donner."""
    anciennes = {}
    for bloc, chemin in FICHIERS.items():
        try:
            r = subprocess.run(["git", "show", f"{commit}:{metier}/{chemin}"], cwd=racine, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode != 0:
            return None
        for l in r.stdout.splitlines():
            if l.strip():
                t = json.loads(l)
                anciennes[(bloc, t["id"])] = t
    return anciennes


def consigne_modifiee(bloc: str, avant: dict, maintenant: dict) -> bool:
    return any(avant.get(c) != maintenant.get(c) for c in VUS_PAR_LE_MODELE[bloc])


def rejouer(enr: dict, tache: dict, jeux: dict):
    env = ag.Environnement(jeux["documents"], jeux["environnement"], tache["pannes"])
    for appel in enr.get("journal", []):
        env.appeler(appel["outil"], appel["arguments"])
    return env, _etat_conforme(env, enr.get("tableaux_finaux") or {}) and env.brouillons == enr.get("brouillons", [])


def _etat_conforme(env, enregistres: dict) -> bool:
    """Le rejeu redonne les tableaux enregistres. Un tableau ou une ligne ajoutes a l'environnement apres la mesure
    sont admis s'ils sont restes dans leur etat initial : le modele ne les a pas vus et n'y a rien ecrit."""
    initial = env.etat_initial["tableaux"]
    for nom, tab in env.tableaux.items():
        for ligne, cellules in tab["lignes"].items():
            attendu = enregistres.get(nom, {}).get(ligne)
            if attendu is None:
                attendu = initial[nom]["lignes"][ligne]
            if cellules != attendu:
                return False
    return all(nom in env.tableaux and set(lignes) <= set(env.tableaux[nom]["lignes"]) for nom, lignes in enregistres.items())


_BLOC_APPEL = re.compile(r"<appel>\s*\{")


def est_voie_cli(releve: dict) -> bool:
    return (releve.get("modele_catalogue", {}).get("fournisseur") == "claude_cli"
            or str(releve.get("serveur", {}).get("voie") or "").startswith("claude -p"))


def anomalies_des_tours(enr: dict) -> list:
    """Anomalies recalculees sur le texte conserve de chaque tour, avec la detection actuelle."""
    sorties = []
    for t in enr.get("tours") or []:
        texte = t.get("texte") or ""
        if t.get("fin") == "tool_calls":
            # Des appels ont ete executes a ce tour : un <invoke> a cote d'un <appel> valide double le meme appel,
            # seul un bloc <appel> reste illisible (le client retire ceux qu'il a lus) signale une perte.
            a = t.get("anomalie") or ("appel_outil_non_analyse" if _BLOC_APPEL.search(texte) else None)
        else:
            a = t.get("anomalie") or ag.anomalie(Reponse(texte=texte, fin=t.get("fin")))
        if a:
            sorties.append(a)
    return sorties


def renoter_enregistrement(enr: dict, tache: dict, jeux: dict):
    """Renvoie (nouvelle note ou None si elle ne peut pas etre recalculee, statut)."""
    reponse = enr.get("reponse") or ""
    if enr["bloc"] == "chat":
        note = n.noter_chat(tache, reponse)
    elif enr["bloc"] == "rag":
        note = n.noter_rag(tache, enr["note"]["recuperes"], reponse, jeux["documents"])
    else:
        env, conforme = rejouer(enr, tache, jeux)
        if not conforme:
            return None, "rejeu_divergent"
        note = n.noter_agentique(tache, env, reponse)
    if enr["note"].get("juge") is not None:
        note["juge"] = enr["note"]["juge"]
    return n.serialiser(note), "renote"


def renoter(dossier: Path, jeux=None, anciennes="git", recent_ok=False) -> dict:
    dossier = Path(dossier)
    age = time.time() - (dossier / "resultats.jsonl").stat().st_mtime
    if age < DELAI_INACTIVITE and not recent_ok:
        raise MesureEnCours(f"{dossier} : resultats modifies il y a {age:.0f} s, une mesure est peut-etre en cours (--force pour passer outre)")
    releve = json.loads((dossier / "releve.json").read_text(encoding="utf-8"))
    metier = releve["metier"]
    if jeux is None:
        jeux = lancer.charger_jeux(metier, releve.get("extraction", {}).get("moteur", "tika"))
    taches = {(b, t["id"]): t for b in FICHIERS for t in jeux[b]}
    commit = releve.get("moteur", {}).get("commit")
    if anciennes == "git":
        anciennes = taches_au_commit(metier, commit) if commit else None
    chemin = dossier / "resultats.jsonl"
    lignes = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
    bilan = {"date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "commit": lancer._commit(),
             "consignes_verifiees": anciennes is not None, "renotees": 0, "reussite_changee": [],
             "tache_absente": [], "consigne_modifiee": [], "rejeu_divergent": [], "erreur_voie_cli": []}
    voie_cli = est_voie_cli(releve)
    for enr in lignes:
        if enr.get("erreur"):
            continue
        cle = (enr["bloc"], enr["tache"])
        etiquette = f"{enr['tache']} passe {enr['passe']}"
        tache = taches.get(cle)
        if tache is None:
            bilan["tache_absente"].append(etiquette)
            continue
        if anciennes is not None and (cle not in anciennes or consigne_modifiee(enr["bloc"], anciennes[cle], tache)):
            bilan["consigne_modifiee"].append(etiquette)
            continue
        if enr["bloc"] == "agentique" and enr.get("tours"):
            enr["anomalies_serveur"] = anomalies_des_tours(enr)
        note, statut = renoter_enregistrement(enr, tache, jeux)
        if (note is not None and voie_cli and not note.get("reussite")
                and "appel_outil_non_analyse" in enr.get("anomalies_serveur", [])):
            # Le protocole d'outils de la voie CLI est notre emulation, pas ce que le modele aurait via l'API :
            # un echec qu'il a cause est une erreur d'infrastructure, retiree du calcul et rejouable.
            enr["erreur"] = ("voie CLI : appel d'outil illisible dans le protocole emule, non execute "
                             "(erreur d'infrastructure, rejouable avec --reprise)")
            enr["note"] = note
            bilan["erreur_voie_cli"].append(etiquette)
            continue
        if note is None:
            bilan[statut].append(etiquette)
            continue
        avant = rapport.reussite(enr)
        enr["note"] = note
        bilan["renotees"] += 1
        if rapport.reussite(enr) != avant:
            bilan["reussite_changee"].append(f"{etiquette} : {'réussite' if avant else 'échec'} -> {'réussite' if not avant else 'échec'}")
    sauvegarde = dossier / "resultats.avant-renotage.jsonl"
    if not sauvegarde.exists():
        sauvegarde.write_text(chemin.read_text(encoding="utf-8"), encoding="utf-8")
    chemin.write_text("".join(json.dumps(e, ensure_ascii=False, default=str) + "\n" for e in lignes), encoding="utf-8")
    releve.setdefault("renotations", []).append(bilan)
    (dossier / "releve.json").write_text(json.dumps(releve, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rapport.generer(dossier)
    return bilan


def main(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m core.renoter", description=__doc__.splitlines()[0])
    p.add_argument("dossiers", nargs="+")
    p.add_argument("--force", action="store_true", help="renoter meme un dossier modifie dans les dix dernieres minutes")
    a = p.parse_args(argv)
    for dossier in a.dossiers:
        try:
            b = renoter(Path(dossier), recent_ok=a.force)
        except MesureEnCours as e:
            print(f"IGNORE {e}", file=sys.stderr)
            continue
        print(f"{dossier} : {b['renotees']} renotees, {len(b['reussite_changee'])} verdicts changes")
        for ligne in b["reussite_changee"]:
            print(f"  {ligne}")
        for cle in ("tache_absente", "consigne_modifiee", "rejeu_divergent", "erreur_voie_cli"):
            if b[cle]:
                print(f"  {cle} : {', '.join(b[cle])}")
        if not b["consignes_verifiees"]:
            print("  attention : commit de la mesure inconnu, les consignes n'ont pas pu etre comparees")


if __name__ == "__main__":
    main()
