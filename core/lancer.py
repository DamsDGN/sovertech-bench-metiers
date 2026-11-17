import argparse
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import agentique as ag
from . import catalogue, prompts, rag
from . import donnees as d
from . import notation as n
from .client import ErreurClient
from .fournisseurs import creer_client

MAX_TOKENS_DEFAUT = 32768


def _commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d.RACINE, capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def memoire_gpu_locale():
    if not shutil.which("nvidia-smi"):
        return {"valeur_mib": None, "raison": "nvidia-smi absent de la machine qui lance le benchmark (serveur distant ou carte non NVIDIA)"}
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        return {"valeur_mib": max(int(x) for x in r.stdout.split()), "raison": None}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"valeur_mib": None, "raison": "nvidia-smi present mais illisible"}


def construire_releve(config, entree, infos_serveur, jeux) -> dict:
    servi = infos_serveur.get("modele_servi")
    raisons = []
    etalon = catalogue.est_etalon(entree)
    if entree.get("fournisseur") == "claude_cli":
        raisons.append("obtenu via le CLI claude -p (abonnement) : prompt systeme du CLI en plus, appels d'outils emules en texte, "
                       "conversations rejouees en transcription ; pas un appel d'API direct")
    if not etalon:
        if not config.get("materiel"):
            raisons.append("materiel non declare (--materiel)")
        if servi != entree["depot_hf"]:
            raisons.append(f"modele servi ({servi}) different du catalogue ({entree['depot_hf']})")
    return {
        "etalon_cloud": etalon, "budget_usd": config.get("budget_usd"),
        "extraction": informations_extraction(jeux.get("extraction", "tika"), config["metier"]),
        "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "metier": config["metier"], "modele_catalogue": entree, "serveur": infos_serveur,
        "materiel_declare": config.get("materiel"), "memoire_gpu": memoire_gpu_locale(),
        "etiquette": config.get("etiquette"),
        "moteur": {"commit": _commit(), "python": platform.python_version(), "prompts": prompts.VERSION,
                   "empreinte_prompts": prompts.empreinte(jeux["prompts"], jeux["systeme_agent"])},
        "recuperateur": rag.PARAMETRES, "echantillonnage": entree["echantillonnage"],
        "max_tokens": config["max_tokens"], "passes": config["passes"], "blocs": config["blocs"],
        "prix_horaire": config.get("prix_horaire"),
        "comparable_aux_resultats_publies": not raisons, "raisons_non_comparable": raisons,
    }


def informations_extraction(moteur: str, metier: str = "expert-comptable") -> dict:
    fichier = d.RACINE / metier / "corpus" / ("MANIFESTE.json" if moteur == "tika" else f"MANIFESTE-{moteur}.json")
    if not fichier.exists():
        return {"moteur": moteur}
    e = json.loads(fichier.read_text(encoding="utf-8"))["extraction"]
    return {"moteur": moteur, "outil": e.get("outil"), "date": e.get("date"), "note": e.get("note")}


def charger_jeux(metier: str, extraction: str = "tika") -> dict:
    jeux = d.charger_metier(metier, extraction=extraction)
    jeux["extraction"] = extraction
    jeux["metier"] = metier
    jeux["prompts"] = prompts.charger(metier)
    base = d.RACINE / metier / "agentique" / "environnement"
    jeux["outils"] = json.loads((base / "outils.json").read_text(encoding="utf-8"))
    jeux["systeme_agent"] = (base / "consigne_systeme.md").read_text(encoding="utf-8").strip()
    return jeux


def _mesures(reponses):
    ttfts = [r["ttft"] for r in reponses if r["ttft"] is not None]
    tp = [r["tokens_prompt"] for r in reponses if r["tokens_prompt"] is not None]
    tc = [r["tokens_completion"] for r in reponses if r["tokens_completion"] is not None]
    duree = sum(r["duree"] for r in reponses)
    decodage = sum(r["duree"] - (r["ttft"] or 0) for r in reponses)
    return {"ttft": ttfts[0] if ttfts else None, "duree": duree, "appels": len(reponses),
            "tokens_prompt": sum(tp) if tp else None, "tokens_completion": sum(tc) if tc else None,
            "debit": (sum(tc) / decodage) if tc and decodage > 0 else None}


def _resume_reponse(r):
    return {"ttft": r.ttft, "duree": r.duree, "tokens_prompt": r.tokens_prompt, "tokens_completion": r.tokens_completion, "fin": r.fin}


def jouer_chat(client, tache, jeux, config):
    docs = jeux["documents"]
    passages = [rag.passage(docs[i]) for i in tache["contexte"]]
    msgs = [{"role": "system", "content": jeux["prompts"]["chat_systeme"]},
            {"role": "user", "content": prompts.chat_utilisateur(tache["consigne"], passages)}]
    r = client.completer(msgs, None, config["echantillonnage"], config["max_tokens"])
    reponses, mesures, raisonnement = [r], [_resume_reponse(r)], len(r.raisonnement)
    for suite in tache.get("suite", []):
        msgs += [{"role": "assistant", "content": r.texte}, {"role": "user", "content": suite}]
        r = client.completer(msgs, None, config["echantillonnage"], config["max_tokens"])
        reponses.append(r)
        mesures.append(_resume_reponse(r))
        raisonnement += len(r.raisonnement)
    sortie = {"reponse": r.texte, "fin": r.fin, "mesures": _mesures(mesures),
              "note": n.noter_chat(tache, r.texte), "raisonnement_caracteres": raisonnement}
    if len(reponses) > 1:
        sortie["reponses_precedentes"] = [x.texte for x in reponses[:-1]]
    return sortie


def jouer_rag(client, question, jeux, config, index):
    docs = jeux["documents"]
    recuperes = index.rechercher(question["question"], rag.PARAMETRES["k"])
    passages = [rag.passage(docs[i]) for i in recuperes]
    msgs = [{"role": "system", "content": jeux["prompts"]["rag_systeme"]},
            {"role": "user", "content": prompts.rag_utilisateur(question["question"], passages)}]
    r = client.completer(msgs, None, config["echantillonnage"], config["max_tokens"])
    return {"reponse": r.texte, "fin": r.fin, "mesures": _mesures([_resume_reponse(r)]), "type_question": question["type_question"],
            "note": n.noter_rag(question, recuperes, r.texte, docs), "raisonnement_caracteres": len(r.raisonnement)}


def jouer_agentique(client, tache, jeux, config):
    env = ag.Environnement(jeux["documents"], jeux["environnement"], tache["pannes"])
    sortie = ag.executer_agent(client, tache, env, jeux["systeme_agent"], jeux["outils"],
                               config["echantillonnage"], config["max_tokens"])
    anomalies = [m["anomalie"] for m in sortie["mesures"] if m.get("anomalie")]
    return {"reponse": sortie["message_final"], "fin": sortie["arret"], "mesures": _mesures(sortie["mesures"]),
            "anomalies_serveur": anomalies, "brouillons": [dict(b) for b in env.brouillons], "tours": [{k: m[k] for k in ("fin", "anomalie", "texte")} for m in sortie["mesures"]],
            "note": n.noter_agentique(tache, env, sortie["message_final"]),
            "journal": env.journal, "brouillons": env.brouillons,
            "tableaux_finaux": {k: v["lignes"] for k, v in env.tableaux.items()}}


def _deja_faits(chemin: Path) -> set:
    if not chemin.exists():
        return set()
    faits = set()
    for l in chemin.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if not r.get("erreur"):
                faits.add((r["tache"], r["passe"]))
    return faits


def executer(config: dict, client, jeux: dict, sortie: Path, journal=print) -> Path:
    entree = catalogue.charger(config["modele_catalogue"])
    if config.get("via_cli"):
        entree = {**entree, "fournisseur": "claude_cli"}
    config = {**config, "echantillonnage": entree["echantillonnage"]}
    sortie.mkdir(parents=True, exist_ok=True)
    releve = construire_releve(config, entree, client.infos_serveur() if hasattr(client, "infos_serveur") else {}, jeux)
    (sortie / "releve.json").write_text(json.dumps(releve, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    chemin = sortie / "resultats.jsonl"
    faits = _deja_faits(chemin) if config.get("reprise") else set()
    if chemin.exists() and not config.get("reprise"):
        chemin.unlink()
    index = rag.Index(jeux["documents"])
    taches = []
    for bloc, cle in (("chat", "chat"), ("rag", "rag"), ("agentique", "agentique")):
        if bloc in config["blocs"]:
            lot = [t for t in jeux[cle] if not config.get("taches") or t["id"] in config["taches"]]
            taches += [(bloc, t) for t in (lot[:config["limite"]] if config.get("limite") else lot)]
    depense = sum(json.loads(l).get("cout_usd", 0) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()) if chemin.exists() else 0.0
    budget, arret = config.get("budget_usd"), None
    with chemin.open("a", encoding="utf-8") as f:
        for passe in range(1, config["passes"] + 1):
            for bloc, t in taches:
                if (t["id"], passe) in faits:
                    continue
                if budget is not None and depense >= budget:
                    arret = {"depense_usd": round(depense, 4), "budget_usd": budget, "derniere_tache": t["id"], "passe": passe}
                    break
                debut = time.monotonic()
                enr = {"metier": config["metier"], "bloc": bloc, "tache": t["id"], "niveau": t["niveau"], "gravite": t.get("gravite"), "passe": passe,
                       "modele_id": entree["id"], "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                       "erreur": None}
                try:
                    if bloc == "chat":
                        enr.update(jouer_chat(client, t, jeux, config))
                    elif bloc == "rag":
                        enr.update(jouer_rag(client, t, jeux, config, index))
                    else:
                        enr.update(jouer_agentique(client, t, jeux, config))
                    if config.get("prix_horaire"):
                        enr["cout"] = enr["mesures"]["duree"] / 3600 * config["prix_horaire"]
                    cout = catalogue.cout_usd(entree, enr["mesures"]["tokens_prompt"], enr["mesures"]["tokens_completion"])
                    if cout is not None:
                        enr["cout_usd"] = cout
                        depense += cout
                except ErreurClient as e:
                    enr["erreur"] = str(e)
                f.write(json.dumps(enr, ensure_ascii=False, default=str) + "\n")
                f.flush()
                statut = "ERREUR" if enr["erreur"] else ("ok" if _reussi(enr) else "echec")
                journal(f"[passe {passe}/{config['passes']}] {t['id']} {statut} ({time.monotonic() - debut:.1f} s)")
                if config.get("pause"):
                    time.sleep(config["pause"])
            if arret:
                break
    if arret:
        releve["arret_budget"] = arret
        journal(f"PLAFOND DE DEPENSE ATTEINT : {arret['depense_usd']} USD sur {arret['budget_usd']} USD, passe interrompue avant {arret['derniere_tache']}")
    releve["depense_usd"] = round(depense, 4) if entree.get("prix_mtok") else None
    (sortie / "releve.json").write_text(json.dumps(releve, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    from . import rapport
    rapport.generer(sortie)
    return sortie


def _reussi(enr) -> bool:
    note = enr["note"]
    return note.get("reussite_auto", note.get("reussite_generation", note.get("reussite")))


def analyser(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m core.lancer", description="Lance le benchmark contre un serveur compatible OpenAI.")
    p.add_argument("--metier", default="expert-comptable")
    p.add_argument("--modele-catalogue", required=True, help="identifiant dans core/catalogue/")
    p.add_argument("--blocs", default="chat,rag,agentique")
    p.add_argument("--passes", type=int, default=5)
    p.add_argument("--taches", default="", help="identifiants separes par des virgules")
    p.add_argument("--limite", type=int, default=0, help="nombre de taches par bloc (essais rapides)")
    p.add_argument("--max-tokens", type=int, default=None,
                   help=f"plafond de generation (raisonnement compris) ; par defaut celui du catalogue, sinon {MAX_TOKENS_DEFAUT}")
    p.add_argument("--prix-horaire", type=float, default=None, help="tarif horaire de la machine, pour le cout par tache")
    p.add_argument("--materiel", default=None, help="description du materiel (ex. carte Blackwell 48 Go)")
    p.add_argument("--etiquette", default=None)
    p.add_argument("--extraction", choices=sorted(d.MOTEURS_EXTRACTION), default="tika",
                   help="moteur d'extraction du texte des documents (tika : reference, docling : variante de comparaison)")
    p.add_argument("--budget-usd", type=float, default=None,
                   help="plafond de depense en dollars, OBLIGATOIRE pour un modele facture a l'usage (la passe s'arrete a une tache pres)")
    p.add_argument("--via-cli", action="store_true",
                   help="etalon Anthropic uniquement : interroger Claude par le CLI `claude -p` (abonnement, session isolee sans outils) "
                        "au lieu de l'API. Resultat marque non comparable")
    p.add_argument("--pause", type=float, default=0, help="secondes entre deux taches")
    p.add_argument("--reprise", action="store_true")
    p.add_argument("--sortie", default=None)
    return p.parse_args(argv)


def plafond(demande, entree: dict) -> int:
    """Plafond de generation : l'option de la ligne de commande, sinon celui du catalogue, sinon le defaut.
    Le raisonnement compte dans le plafond : un modele qui raisonne beaucoup a besoin d'une marge plus large."""
    return demande or entree.get("max_tokens") or MAX_TOKENS_DEFAUT


def main(argv=None):
    a = analyser(argv)
    entree = catalogue.charger(a.modele_catalogue)
    if a.via_cli:
        if entree.get("fournisseur") != "anthropic":
            sys.exit("--via-cli ne vaut que pour un etalon Anthropic du catalogue")
        entree = {**entree, "fournisseur": "claude_cli"}
        a.etiquette = a.etiquette or "via-cli"
    if catalogue.est_etalon(entree) and not a.budget_usd:
        sys.exit(f"{entree['nom']} est facture a l'usage ({entree['prix_mtok']['entree']} / {entree['prix_mtok']['sortie']} USD par million de tokens). "
                 "Relancer avec --budget-usd N : la passe s'arrete a une tache pres quand N dollars sont depenses.")
    try:
        client = creer_client(entree)
    except ErreurClient as e:
        sys.exit(str(e))
    config = {"budget_usd": a.budget_usd, "metier": a.metier, "modele_catalogue": a.modele_catalogue, "blocs": [b for b in a.blocs.split(",") if b],
              "passes": a.passes, "taches": [t for t in a.taches.split(",") if t], "limite": a.limite,
              "max_tokens": plafond(a.max_tokens, entree), "prix_horaire": a.prix_horaire, "materiel": a.materiel,
              "etiquette": a.etiquette, "via_cli": a.via_cli, "pause": a.pause, "reprise": a.reprise}
    jour = datetime.date.today().isoformat()
    nom = a.modele_catalogue + (f"-{a.etiquette}" if a.etiquette else "") + ("" if a.extraction == "tika" else f"-extraction-{a.extraction}")
    sortie = Path(a.sortie) if a.sortie else d.RACINE / "results" / a.metier / jour / nom
    executer(config, client, charger_jeux(a.metier, a.extraction), sortie)
    print(f"Resultats : {sortie}")


if __name__ == "__main__":
    main()
