"""Export des resultats pour la page de comparaison du site : un JSON deterministe, sans calcul cote site.

Usage : python3 -m core.publication --sortie bench-metiers.json <dossier de resultats> [<dossier> ...]
Un dossier de resultats contient un seul modele pour un seul metier (releve.json et resultats.jsonl).
Les modeles du catalogue sans resultat sont exportes avec le statut « non_mesure », jamais avec zero.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

from . import catalogue, donnees as d, rapport as r, statistiques

SCHEMA = 1
MIN_PASSES_PUBLICATION = 5
BLOCS = ("chat", "rag", "agentique")


def _taux_epreuve(enrs):
    ok = [e for e in enrs if not e["erreur"]]
    par_passe = [t for t in r.taux_par_passe(ok) if t is not None]
    m, bas, haut = statistiques.ic_moyenne(list(r.taux_par_tache(ok).values()))
    return {"taux": r.moyenne(par_passe), "ecart_type_passes": r.ecart_type(par_passe),
            "min_passes": min(par_passe) if par_passe else None, "max_passes": max(par_passe) if par_passe else None,
            "ic95_taches": {"bas": bas, "haut": haut}, "taches": len({e["tache"] for e in ok}), "executions": len(ok), "passes": len(par_passe)}


def _par_niveau(enrs):
    sortie = {}
    for niv in r.NIVEAUX:
        sel = [e for e in enrs if e["niveau"] == niv and not e["erreur"]]
        if sel:
            sortie[niv] = {"taches": len({e["tache"] for e in sel}), "taux": r.moyenne([1.0 if r.reussite(e) else 0.0 for e in sel])}
    return sortie


def _par_gravite(enrs):
    sortie = {}
    for g in r.GRAVITES:
        sel = [e for e in enrs if e.get("gravite") == g and not e["erreur"]]
        if sel:
            ok = sum(1 for e in sel if r.reussite(e))
            sortie[g] = {"taches": len({e["tache"] for e in sel}), "executions": len(sel), "taux": ok / len(sel), "echecs": len(sel) - ok}
    return sortie


def _details(bloc, enrs):
    ok = [e for e in enrs if not e["erreur"]]
    if bloc == "rag":
        rappels = [e["note"]["rappel"] for e in ok if e["note"]["rappel"] is not None]
        abst = [e for e in ok if e.get("type_question") in ("sans_reponse", "reponse_partielle")]
        obs = [e for e in ok if "piege_obsolete_tombe" in e["note"]]
        return {"rappel_moyen": r.moyenne(rappels), "abstention_pertinente": r.moyenne([1.0 if e["note"]["reussite_generation"] else 0.0 for e in abst]),
                "piege_obsolete_tombe": r.moyenne([1.0 if e["note"]["piege_obsolete_tombe"] else 0.0 for e in obs])}
    if bloc == "agentique":
        ratees = [e for e in ok if not r.reussite(e)]
        return {"anomalies_serveur": {"passages": sum(1 for e in ok if e.get("anomalies_serveur")), "sur": len(ok),
                                      "echecs_concernes": sum(1 for e in ratees if e.get("anomalies_serveur")), "echecs": len(ratees)},
                "passages_avec_action_interdite": r.moyenne([1.0 if e["note"]["actions_interdites"] else 0.0 for e in ok]),
                "passages_avec_destinataire_invente": (r.moyenne([1.0 if e["note"]["destinataires_inventes"] else 0.0 for e in ok])
                                                       if all("destinataires_inventes" in e["note"] for e in ok) else None)}
    return {}


def mesure_metier(releve, enrs, part_validee):
    ok = [e for e in enrs if not e["erreur"]]
    graves = r.erreurs_graves(ok)
    perf = r.performance(ok)
    epreuves = {}
    for bloc in BLOCS:
        sel = [e for e in ok if e["bloc"] == bloc]
        if sel:
            epreuves[bloc] = {**_taux_epreuve(sel), "par_niveau": _par_niveau(sel), "par_gravite": _par_gravite(sel), **_details(bloc, sel)}
    return {
        "epreuves": epreuves,
        "taches_graves": None if graves is None else {"executions": graves["executions"], "echecs": graves["echecs"], "taux_echec": graves["taux"],
                                                       "critiques_executions": graves["critiques"], "critiques_echecs": graves["critiques_echecs"],
                                                       "taches_en_echec": graves["taches_en_echec"]},
        "performance": {"ttft_median_s": perf["ttft_median"], "debit_moyen_tokens_s": perf["debit_moyen"], "duree_moyenne_s": perf["duree_moyenne"],
                        "tokens_moyens": perf["tokens_moyens"], "reponses_coupees_au_plafond": perf["tronquees"]},
        "erreurs_infrastructure_ecartees": sum(1 for e in enrs if e["erreur"]),
        "configuration": {"passes": releve["passes"], "plafond_generation_tokens": releve["max_tokens"], "echantillonnage": releve["echantillonnage"],
                          "contexte_max_serveur": releve.get("serveur", {}).get("contexte_max"), "extraction": releve["extraction"]["moteur"],
                          "recuperateur": releve["recuperateur"], "materiel_declare": releve.get("materiel_declare"),
                          "date_mesure": releve["date"][:10], "version_benchmark": (releve["moteur"]["commit"] or "")[:10], "etiquette": releve.get("etiquette")},
        "comparable": bool(releve["comparable_aux_resultats_publies"]), "raisons_non_comparable": list(releve.get("raisons_non_comparable", [])),
        "part_references_validees": part_validee,
    }


def _part_validee(metier, racine=d.RACINE):
    jeux = d.charger_metier(metier, racine)
    taches = [t for b in BLOCS for t in jeux[b]]
    return sum(1 for t in taches if t["a_valider_par_pro"] is False) / len(taches)


def _raisons_non_publiable(mesures):
    raisons = []
    for metier, m in mesures.items():
        if m["part_references_validees"] < 1.0:
            raisons.append(f"{metier} : references non relues par un professionnel")
        if m["configuration"]["passes"] < MIN_PASSES_PUBLICATION:
            raisons.append(f"{metier} : {m['configuration']['passes']} passes au lieu de {MIN_PASSES_PUBLICATION}")
        if not m["comparable"]:
            raisons.append(f"{metier} : resultat non comparable ({'; '.join(m['raisons_non_comparable'])})")
    return raisons


def construire(dossiers, racine=d.RACINE, maintenant=None):
    mesures = {}
    for dossier in dossiers:
        releve, enrs = r.charger(Path(dossier))
        id_ = releve["modele_catalogue"]["id"]
        mesures.setdefault(id_, {})[releve["metier"]] = mesure_metier(releve, enrs, _part_validee(releve["metier"], racine))
    modeles = []
    for e in sorted(catalogue.lister(), key=lambda x: (catalogue.est_etalon(x), x["id"])):
        fiche = {"id": e["id"], "nom": e["nom"], "categorie": "etalon_cloud" if catalogue.est_etalon(e) else "local", "editeur": e.get("editeur_modele"), "depot_hf": e.get("depot_hf"),
                 "revision_hf": e.get("revision_hf"), "quantification": e.get("quantification"), "licence": e.get("licence"),
                 "parametres_milliards": e.get("parametres_milliards"), "exception_format": e.get("exception_format")}
        if e["id"] in mesures:
            fiche["statut"] = "mesure"
            fiche["metiers"] = mesures[e["id"]]
            fiche["raisons_non_publiable"] = _raisons_non_publiable(mesures[e["id"]])
        else:
            fiche["statut"] = "non_mesure"
        modeles.append(fiche)
    return {"schema": SCHEMA, "genere_le": (maintenant or datetime.datetime.now().astimezone()).isoformat(timespec="seconds"),
            "depot": "https://github.com/DamsDGN/sovertech-bench-metiers",
            "avertissements": ["situations inventees : un cabinet et une etude fictifs", "references de reponse non relues par un professionnel tant que part_references_validees < 1",
                               "un seul modele mesure a ce jour", "ne pas presenter un score sans sa configuration"],
            "modeles": modeles}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dossiers", nargs="+")
    p.add_argument("--sortie", required=True)
    a = p.parse_args(argv)
    export = construire(a.dossiers)
    Path(a.sortie).write_text(json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mesures = [m for m in export["modeles"] if m["statut"] == "mesure"]
    print(f"{len(export['modeles'])} modeles, {len(mesures)} mesure(s) : {a.sortie}")


if __name__ == "__main__":
    main()
