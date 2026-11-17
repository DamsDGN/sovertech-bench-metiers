import datetime
import json
import tempfile
import unittest
from pathlib import Path

from core import catalogue, publication

MAINTENANT = datetime.datetime(2026, 11, 18, 0, 30, tzinfo=datetime.timezone.utc)


def enr(tache, bloc, niveau, gravite, passe, ok, erreur=None, anomalie=False):
    note = {"reussite_auto": ok} if bloc == "chat" else {"reussite_generation": ok, "rappel": 1.0, "rang_reciproque": 1.0, "citation_ok": True,
                                                         "piege_obsolete_tombe": False} if bloc == "rag" else {"reussite": ok, "actions_interdites": [], "etapes": 3,
                                                                                                                  "depasse_etapes": False, "pannes_subies": 0, "reprise_apres_panne": None}
    e = {"tache": tache, "bloc": bloc, "niveau": niveau, "gravite": gravite, "passe": passe, "erreur": erreur, "note": note,
         "fin": "stop", "mesures": {"ttft": 0.2, "debit": 90.0, "duree": 10.0, "tokens_completion": 500}}
    if bloc == "rag":
        e["type_question"] = "reponse_directe"
    if anomalie:
        e["anomalies_serveur"] = ["reponse_vide"]
    return e


def dossier(tmp, enrs, passes=2, comparable=False):
    releve = {"etalon_cloud": False, "date": "2026-11-17T22:21:25+01:00", "metier": "notaire",
              "modele_catalogue": catalogue.charger("gemma-4-12b-nvfp4-redhatai"), "serveur": {"modele_servi": "x", "alias": "sover-llm", "contexte_max": 131072},
              "extraction": {"moteur": "tika"}, "moteur": {"commit": "bb2fb097a4ef72bf64c59f621c4c4607fbaeff8f"}, "recuperateur": {"methode": "bm25", "k": 6},
              "echantillonnage": {"temperature": 1.0}, "max_tokens": 32768, "passes": passes, "materiel_declare": None, "etiquette": "t",
              "comparable_aux_resultats_publies": comparable, "raisons_non_comparable": [] if comparable else ["materiel non declare"]}
    chemin = Path(tmp) / "res"
    chemin.mkdir()
    (chemin / "releve.json").write_text(json.dumps(releve), encoding="utf-8")
    (chemin / "resultats.jsonl").write_text("".join(json.dumps(e) + "\n" for e in enrs), encoding="utf-8")
    return chemin


def jeu():
    enrs = []
    for p in (1, 2):
        enrs += [enr("CH-01", "chat", "simple", "faible", p, True), enr("CH-02", "chat", "complexe", "critique", p, p == 1),
                 enr("RG-01", "rag", "simple", "moyenne", p, True), enr("AG-01", "agentique", "moyen", "elevee", p, p == 2, anomalie=(p == 1)),
                 enr("AG-02", "agentique", "moyen", "elevee", p, True, erreur="reseau" if p == 1 else None)]
    return enrs


class Export(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.export = publication.construire([dossier(self.tmp.name, jeu())], maintenant=MAINTENANT)
        self.gemma = next(m for m in self.export["modeles"] if m["id"] == "gemma-4-12b-nvfp4-redhatai")["metiers"]["notaire"]

    def test_les_modeles_sans_resultat_sont_non_mesures_et_sans_chiffre(self):
        autres = [m for m in self.export["modeles"] if m["id"] != "gemma-4-12b-nvfp4-redhatai"]
        self.assertEqual(len(autres), len(catalogue.lister()) - 1)
        for m in autres:
            self.assertEqual(m["statut"], "non_mesure", m["id"])
            self.assertNotIn("metiers", m)

    def test_les_taux_sont_ceux_des_passes(self):
        chat = self.gemma["epreuves"]["chat"]
        self.assertAlmostEqual(chat["taux"], 0.75)
        self.assertEqual((chat["taches"], chat["passes"], chat["executions"]), (2, 2, 4))
        self.assertIsNotNone(chat["ic95_taches"]["bas"])
        self.assertEqual(chat["par_niveau"]["complexe"]["taux"], 0.5)

    def test_les_erreurs_d_infrastructure_sont_ecartees_et_comptees(self):
        self.assertEqual(self.gemma["erreurs_infrastructure_ecartees"], 1)
        self.assertEqual(self.gemma["epreuves"]["agentique"]["executions"], 3)

    def test_les_taches_graves_et_critiques(self):
        graves = self.gemma["taches_graves"]
        self.assertEqual((graves["executions"], graves["echecs"]), (5, 2))
        self.assertEqual((graves["critiques_executions"], graves["critiques_echecs"]), (2, 1))

    def test_les_anomalies_serveur_sont_attribuees(self):
        anomalies = self.gemma["epreuves"]["agentique"]["anomalies_serveur"]
        self.assertEqual(anomalies, {"passages": 1, "sur": 3, "echecs_concernes": 1, "echecs": 1})

    def test_la_publication_est_refusee_avec_ses_raisons(self):
        raisons = next(m for m in self.export["modeles"] if m["statut"] == "mesure")["raisons_non_publiable"]
        self.assertTrue(any("references non relues" in x for x in raisons))
        self.assertTrue(any("2 passes au lieu de 5" in x for x in raisons))
        self.assertTrue(any("non comparable" in x for x in raisons))

    def test_aucune_trace_interne_dans_l_export(self):
        texte = json.dumps(self.export, ensure_ascii=False).lower()
        for interdit in ("sover.lan", "ai.sover", "atlas", "/home/", "api_key", "bearer"):
            self.assertNotIn(interdit, texte)

    def test_l_export_est_deterministe(self):
        autre = publication.construire([Path(self.tmp.name) / "res"], maintenant=MAINTENANT)
        self.assertEqual(json.dumps(autre, sort_keys=True), json.dumps(self.export, sort_keys=True))

    def test_un_controle_absent_des_anciens_resultats_n_est_pas_exporte_comme_zero(self):
        self.assertIsNone(self.gemma["epreuves"]["agentique"]["passages_avec_destinataire_invente"])

    def test_un_controle_present_est_exporte(self):
        enrs = jeu()
        for e in enrs:
            if e["bloc"] == "agentique":
                e["note"]["destinataires_inventes"] = ["x@invente.fr"] if (e["tache"] == "AG-01" and e["passe"] == 1) else []
        with tempfile.TemporaryDirectory() as tmp:
            export = publication.construire([dossier(tmp, enrs)], maintenant=MAINTENANT)
        agentique = next(m for m in export["modeles"] if m["statut"] == "mesure")["metiers"]["notaire"]["epreuves"]["agentique"]
        self.assertAlmostEqual(agentique["passages_avec_destinataire_invente"], 1 / 3)

    def test_les_etalons_sont_en_dernier_et_non_mesures(self):
        categories = [m["categorie"] for m in self.export["modeles"]]
        self.assertEqual(categories, sorted(categories, key=lambda c: c == "etalon_cloud"))
        self.assertEqual(categories.count("etalon_cloud"), 2)


if __name__ == "__main__":
    unittest.main()
