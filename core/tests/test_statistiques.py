import math
import unittest

from core import statistiques as s


class IntervalleBootstrap(unittest.TestCase):
    def test_valeurs_identiques_donnent_un_intervalle_nul(self):
        m, bas, haut = s.ic_moyenne([0.5] * 20)
        self.assertEqual((m, bas, haut), (0.5, 0.5, 0.5))

    def test_l_intervalle_contient_la_moyenne_et_se_resserre_avec_plus_de_donnees(self):
        petit = [1.0, 0.0] * 5
        grand = [1.0, 0.0] * 100
        m1, b1, h1 = s.ic_moyenne(petit)
        m2, b2, h2 = s.ic_moyenne(grand)
        self.assertEqual((m1, m2), (0.5, 0.5))
        self.assertTrue(b1 <= m1 <= h1 and b2 <= m2 <= h2)
        self.assertLess(h2 - b2, h1 - b1)

    def test_deterministe(self):
        v = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.5]
        self.assertEqual(s.ic_moyenne(v), s.ic_moyenne(v))

    def test_pas_de_valeur(self):
        self.assertEqual(s.ic_moyenne([]), (None, None, None))

    def test_une_seule_valeur_ne_donne_pas_d_intervalle_fiable(self):
        m, bas, haut = s.ic_moyenne([0.7])
        self.assertEqual((m, bas, haut), (0.7, None, None))


class TestDesSignes(unittest.TestCase):
    def test_dix_contre_zero(self):
        self.assertAlmostEqual(s.test_des_signes(10, 0), 2 * 0.5 ** 10)

    def test_egalite(self):
        self.assertEqual(s.test_des_signes(5, 5), 1.0)

    def test_symetrique(self):
        self.assertEqual(s.test_des_signes(7, 2), s.test_des_signes(2, 7))

    def test_aucune_difference(self):
        self.assertEqual(s.test_des_signes(0, 0), 1.0)

    def test_valeur_connue(self):
        self.assertAlmostEqual(s.test_des_signes(8, 2), 2 * sum(math.comb(10, k) for k in range(0, 3)) / 2 ** 10)


class ComparaisonAppariee(unittest.TestCase):
    def test_difference_constante_demontree(self):
        a = {f"T{i}": 0.0 for i in range(12)}
        b = {f"T{i}": 1.0 for i in range(12)}
        r = s.comparaison_appariee(a, b)
        self.assertEqual((r["n"], r["b_mieux"], r["a_mieux"], r["egales"]), (12, 12, 0, 0))
        self.assertEqual(r["difference"], 1.0)
        self.assertTrue(r["demontree"])
        self.assertLess(r["p_signes"], 0.01)

    def test_bruit_symetrique_non_demontre(self):
        a = {f"T{i}": float(i % 2) for i in range(20)}
        b = {f"T{i}": float((i + 1) % 2) for i in range(20)}
        r = s.comparaison_appariee(a, b)
        self.assertEqual(r["difference"], 0.0)
        self.assertFalse(r["demontree"])

    def test_ne_compare_que_les_taches_communes(self):
        r = s.comparaison_appariee({"A": 1.0, "B": 0.0, "C": 1.0}, {"B": 1.0, "C": 1.0, "D": 0.0})
        self.assertEqual(r["n"], 2)
        self.assertEqual((r["b_mieux"], r["egales"]), (1, 1))

    def test_trop_peu_de_taches(self):
        r = s.comparaison_appariee({"A": 0.0, "B": 0.0}, {"A": 1.0, "B": 1.0})
        self.assertFalse(r["demontree"])
        self.assertTrue(r["trop_peu"])

    def test_difference_moyenne_avec_taux_intermediaires(self):
        r = s.comparaison_appariee({"A": 0.0, "B": 1.0, "C": 0.5}, {"A": 1.0, "B": 1.0, "C": 0.0})
        self.assertAlmostEqual(r["difference"], (1.0 + 0.0 - 0.5) / 3)
        self.assertEqual((r["b_mieux"], r["a_mieux"], r["egales"]), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
