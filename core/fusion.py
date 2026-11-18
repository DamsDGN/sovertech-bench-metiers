"""Regroupe plusieurs mesures du meme modele et du meme metier en une seule, pour en publier la moyenne.

Les passes de chaque mesure sont renumerotees a la suite : deux mesures de 2 passes donnent une mesure de
4 passes. Le releve garde la trace de chaque mesure d'origine (etiquette, date, passes).
Usage : python3 -m core.fusion --sortie DOSSIER mesure1 mesure2 ...
"""
import argparse
import json
from pathlib import Path


def fusionner(dossiers, sortie):
    releves = [json.loads((Path(d) / "releve.json").read_text(encoding="utf-8")) for d in dossiers]
    for cle in ("metier",):
        if len({r[cle] for r in releves}) != 1:
            raise ValueError(f"mesures de {cle} differents : fusion impossible")
    if len({r["modele_catalogue"]["id"] for r in releves}) != 1:
        raise ValueError("mesures de modeles differents : fusion impossible")
    lignes, decalage, origine = [], 0, []
    for d, rel in zip(dossiers, releves):
        for l in (Path(d) / "resultats.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                e = json.loads(l)
                e["passe"] += decalage
                lignes.append(json.dumps(e, ensure_ascii=False))
        origine.append({"etiquette": rel.get("etiquette"), "date": rel["date"][:10], "passes": rel["passes"]})
        decalage += rel["passes"]
    releve = {**releves[-1], "passes": decalage, "mesures_combinees": origine,
              "depense_usd": sum(r.get("depense_usd") or 0 for r in releves)}
    sortie = Path(sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "resultats.jsonl").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    (sortie / "releve.json").write_text(json.dumps(releve, ensure_ascii=False, indent=2), encoding="utf-8")
    return releve


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dossiers", nargs="+")
    p.add_argument("--sortie", required=True)
    a = p.parse_args(argv)
    r = fusionner(a.dossiers, a.sortie)
    print(f"{r['passes']} passes ecrites dans {a.sortie}")


if __name__ == "__main__":
    main()
