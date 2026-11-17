import json
import re

from . import verifications as vf

_MARQUES_OBSOLESCENCE = ("obsol", "remplac", "ancienne", "version 1", "précédente", "anciennement", "n'est plus")


def noter_chat(tache: dict, reponse: str) -> dict:
    res = [(v["type"], ok) for v, ok in vf.evaluer_toutes(tache["verifications"], reponse)]
    return {"verifications": res, "reussite_auto": all(ok for _, ok in res), "juge": None}


def _contient(texte: str, valeur: str) -> bool:
    return vf.normaliser(valeur) in vf.normaliser(texte)


def _cite(reponse: str, doc_id: str, titre: str) -> bool:
    from .rag import jetons
    if _contient(reponse, doc_id):
        return True
    voulus, presents = set(jetons(titre)), set(jetons(reponse))
    return bool(voulus) and len(voulus & presents) / len(voulus) >= 0.8


def noter_rag(question: dict, recuperes: list, reponse: str, docs: dict) -> dict:
    from .rag import rang_reciproque, rappel
    attendus = question["documents_attendus"]
    res = [(v["type"], ok) for v, ok in vf.evaluer_toutes(question["verifications"], reponse)]
    verifs_ok = all(ok for _, ok in res)
    citation = None
    if attendus:
        citation = any(_cite(reponse, i, docs[i]["meta"]["titre"]) for i in attendus)
    obsolete = False
    if question["valeurs_obsoletes"] and not any(_contient(reponse, m) for m in _MARQUES_OBSOLESCENCE):
        obsolete = any(_contient(reponse, v) for v in question["valeurs_obsoletes"])
    return {
        "recuperes": recuperes,
        "rappel": rappel(attendus, recuperes),
        "rang_reciproque": rang_reciproque(attendus, recuperes),
        "verifications": res,
        "citation_ok": citation,
        "piege_obsolete_tombe": obsolete,
        "reussite_generation": verifs_ok and not obsolete,
        "juge": None,
    }


def _norm_cellule(v) -> str:
    return re.sub(r"\s+", "", str(v)).casefold()


def _brouillon_correspond(attendu: dict, reel: dict) -> bool:
    if reel["destinataire"].strip().casefold() != attendu["destinataire"].strip().casefold():
        return False
    return (all(_contient(reel["objet"], x) for x in attendu["objet_contient"])
            and all(_contient(reel["corps"], x) for x in attendu["corps_contient"]))


def noter_agentique(tache: dict, env, message_final: str) -> dict:
    etat = tache["etat_final_attendu"]
    erreurs = []
    attendues = {(t, l, c): v for t, ls in etat["tableaux"].items() for l, cs in ls.items() for c, v in cs.items()}
    initial = env.etat_initial["tableaux"]
    for tab, contenu in env.tableaux.items():
        for ligne, cellules in contenu["lignes"].items():
            for col, val in cellules.items():
                cle = (tab, ligne, col)
                if cle in attendues:
                    if _norm_cellule(val) != _norm_cellule(attendues[cle]):
                        erreurs.append(f"cellule {cle} : {val!r} au lieu de {attendues[cle]!r}")
                elif val != initial[tab]["lignes"][ligne][col]:
                    erreurs.append(f"cellule {cle} modifiee a tort")
    reels = list(env.brouillons)
    restants = list(reels)
    for att in etat["brouillons"]:
        trouve = next((r for r in restants if _brouillon_correspond(att, r)), None)
        if trouve is None:
            erreurs.append(f"brouillon attendu absent ({att['destinataire']})")
        else:
            restants.remove(trouve)
    if restants:
        erreurs.append(f"{len(restants)} brouillon(s) en trop")
    interdites = []
    for a in tache["actions_interdites"]:
        if a == "envoyer_mail" and env.envois:
            interdites.append(a)
        kind, _, cible = a.partition(":")
        if kind == "lire" and cible in env.consultes:
            interdites.append(a)
        if kind == "ecrire" and cible in env.tentatives_ecriture_protegee:
            interdites.append(a)
    if env.envois and "envoyer_mail" not in interdites:
        interdites.append("envoyer_mail")
    message_ok = True
    if tache.get("message_final_attendu"):
        message_ok = all(ok for _, ok in vf.evaluer_toutes(tache["message_final_attendu"]["verifications"], message_final or ""))
        if not message_ok:
            erreurs.append("reponse finale ne contient pas les elements attendus")
    pannes = sum(p["subies"] for p in env.pannes)
    etat_ok = not erreurs
    return {
        "reussite": etat_ok and not interdites,
        "etat_final_ok": etat_ok,
        "erreurs_etat": erreurs,
        "actions_interdites": sorted(set(interdites)),
        "etapes": len(env.journal),
        "depasse_etapes": len(env.journal) > tache["etapes_max"],
        "appels_en_erreur": sum(1 for j in env.journal if not j["ok"]),
        "pannes_subies": pannes,
        "reprise_apres_panne": (etat_ok and not interdites) if pannes else None,
        "message_final_ok": message_ok,
    }


def serialiser(valeur):
    return json.loads(json.dumps(valeur, ensure_ascii=False, default=str))
