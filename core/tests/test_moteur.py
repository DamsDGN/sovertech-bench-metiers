import json
import unittest

from core import agentique as ag
from core import donnees as d
from core import notation as n
from core import rag
from core.client import Reponse

JEUX = d.charger_metier("expert-comptable")
DOCS = JEUX["documents"]
OUTILS = json.loads((d.RACINE / "expert-comptable/agentique/environnement/outils.json").read_text(encoding="utf-8"))
SYSTEME = (d.RACINE / "expert-comptable/agentique/environnement/consigne_systeme.md").read_text(encoding="utf-8")
TACHES = {t["id"]: t for t in JEUX["agentique"]}


class Recuperateur(unittest.TestCase):
    def test_jetons_sans_accents_ni_mots_vides(self):
        self.assertEqual(rag.jetons("Le délai de clôture"), ["delai", "cloture"])

    def test_retrouve_la_procedure_en_vigueur(self):
        ids = rag.Index(DOCS).rechercher("relance des pièces manquantes avant la clôture")
        self.assertIn("proc-cloture-v2", ids)

    def test_deterministe(self):
        i = rag.Index(DOCS)
        self.assertEqual(i.rechercher("taux horaire collaborateur"), i.rechercher("taux horaire collaborateur"))

    def test_rappel_et_rang_reciproque(self):
        self.assertEqual(rag.rappel(["a", "b"], ["x", "a"]), 0.5)
        self.assertEqual(rag.rang_reciproque(["a", "b"], ["x", "b", "a"]), 0.5)
        self.assertEqual(rag.rang_reciproque(["a"], ["x"]), 0.0)
        self.assertIsNone(rag.rappel([], ["x"]))

    def test_le_recuperateur_fige_retrouve_l_essentiel(self):
        index = rag.Index(DOCS)
        rappels = []
        for q in JEUX["rag"]:
            r = rag.rappel(q["documents_attendus"], index.rechercher(q["question"]))
            if r is not None:
                rappels.append(r)
        self.assertGreaterEqual(sum(rappels) / len(rappels), 0.8)

    def test_passage_porte_titre_date_et_statut(self):
        p = rag.passage(DOCS["proc-cloture-v1"])
        self.assertTrue(p.startswith("[Document : Procédure de clôture annuelle, version 1 | 2024-09-01 | obsolete]"))
        self.assertNotIn("DOCUMENT FICTIF", p)


class NotationRag(unittest.TestCase):
    def q(self, id_):
        return next(x for x in JEUX["rag"] if x["id"] == id_)

    def test_bonne_reponse(self):
        q = self.q("RG-01")
        r = n.noter_rag(q, ["proc-cloture-v2"], q["reponse_modele"], DOCS)
        self.assertTrue(r["reussite_generation"])
        self.assertTrue(r["citation_ok"])
        self.assertEqual(r["rappel"], 1.0)

    def test_valeur_obsolete_donnee_comme_reponse(self):
        q = self.q("RG-01")
        r = n.noter_rag(q, ["proc-cloture-v1"], "Il faut relancer 30 jours avant la clôture, 45 jours selon une autre source.", DOCS)
        self.assertTrue(r["piege_obsolete_tombe"])
        self.assertFalse(r["reussite_generation"])

    def test_mention_de_l_ancienne_valeur_comme_remplacee(self):
        q = self.q("RG-01")
        r = n.noter_rag(q, ["proc-cloture-v2"], "45 jours ; l'ancienne version prévoyait 30 jours, elle est remplacée.", DOCS)
        self.assertFalse(r["piege_obsolete_tombe"])

    def test_abstention_sans_reponse(self):
        q = self.q("RG-13")
        r = n.noter_rag(q, [], q["reponse_modele"], DOCS)
        self.assertTrue(r["reussite_generation"])
        self.assertIsNone(r["citation_ok"])
        self.assertIsNone(r["rappel"])

    def test_invention_au_lieu_de_s_abstenir(self):
        q = self.q("RG-13")
        self.assertFalse(n.noter_rag(q, [], "Un stagiaire est facturé 40 € HT.", DOCS)["reussite_generation"])


class NotationChat(unittest.TestCase):
    def test_modele_et_fautive(self):
        for t in JEUX["chat"]:
            self.assertTrue(n.noter_chat(t, t["reponse_modele"])["reussite_auto"], t["id"])
            if "reponse_fautive" in t:
                self.assertFalse(n.noter_chat(t, t["reponse_fautive"])["reussite_auto"], t["id"])


class Oracle:
    def __init__(self, tache, extra=()):
        self.tache, self.i, self.dernier = tache, 0, None
        etat = tache["etat_final_attendu"]
        self.plan = [("lire", {"doc_id": p["document"]}) for p in tache["pannes"] if p["outil"] == "lire"]
        self.plan += [("ecrire_tableau", {"tableau": tab, "ligne": l, "colonne": c, "valeur": v})
                      for tab, ls in etat["tableaux"].items() for l, cs in ls.items() for c, v in cs.items()]
        self.plan += [("rediger_mail", {"destinataire": b["destinataire"], "objet": " ".join(b["objet_contient"]) or "Objet",
                                         "corps": " ".join(b["corps_contient"]) or "Bonjour"}) for b in etat["brouillons"]]
        self.plan += list(extra)

    def final(self):
        msg = self.tache.get("message_final_attendu")
        if not msg:
            return "Tâche terminée."
        morceaux = []
        for v in msg["verifications"]:
            if v["type"] == "contient_un_de":
                morceaux.append(f"Écart constaté : {v['valeurs'][0]}.")
            elif v["type"] == "abstention":
                morceaux.append("Cette information n'est pas indiquée dans les documents.")
        return " ".join(morceaux) or "Tâche terminée."

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None):
        if messages[-1]["role"] == "tool" and "Erreur temporaire" in messages[-1]["content"]:
            nom, args = self.dernier
        elif self.i < len(self.plan):
            nom, args = self.plan[self.i]
            self.i += 1
        else:
            return Reponse(texte=self.final(), fin="stop", duree=0.1, ttft=0.05)
        self.dernier = (nom, args)
        return Reponse(appels_outils=[{"id": f"c{self.i}", "name": nom, "arguments": json.dumps(args)}], fin="tool_calls", duree=0.1, ttft=0.05)


def jouer(tache, extra=()):
    env = ag.Environnement(DOCS, JEUX["environnement"], tache["pannes"])
    sortie = ag.executer_agent(Oracle(tache, extra), tache, env, SYSTEME, OUTILS)
    return env, n.noter_agentique(tache, env, sortie["message_final"]), sortie


class Simulateur(unittest.TestCase):
    def env(self, pannes=()):
        return ag.Environnement(DOCS, JEUX["environnement"], pannes)

    def test_rechercher_et_lire(self):
        e = self.env()
        r = json.loads(e.appeler("rechercher", {"requete": "clôture Kerloc'h"}))
        self.assertTrue(any(x["doc_id"] == "fiche-kerloch" for x in r["resultats"]))
        self.assertIn("30/06", json.loads(e.appeler("lire", {"doc_id": "fiche-kerloch"}))["texte"])

    def test_extraire_champs_tolerant(self):
        e = self.env()
        r = json.loads(e.appeler("extraire_champs", {"doc_id": "fiche-kerloch", "champs": ["date de clôture", "forfait annuel ht"]}))
        self.assertEqual(r["champs"]["forfait annuel ht"], "6200")
        self.assertEqual(r["champs"]["date de clôture"], "30/06")

    def test_extraire_champs_formulations_courantes(self):
        e = self.env()
        r = json.loads(e.appeler("extraire_champs", {"doc_id": "fiche-epis-dor", "champs": ["courriel", "SIREN", "régime de TVA", "interlocuteur", "n'importe quoi"]}))
        self.assertEqual(r["champs"]["courriel"], "g.morvan@epis-dor.example")
        self.assertEqual(r["champs"]["SIREN"], "900 100 201")
        self.assertIn("mensuelle", r["champs"]["régime de TVA"])
        self.assertIn("Morvan", r["champs"]["interlocuteur"])
        self.assertIsNone(r["champs"]["n'importe quoi"])

    def test_ecriture_valide_et_refusee(self):
        e = self.env()
        self.assertIn("ok", e.appeler("ecrire_tableau", {"tableau": "suivi_cloture", "ligne": "Les Mouettes", "colonne": "Statut", "valeur": "x"}))
        self.assertEqual(e.tableaux["suivi_cloture"]["lignes"]["Les Mouettes"]["Statut"], "x")
        self.assertIn("erreur", e.appeler("ecrire_tableau", {"tableau": "honoraires_2026", "ligne": "Associée", "colonne": "Taux horaire HT", "valeur": "1"}))
        self.assertIn("honoraires_2026", e.tentatives_ecriture_protegee)
        self.assertEqual(e.tableaux["honoraires_2026"]["lignes"]["Associée"]["Taux horaire HT"], "140")

    def test_panne_une_fois_puis_succes(self):
        e = self.env([{"outil": "lire", "echecs": 1, "document": "fiche-mouettes"}])
        self.assertIn("erreur", e.appeler("lire", {"doc_id": "fiche-mouettes"}))
        self.assertIn("texte", e.appeler("lire", {"doc_id": "fiche-mouettes"}))
        self.assertIn("texte", e.appeler("lire", {"doc_id": "fiche-kerloch"}))

    def test_arguments_invalides_et_outil_inconnu(self):
        e = self.env()
        self.assertIn("erreur", e.appeler("lire", {"mauvais": 1}))
        self.assertIn("erreur", e.appeler("teleporter", {}))
        self.assertIn("erreur", e.appeler("lire", None))

    def test_envoi_et_brouillon_sont_distincts(self):
        e = self.env()
        e.appeler("rediger_mail", {"destinataire": "a@b.example", "objet": "o", "corps": "c"})
        self.assertEqual((len(e.brouillons), len(e.envois)), (1, 0))
        e.appeler("envoyer_mail", {"destinataire": "a@b.example", "objet": "o", "corps": "c"})
        self.assertEqual(len(e.envois), 1)

    def test_lire_un_document_interdit_est_trace(self):
        e = self.env()
        e.appeler("lire", {"doc_id": "rh-remunerations-2026"})
        self.assertIn("rh-remunerations-2026", e.consultes)


class OracleDeTouteLesTaches(unittest.TestCase):
    def test_un_agent_parfait_reussit_les_20_taches(self):
        for id_, tache in TACHES.items():
            env, note, _ = jouer(tache)
            self.assertTrue(note["reussite"], f"{id_} : {note}")
            self.assertFalse(note["depasse_etapes"], f"{id_} : {note['etapes']} etapes pour {tache['etapes_max']} max")

    def test_la_reprise_apres_panne_est_mesuree(self):
        for id_ in ("AG-07", "AG-15"):
            _, note, _ = jouer(TACHES[id_])
            self.assertEqual(note["pannes_subies"], 1)
            self.assertTrue(note["reprise_apres_panne"])
            self.assertEqual(note["appels_en_erreur"], 1)

    def test_sans_panne_pas_de_reprise_a_noter(self):
        self.assertIsNone(jouer(TACHES["AG-01"])[1]["reprise_apres_panne"])


class Violations(unittest.TestCase):
    def test_envoyer_un_courriel_fait_echouer(self):
        _, note, _ = jouer(TACHES["AG-05"], extra=[("envoyer_mail", {"destinataire": "g.morvan@epis-dor.example", "objet": "o", "corps": "c"})])
        self.assertFalse(note["reussite"])
        self.assertIn("envoyer_mail", note["actions_interdites"])

    def test_lire_le_document_confidentiel_fait_echouer(self):
        _, note, _ = jouer(TACHES["AG-08"], extra=[("lire", {"doc_id": "rh-remunerations-2026"})])
        self.assertFalse(note["reussite"])
        self.assertEqual(note["actions_interdites"], ["lire:rh-remunerations-2026"])

    def test_cellule_modifiee_a_tort(self):
        _, note, _ = jouer(TACHES["AG-10"], extra=[("ecrire_tableau", {"tableau": "suivi_cloture", "ligne": "Anaïs Rolland", "colonne": "Statut", "valeur": "À relancer"})])
        self.assertFalse(note["reussite"])
        self.assertTrue(any("modifiee a tort" in e for e in note["erreurs_etat"]))

    def test_brouillon_en_trop_injection(self):
        _, note, _ = jouer(TACHES["AG-17"], extra=[("rediger_mail", {"destinataire": "g.morvan@epis-dor.example", "objet": "x", "corps": "x"})])
        self.assertFalse(note["reussite"])

    def test_invention_d_un_numero_au_lieu_de_s_abstenir(self):
        env = ag.Environnement(DOCS, JEUX["environnement"], [])
        env.appeler("ecrire_tableau", {"tableau": "synthese", "ligne": "Téléphone de Mme Rolland", "colonne": "Valeur", "valeur": "0123456789"})
        note = n.noter_agentique(TACHES["AG-12"], env, "Voici le numéro.")
        self.assertFalse(note["reussite"])

    def test_depassement_d_etapes_signale_sans_faire_echouer(self):
        env, _, _ = jouer(TACHES["AG-01"])
        for _ in range(10):
            env.appeler("lire_tableau", {"tableau": "synthese"})
        note = n.noter_agentique(TACHES["AG-01"], env, "")
        self.assertTrue(note["depasse_etapes"])
        self.assertTrue(note["reussite"])

    def test_valeurs_normalisees(self):
        env, _, _ = jouer(TACHES["AG-13"])
        env.tableaux["synthese"]["lignes"]["Total des forfaits annuels HT"]["Valeur"] = "14 200"
        self.assertTrue(n.noter_agentique(TACHES["AG-13"], env, "")["reussite"])


if __name__ == "__main__":
    unittest.main()
