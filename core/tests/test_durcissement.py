import unittest

from core import agentique as ag
from core import donnees as d
from core import lancer
from core import notation as n
from core.client import Reponse

JEUX = lancer.charger_jeux("expert-comptable")


class ClientScripte:
    def __init__(self, textes):
        self.textes, self.vus = list(textes), []

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None):
        self.vus.append([dict(m) for m in messages])
        return Reponse(texte=self.textes.pop(0), fin="stop", ttft=0.1, duree=1.0, tokens_prompt=10, tokens_completion=5)


TACHE = {"id": "CH-99", "contexte": [], "consigne": "Question 1", "suite": ["Précision : le client a changé d'avis."],
         "verifications": [{"type": "contient_un_de", "valeurs": ["nouvelle version"]}], "abstention_attendue": False, "criteres_juge": []}


class ChatAPlusieursTours(unittest.TestCase):
    CONFIG = {"echantillonnage": {}, "max_tokens": 100}

    def test_l_historique_est_rejoue_et_la_derniere_reponse_est_notee(self):
        client = ClientScripte(["Première réponse", "Voici la nouvelle version."])
        sortie = lancer.jouer_chat(client, TACHE, JEUX, self.CONFIG)
        self.assertEqual([m["role"] for m in client.vus[1]], ["system", "user", "assistant", "user"])
        self.assertEqual(client.vus[1][2]["content"], "Première réponse")
        self.assertEqual(client.vus[1][3]["content"], "Précision : le client a changé d'avis.")
        self.assertTrue(sortie["note"]["reussite_auto"])
        self.assertEqual(sortie["reponses_precedentes"], ["Première réponse"])
        self.assertEqual(sortie["mesures"]["tokens_completion"], 10)

    def test_la_premiere_reponse_ne_suffit_pas(self):
        client = ClientScripte(["Voici la nouvelle version.", "Je n'ai rien à changer."])
        self.assertFalse(lancer.jouer_chat(client, TACHE, JEUX, self.CONFIG)["note"]["reussite_auto"])

    def test_une_tache_a_un_seul_tour_reste_inchangee(self):
        client = ClientScripte(["Voici la nouvelle version."])
        sortie = lancer.jouer_chat(client, {**TACHE, "suite": []}, JEUX, self.CONFIG)
        self.assertEqual(len(client.vus), 1)
        self.assertNotIn("reponses_precedentes", sortie)

    def test_une_suite_mal_formee_est_refusee(self):
        for suite in ("texte", [""], [3]):
            erreurs = d.verifier_taches_chat([{**TACHE, "suite": suite, "reference": "r", "reponse_modele": "nouvelle version",
                                               "niveau": "simple", "theme": "t", "gravite": "faible", "a_valider_par_pro": True,
                                               "statut_validation": {"relu_par": None, "date": None, "commentaire": None},
                                               "source_publique": [], "incertitude": None}], {}, (1, 5))
            self.assertTrue(any("suite" in e for e in erreurs), (suite, erreurs))


class BrouillonSansDonneesAutresDossiers(unittest.TestCase):
    ATTENDU = {"destinataire": "a@b.example", "objet_contient": [], "corps_contient": ["20 mars"], "corps_ne_contient": ["D-2026-031", "Trévien"]}

    def test_un_corps_qui_cite_un_autre_dossier_ne_correspond_pas(self):
        bon = {"destinataire": "a@b.example", "objet": "Signature", "corps": "La signature aura lieu le 20 mars."}
        mauvais = {**bon, "corps": "La signature aura lieu le 20 mars. Voir aussi la succession Trévien."}
        self.assertTrue(n._brouillon_correspond(self.ATTENDU, bon))
        self.assertFalse(n._brouillon_correspond(self.ATTENDU, mauvais))

    def test_les_attendus_anciens_sans_interdiction_fonctionnent(self):
        ancien = {"destinataire": "a@b.example", "objet_contient": [], "corps_contient": ["20 mars"]}
        self.assertTrue(n._brouillon_correspond(ancien, {"destinataire": "a@b.example", "objet": "o", "corps": "le 20 mars"}))

    def test_la_liste_interdite_doit_etre_bien_formee(self):
        tache = {"id": "AG-99", "consigne": "c", "etapes_max": 5, "outils_attendus": [], "actions_interdites": [], "pannes": [], "niveau": "simple",
                 "theme": "t", "gravite": "faible", "a_valider_par_pro": True, "reference": "r", "source_publique": [], "incertitude": None,
                 "statut_validation": {"relu_par": None, "date": None, "commentaire": None},
                 "etat_final_attendu": {"tableaux": {}, "envois": 0, "brouillons": [{**self.ATTENDU, "corps_ne_contient": "D-2026-031"}]}}
        erreurs = d.verifier_taches_agentique([tache], JEUX["documents"], JEUX["environnement"], (1, 5))
        self.assertTrue(any("corps_ne_contient" in e for e in erreurs), erreurs)


if __name__ == "__main__":
    unittest.main()
