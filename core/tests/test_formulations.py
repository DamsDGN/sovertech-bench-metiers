import unittest

from core import donnees as d
from core import verifications as vf

RAG = {q["id"]: q for q in d.charger_metier("expert-comptable")["rag"]}


class FormulationsLegitimes(unittest.TestCase):
    """Reponses justes observees sur Atlas que des controles trop stricts avaient refusees."""

    def passe(self, id_, reponse):
        return all(ok for _, ok in vf.evaluer_toutes(RAG[id_]["verifications"], reponse))

    def test_rg19_accepte_la_formulation_de_la_procedure(self):
        reponse = "Les Épis d'Or (4 800 € HT) et l'Atelier Kerloc'h (6 200 € HT) ont droit au point intermédiaire, 3 mois avant la clôture."
        self.assertTrue(self.passe("RG-19", reponse))

    def test_rg19_refuse_un_client_oublie(self):
        self.assertFalse(self.passe("RG-19", "Seul l'Atelier Kerloc'h bénéficie d'un point intermédiaire, 3 mois avant la clôture."))


if __name__ == "__main__":
    unittest.main()
