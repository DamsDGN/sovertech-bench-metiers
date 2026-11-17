import json
import sys
from pathlib import Path

from .rapport import BLOCS, ecart_type, moyenne, reussite


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


def verdict(a: list, b: list) -> str:
    if len(a) < 2 or len(b) < 2:
        return "non évaluable : il faut au moins deux passes de chaque côté pour connaître la dispersion"
    ecart = moyenne(b) - moyenne(a)
    bruit = max(ecart_type(a) or 0, ecart_type(b) or 0)
    if abs(ecart) <= bruit:
        return f"**dans la dispersion** (écart {100 * ecart:+.1f} points, dispersion entre passes {100 * bruit:.1f} points) : aucune différence démontrée"
    return f"**au-dessus de la dispersion** (écart {100 * ecart:+.1f} points, dispersion entre passes {100 * bruit:.1f} points) : à confirmer avec plus de passes"


def comparer(dossier_a: Path, dossier_b: Path, nom_a: str = "A", nom_b: str = "B") -> str:
    a_tout, b_tout = charger(dossier_a), charger(dossier_b)
    sortie = [f"# Comparaison : {nom_a} contre {nom_b}", "",
              "Même modèle, mêmes tâches, mêmes réglages : seule la variante change. Les exécutions en erreur d'infrastructure sont écartées.", ""]
    for bloc, titre in BLOCS.items():
        a, b = [e for e in a_tout if e["bloc"] == bloc], [e for e in b_tout if e["bloc"] == bloc]
        if not a or not b:
            continue
        pa, pb = taux_par_passe(a), taux_par_passe(b)
        sortie += [f"## Épreuve « {titre} »", "",
                   f"- {nom_a} : {100 * moyenne(pa):.1f} % de réussite en moyenne sur {len(pa)} passe(s)" + (f", écart-type {100 * ecart_type(pa):.1f} points" if len(pa) > 1 else ""),
                   f"- {nom_b} : {100 * moyenne(pb):.1f} % de réussite en moyenne sur {len(pb)} passe(s)" + (f", écart-type {100 * ecart_type(pb):.1f} points" if len(pb) > 1 else ""),
                   f"- Écart : {verdict(pa, pb)}", ""]
        ta, tb = taux_par_tache(a), taux_par_tache(b)
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
               "- Peu de tâches dépendent réellement du moteur (celles qui lisent le CSV, les scans ou le FEC) : un écart global faible peut cacher un effet net sur ces tâches. Les tâches qui changent sont listées ci-dessus.",
               "- Une tâche qui change avec trois passes peut simplement refléter la variabilité du modèle : se fier d'abord au verdict sur la dispersion.", ""]
    return "\n".join(sortie)


def main(argv=None):
    args = argv or sys.argv[1:]
    if len(args) < 2:
        sys.exit("usage : python3 -m core.comparer <dossier A> <dossier B> [nom A] [nom B]")
    texte = comparer(Path(args[0]), Path(args[1]), *(args[2:4] or ["A", "B"]))
    print(texte)


if __name__ == "__main__":
    main()
