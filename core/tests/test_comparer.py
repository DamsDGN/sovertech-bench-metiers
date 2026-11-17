import json
import tempfile
import unittest
from pathlib import Path

from core import comparer


def ecrire(dossier, lignes):
    dossier.mkdir(parents=True)
    (dossier / "resultats.jsonl").write_text("\n".join(json.dumps(l) for l in lignes) + "\n", encoding="utf-8")
    return dossier


def ligne(tache, passe, ok, bloc="chat", erreur=None):
    e = {"tache": tache, "passe": passe, "bloc": bloc, "erreur": erreur}
    if not erreur:
        e["note"] = {"reussite_auto": ok}
    return e


class Comparer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.racine = Path(self.tmp.name)

    def test_taux_par_passe_et_par_tache(self):
        enrs = [ligne("CH-01", 1, True), ligne("CH-02", 1, False), ligne("CH-01", 2, True), ligne("CH-02", 2, True)]
        self.assertEqual(comparer.taux_par_passe(enrs), [0.5, 1.0])
        self.assertEqual(comparer.taux_par_tache(enrs), {"CH-01": 1.0, "CH-02": 0.5})

    def test_derniere_execution_et_erreurs_ecartees(self):
        d = ecrire(self.racine / "a", [ligne("CH-01", 1, True, erreur="reseau"), ligne("CH-01", 1, False), ligne("CH-02", 1, None, erreur="reseau")])
        enrs = comparer.charger(d)
        self.assertEqual(len(enrs), 1)
        self.assertFalse(enrs[0]["note"]["reussite_auto"])

    def test_verdict_une_seule_passe(self):
        self.assertIn("non évaluable", comparer.verdict([0.5], [0.6]))

    def test_verdict_dans_la_dispersion(self):
        self.assertIn("dans la dispersion", comparer.verdict([0.50, 0.60, 0.55], [0.52, 0.58, 0.60]))

    def test_verdict_au_dessus_de_la_dispersion(self):
        self.assertIn("au-dessus de la dispersion", comparer.verdict([0.50, 0.52, 0.51], [0.80, 0.82, 0.81]))

    def test_rapport_complet(self):
        a = ecrire(self.racine / "a", [ligne(t, p, ok) for p in (1, 2) for t, ok in (("CH-01", True), ("CH-02", True), ("CH-03", False))])
        b = ecrire(self.racine / "b", [ligne(t, p, ok) for p in (1, 2) for t, ok in (("CH-01", True), ("CH-02", False), ("CH-03", False))])
        texte = comparer.comparer(a, b, "Tika", "Docling")
        for attendu in ("Tika contre Docling", "Épreuve « Discuter »", "| CH-02 | 100 % | 0 % |", "Ce que cette comparaison ne dit pas"):
            self.assertIn(attendu, texte)
        self.assertNotIn("| CH-01 |", texte)

    def test_aucune_difference(self):
        lignes = [ligne("CH-01", p, True) for p in (1, 2)]
        texte = comparer.comparer(ecrire(self.racine / "a", lignes), ecrire(self.racine / "b", lignes))
        self.assertIn("Aucune tâche ne change", texte)


if __name__ == "__main__":
    unittest.main()
