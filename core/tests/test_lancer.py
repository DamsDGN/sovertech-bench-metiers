import json
import tempfile
import unittest
from pathlib import Path

from core import lancer
from core.client import ErreurClient, Reponse
from core.tests.test_moteur import Oracle

JEUX = lancer.charger_jeux("expert-comptable")
CHAT = {t["consigne"]: t for t in JEUX["chat"]}
RAG = {t["question"]: t for t in JEUX["rag"]}
AGENT = {t["consigne"]: t for t in JEUX["agentique"]}


class FauxModele:
    def __init__(self):
        self.oracle = None
        self.appels = 0

    def infos_serveur(self):
        return {"modele_servi": "RedHatAI/gemma-4-12B-it-NVFP4", "alias": "faux", "contexte_max": 4096}

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None):
        self.appels += 1
        user = messages[1]["content"]
        if outils:
            if len(messages) == 2:
                self.oracle = Oracle(AGENT[user])
            return self.oracle.completer(messages)
        for consigne, t in CHAT.items():
            if user.endswith(consigne):
                return Reponse(texte=t["reponse_modele"], fin="stop", ttft=0.1, duree=0.5, tokens_prompt=50, tokens_completion=20)
        for question, t in RAG.items():
            if "Question : " + question in user:
                return Reponse(texte=t["reponse_modele"], fin="stop", ttft=0.1, duree=0.5, tokens_prompt=80, tokens_completion=30)
        raise AssertionError("prompt inconnu")


class Panne:
    def completer(self, *a, **k):
        raise ErreurClient("serveur injoignable")


def config(**extra):
    base = {"metier": "expert-comptable", "modele_catalogue": "gemma-4-12b-nvfp4-redhatai", "blocs": ["chat", "rag", "agentique"],
            "passes": 2, "taches": [], "limite": 3, "max_tokens": 1000, "prix_horaire": None, "materiel": None,
            "etiquette": None, "pause": 0, "reprise": False}
    base.update(extra)
    return base


def lire(sortie):
    return [json.loads(l) for l in (sortie / "resultats.jsonl").read_text(encoding="utf-8").splitlines()]


class Lanceur(unittest.TestCase):
    def lancer(self, client=None, **extra):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        sortie = Path(self.tmp.name) / "sortie"
        lancer.executer(config(**extra), client or FauxModele(), JEUX, sortie, journal=lambda *_: None)
        return sortie

    def test_enregistre_chaque_execution_et_tout_reussit(self):
        sortie = self.lancer()
        enrs = lire(sortie)
        self.assertEqual(len(enrs), 3 * 3 * 2)
        for e in enrs:
            self.assertIsNone(e["erreur"], e["tache"])
            self.assertTrue(e["reponse"] or e["bloc"] == "agentique")
            self.assertIn("mesures", e)
        self.assertTrue(all(lancer._reussi(e) for e in enrs), [e["tache"] for e in enrs if not lancer._reussi(e)])
        self.assertEqual({e["passe"] for e in enrs}, {1, 2})

    def test_les_passes_sont_enchainees(self):
        enrs = lire(self.lancer())
        self.assertEqual([e["passe"] for e in enrs], [1] * 9 + [2] * 9)

    def test_releve_de_configuration(self):
        releve = json.loads((self.lancer() / "releve.json").read_text(encoding="utf-8"))
        self.assertEqual(releve["modele_catalogue"]["depot_hf"], "RedHatAI/gemma-4-12B-it-NVFP4")
        self.assertEqual(releve["echantillonnage"]["top_k"], 64)
        self.assertEqual(releve["recuperateur"]["methode"], "bm25")
        self.assertIn("empreinte_prompts", releve["moteur"])
        self.assertFalse(releve["comparable_aux_resultats_publies"])
        self.assertIn("materiel", releve["raisons_non_comparable"][0])

    def test_comparable_si_materiel_declare_et_modele_conforme(self):
        releve = json.loads((self.lancer(materiel="carte Blackwell 48 Go") / "releve.json").read_text(encoding="utf-8"))
        self.assertTrue(releve["comparable_aux_resultats_publies"])

    def test_reprise_ne_refait_pas_ce_qui_est_fait(self):
        client = FauxModele()
        sortie = self.lancer(client)
        avant = client.appels
        lancer.executer(config(reprise=True), client, JEUX, sortie, journal=lambda *_: None)
        self.assertEqual(client.appels, avant)
        self.assertEqual(len(lire(sortie)), 18)

    def test_sans_reprise_on_repart_de_zero(self):
        client = FauxModele()
        sortie = self.lancer(client)
        lancer.executer(config(), client, JEUX, sortie, journal=lambda *_: None)
        self.assertEqual(len(lire(sortie)), 18)

    def test_filtre_de_taches_et_de_blocs(self):
        enrs = lire(self.lancer(blocs=["chat"], taches=["CH-01", "CH-02"], limite=0, passes=1))
        self.assertEqual([e["tache"] for e in enrs], ["CH-01", "CH-02"])

    def test_cout_par_tache_si_tarif_fourni(self):
        enrs = lire(self.lancer(blocs=["chat"], limite=1, passes=1, prix_horaire=3600.0))
        self.assertAlmostEqual(enrs[0]["cout"], enrs[0]["mesures"]["duree"], places=6)

    def test_erreur_d_infrastructure_enregistree_et_non_comptee(self):
        sortie = self.lancer(Panne(), blocs=["chat"], limite=2, passes=1)
        enrs = lire(sortie)
        self.assertTrue(all(e["erreur"] for e in enrs))
        self.assertIn("d'infrastructure", (sortie / "rapport.md").read_text(encoding="utf-8"))


class ReprisePuisRapport(unittest.TestCase):
    def test_une_execution_en_erreur_puis_reprise_ne_compte_qu_une_fois(self):
        from core import rapport
        with tempfile.TemporaryDirectory() as tmp:
            sortie = Path(tmp) / "s"
            lancer.executer(config(blocs=["chat"], limite=2, passes=1), Panne(), JEUX, sortie, journal=lambda *_: None)
            self.assertEqual(len(lire(sortie)), 2)
            lancer.executer(config(blocs=["chat"], limite=2, passes=1, reprise=True), FauxModele(), JEUX, sortie, journal=lambda *_: None)
            brut = lire(sortie)
            self.assertEqual(len(brut), 4)
            releve, enrs = rapport.charger(sortie)
            self.assertEqual(len(enrs), 2)
            self.assertTrue(all(e["erreur"] is None for e in enrs))
            self.assertNotIn("d'infrastructure", (sortie / "rapport.md").read_text(encoding="utf-8"))


class Rapport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.sortie = Path(cls.tmp.name) / "s"
        lancer.executer(config(limite=4), FauxModele(), JEUX, cls.sortie, journal=lambda *_: None)
        cls.texte = (cls.sortie / "rapport.md").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_sections_et_avertissements(self):
        for morceau in ("Épreuve « Discuter »", "Épreuve « Chercher dans les dossiers »", "Épreuve « Agir »",
                        "NON comparable", "Limites de ce rapport", "à valider par un professionnel", "écart-type"):
            self.assertIn(morceau, self.texte)

    def test_taux_et_performance(self):
        self.assertIn("100 %", self.texte)
        self.assertIn("débit moyen", self.texte)
        self.assertIn("coût par tâche non calculé", self.texte)

    def test_csv(self):
        lignes = (self.sortie / "resume.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lignes), 4)
        self.assertTrue(lignes[0].startswith("bloc,taches,passes"))


if __name__ == "__main__":
    unittest.main()
