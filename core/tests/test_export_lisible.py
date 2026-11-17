import unittest

from core import donnees as d
from core import export_lisible as e

VERIFS = [
    {"type": "contient_un_de", "valeurs": ["a", "b"]}, {"type": "ne_contient_aucun", "valeurs": ["x"]},
    {"type": "mots_max", "max": 5}, {"type": "puces", "exact": 3}, {"type": "liste_numerotee", "exact": 5},
    {"type": "reponse_exacte", "valeurs": ["oui"]}, {"type": "aucun_nombre_a_n_chiffres", "n": 9},
    {"type": "tableau_markdown", "colonnes": 3, "lignes": 3},
    {"type": "abstention", "attendue": True}, {"type": "abstention", "attendue": False},
]


class DecrireVerification(unittest.TestCase):
    def test_chaque_type_a_une_description_en_francais(self):
        for v in VERIFS:
            self.assertTrue(e.decrire_verification(v))

    def test_tous_les_types_sont_couverts(self):
        from core import verifications as vf
        self.assertEqual({v["type"] for v in VERIFS}, set(vf.TYPES))


class Themes(unittest.TestCase):
    def test_tous_les_themes_utilises_ont_un_libelle(self):
        jeux = d.charger_metier("expert-comptable")
        utilises = {t["theme"] for b in ("chat", "rag", "agentique") for t in jeux[b]}
        self.assertEqual(utilises - set(e.THEMES), set())


class FichiersGeneres(unittest.TestCase):
    def test_les_taches_md_versionnes_sont_a_jour(self):
        for chemin, texte in e.generer("expert-comptable").items():
            self.assertTrue(chemin.exists(), f"{chemin.name} manquant : lancer python3 -m core.export_lisible")
            self.assertEqual(chemin.read_text(encoding="utf-8"), texte,
                             f"{chemin.parent.name}/TACHES.md n'est pas a jour : lancer python3 -m core.export_lisible")

    def test_chaque_tache_apparait_dans_son_fichier(self):
        jeux = d.charger_metier("expert-comptable")
        sorties = {c.parent.name: t for c, t in e.generer("expert-comptable").items()}
        for bloc in ("chat", "rag", "agentique"):
            for tache in jeux[bloc]:
                self.assertIn(f"## {tache['id']} ", sorties[bloc])


if __name__ == "__main__":
    unittest.main()
