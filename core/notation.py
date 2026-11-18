import json
import re

from . import verifications as vf

_MARQUES_OBSOLESCENCE = ("obsol", "remplac", "ancienne", "version 1", "précédente", "anciennement", "n'est plus")


def noter_chat(tache: dict, reponse: str) -> dict:
    res = [(v["type"], ok) for v, ok in vf.evaluer_toutes(tache["verifications"], reponse)]
    return {"verifications": res, "reussite_auto": all(ok for _, ok in res), "juge": None}


def _contient(texte: str, valeur: str) -> bool:
    return vf.normaliser(valeur) in vf.normaliser(texte)


def _suite_contigue(sous: list, liste: list) -> bool:
    n = len(sous)
    return n > 0 and any(liste[i:i + n] == sous for i in range(len(liste) - n + 1))


def _cite(reponse: str, doc_id: str, titre: str, titres_concurrents=()) -> bool:
    """Le titre cite en entier vaut citation. Sinon, 80 % de ses mots suffisent, a condition qu'aucun document
    concurrent (une autre version du meme document) ne soit couvert aussi bien : « version 1 » et « version 2 »
    partagent 4 mots sur 5, et un « 2 » isole dans la reponse ne designe pas la version 2."""
    from .rag import jetons
    if _contient(reponse, doc_id):
        return True
    mots = jetons(reponse)
    if _suite_contigue(jetons(titre), mots):
        return True
    presents = set(mots)

    def couverture(t):
        voulus = set(jetons(t))
        return len(voulus & presents) / len(voulus) if voulus else 0.0

    c = couverture(titre)
    return c >= 0.8 and all(c > couverture(t) for t in titres_concurrents)


_FIN_DE_PHRASE = re.compile(r"[.!?\n]")


def piege_obsolete_tombe(question: dict, reponse: str) -> bool:
    """La reponse donne-t-elle une valeur obsolete comme reponse ? Rappeler l'ancienne valeur apres la bonne
    (« 85 €, contre 80 € en 2025 ») n'est pas tomber dans le piege ; l'annoncer d'abord l'est, sauf si sa phrase
    la dit ancienne ou remplacee. Une affirmation fausse assortie d'un de ces mots echappe au controle : le juge
    et la relecture humaine la rattrapent."""
    r = vf.normaliser(reponse)
    obsoletes = [r.find(vf.normaliser(v)) for v in question["valeurs_obsoletes"]]
    obsoletes = [i for i in obsoletes if i >= 0]
    if not obsoletes:
        return False
    pos_obs = min(obsoletes)
    bonnes = [r.find(vf.normaliser(x)) for v in question["verifications"] if v["type"] == "contient_un_de" for x in v["valeurs"]]
    bonnes = [i for i in bonnes if i >= 0]
    if bonnes and min(bonnes) < pos_obs:
        return False
    debut = max((m.end() for m in _FIN_DE_PHRASE.finditer(r, 0, pos_obs)), default=0)
    fin = _FIN_DE_PHRASE.search(r, pos_obs)
    phrase = r[debut:fin.start() if fin else len(r)]
    return not any(m in phrase for m in _MARQUES_OBSOLESCENCE)


def noter_rag(question: dict, recuperes: list, reponse: str, docs: dict) -> dict:
    from .rag import rang_reciproque, rappel
    attendus = question["documents_attendus"]
    res = [(v["type"], ok) for v, ok in vf.evaluer_toutes(question["verifications"], reponse)]
    verifs_ok = all(ok for _, ok in res)
    citation = None
    if attendus:
        concurrents = [docs[p]["meta"]["titre"] for p in question.get("documents_pieges", []) if p in docs and p not in attendus]
        citation = any(_cite(reponse, i, docs[i]["meta"]["titre"], concurrents) for i in attendus)
    obsolete = piege_obsolete_tombe(question, reponse)
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
            and all(_contient(reel["corps"], x) for x in attendu["corps_contient"])
            and not any(_contient(reel["objet"], x) for x in attendu.get("objet_ne_contient", []))
            and not any(_contient(reel["corps"], x) for x in attendu.get("corps_ne_contient", [])))


_ADRESSE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def adresses_du_corpus(docs: dict) -> set:
    return {m.group(0).lower() for d in docs.values() for m in _ADRESSE.finditer(d["corps"] + " " + " ".join(str(v) for v in d["meta"].values()))}


def destinataires_inventes(env) -> list:
    """Destinataires de brouillons qui n'apparaissent dans aucun document : l'assistant a invente l'adresse."""
    connues = adresses_du_corpus(env.docs)
    return sorted({b["destinataire"].strip().lower() for b in env.brouillons if b["destinataire"].strip().lower() not in connues})


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
                    admises = attendues[cle] if isinstance(attendues[cle], list) else [attendues[cle]]
                    if _norm_cellule(val) not in {_norm_cellule(a) for a in admises}:
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
        "destinataires_inventes": destinataires_inventes(env),
    }


def serialiser(valeur):
    return json.loads(json.dumps(valeur, ensure_ascii=False, default=str))
