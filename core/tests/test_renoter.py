import copy
import json
import os
import time
import tempfile
import unittest
from pathlib import Path

from core import catalogue, lancer, rapport, renoter

JEUX = lancer.charger_jeux("expert-comptable")
CONFIG = {"metier": "expert-comptable", "max_tokens": 32768, "passes": 1, "blocs": ["chat", "rag", "agentique"]}
TACHE_AG = next(t for t in JEUX["agentique"] if t["id"] == "AG-01")


def tableaux_apres(ecritures):
    tab = copy.deepcopy({k: v["lignes"] for k, v in JEUX["environnement"]["tableaux"].items()})
    for t, l, c, v in ecritures:
        tab[t][l][c] = v
    return tab


def enr(bloc, tache, note, reponse, passe=1, **extra):
    return {"metier": "expert-comptable", "bloc": bloc, "tache": tache, "niveau": "simple", "gravite": "moyenne", "passe": passe,
            "erreur": None, "reponse": reponse, "fin": "stop", "note": note,
            "mesures": {"ttft": 0.1, "duree": 1.0, "appels": 1, "tokens_prompt": 10, "tokens_completion": 10, "debit": 10.0}, **extra}


def mesure(dossier: Path, lignes):
    releve = lancer.construire_releve(CONFIG, catalogue.charger("gemma-4-12b-nvfp4-redhatai"), {}, JEUX)
    releve["moteur"]["commit"] = None
    (dossier / "releve.json").write_text(json.dumps(releve), encoding="utf-8")
    (dossier / "resultats.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes), encoding="utf-8")


def relire(dossier: Path):
    return {(e["tache"], e["passe"]): e for e in map(json.loads, (dossier / "resultats.jsonl").read_text(encoding="utf-8").splitlines())}


class Renoter(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp())
        ecriture = ("suivi_cloture", "Les Épis d'Or", "Date de clôture", "31/12/2026")
        journal = [{"outil": "ecrire_tableau", "arguments": {"tableau": ecriture[0], "ligne": ecriture[1], "colonne": ecriture[2], "valeur": ecriture[3]}, "ok": True}]
        mesure(self.dossier, [
            enr("chat", "CH-02", {"verifications": [], "reussite_auto": False, "juge": None}, "TVA : 240,00 €\nTTC : 1 440,00 €"),
            enr("rag", "RG-03", {"recuperes": ["honoraires-2026", "honoraires-2025"], "reussite_generation": False, "piege_obsolete_tombe": True,
                                 "verifications": [], "citation_ok": True, "rappel": 1.0, "rang_reciproque": 1.0, "juge": None},
                "85 € HT de l'heure en 2026 (contre 80 € en 2025). Source : Taux horaires du cabinet, année 2026", type_question="version_obsolete"),
            enr("agentique", "AG-01", {"reussite": False, "actions_interdites": [], "etapes": 1, "depasse_etapes": False,
                                       "pannes_subies": 0, "reprise_apres_panne": None}, "Fait.",
                journal=journal, brouillons=[], tableaux_finaux=tableaux_apres([ecriture])),
            enr("agentique", "AG-01", {"reussite": False, "actions_interdites": [], "etapes": 1, "depasse_etapes": False,
                                       "pannes_subies": 0, "reprise_apres_panne": None}, "Fait.", passe=2,
                journal=journal, brouillons=[], tableaux_finaux=tableaux_apres([])),
            enr("chat", "CH-999", {"reussite_auto": True}, "Ancienne tâche."),
        ])

    def test_renote_avec_les_grilles_actuelles(self):
        b = renoter.renoter(self.dossier, anciennes=None, recent_ok=True)
        r = relire(self.dossier)
        self.assertTrue(r[("CH-02", 1)]["note"]["reussite_auto"])
        self.assertFalse(r[("RG-03", 1)]["note"]["piege_obsolete_tombe"])
        self.assertTrue(r[("RG-03", 1)]["note"]["reussite_generation"])
        self.assertTrue(r[("AG-01", 1)]["note"]["reussite"])
        self.assertEqual(b["renotees"], 3)
        self.assertEqual(len(b["reussite_changee"]), 3)

    def test_un_rejeu_qui_ne_redonne_pas_l_etat_enregistre_garde_l_ancienne_note(self):
        b = renoter.renoter(self.dossier, anciennes=None, recent_ok=True)
        self.assertEqual(b["rejeu_divergent"], ["AG-01 passe 2"])
        self.assertFalse(relire(self.dossier)[("AG-01", 2)]["note"]["reussite"])

    def test_tableaux_et_lignes_ajoutes_a_l_environnement_depuis_la_mesure(self):
        ecriture = ("suivi_cloture", "Les Épis d'Or", "Date de clôture", "31/12/2026")
        ancien = tableaux_apres([ecriture])
        del ancien["synthese"]
        ancien["suivi_cloture"].pop("Les Mouettes")
        e = enr("agentique", "AG-01", {}, "Fait.", brouillons=[], tableaux_finaux=ancien,
                journal=[{"outil": "ecrire_tableau", "arguments": dict(zip(("tableau", "ligne", "colonne", "valeur"), ecriture)), "ok": True}])
        self.assertTrue(renoter.rejouer(e, TACHE_AG, JEUX)[1])

    def test_une_ligne_ajoutee_depuis_mais_modifiee_au_rejeu_diverge(self):
        ecriture = ("suivi_cloture", "Les Mouettes", "Date de clôture", "31/12/2026")
        ancien = tableaux_apres([])
        ancien["suivi_cloture"].pop("Les Mouettes")
        e = enr("agentique", "AG-01", {}, "Fait.", brouillons=[], tableaux_finaux=ancien,
                journal=[{"outil": "ecrire_tableau", "arguments": dict(zip(("tableau", "ligne", "colonne", "valeur"), ecriture)), "ok": True}])
        self.assertFalse(renoter.rejouer(e, TACHE_AG, JEUX)[1])

    def test_tache_disparue_signalee_et_laissee_telle_quelle(self):
        b = renoter.renoter(self.dossier, anciennes=None, recent_ok=True)
        self.assertEqual(b["tache_absente"], ["CH-999 passe 1"])
        self.assertTrue(relire(self.dossier)[("CH-999", 1)]["note"]["reussite_auto"])

    def test_consigne_changee_depuis_la_mesure_non_renotee(self):
        anciennes = {(b, t["id"]): t for b in renoter.FICHIERS for t in JEUX[b]}
        anciennes[("chat", "CH-02")] = {**anciennes[("chat", "CH-02")], "consigne": "Ancienne consigne."}
        b = renoter.renoter(self.dossier, anciennes=anciennes, recent_ok=True)
        self.assertIn("CH-02 passe 1", b["consigne_modifiee"])
        self.assertFalse(relire(self.dossier)[("CH-02", 1)]["note"]["reussite_auto"])

    def test_sauvegarde_releve_et_rapport(self):
        avant = (self.dossier / "resultats.jsonl").read_text(encoding="utf-8")
        renoter.renoter(self.dossier, anciennes=None, recent_ok=True)
        renoter.renoter(self.dossier, anciennes=None, recent_ok=True)
        self.assertEqual((self.dossier / "resultats.avant-renotage.jsonl").read_text(encoding="utf-8"), avant)
        releve = json.loads((self.dossier / "releve.json").read_text(encoding="utf-8"))
        self.assertEqual(len(releve["renotations"]), 2)
        self.assertFalse(releve["renotations"][0]["consignes_verifiees"])
        self.assertTrue((self.dossier / "rapport.md").exists())

    def test_refuse_une_mesure_peut_etre_en_cours(self):
        maintenant = time.time()
        os.utime(self.dossier / "resultats.jsonl", (maintenant, maintenant))
        with self.assertRaises(renoter.MesureEnCours):
            renoter.renoter(self.dossier, anciennes=None, recent_ok=False)
        self.assertFalse((self.dossier / "resultats.avant-renotage.jsonl").exists())

    def test_seule_la_consigne_vue_par_le_modele_compte(self):
        t = JEUX["chat"][0]
        self.assertFalse(renoter.consigne_modifiee("chat", {**t, "reference": "autre"}, t))
        self.assertTrue(renoter.consigne_modifiee("chat", {**t, "contexte": ["autre"]}, t))


class VoieCli(unittest.TestCase):
    def mesure(self, voie):
        dossier = Path(tempfile.mkdtemp())
        e = enr("agentique", "AG-01", {"reussite": False, "actions_interdites": [], "etapes": 0}, "", journal=[], brouillons=[],
                tableaux_finaux=tableaux_apres([]), tours=[{"fin": "stop", "anomalie": None, "texte": '<invoke name="lire_tableau">'}])
        mesure(dossier, [e])
        releve = json.loads((dossier / "releve.json").read_text(encoding="utf-8"))
        releve["serveur"]["voie"] = voie
        (dossier / "releve.json").write_text(json.dumps(releve), encoding="utf-8")
        b = renoter.renoter(dossier, anciennes=None, recent_ok=True)
        return relire(dossier)[("AG-01", 1)], b

    def test_appel_illisible_par_la_voie_cli_devient_une_erreur_rejouable(self):
        e, b = self.mesure("claude -p (abonnement), session isolee sans outils")
        self.assertIn("voie CLI", e["erreur"])
        self.assertEqual(e["anomalies_serveur"], ["appel_outil_non_analyse"])
        self.assertEqual(b["erreur_voie_cli"], ["AG-01 passe 1"])

    def test_une_reussite_n_est_jamais_ecartee(self):
        dossier = Path(tempfile.mkdtemp())
        ecriture = ("suivi_cloture", "Les Épis d'Or", "Date de clôture", "31/12/2026")
        e = enr("agentique", "AG-01", {"reussite": False}, "Fait.", brouillons=[], tableaux_finaux=tableaux_apres([ecriture]),
                journal=[{"outil": "ecrire_tableau", "arguments": dict(zip(("tableau", "ligne", "colonne", "valeur"), ecriture)), "ok": True}],
                tours=[{"fin": "stop", "anomalie": None, "texte": '<invoke name="lire">'}])
        mesure(dossier, [e])
        releve = json.loads((dossier / "releve.json").read_text(encoding="utf-8"))
        releve["serveur"]["voie"] = "claude -p (abonnement)"
        (dossier / "releve.json").write_text(json.dumps(releve), encoding="utf-8")
        renoter.renoter(dossier, anciennes=None, recent_ok=True)
        r = relire(dossier)[("AG-01", 1)]
        self.assertIsNone(r["erreur"])
        self.assertTrue(r["note"]["reussite"])

    def test_mentionner_le_format_appel_n_est_pas_un_bloc_perdu(self):
        e = enr("agentique", "AG-01", {}, "", tours=[{"fin": "tool_calls", "anomalie": None, "texte": "Oups, mauvais format, j'utilise <appel>."}])
        self.assertEqual(renoter.anomalies_des_tours(e), [])

    def test_un_appel_double_en_invoke_et_en_appel_valide_n_est_pas_une_perte(self):
        e = enr("agentique", "AG-01", {}, "", tours=[{"fin": "tool_calls", "anomalie": None, "texte": '<invoke name="lire_tableau">\n</invoke>'},
                                                     {"fin": "stop", "anomalie": None, "texte": "Fait."}])
        self.assertEqual(renoter.anomalies_des_tours(e), [])

    def test_un_bloc_appel_reste_illisible_est_une_perte_meme_si_d_autres_appels_passent(self):
        e = enr("agentique", "AG-01", {}, "", tours=[{"fin": "tool_calls", "anomalie": None, "texte": 'Je rédige. <appel>{"name": "rediger_mail", "argu'}])
        self.assertEqual(renoter.anomalies_des_tours(e), ["appel_outil_non_analyse"])


        e, b = self.mesure(None)
        self.assertIsNone(e["erreur"])
        self.assertEqual(e["anomalies_serveur"], ["appel_outil_non_analyse"])


class PlafondAgentique(unittest.TestCase):
    def test_une_execution_agentique_coupee_au_plafond_est_comptee(self):
        e = enr("agentique", "AG-01", {"reussite": False}, "", tours=[{"fin": "tool_calls"}, {"fin": "length"}])
        e["fin"] = "termine"
        self.assertEqual(rapport.performance([e])["tronquees"], 1)


if __name__ == "__main__":
    unittest.main()
