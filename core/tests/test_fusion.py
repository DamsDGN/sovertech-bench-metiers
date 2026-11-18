import json
import tempfile
import unittest
from pathlib import Path

from core import fusion


def _mesure(racine, nom, passes, etiquette, metier="notaire", modele="m"):
    d = Path(racine) / nom
    d.mkdir()
    (d / "releve.json").write_text(json.dumps({"metier": metier, "modele_catalogue": {"id": modele}, "passes": passes,
                                               "etiquette": etiquette, "date": "2026-11-18T00:00:00", "depense_usd": 1.0}), encoding="utf-8")
    (d / "resultats.jsonl").write_text("\n".join(json.dumps({"tache": "T1", "passe": p}) for p in range(1, passes + 1)) + "\n", encoding="utf-8")
    return d


class Fusion(unittest.TestCase):
    def test_les_passes_sont_renumerotees_a_la_suite(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = _mesure(t, "a", 2, "un"), _mesure(t, "b", 2, "deux")
            rel = fusion.fusionner([a, b], Path(t) / "out")
            self.assertEqual(rel["passes"], 4)
            self.assertEqual([m["etiquette"] for m in rel["mesures_combinees"]], ["un", "deux"])
            passes = [json.loads(l)["passe"] for l in (Path(t) / "out" / "resultats.jsonl").read_text().splitlines()]
            self.assertEqual(passes, [1, 2, 3, 4])

    def test_refuse_des_modeles_ou_metiers_differents(self):
        with tempfile.TemporaryDirectory() as t:
            a = _mesure(t, "a", 1, "un")
            with self.assertRaises(ValueError):
                fusion.fusionner([a, _mesure(t, "b", 1, "deux", modele="autre")], Path(t) / "out")
            with self.assertRaises(ValueError):
                fusion.fusionner([a, _mesure(t, "c", 1, "trois", metier="expert-comptable")], Path(t) / "out2")


if __name__ == "__main__":
    unittest.main()
