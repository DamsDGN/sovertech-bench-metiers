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

    def test_phrase_trop_peu_de_taches(self):
        from core import statistiques
        texte = " ".join(comparer.phrase_appariee(statistiques.comparaison_appariee({"A": 0.0, "B": 0.0}, {"A": 1.0, "B": 1.0}), "A", "B"))
        self.assertIn("trop peu pour conclure", texte)

    def test_phrase_difference_demontree_et_non_demontree(self):
        from core import statistiques
        a = {f"T{i}": 0.0 for i in range(12)}
        b = {f"T{i}": 1.0 for i in range(12)}
        self.assertIn("différence démontrée", " ".join(comparer.phrase_appariee(statistiques.comparaison_appariee(a, b), "A", "B")))
        c = {f"T{i}": float(i % 2) for i in range(12)}
        d = {f"T{i}": float((i + 1) % 2) for i in range(12)}
        self.assertIn("différence non démontrée", " ".join(comparer.phrase_appariee(statistiques.comparaison_appariee(c, d), "A", "B")))

    def test_rapport_complet(self):
        a = ecrire(self.racine / "a", [ligne(t, p, ok) for p in (1, 2) for t, ok in (("CH-01", True), ("CH-02", True), ("CH-03", False))])
        b = ecrire(self.racine / "b", [ligne(t, p, ok) for p in (1, 2) for t, ok in (("CH-01", True), ("CH-02", False), ("CH-03", False))])
        texte = comparer.comparer(a, b, "Tika", "Docling")
        for attendu in ("Tika contre Docling", "Épreuve « Discuter »", "| CH-02 | 100 % | 0 % |", "Ce que cette comparaison ne dit pas", "appariée par tâche", "trop peu pour conclure"):
            self.assertIn(attendu, texte)
        self.assertNotIn("| CH-01 |", texte)

    def test_aucune_difference(self):
        lignes = [ligne("CH-01", p, True) for p in (1, 2)]
        texte = comparer.comparer(ecrire(self.racine / "a", lignes), ecrire(self.racine / "b", lignes))
        self.assertIn("Aucune tâche ne change", texte)


if __name__ == "__main__":
    unittest.main()
