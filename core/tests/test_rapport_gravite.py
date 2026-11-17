import unittest

from core import rapport


def e(tache, gravite, ok, passe=1, bloc="chat", erreur=None, cout=None):
    r = {"tache": tache, "gravite": gravite, "passe": passe, "bloc": bloc, "niveau": "simple", "erreur": erreur}
    if not erreur:
        r["note"] = {"reussite_auto": ok}
        r["mesures"] = {"ttft": 0.1, "debit": 100.0, "duree": 1.0, "tokens_completion": 10}
        if cout is not None:
            r["cout_usd"] = cout
    return r


class Plafond(unittest.TestCase):
    def test_les_reponses_coupees_sont_comptees(self):
        coupee = e("A", "faible", False)
        coupee["fin"] = "length"
        self.assertEqual(rapport.performance([coupee, e("B", "faible", True)])["tronquees"], 1)


class ErreursGraves(unittest.TestCase):
    def test_comptage(self):
        enrs = [e("A", "faible", False), e("B", "elevee", True), e("C", "elevee", False), e("D", "critique", False), e("E", "critique", True)]
        g = rapport.erreurs_graves(enrs)
        self.assertEqual((g["executions"], g["echecs"]), (4, 2))
        self.assertEqual((g["critiques"], g["critiques_echecs"]), (2, 1))
        self.assertEqual(g["taches_en_echec"], ["C", "D"])
        self.assertAlmostEqual(g["taux"], 0.5)

    def test_les_echecs_faibles_ne_comptent_pas_comme_graves(self):
        self.assertEqual(rapport.erreurs_graves([e("A", "faible", False), e("B", "moyenne", False)]), None)

    def test_les_erreurs_d_infrastructure_sont_ecartees(self):
        g = rapport.erreurs_graves([e("A", "elevee", None, erreur="reseau"), e("B", "elevee", True)])
        self.assertEqual((g["executions"], g["echecs"]), (1, 0))

    def test_anciens_resultats_sans_gravite(self):
        enrs = [dict(e("A", None, True)), dict(e("B", None, False))]
        self.assertIsNone(rapport.erreurs_graves(enrs))
        self.assertEqual(rapport._par_gravite(enrs), [])

    def test_tableau_par_gravite(self):
        enrs = [e("A", "faible", True), e("B", "elevee", False), e("B", "elevee", True, passe=2)]
        texte = "\n".join(rapport._par_gravite(enrs))
        self.assertIn("| faible | 1 | 1 | 100 % | 0 |", texte)
        self.assertIn("| élevée | 1 | 2 | 50 % | 1 |", texte)


class CoutParReussite(unittest.TestCase):
    def test_les_echecs_comptent_dans_le_cout(self):
        enrs = [e("A", "faible", True, cout=1.0), e("B", "faible", False, cout=3.0), e("C", "faible", False, cout=2.0)]
        p = rapport.performance(enrs)
        self.assertAlmostEqual(p["cout_usd_moyen"], 2.0)
        self.assertAlmostEqual(p["cout_usd_par_reussite"], 6.0)

    def test_aucune_reussite(self):
        self.assertIsNone(rapport.performance([e("A", "faible", False, cout=1.0)])["cout_usd_par_reussite"])

    def test_sans_cout(self):
        self.assertIsNone(rapport.performance([e("A", "faible", True)])["cout_usd_par_reussite"])


class IntervalleSurLesTaches(unittest.TestCase):
    def test_taux_par_tache_moyenne_les_passes(self):
        enrs = [e("A", "faible", True, passe=1), e("A", "faible", False, passe=2), e("B", "faible", True)]
        self.assertEqual(rapport.taux_par_tache(enrs), {"A": 0.5, "B": 1.0})

    def test_texte_de_l_intervalle(self):
        enrs = [e(f"T{i}", "faible", i % 2 == 0) for i in range(20)]
        self.assertIn("intervalle de confiance à 95 % sur les tâches : de", rapport.ic_taches(enrs))

    def test_une_seule_tache(self):
        self.assertIn("non calculable", rapport.ic_taches([e("A", "faible", True)]))

    def test_l_intervalle_est_plus_large_que_la_variabilite_entre_passes(self):
        # 5 passes identiques sur 10 taches : aucune variabilite entre passes, mais l'incertitude due aux taches demeure
        enrs = [e(f"T{i}", "faible", i < 7, passe=p) for i in range(10) for p in range(1, 6)]
        self.assertEqual(rapport.ecart_type(rapport.taux_par_passe(enrs)), 0.0)
        m, bas, haut = rapport.statistiques.ic_moyenne(list(rapport.taux_par_tache(enrs).values()))
        self.assertGreater(haut - bas, 0.3)


if __name__ == "__main__":
    unittest.main()
