import unittest

from core import verifications as v


def ok(verif, reponse):
    return v.evaluer(verif, reponse)


class ContientUnDe(unittest.TestCase):
    def test_trouve_sans_tenir_compte_de_la_casse(self):
        self.assertTrue(ok({"type": "contient_un_de", "valeurs": ["relevés bancaires"]}, "Merci d'envoyer vos Relevés Bancaires."))

    def test_une_seule_alternative_suffit(self):
        self.assertTrue(ok({"type": "contient_un_de", "valeurs": ["1 500", "1500"]}, "Le TTC est de 1500,00 €."))

    def test_espaces_insecables_equivalents_aux_espaces(self):
        self.assertTrue(ok({"type": "contient_un_de", "valeurs": ["6 440,50"]}, "L'écart est de 6 440,50 €."))
        self.assertTrue(ok({"type": "contient_un_de", "valeurs": ["6 440,50"]}, "L'écart est de 6 440,50 €."))

    def test_absent(self):
        self.assertFalse(ok({"type": "contient_un_de", "valeurs": ["10 février"]}, "Merci de répondre vite."))


class NeContientAucun(unittest.TestCase):
    def test_refuse_si_present(self):
        self.assertFalse(ok({"type": "ne_contient_aucun", "valeurs": ["[Nom]"]}, "Bonjour [Nom],"))

    def test_accepte_si_absent(self):
        self.assertTrue(ok({"type": "ne_contient_aucun", "valeurs": ["[Nom]", "[date]"]}, "Bonjour Madame Morvan,"))


class MotsMax(unittest.TestCase):
    def test_limite(self):
        self.assertTrue(ok({"type": "mots_max", "max": 5}, "un deux trois quatre cinq"))
        self.assertFalse(ok({"type": "mots_max", "max": 5}, "un deux trois quatre cinq six"))


class Puces(unittest.TestCase):
    def test_compte_les_puces(self):
        texte = "Résumé :\n- un\n- deux\n* trois\nFin"
        self.assertTrue(ok({"type": "puces", "exact": 3}, texte))
        self.assertFalse(ok({"type": "puces", "exact": 2}, texte))

    def test_puce_typographique(self):
        self.assertTrue(ok({"type": "puces", "exact": 2}, "• a\n• b"))


class ListeNumerotee(unittest.TestCase):
    def test_compte(self):
        texte = "1. a\n2. b\n3) c"
        self.assertTrue(ok({"type": "liste_numerotee", "exact": 3}, texte))
        self.assertFalse(ok({"type": "liste_numerotee", "exact": 4}, texte))


class ReponseExacte(unittest.TestCase):
    def test_ignore_ponctuation_et_casse(self):
        verif = {"type": "reponse_exacte", "valeurs": ["oui"]}
        self.assertTrue(ok(verif, "Oui."))
        self.assertTrue(ok(verif, "  oui  "))
        self.assertTrue(ok(verif, "« Oui »"))

    def test_refuse_une_phrase(self):
        self.assertFalse(ok({"type": "reponse_exacte", "valeurs": ["oui"]}, "Oui, le taux normal est de 20 %."))


class AucunNombreANChiffres(unittest.TestCase):
    def test_detecte_un_siren_avec_espaces(self):
        verif = {"type": "aucun_nombre_a_n_chiffres", "n": 9}
        self.assertFalse(ok(verif, "Son SIREN est 123 456 789."))
        self.assertFalse(ok(verif, "Son SIREN est 123456789."))

    def test_accepte_les_autres_nombres(self):
        verif = {"type": "aucun_nombre_a_n_chiffres", "n": 9}
        self.assertTrue(ok(verif, "Je n'ai pas cette information. Le forfait est de 6200 euros."))


class TableauMarkdown(unittest.TestCase):
    def test_dimensions(self):
        tableau = "| Compte | Libellé | Sens |\n|---|---|---|\n| 411 | Clients | Débit |\n| 512 | Banque | Débit |\n| 706 | Prestations | Crédit |"
        self.assertTrue(ok({"type": "tableau_markdown", "colonnes": 3, "lignes": 3}, tableau))
        self.assertFalse(ok({"type": "tableau_markdown", "colonnes": 3, "lignes": 4}, tableau))
        self.assertFalse(ok({"type": "tableau_markdown", "colonnes": 2, "lignes": 3}, tableau))

    def test_pas_de_tableau(self):
        self.assertFalse(ok({"type": "tableau_markdown", "colonnes": 3, "lignes": 3}, "Voici : 411, 512, 706"))


class MotsMaxTexteLivre(unittest.TestCase):
    def test_les_notes_sous_un_separateur_ne_comptent_pas(self):
        texte = "Madame,\n\n" + "mot " * 18 + "\n\nCordialement\n\n---\n\nNote : la date du 20 février est passée, à vérifier."
        self.assertTrue(ok({"type": "mots_max", "max": 20}, texte))
        self.assertFalse(ok({"type": "mots_max", "max": 20}, texte.replace("---", "")))

    def test_le_texte_livre_est_le_plus_long_des_blocs(self):
        texte = "Voici une proposition.\n\n***\n\n" + "mot " * 30 + "\n\n***\n\nNote : à relire."
        self.assertFalse(ok({"type": "mots_max", "max": 20}, texte))
        self.assertTrue(ok({"type": "mots_max", "max": 30}, texte))

    def test_sans_separateur_tout_compte(self):
        self.assertFalse(ok({"type": "mots_max", "max": 3}, "un deux trois quatre"))


class Abstention(unittest.TestCase):
    def test_detecte_une_abstention(self):
        for phrase in [
            "Je ne sais pas, cette information ne figure pas dans le dossier.",
            "Le numéro de téléphone n'est pas indiqué dans les documents fournis.",
            "Je ne dispose pas de cette information.",
            "Aucun numéro de téléphone n'a été communiqué au cabinet.",
            "Le SIREN n'est pas renseigné dans la fiche.",
            "Les documents ne donnent pas de taux pour un stagiaire.",
            "La fiche ne mentionne pas de chiffre d'affaires.",
        ]:
            self.assertTrue(ok({"type": "abstention", "attendue": True}, phrase), phrase)

    def test_formulations_relevees_sur_des_reponses_reelles(self):
        for phrase in [
            "Les extraits ne mentionnent aucun taux horaire pour un stagiaire.",
            "Les extraits ne contiennent ni le montant des émoluments, ni le barème. Je ne peux donc pas répondre.",
            "Je ne peux malheureusement pas vous la donner.",
            "Aucun des extraits fournis ne la mentionne.",
            "La fiche ne comporte aucune donnée financière.",
        ]:
            self.assertTrue(ok({"type": "abstention", "attendue": True}, phrase), phrase)

    def test_formulations_relevees_dans_l_epreuve_agir(self):
        for phrase in [
            "La cellule reste vide, car aucun document de l'étude ne donne son numéro de téléphone.",
            "Je n'ai pas trouvé le numéro de téléphone de Mme Quéméner, donc je n'ai rien écrit.",
        ]:
            self.assertTrue(ok({"type": "abstention", "attendue": True}, phrase), phrase)

    def test_une_reponse_chiffree_n_est_pas_une_abstention(self):
        for phrase in ["Le forfait est de 4 800 € HT.", "La date de relance est le 16/05/2026, selon la procédure en vigueur.",
                       "Le cabinet peut facturer 45 € HT, comme le prévoit la lettre de mission."]:
            self.assertFalse(ok({"type": "abstention", "attendue": True}, phrase), phrase)

    def test_une_reponse_affirmative_n_est_pas_une_abstention(self):
        self.assertFalse(ok({"type": "abstention", "attendue": True}, "Son numéro est le 06 12 34 56 78."))

    def test_abstention_non_attendue(self):
        self.assertTrue(ok({"type": "abstention", "attendue": False}, "Le forfait est de 4 800 € HT."))
        self.assertFalse(ok({"type": "abstention", "attendue": False}, "Je ne sais pas."))


class EvaluerToutes(unittest.TestCase):
    def test_rend_un_resultat_par_verification(self):
        verifs = [
            {"type": "mots_max", "max": 3},
            {"type": "contient_un_de", "valeurs": ["bonjour"]},
        ]
        res = v.evaluer_toutes(verifs, "Bonjour tout le monde ici")
        self.assertEqual([ok_ for _, ok_ in res], [False, True])

    def test_type_inconnu_leve_une_erreur(self):
        with self.assertRaises(ValueError):
            v.evaluer({"type": "inconnu"}, "x")


class TypesConnus(unittest.TestCase):
    def test_liste_des_types(self):
        self.assertEqual(
            set(v.TYPES),
            {"contient_un_de", "ne_contient_aucun", "mots_max", "puces", "liste_numerotee",
             "reponse_exacte", "aucun_nombre_a_n_chiffres", "tableau_markdown", "abstention"},
        )

    def test_champs_obligatoires_par_type(self):
        self.assertEqual(v.champs_obligatoires("mots_max"), {"max"})
        self.assertEqual(v.champs_obligatoires("tableau_markdown"), {"colonnes", "lignes"})


if __name__ == "__main__":
    unittest.main()
