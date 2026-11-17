import json
import sys
from pathlib import Path

from . import statistiques
from .rapport import BLOCS, ecart_type, moyenne, reussite

GRAVES = {"elevee", "critique"}


def charger(dossier: Path) -> list:
    derniers = {}
    for l in (dossier / "resultats.jsonl").read_text(encoding="utf-8").splitlines():
        if l.strip():
            e = json.loads(l)
            derniers[(e["tache"], e["passe"])] = e
    return [e for e in derniers.values() if not e["erreur"]]


def taux_par_passe(enrs: list) -> list:
    par = {}
    for e in enrs:
        par.setdefault(e["passe"], []).append(1.0 if reussite(e) else 0.0)
    return [moyenne(v) for _, v in sorted(par.items())]


def taux_par_tache(enrs: list) -> dict:
    par = {}
    for e in enrs:
        par.setdefault(e["tache"], []).append(1.0 if reussite(e) else 0.0)
    return {t: moyenne(v) for t, v in par.items()}


def gravite_de(enrs: list, tache: str):
    return next((e.get("gravite") for e in enrs if e["tache"] == tache), None)


def phrase_appariee(r: dict, nom_a: str, nom_b: str) -> list:
    if r["n"] == 0:
        return ["- Aucune tâche commune : comparaison impossible."]
    if r["trop_peu"]:
        return [f"- Seulement {r['n']} tâche(s) commune(s) : **trop peu pour conclure** (minimum {statistiques.MINIMUM_TACHES})."]
    ic = f"intervalle de confiance à 95 % sur les tâches : de {100 * r['ic_bas']:+.1f} à {100 * r['ic_haut']:+.1f} points"
    verdict = ("**différence démontrée** (l'intervalle exclut zéro)" if r["demontree"]
               else "**différence non démontrée** (l'intervalle contient zéro) : on ne peut pas départager les deux")
    return [f"- Écart de réussite ({nom_b} moins {nom_a}) : **{100 * r['difference']:+.1f} points**, {ic}.",
            f"- {nom_b} l'emporte sur {r['b_mieux']} tâche(s), {nom_a} sur {r['a_mieux']}, égalité sur {r['egales']} (test des signes : p = {r['p_signes']:.3f}).",
            f"- Verdict : {verdict}."]


def comparer(dossier_a: Path, dossier_b: Path, nom_a: str = "A", nom_b: str = "B") -> str:
    a_tout, b_tout = charger(dossier_a), charger(dossier_b)
    sortie = [f"# Comparaison : {nom_a} contre {nom_b}", "",
              "Même modèle, mêmes tâches, mêmes réglages : seule la variante change. Les exécutions en erreur d'infrastructure sont écartées.",
              "La comparaison est **appariée par tâche** : on regarde, pour chaque tâche, laquelle des deux variantes réussit le mieux, "
              "puis on évalue si l'écart moyen dépasse ce que le hasard du choix des tâches suffirait à produire.", ""]
    for bloc, titre in BLOCS.items():
        a, b = [e for e in a_tout if e["bloc"] == bloc], [e for e in b_tout if e["bloc"] == bloc]
        if not a or not b:
            continue
        pa, pb = taux_par_passe(a), taux_par_passe(b)
        ta, tb = taux_par_tache(a), taux_par_tache(b)
        sortie += [f"## Épreuve « {titre} »", "",
                   f"- {nom_a} : {100 * moyenne(pa):.1f} % de réussite en moyenne sur {len(pa)} passe(s)" + (f", variabilité entre passes {100 * ecart_type(pa):.1f} points" if len(pa) > 1 else ""),
                   f"- {nom_b} : {100 * moyenne(pb):.1f} % de réussite en moyenne sur {len(pb)} passe(s)" + (f", variabilité entre passes {100 * ecart_type(pb):.1f} points" if len(pb) > 1 else "")]
        sortie += phrase_appariee(statistiques.comparaison_appariee(ta, tb), nom_a, nom_b) + [""]
        graves_a = {t: v for t, v in ta.items() if gravite_de(a, t) in GRAVES}
        graves_b = {t: v for t, v in tb.items() if gravite_de(b, t) in GRAVES}
        if graves_a and graves_b:
            sortie += ["Sur les seules tâches **de gravité élevée ou critique** :", ""] + phrase_appariee(statistiques.comparaison_appariee(graves_a, graves_b), nom_a, nom_b) + [""]
        differences = sorted((t, ta[t], tb[t]) for t in ta if t in tb and abs(ta[t] - tb[t]) > 1e-9)
        if differences:
            sortie += [f"Tâches dont le taux de réussite diffère ({len(differences)} sur {len(set(ta) & set(tb))}) :", "",
                       f"| Tâche | {nom_a} | {nom_b} |", "|---|---|---|"]
            sortie += [f"| {t} | {100 * x:.0f} % | {100 * y:.0f} % |" for t, x, y in differences]
            sortie.append("")
        else:
            sortie += ["Aucune tâche ne change de taux de réussite.", ""]
    sortie += ["## Ce que cette comparaison ne dit pas", "",
               "- Un seul modèle : un effet peut exister sur un autre modèle sans apparaître ici.",
               "- Peu de tâches dépendent réellement de la variante (celles qui lisent le CSV, les scans ou le FEC) : un écart global faible peut cacher un effet net sur ces tâches, listées ci-dessus.",
               "- Un intervalle qui contient zéro ne prouve pas que les deux variantes se valent : il dit que cet échantillon de tâches ne permet pas de les départager.", ""]
    return "\n".join(sortie)


def main(argv=None):
    args = argv or sys.argv[1:]
    if len(args) < 2:
        sys.exit("usage : python3 -m core.comparer <dossier A> <dossier B> [nom A] [nom B]")
    texte = comparer(Path(args[0]), Path(args[1]), *(args[2:4] or ["A", "B"]))
    print(texte)


if __name__ == "__main__":
    main()
