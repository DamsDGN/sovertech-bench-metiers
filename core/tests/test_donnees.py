import copy
import unittest

from core import donnees as d


def doc(id_, **meta):
    base = {"id": id_, "titre": "Titre", "type": "procedure", "date": "2026-01-15", "statut": "en_vigueur"}
    base.update(meta)
    corps = "DOCUMENT FICTIF\n\nContenu."
    return {"meta": base, "corps": corps}


def erreurs_contiennent(erreurs, morceau):
    return any(morceau in e for e in erreurs)


class Luhn(unittest.TestCase):
    def test_valide_et_invalide(self):
        self.assertTrue(d.luhn_valide("000000018"))
        self.assertFalse(d.luhn_valide("123456789"))

    def test_ignore_les_espaces(self):
        self.assertFalse(d.luhn_valide("123 456 789"))


class ParserDocument(unittest.TestCase):
    def test_entete_et_corps(self):
        meta, corps = d.parser_document("---\nid: a\ntitre: Un titre : avec deux points\n---\nCorps ici\n")
        self.assertEqual(meta, {"id": "a", "titre": "Un titre : avec deux points"})
        self.assertEqual(corps.strip(), "Corps ici")

    def test_sans_entete(self):
        with self.assertRaises(ValueError):
            d.parser_document("Pas d'entete")


class VerifierDocuments(unittest.TestCase):
    def test_corpus_minimal_valide(self):
        docs = {"a": doc("a")}
        self.assertEqual(d.verifier_documents(docs), [])

    def test_champ_manquant(self):
        docs = {"a": doc("a")}
        del docs["a"]["meta"]["statut"]
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "statut"))

    def test_statut_inconnu(self):
        docs = {"a": doc("a", statut="brouillon")}
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "statut"))

    def test_obsolete_doit_pointer_vers_un_document_en_vigueur(self):
        docs = {"a": doc("a", statut="obsolete", remplace_par="b"), "b": doc("b", remplace="a")}
        self.assertEqual(d.verifier_documents(docs), [])
        docs["b"]["meta"]["statut"] = "obsolete"
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "en vigueur"))

    def test_obsolete_sans_remplacant(self):
        docs = {"a": doc("a", statut="obsolete")}
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "remplace_par"))

    def test_remplacant_inexistant(self):
        docs = {"a": doc("a", statut="obsolete", remplace_par="zzz")}
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "zzz"))

    def test_siren_valide_refuse(self):
        docs = {"f": doc("f", type="fiche_client", siren="000000018")}
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "SIREN"))

    def test_siren_invalide_accepte(self):
        docs = {"f": doc("f", type="fiche_client", siren="123456789")}
        self.assertEqual(d.verifier_documents(docs), [])

    def test_courriel_hors_example_refuse(self):
        docs = {"a": doc("a")}
        docs["a"]["corps"] += "\nContact : jean@gmail.com"
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "courriel"))

    def test_courriel_example_accepte(self):
        docs = {"a": doc("a")}
        docs["a"]["corps"] += "\nContact : jean@client.example"
        self.assertEqual(d.verifier_documents(docs), [])

    def test_iban_et_telephone_refuses(self):
        for texte in ["IBAN FR76 3000 6000 0112 3456 7890 189", "Appelez le 06 12 34 56 78", "Tel +33 6 12 34 56 78"]:
            docs = {"a": doc("a")}
            docs["a"]["corps"] += "\n" + texte
            self.assertTrue(d.verifier_documents(docs), texte)

    def test_mot_interdit_fourni_par_l_appelant(self):
        docs = {"a": doc("a")}
        docs["a"]["corps"] += "\nUn motsecret ici"
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs, mots_interdits=["MotSecret"]), "interdit"))
        self.assertEqual(d.verifier_documents(docs), [])

    def test_mots_interdits_lus_dans_un_fichier_local(self):
        import tempfile, pathlib
        with tempfile.TemporaryDirectory() as tmp:
            f = pathlib.Path(tmp) / "mots.txt"
            f.write_text("# commentaire\nPremier\n\nSecond\n", encoding="utf-8")
            self.assertEqual(d.lire_mots_interdits(f), ["Premier", "Second"])
            self.assertEqual(d.lire_mots_interdits(pathlib.Path(tmp) / "absent.txt"), [])

    def test_bandeau_fictif_obligatoire_hors_texte_public(self):
        docs = {"a": doc("a")}
        docs["a"]["corps"] = "Contenu sans bandeau"
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "DOCUMENT FICTIF"))

    def test_texte_public_demande_une_source(self):
        docs = {"p": doc("p", type="texte_public")}
        docs["p"]["corps"] = "Contenu public"
        self.assertTrue(erreurs_contiennent(d.verifier_documents(docs), "source_publique"))
        docs["p"]["meta"]["source_publique"] = "Code de commerce"
        self.assertEqual(d.verifier_documents(docs), [])


def tache_commune(id_, **extra):
    base = {
        "id": id_, "theme": "redaction", "niveau": "simple", "gravite": "moyenne",
        "a_valider_par_pro": True,
        "statut_validation": {"relu_par": None, "date": None, "commentaire": None},
        "source_publique": [], "incertitude": None,
    }
    base.update(extra)
    return base


def tache_chat(id_="CH-01", **extra):
    return tache_commune(
        id_, bloc="chat", consigne="Réponds.", contexte=[], reference="Attendu.",
        abstention_attendue=False,
        verifications=[{"type": "contient_un_de", "valeurs": ["bonjour"]}],
        criteres_juge=["Français correct"],
        reponse_modele="Bonjour à tous.",
        **extra,
    )


class VerifierChat(unittest.TestCase):
    def setUp(self):
        self.docs = {"a": doc("a")}

    def test_gravite_obligatoire_et_connue(self):
        for valeur in (None, "enorme"):
            t = tache_chat()
            t["gravite"] = valeur
            self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "gravite"))
        for valeur in d.GRAVITES:
            t = tache_chat()
            t["gravite"] = valeur
            self.assertEqual(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), [])

    def test_tache_valide(self):
        self.assertEqual(d.verifier_taches_chat([tache_chat()], self.docs, bornes=(1, 5)), [])

    def test_bornes(self):
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([tache_chat()], self.docs, bornes=(2, 5)), "nombre"))

    def test_identifiant_en_double(self):
        erreurs = d.verifier_taches_chat([tache_chat(), tache_chat()], self.docs, bornes=(1, 5))
        self.assertTrue(erreurs_contiennent(erreurs, "double"))

    def test_identifiant_mal_forme(self):
        erreurs = d.verifier_taches_chat([tache_chat("XX-1")], self.docs, bornes=(1, 5))
        self.assertTrue(erreurs_contiennent(erreurs, "identifiant"))

    def test_a_valider_obligatoire_sans_relecture(self):
        t = tache_chat()
        t["a_valider_par_pro"] = False
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "relu_par"))

    def test_validee_avec_relecteur(self):
        t = tache_chat()
        t["a_valider_par_pro"] = False
        t["statut_validation"] = {"relu_par": "Mme X", "date": "2026-12-01", "commentaire": ""}
        self.assertEqual(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), [])

    def test_document_de_contexte_inexistant(self):
        t = tache_chat()
        t["contexte"] = ["zzz"]
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "zzz"))

    def test_verification_inconnue(self):
        t = tache_chat()
        t["verifications"] = [{"type": "magique"}]
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "magique"))

    def test_champ_de_verification_manquant(self):
        t = tache_chat()
        t["verifications"] = [{"type": "mots_max"}]
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "max"))

    def test_la_reponse_modele_doit_passer_ses_verifications(self):
        t = tache_chat()
        t["reponse_modele"] = "Salut."
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "reponse_modele"))

    def test_la_reponse_fautive_doit_echouer(self):
        t = tache_chat()
        t["reponse_fautive"] = "Bonjour encore."
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "reponse_fautive"))
        t["reponse_fautive"] = "Salut."
        self.assertEqual(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), [])

    def test_abstention_attendue_exige_la_verification(self):
        t = tache_chat()
        t["abstention_attendue"] = True
        self.assertTrue(erreurs_contiennent(d.verifier_taches_chat([t], self.docs, bornes=(1, 5)), "abstention"))


def question_rag(id_="RG-01", **extra):
    base = tache_commune(
        id_, bloc="rag", question="Quel délai ?", type_question="reponse_directe",
        documents_attendus=["a"], documents_pieges=[], reference="45 jours.",
        verifications=[{"type": "contient_un_de", "valeurs": ["45"]}], reponse_modele="45 jours.",
        elements_documents=["45 jours"], valeurs_obsoletes=[], criteres_juge=[],
        abstention_attendue=False,
    )
    base.update(extra)
    return base


ABST = [{"type": "abstention", "attendue": True}]
REP_ABST = "Je ne sais pas, cela ne figure pas dans les documents."


class VerifierRag(unittest.TestCase):
    def setUp(self):
        self.docs = {"a": doc("a"), "b": doc("b")}
        self.docs["a"]["corps"] += "\nLe délai est de 45 jours."

    def test_valide(self):
        self.assertEqual(d.verifier_questions_rag([question_rag()], self.docs, bornes=(1, 5)), [])

    def test_element_absent_des_documents(self):
        q = question_rag(elements_documents=["99 jours"])
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "99 jours"))

    def test_sans_reponse_ne_cite_aucun_document(self):
        q = question_rag(type_question="sans_reponse", documents_attendus=["a"], abstention_attendue=True,
                         verifications=ABST, reponse_modele=REP_ABST, elements_documents=[])
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "sans_reponse"))
        q["documents_attendus"] = []
        self.assertEqual(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), [])

    def test_reponse_partielle_cite_un_document_et_exige_l_abstention(self):
        q = question_rag(type_question="reponse_partielle", abstention_attendue=True,
                         verifications=[{"type": "contient_un_de", "valeurs": ["45"]}] + ABST,
                         reponse_modele="45 jours, mais le reste ne figure pas dans les documents.")
        self.assertEqual(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), [])
        q["documents_attendus"] = []
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "aucun document"))

    def test_sans_reponse_exige_l_abstention(self):
        q = question_rag(type_question="sans_reponse", documents_attendus=[], abstention_attendue=False,
                         verifications=ABST, reponse_modele=REP_ABST, elements_documents=[])
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "abstention"))

    def test_version_obsolete_exige_un_piege_obsolete(self):
        self.docs["b"]["meta"]["statut"] = "obsolete"
        self.docs["b"]["meta"]["remplace_par"] = "a"
        q = question_rag(type_question="version_obsolete", valeurs_obsoletes=["30 jours"], documents_pieges=["b"])
        self.assertEqual(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), [])
        q["documents_pieges"] = []
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "version_obsolete"))

    def test_document_attendu_en_vigueur_pour_une_version_obsolete(self):
        self.docs["a"]["meta"]["statut"] = "obsolete"
        self.docs["a"]["meta"]["remplace_par"] = "b"
        q = question_rag(type_question="version_obsolete", valeurs_obsoletes=["30 jours"], documents_pieges=["b"])
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "en vigueur"))

    def test_contradiction_et_plusieurs_documents_demandent_deux_documents(self):
        for type_q in ("contradiction", "plusieurs_documents"):
            q = question_rag(type_question=type_q)
            self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), type_q))

    def test_la_reponse_modele_doit_passer_les_verifications(self):
        q = question_rag(reponse_modele="Trente jours.")
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "reponse_modele"))

    def test_document_inexistant(self):
        q = question_rag(documents_attendus=["zzz"])
        self.assertTrue(erreurs_contiennent(d.verifier_questions_rag([q], self.docs, bornes=(1, 5)), "zzz"))


ENV = {
    "tableaux": {
        "suivi_cloture": {
            "colonnes": ["Date de clôture", "Date de relance", "Statut"],
            "lignes": {"Client A": {"Date de clôture": "", "Date de relance": "", "Statut": ""}},
            "colonnes_modifiables": ["Date de clôture", "Date de relance", "Statut"],
        },
    },
    "documents_interdits": ["secret"],
}


def tache_ag(id_="AG-01", **extra):
    base = tache_commune(
        id_, bloc="agentique", consigne="Remplis.", etapes_max=5,
        outils_attendus=["lire", "ecrire_tableau"],
        etat_final_attendu={
            "tableaux": {"suivi_cloture": {"Client A": {"Date de clôture": "31/12/2026"}}},
            "brouillons": [], "envois": 0,
        },
        actions_interdites=["envoyer_mail"], pannes=[], message_final_attendu=None,
    )
    base.update(extra)
    return base


class VerifierAgentique(unittest.TestCase):
    def setUp(self):
        self.docs = {"fiche-a": doc("fiche-a", type="fiche_client", client="Client A",
                                    cloture_jour_mois="31/12", exercice_en_cours="2026", forfait_annuel_ht="4800")}

    def test_valide(self):
        self.assertEqual(d.verifier_taches_agentique([tache_ag()], self.docs, ENV, bornes=(1, 5)), [])

    def test_cellule_inexistante(self):
        t = tache_ag()
        t["etat_final_attendu"]["tableaux"]["suivi_cloture"]["Client A"] = {"Colonne fantome": "x"}
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "Colonne fantome"))

    def test_valeur_attendue_coherente_avec_la_fiche(self):
        t = tache_ag()
        t["etat_final_attendu"]["tableaux"]["suivi_cloture"]["Client A"] = {"Date de clôture": "30/06/2026"}
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "fiche"))

    def test_date_de_relance_est_la_cloture_moins_45_jours(self):
        t = tache_ag()
        t["etat_final_attendu"]["tableaux"]["suivi_cloture"]["Client A"] = {"Date de relance": "16/11/2026"}
        self.assertEqual(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), [])
        t["etat_final_attendu"]["tableaux"]["suivi_cloture"]["Client A"] = {"Date de relance": "15/11/2026"}
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "45"))

    def test_outil_attendu_inconnu(self):
        t = tache_ag(outils_attendus=["teleporter"])
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "teleporter"))

    def test_action_interdite_inconnue(self):
        t = tache_ag(actions_interdites=["lire:inexistant"])
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "inexistant"))

    def test_lecture_interdite_valide(self):
        t = tache_ag(actions_interdites=["envoyer_mail", "lire:secret"])
        self.assertEqual(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), [])

    def test_etapes_max_positif(self):
        t = tache_ag(etapes_max=0)
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "etapes_max"))

    def test_panne_sur_un_outil_inconnu(self):
        t = tache_ag(pannes=[{"outil": "teleporter", "echecs": 1}])
        self.assertTrue(erreurs_contiennent(d.verifier_taches_agentique([t], self.docs, ENV, bornes=(1, 5)), "teleporter"))


class JeuxReels(unittest.TestCase):
    def test_les_jeux_expert_comptable_sont_valides(self):
        erreurs = d.verifier_metier("expert-comptable")
        self.assertEqual(erreurs, [], "\n".join(erreurs))

    def test_chaque_tache_a_une_gravite_proposee(self):
        jeux = d.charger_metier("expert-comptable")
        for bloc in ("chat", "rag", "agentique"):
            for t in jeux[bloc]:
                self.assertIn(t["gravite"], d.GRAVITES, t["id"])

    def test_les_taches_critiques_sont_celles_d_actions_non_autorisees_ou_d_affirmation_reglementaire(self):
        jeux = d.charger_metier("expert-comptable")
        critiques = sorted(t["id"] for b in ("chat", "rag", "agentique") for t in jeux[b] if t["gravite"] == "critique")
        self.assertEqual(critiques, ["AG-06", "AG-08", "AG-17", "AG-28", "AG-29", "CH-15"])

    def test_effectifs_de_la_v0(self):
        jeux = d.charger_metier("expert-comptable")
        self.assertEqual((len(jeux["chat"]), len(jeux["rag"]), len(jeux["agentique"])), (32, 29, 30))


if __name__ == "__main__":
    unittest.main()
