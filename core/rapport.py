import csv
import json
import statistics
from pathlib import Path

NIVEAUX = ("simple", "moyen", "complexe")
BLOCS = {"chat": "Discuter", "rag": "Chercher dans les dossiers", "agentique": "Agir"}


def moyenne(x):
    return sum(x) / len(x) if x else None


def ecart_type(x):
    return statistics.stdev(x) if len(x) > 1 else None


def pct(v):
    return "n/d" if v is None else f"{100 * v:.0f} %"


def pct_ecart(valeurs):
    m = moyenne(valeurs)
    if m is None:
        return "n/d"
    e = ecart_type(valeurs)
    return f"{100 * m:.0f} %" + (f" (écart-type {100 * e:.0f} points, de {100 * min(valeurs):.0f} à {100 * max(valeurs):.0f} %)" if e is not None else " (une seule passe : pas de dispersion)")


def nombre(v, nd=1, unite=""):
    return "n/d" if v is None else f"{v:.{nd}f}{unite}"


def reussite(enr):
    note = enr["note"]
    for cle in ("reussite_auto", "reussite_generation", "reussite"):
        if cle in note:
            return bool(note[cle])
    return False


def taux_par_passe(enrs, filtre=lambda e: True, valeur=reussite):
    par = {}
    for e in enrs:
        if filtre(e):
            par.setdefault(e["passe"], []).append(1.0 if valeur(e) else 0.0)
    return [moyenne(v) for _, v in sorted(par.items())]


def charger(dossier: Path):
    releve = json.loads((dossier / "releve.json").read_text(encoding="utf-8"))
    enrs = [json.loads(l) for l in (dossier / "resultats.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return releve, enrs


def _bloc_chat(enrs):
    return [f"- Réussite aux contrôles automatiques : **{pct_ecart(taux_par_passe(enrs))}**",
            "- Les critères du juge (qualité du français, clarté, prudence) ne sont **pas notés** dans ce rapport"]


def _bloc_rag(enrs):
    ok = [e for e in enrs if not e["erreur"]]
    rappels = [e["note"]["rappel"] for e in ok if e["note"]["rappel"] is not None]
    mrr = [e["note"]["rang_reciproque"] for e in ok if e["note"]["rang_reciproque"] is not None]
    cond = [e for e in ok if e["note"]["rappel"] == 1.0]
    cit = [e["note"]["citation_ok"] for e in ok if e["note"]["citation_ok"] is not None]
    abst = [e for e in ok if e.get("type_question") in ("sans_reponse", "reponse_partielle")]
    obs = [e for e in ok if "piege_obsolete_tombe" in e["note"]]
    return [f"- **Récupération** : rappel moyen {pct(moyenne(rappels))}, rang réciproque moyen {nombre(moyenne(mrr), 2)} "
            "(le bon document est-il parmi les premiers retrouvés ?)",
            f"- **Génération** (réussite aux contrôles automatiques) : **{pct_ecart(taux_par_passe(enrs))}**",
            f"- Génération quand tous les documents attendus ont été retrouvés : {pct(moyenne([1.0 if e['note']['reussite_generation'] else 0.0 for e in cond]))} ({len(cond)} passages)",
            f"- Citation d'un document attendu : {pct(moyenne([1.0 if c else 0.0 for c in cit]))}",
            f"- Questions où il fallait s'abstenir (sans réponse ou réponse partielle) : {pct(moyenne([1.0 if e['note']['reussite_generation'] else 0.0 for e in abst]))} ({len(abst)} passages)",
            f"- Pièges « version obsolète » dans lesquels le modèle est tombé : {pct(moyenne([1.0 if e['note']['piege_obsolete_tombe'] else 0.0 for e in obs]))}"]


def _bloc_agentique(enrs):
    ok = [e for e in enrs if not e["erreur"]]
    interdit = [1.0 if e["note"]["actions_interdites"] else 0.0 for e in ok]
    etapes = [e["note"]["etapes"] for e in ok]
    depasse = [1.0 if e["note"]["depasse_etapes"] else 0.0 for e in ok]
    reprise = [1.0 if e["note"]["reprise_apres_panne"] else 0.0 for e in ok if e["note"]["reprise_apres_panne"] is not None or e["note"]["pannes_subies"]]
    anom = [e for e in ok if e.get("anomalies_serveur")]
    ratees = [e for e in ok if not reussite(e)]
    attribuables = [e for e in ratees if e.get("anomalies_serveur")]
    return [f"- **Réussite** (état final exact, aucune action interdite) : **{pct_ecart(taux_par_passe(enrs))}**",
            f"- **Anomalies côté serveur** : {len(anom)} passage(s) sur {len(ok)} où le serveur n'a pas converti un appel d'outil du modèle (texte brut d'appel dans la réponse) ou a rendu une réponse vide ; "
            f"{len(attribuables)} des {len(ratees)} échecs en comportent. Ces échecs relèvent de l'ensemble modèle + serveur (analyseur d'outils), pas du seul modèle.",
            f"- Passages avec une action interdite : {pct(moyenne(interdit))}",
            f"- Nombre moyen d'appels d'outils : {nombre(moyenne(etapes))} ; passages au-dessus du maximum prévu : {pct(moyenne(depasse))}",
            f"- Reprise après une panne d'outil simulée : {pct(moyenne(reprise))} ({len(reprise)} passages concernés)"]


def _par_niveau(enrs):
    lignes = ["| Niveau | Tâches | Réussite |", "|---|---|---|"]
    for niv in NIVEAUX:
        sel = [e for e in enrs if e["niveau"] == niv and not e["erreur"]]
        if sel:
            lignes.append(f"| {niv} | {len({e['tache'] for e in sel})} | {pct(moyenne([1.0 if reussite(e) else 0.0 for e in sel]))} |")
    return lignes


def performance(enrs):
    ok = [e for e in enrs if not e["erreur"] and e.get("mesures")]
    ttft = [e["mesures"]["ttft"] for e in ok if e["mesures"]["ttft"] is not None]
    debit = [e["mesures"]["debit"] for e in ok if e["mesures"]["debit"]]
    duree = [e["mesures"]["duree"] for e in ok]
    tc = [e["mesures"]["tokens_completion"] for e in ok if e["mesures"]["tokens_completion"] is not None]
    couts = [e["cout"] for e in ok if "cout" in e]
    return {"ttft_median": statistics.median(ttft) if ttft else None, "debit_moyen": moyenne(debit),
            "duree_moyenne": moyenne(duree), "tokens_moyens": moyenne(tc), "cout_moyen": moyenne(couts) if couts else None,
            "tronquees": sum(1 for e in ok if e.get("fin") == "length")}


def generer(dossier: Path) -> Path:
    releve, enrs = charger(dossier)
    m = releve["modele_catalogue"]
    erreurs = [e for e in enrs if e["erreur"]]
    out = [f"# Rapport : {m['nom']} ({m['quantification']})", "",
           f"Généré le {releve['date']}. Métier : {releve['metier']}.", ""]
    if not releve["comparable_aux_resultats_publies"]:
        out += ["> **Résultat NON comparable aux résultats publiés.** " + " ; ".join(releve["raisons_non_comparable"]) + ".",
                "> Il valide le fonctionnement du benchmark et donne une indication de comportement : il ne doit pas être classé avec les autres modèles.", ""]
    out += ["## Configuration", "",
            f"- Dépôt du modèle : `{m['depot_hf']}` (révision `{m.get('revision_hf')}`)",
            f"- Modèle réellement servi : `{releve['serveur'].get('modele_servi')}`, contexte maximal {releve['serveur'].get('contexte_max')}",
            f"- Réglages d'échantillonnage (ceux de l'éditeur) : {releve['echantillonnage']}",
            f"- Récupérateur du RAG : {releve['recuperateur']}", f"- Prompts : version {releve['moteur']['prompts']} (empreinte {releve['moteur']['empreinte_prompts']})",
            f"- Moteur : commit `{(releve['moteur']['commit'] or 'inconnu')[:10]}`, plafond de génération {releve['max_tokens']} tokens",
            f"- Matériel déclaré : {releve['materiel_declare'] or 'non déclaré'} ; mémoire GPU : "
            + (f"{releve['memoire_gpu']['valeur_mib']} Mio" if releve['memoire_gpu']['valeur_mib'] else f"non relevée ({releve['memoire_gpu']['raison']})"), ""]
    lignes_csv = []
    for bloc, titre in BLOCS.items():
        tous = [e for e in enrs if e["bloc"] == bloc]
        if not tous:
            continue
        sel = [e for e in tous if not e["erreur"]]
        ok = sel
        out += [f"## Épreuve « {titre} »", "",
                f"{len({e['tache'] for e in tous})} tâches, {len({e['passe'] for e in tous})} passe(s), {len(tous)} exécutions dont {len(sel)} valides.", ""]
        if not sel:
            out += ["Aucune exécution valide : voir les erreurs d'infrastructure en fin de rapport.", ""]
            continue
        out += {"chat": _bloc_chat, "rag": _bloc_rag, "agentique": _bloc_agentique}[bloc](sel) + [""] + _par_niveau(sel) + [""]
        faibles = {}
        for e in ok:
            faibles.setdefault(e["tache"], []).append(1.0 if reussite(e) else 0.0)
        ratees = sorted((moyenne(v), t) for t, v in faibles.items() if moyenne(v) < 1)
        if ratees:
            out += ["Tâches non réussies à toutes les passes : " + ", ".join(f"{t} ({pct(r)})" for r, t in ratees), ""]
        p = performance(sel)
        out += [f"Performance : temps avant la première réponse (médiane) {nombre(p['ttft_median'], 2, ' s')} ; débit moyen {nombre(p['debit_moyen'], 1, ' tokens/s')} ; "
                f"durée moyenne par tâche {nombre(p['duree_moyenne'], 1, ' s')} ; tokens générés par tâche {nombre(p['tokens_moyens'], 0)} ; "
                f"réponses coupées au plafond : {p['tronquees']}"
                + (f" ; coût moyen par tâche {nombre(p['cout_moyen'], 4, ' €')}" if p["cout_moyen"] is not None else " ; coût par tâche non calculé (aucun tarif horaire fourni)"), ""]
        lignes_csv.append([bloc, len({e['tache'] for e in sel}), len({e['passe'] for e in sel}), moyenne(taux_par_passe(sel)),
                           ecart_type(taux_par_passe(sel)), p["ttft_median"], p["debit_moyen"], p["duree_moyenne"], p["cout_moyen"]])
    out += ["## Limites de ce rapport", "",
            f"- Nombre de passes : {releve['passes']} (une seule passe ne donne aucune dispersion ; la méthode en prévoit 5).",
            "- Les notes sont **automatiques**. La notation par un juge (qualité du français, clarté, prudence) n'est pas incluse : les critères du juge restent à noter.",
            "- **Toutes les réponses de référence sont « à valider par un professionnel »** : un score de justesse métier n'est pas établi.",
            "- Les contrôles automatiques sont stricts et lexicaux : une bonne réponse très inhabituelle peut échouer, et une réponse d'abstention est repérée par une liste de formulations.",
            "- Avec une vingtaine de tâches par épreuve, un petit écart entre deux modèles n'est pas significatif : un écart n'est annoncé que s'il dépasse la dispersion observée.", ""]
    if erreurs:
        out += [f"- **{len(erreurs)} exécution(s) en erreur d'infrastructure** (serveur injoignable, délai dépassé), non comptées dans les taux.", ""]
    (dossier / "rapport.md").write_text("\n".join(out), encoding="utf-8")
    with (dossier / "resume.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bloc", "taches", "passes", "reussite_moyenne", "ecart_type_entre_passes", "ttft_median_s", "debit_tokens_s", "duree_moyenne_s", "cout_moyen_par_tache"])
        w.writerows(lignes_csv)
    return dossier / "rapport.md"


def main(argv=None):
    import sys
    chemin = generer(Path((argv or sys.argv[1:])[0]))
    print(chemin)


if __name__ == "__main__":
    main()
