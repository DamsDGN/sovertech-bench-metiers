"""Genere le FEC fictif de la SARL Les Epis d'Or (exercice 2025), cale sur la balance du corpus.

Le fichier suit la structure a 18 colonnes separees par des tabulations (dates AAAAMMJJ, virgule decimale).
Anomalies plantees pour les taches de controle : un doublon de facture, une ecriture sans reference de piece,
un compte d'attente non solde, une ecriture desequilibree, une facture avec un taux de TVA different des autres.
Usage : python3 outils/generer_fec.py
"""
import datetime
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CORPUS = RACINE / "expert-comptable" / "corpus"
COLONNES = ["JournalCode", "JournalLib", "EcritureNum", "EcritureDate", "CompteNum", "CompteLib", "CompAuxNum", "CompAuxLib",
            "PieceRef", "PieceDate", "EcritureLib", "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise"]
JOURNAUX = {"AN": "A-nouveaux", "AC": "Achats", "VT": "Ventes", "BQ": "Banque", "PA": "Paie", "OD": "Operations diverses"}
LIBELLES = {
    "101": "Capital", "106": "Reserves", "164": "Emprunts aupres des etablissements de credit", "215": "Materiel et outillage",
    "2182": "Materiel de transport", "2815": "Amortissements materiel et outillage", "28182": "Amortissements materiel de transport",
    "401": "Fournisseurs", "411": "Clients", "421": "Personnel remunerations dues", "431": "Securite sociale", "44551": "TVA a decaisser",
    "44566": "TVA deductible sur biens et services", "44571": "TVA collectee", "467": "Autres comptes debiteurs ou crediteurs",
    "471": "Compte d'attente", "512": "Banque", "530": "Caisse", "607": "Achats de marchandises", "613": "Locations",
    "616": "Primes d'assurances", "622": "Remunerations d'intermediaires et honoraires", "641": "Remunerations du personnel",
    "645": "Charges de securite sociale et de prevoyance", "661": "Charges d'interets", "681": "Dotations aux amortissements",
    "707": "Ventes de marchandises",
}
TOTAUX_BALANCE = {"607": 19840000, "613": 2400000, "616": 360000, "622": 480000, "641": 11870000, "645": 4150000,
                  "661": 290000, "681": 920000, "707": 41310000}
POIDS_SAISON = [0.9, 0.9, 1.0, 1.0, 1.05, 1.15, 1.3, 1.35, 1.05, 1.0, 0.95, 1.1]
TIERS = {"minoterie": ("4010001", "Minoterie du Blavet"), "laiterie": ("4010002", "Laiterie du Scorff"),
         "cabinet": ("4010003", "Cabinet Aubepine et Associes"), "mairie": ("4110001", "Mairie de Lorient")}


def arrondi(x):
    return int(Decimal(x).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def tva(ht, taux_milliemes):
    return arrondi(Decimal(ht) * taux_milliemes / 1000)


def repartir(total, poids):
    brut = [arrondi(Decimal(total) * Decimal(str(p)) / Decimal(str(sum(poids)))) for p in poids]
    brut[-1] += total - sum(brut)
    return brut


def fmt(c):
    return "" if not c else f"{c // 100},{c % 100:02d}"


def dernier_jour(mois):
    return (datetime.date(2025, mois % 12 + 1, 1) - datetime.timedelta(days=1)).day if mois < 12 else 31


class Fec:
    def __init__(self):
        self.ecritures, self.compteurs, self.lettres = [], {j: 0 for j in JOURNAUX}, 0

    def lettre(self):
        self.lettres += 1
        n = self.lettres - 1
        return chr(65 + n // 26 % 26) + chr(65 + n % 26)

    def ecriture(self, journal, date, piece, libelle, lignes, piece_date=None):
        self.compteurs[journal] += 1
        num = f"{journal}-{self.compteurs[journal]:04d}"
        e = {"journal": journal, "num": num, "date": date, "lignes": []}
        for ligne in lignes:
            compte, debit, credit = ligne[0], ligne[1], ligne[2]
            aux = ligne[3] if len(ligne) > 3 else None
            let = ligne[4] if len(ligne) > 4 else ("", "")
            e["lignes"].append({"JournalCode": journal, "JournalLib": JOURNAUX[journal], "EcritureNum": num,
                                "EcritureDate": date.strftime("%Y%m%d"), "CompteNum": compte, "CompteLib": LIBELLES[compte],
                                "CompAuxNum": aux[0] if aux else "", "CompAuxLib": aux[1] if aux else "",
                                "PieceRef": piece, "PieceDate": (piece_date or date).strftime("%Y%m%d") if piece else "",
                                "EcritureLib": libelle, "Debit": fmt(debit), "Credit": fmt(credit),
                                "EcritureLet": let[0], "DateLet": let[1], "ValidDate": date.strftime("%Y%m%d"),
                                "Montantdevise": "", "Idevise": ""})
        self.ecritures.append(e)
        return e

    def texte(self):
        ordre = list(JOURNAUX)
        lignes = ["\t".join(COLONNES)]
        for e in sorted(self.ecritures, key=lambda e: (ordre.index(e["journal"]), e["num"])):
            for l in e["lignes"]:
                lignes.append("\t".join(l[c] for c in COLONNES))
        return "\n".join(lignes) + "\n"


def construire():
    f = Fec()
    d = datetime.date
    f.ecriture("AN", d(2025, 1, 1), "AN-0001", "A-nouveaux 2025", [
        ("215", 4500000, 0), ("2182", 2200000, 0), ("512", 1250000, 0), ("411", 320000, 0),
        ("2815", 0, 1800000), ("401", 0, 980000), ("101", 0, 1000000), ("106", 0, 1490000), ("164", 0, 3000000)])
    total607, u = TOTAUX_BALANCE["607"], TOTAUX_BALANCE["607"]
    for _ in range(100):
        dup_ht = arrondi(Decimal(repartir(u, POIDS_SAISON)[5]) * Decimal("0.6"))
        if total607 - dup_ht == u:
            break
        u = total607 - dup_ht
    achats = repartir(u, POIDS_SAISON)
    dup_ht = arrondi(Decimal(achats[5]) * Decimal("0.6"))
    achats[11] += total607 - (sum(achats) + dup_ht)
    ventes_mairie = [0, 0, 600000, 0, 0, 600000, 0, 0, 600000, 0, 0, 600000]
    ventes_comptoir = repartir(TOTAUX_BALANCE["707"] - sum(ventes_mairie), POIDS_SAISON)
    tva_collectee, tva_deductible = [0] * 12, [0] * 12
    factures_a_payer, paie, charges = [], [], []
    num_fa = 440
    for m in range(1, 13):
        ht_total = achats[m - 1]
        ht_mino = arrondi(Decimal(ht_total) * Decimal("0.6"))
        for cle, ht, jour in (("minoterie", ht_mino, 5), ("laiterie", ht_total - ht_mino, 12)):
            taux = 200 if (cle == "laiterie" and m == 9) else 55
            t = tva(ht, taux)
            num_fa += 1
            date = d(2025, m, jour)
            piece = f"FA-2025-{num_fa:04d}"
            e = f.ecriture("AC", date, piece, f"Facture {TIERS[cle][1]} {piece}",
                           [("607", ht, 0), ("44566", t, 0), ("401", 0, ht + t, TIERS[cle])])
            tva_deductible[m - 1] += t
            factures_a_payer.append((e, date + datetime.timedelta(days=30), ht + t, TIERS[cle], piece))
            if cle == "minoterie" and m == 6:
                assert ht == dup_ht
                f.ecriture("AC", date, piece, f"Facture {TIERS[cle][1]} {piece}",
                           [("607", ht, 0), ("44566", t, 0), ("401", 0, ht + t, TIERS[cle])])
                tva_deductible[m - 1] += t
                doublon = {"ecriture_origine": e["num"], "ecriture_doublon": f.ecritures[-1]["num"], "piece": piece, "ht": ht, "tva": t}
        t_cab = tva(40000, 200)
        date = d(2025, m, 28)
        piece = f"HON-2025-{m:02d}"
        e = f.ecriture("AC", date, piece, f"Honoraires {TIERS['cabinet'][1]} {m:02d}/2025",
                       [("622", 40000, 0), ("44566", t_cab, 0), ("401", 0, 40000 + t_cab, TIERS["cabinet"])])
        tva_deductible[m - 1] += t_cab
        factures_a_payer.append((e, d(2025, m, 28) + datetime.timedelta(days=30), 40000 + t_cab, TIERS["cabinet"], piece))
        fin = d(2025, m, dernier_jour(m))
        ht_c = ventes_comptoir[m - 1]
        t_c = tva(ht_c, 55)
        tva_collectee[m - 1] += t_c
        f.ecriture("VT", fin, f"VT-2025-{m:02d}", f"Ventes comptoir {m:02d}/2025", [("530", ht_c + t_c, 0), ("707", 0, ht_c), ("44571", 0, t_c)])
        f.ecriture("BQ", fin, f"REM-2025-{m:02d}", f"Remise especes et CB {m:02d}/2025", [("512", ht_c + t_c, 0), ("530", 0, ht_c + t_c)])
        if ventes_mairie[m - 1]:
            ht_m = ventes_mairie[m - 1]
            t_m = tva(ht_m, 100)
            tva_collectee[m - 1] += t_m
            piece = f"FV-2025-{m:02d}"
            e = f.ecriture("VT", d(2025, m, 25), piece, f"Facture traiteur Mairie de Lorient {piece}",
                           [("411", ht_m + t_m, 0, TIERS["mairie"]), ("707", 0, ht_m), ("44571", 0, t_m)])
            factures_a_payer.append((e, d(2025, m, 25) + datetime.timedelta(days=45), ht_m + t_m, TIERS["mairie"], piece))
        f.ecriture("BQ", d(2025, m, 2), f"PRLV-ASS-{m:02d}", f"Prelevement assurance {m:02d}/2025", [("616", 30000, 0), ("512", 0, 30000)])
        f.ecriture("BQ", d(2025, m, 20), f"PRLV-LOY-{m:02d}", f"Loyer local commercial {m:02d}/2025", [("613", 200000, 0), ("512", 0, 200000)])
    brut = repartir(TOTAUX_BALANCE["641"], POIDS_SAISON)
    soc = repartir(TOTAUX_BALANCE["645"], POIDS_SAISON)
    for m in range(1, 13):
        fin = d(2025, m, dernier_jour(m))
        f.ecriture("PA", fin, f"PAIE-2025-{m:02d}", f"Paie {m:02d}/2025", [("641", brut[m - 1], 0), ("645", soc[m - 1], 0), ("421", 0, brut[m - 1]), ("431", 0, soc[m - 1])])
        f.ecriture("BQ", fin, f"VIR-PAIE-{m:02d}", f"Virement salaires {m:02d}/2025", [("421", brut[m - 1], 0), ("512", 0, brut[m - 1])])
        if m < 12:
            f.ecriture("BQ", d(2025, m + 1, 15), f"URSSAF-{m:02d}", f"Cotisations sociales {m:02d}/2025", [("431", soc[m - 1], 0), ("512", 0, soc[m - 1])])
    for echeance in (3, 6, 9, 12):
        jour = d(2025, echeance, dernier_jour(echeance))
        f.ecriture("BQ", jour, f"ECH-PRET-T{echeance // 3}", f"Echeance pret T{echeance // 3}", [("661", 72500, 0), ("164", 250000, 0), ("512", 0, 322500)])
    for m in range(1, 13):
        net = tva_collectee[m - 1] - tva_deductible[m - 1]
        assert net > 0
        f.ecriture("OD", d(2025, m, dernier_jour(m)), f"TVA-2025-{m:02d}", f"Declaration de TVA {m:02d}/2025",
                   [("44571", tva_collectee[m - 1], 0), ("44566", 0, tva_deductible[m - 1]), ("44551", 0, net)])
        if m < 12:
            f.ecriture("BQ", d(2025, m + 1, 20), f"TVA-PAIEMENT-{m:02d}", f"Paiement TVA {m:02d}/2025", [("44551", net, 0), ("512", 0, net)])
    for e, date_paiement, montant, tiers, piece in factures_a_payer:
        if date_paiement.year > 2025:
            continue
        lettre = f.lettre()
        for l in e["lignes"]:
            if l["CompAuxNum"] == tiers[0]:
                l["EcritureLet"], l["DateLet"] = lettre, date_paiement.strftime("%Y%m%d")
        sens = ("401", montant, 0) if tiers[0].startswith("401") else ("411", 0, montant)
        banque = ("512", 0, montant) if tiers[0].startswith("401") else ("512", montant, 0)
        f.ecriture("BQ", date_paiement, f"REG-{piece}", f"Reglement {tiers[1]} {piece}",
                   [(sens[0], sens[1], sens[2], tiers, (lettre, date_paiement.strftime("%Y%m%d"))), banque])
    f.ecriture("BQ", d(2025, 11, 12), "", "Virement SEPA non identifie", [("471", 150000, 0), ("512", 0, 150000)])
    f.ecriture("OD", d(2025, 9, 15), "OD-REG-0915", "Regularisation divers", [("467", 25000, 0), ("512", 0, 24000)])
    f.ecriture("OD", d(2025, 12, 31), "OD-AMORT-2025", "Dotations aux amortissements 2025",
               [("681", 920000, 0), ("2815", 0, 620000), ("28182", 0, 300000)])
    return f, doublon


def analyser(texte):
    """Recalcule toutes les verites a partir du texte du fichier (analyse independante de la construction)."""
    lignes = [l.split("\t") for l in texte.splitlines()]
    en_tete, corps = lignes[0], lignes[1:]
    idx = {c: i for i, c in enumerate(en_tete)}
    def cents(x):
        return 0 if not x else int(x.replace(",", "")) if "," in x else int(x) * 100
    par_compte, par_ecriture, sans_piece, pieces = {}, {}, [], {}
    for l in corps:
        c = l[idx["CompteNum"]]
        solde = par_compte.setdefault(c, [0, 0])
        solde[0] += cents(l[idx["Debit"]]); solde[1] += cents(l[idx["Credit"]])
        e = par_ecriture.setdefault(l[idx["EcritureNum"]], [0, 0])
        e[0] += cents(l[idx["Debit"]]); e[1] += cents(l[idx["Credit"]])
        if not l[idx["PieceRef"]]:
            sans_piece.append(l[idx["EcritureNum"]])
        if l[idx["JournalCode"]] == "AC" and l[idx["CompteNum"]] == "401":
            pieces.setdefault((l[idx["PieceRef"]], l[idx["CompAuxNum"]]), set()).add(l[idx["EcritureNum"]])
    ouvertes = [l for l in corps if l[idx["CompAuxNum"]] and not l[idx["EcritureLet"]]]
    achats_607, taux = {}, {}
    for l in corps:
        if l[idx["JournalCode"]] == "AC" and l[idx["CompteNum"]] in ("607", "44566") and l[idx["PieceRef"]].startswith("FA-"):
            e = achats_607.setdefault(l[idx["EcritureNum"]], {})
            e[l[idx["CompteNum"]]] = cents(l[idx["Debit"]])
    for num, e in achats_607.items():
        taux.setdefault(round(e["44566"] * 1000 / e["607"] / 5) * 5, []).append(num)
    return {
        "nombre_lignes": len(corps), "nombre_ecritures": len(par_ecriture),
        "total_debit_cents": sum(v[0] for v in par_compte.values()), "total_credit_cents": sum(v[1] for v in par_compte.values()),
        "solde_par_compte_cents": {c: v[0] - v[1] for c, v in sorted(par_compte.items())},
        "ecritures_desequilibrees": {n: v[0] - v[1] for n, v in par_ecriture.items() if v[0] != v[1]},
        "ecritures_sans_piece": sorted(set(sans_piece)),
        "factures_saisies_en_double": [sorted(v) for v in pieces.values() if len(v) > 1],
        "lignes_tiers_non_lettrees": len(ouvertes),
        "achats_607_par_taux_de_tva_milliemes": {str(k): sorted(v) for k, v in sorted(taux.items())},
    }


def main():
    f, doublon = construire()
    texte = f.texte()
    (CORPUS / "fichiers" / "fec-epis-dor-2025.txt").write_text(texte, encoding="utf-8")
    v = analyser(texte)
    sc = v["solde_par_compte_cents"]
    for compte, total in TOTAUX_BALANCE.items():
        assert abs(sc[compte]) == total, (compte, sc[compte], total)
    v["resultat_avant_impot_cents"] = -(sum(x for c, x in sc.items() if c[0] in "67"))
    v["doublon"] = doublon
    (CORPUS / "fec-epis-dor-2025.verites.json").write_text(json.dumps(v, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v[k] for k in ("nombre_lignes", "nombre_ecritures", "ecritures_desequilibrees", "ecritures_sans_piece",
                                          "factures_saisies_en_double", "resultat_avant_impot_cents", "lignes_tiers_non_lettrees")}, ensure_ascii=False))
    print("soldes :", {c: sc[c] for c in ("471", "512", "411", "401", "44551", "421", "431", "530")})


if __name__ == "__main__":
    main()
