import unittest

from core import donnees as d

JEUX = d.charger_metier("expert-comptable")
ROWS = JEUX["documents"]["fec-epis-dor-2025"]["donnees"]
CH = {t["id"]: t for t in JEUX["chat"]}
M = lambda x: 0 if not x else int(x.replace(",", ""))


def lignes(ecriture):
    return [r for r in ROWS if r["EcritureNum"] == ecriture]


class FaitsDuFec(unittest.TestCase):
    def test_le_doublon(self):
        a, b = lignes("AC-0016"), lignes("AC-0017")
        self.assertEqual([(r["PieceRef"], r["CompteNum"], r["Debit"], r["Credit"]) for r in a],
                         [(r["PieceRef"], r["CompteNum"], r["Debit"], r["Credit"]) for r in b])
        self.assertEqual(a[0]["PieceRef"], "FA-2025-0451")
        self.assertEqual(a[0]["Debit"], "10185,71")
        texte = CH["CH-21"]["reponse_modele"]
        for attendu in ("FA-2025-0451", "AC-0016", "AC-0017", "10 185,71"):
            self.assertIn(attendu, texte)

    def test_ecriture_desequilibree_et_ecriture_sans_piece(self):
        od = lignes("OD-0013")
        self.assertEqual(sum(M(r["Debit"]) for r in od) - sum(M(r["Credit"]) for r in od), 1000)
        self.assertEqual((od[0]["EcritureDate"], M(od[0]["Debit"]), M(od[1]["Credit"])), ("20250915", 25000, 24000))
        bq = lignes("BQ-0111")
        self.assertTrue(all(r["PieceRef"] == "" for r in bq))
        self.assertEqual((bq[0]["EcritureDate"], bq[0]["CompteNum"], bq[0]["Debit"]), ("20251112", "471", "1500,00"))
        sans_piece = {r["EcritureNum"] for r in ROWS if not r["PieceRef"]}
        self.assertEqual(sans_piece, {"BQ-0111"})
        texte = CH["CH-22"]["reponse_modele"]
        for attendu in ("OD-0013", "15/09/2025", "250,00", "240,00", "10,00", "BQ-0111", "12/11/2025", "1 500,00"):
            self.assertIn(attendu, texte)

    def test_resultat_avec_et_sans_doublon(self):
        resultat = -sum(M(r["Debit"]) - M(r["Credit"]) for r in ROWS if r["CompteNum"][0] in "67")
        self.assertEqual(resultat, 1_000_000)
        self.assertEqual(resultat + M("10185,71"), 2_018_571)
        texte = CH["CH-23"]["reponse_modele"]
        self.assertIn("10 000,00", texte)
        self.assertIn("20 185,71", texte)

    def test_taux_de_tva_atypique(self):
        par_ecriture = {}
        for r in ROWS:
            if r["JournalCode"] == "AC" and r["PieceRef"].startswith("FA-") and r["CompteNum"] in ("607", "44566"):
                par_ecriture.setdefault(r["EcritureNum"], {})[r["CompteNum"]] = (M(r["Debit"]), r["PieceRef"], r["EcritureDate"])
        taux = {n: round(v["44566"][0] * 1000 / v["607"][0]) for n, v in par_ecriture.items()}
        atypiques = [n for n, t in taux.items() if t != 55]
        self.assertEqual(atypiques, ["AC-0027"])
        self.assertEqual(taux["AC-0027"], 200)
        self.assertEqual(par_ecriture["AC-0027"]["607"][1:], ("FA-2025-0458", "20250912"))
        self.assertEqual(sum(1 for t in taux.values() if t == 55), 24)
        texte = CH["CH-24"]["reponse_modele"]
        for attendu in ("FA-2025-0458", "12 septembre 2025", "Laiterie du Scorff", "20 %", "5,5 %"):
            self.assertIn(attendu, texte)

    def test_faits_pour_l_agent(self):
        self.assertEqual(d.faits_fec(JEUX["documents"]), {
            "Total des ventes 2025 (compte 707)": "413100,00", "Solde du compte d'attente 471": "1500,00",
            "Facture saisie en double (référence de pièce)": "FA-2025-0451"})


if __name__ == "__main__":
    unittest.main()
