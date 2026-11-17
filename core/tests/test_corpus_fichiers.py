import json
import shutil
import tempfile
import unittest
from pathlib import Path

from core import donnees as d

SOURCE = d.RACINE / "expert-comptable" / "corpus"


class VarianteDocling(unittest.TestCase):
    def test_la_variante_est_complete_et_coherente(self):
        self.assertEqual(d.verifier_variante_extraction("expert-comptable", "docling"), [])
        manifeste = json.loads((SOURCE / "MANIFESTE-docling.json").read_text(encoding="utf-8"))["documents"]
        self.assertEqual(len(manifeste), 37)

    def test_les_formats_herites_sont_convertis_avant_docling(self):
        manifeste = json.loads((SOURCE / "MANIFESTE-docling.json").read_text(encoding="utf-8"))["documents"]
        for id_, e in manifeste.items():
            if e["format"] in ("doc", "xls"):
                self.assertTrue(e["conversion_prealable"], id_)
            else:
                self.assertIsNone(e["conversion_prealable"], id_)

    def test_les_deux_moteurs_donnent_des_textes_distincts_pour_les_memes_documents(self):
        a = d.charger_documents("expert-comptable")
        b = d.charger_documents("expert-comptable", extraction="docling")
        self.assertEqual(set(a), set(b))
        self.assertTrue(all(a[i]["corps"] != b[i]["corps"] for i in a))
        self.assertTrue(a["releve-banque-epis-2026-01"]["corps"].count("\n") < 3)
        self.assertGreater(b["releve-banque-epis-2026-01"]["corps"].count("\n"), 8)

    def test_moteur_inconnu(self):
        with self.assertRaises(ValueError):
            d.charger_documents("expert-comptable", extraction="inconnu")


class CorpusReel(unittest.TestCase):
    def test_formats_representatifs(self):
        formats = json.loads((SOURCE / "formats.json").read_text(encoding="utf-8"))
        utilises = {s["format"] for k, s in formats.items() if not k.startswith("_")}
        self.assertTrue(d.FORMATS_REQUIS <= utilises, utilises)
        degrades = [k for k, s in formats.items() if not k.startswith("_") and s.get("degradation")]
        self.assertGreaterEqual(len(degrades), 2)

    def test_les_scans_n_ont_pas_de_couche_texte(self):
        for id_, s in json.loads((SOURCE / "formats.json").read_text(encoding="utf-8")).items():
            if not id_.startswith("_") and s.get("degradation"):
                octets = (SOURCE / "fichiers" / f"{id_}.pdf").read_bytes()
                self.assertNotIn(b"/Font", octets, id_)

    def test_le_corpus_complet_est_coherent(self):
        docs = d.charger_documents("expert-comptable")
        self.assertEqual(d.verifier_fichiers("expert-comptable", docs), [])

    def test_le_fec_est_equilibre_sauf_anomalies_declarees(self):
        v = json.loads((SOURCE / "fec-epis-dor-2025.verites.json").read_text(encoding="utf-8"))
        self.assertEqual(list(v["ecritures_desequilibrees"]), ["OD-0013"])
        self.assertEqual(v["resultat_avant_impot_cents"], 1_000_000)
        self.assertEqual(len(v["factures_saisies_en_double"]), 1)
        self.assertEqual(len(v["ecritures_sans_piece"]), 1)
        self.assertEqual(v["solde_par_compte_cents"]["471"], 150_000)


class Alterations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.racine = Path(self.tmp.name)
        shutil.copytree(SOURCE, self.racine / "expert-comptable" / "corpus")
        self.corpus = self.racine / "expert-comptable" / "corpus"

    def erreurs(self):
        docs = d.charger_documents("expert-comptable", self.racine)
        return d.verifier_fichiers("expert-comptable", docs, self.racine)

    def test_copie_intacte(self):
        self.assertEqual(self.erreurs(), [])

    def test_fichier_modifie_apres_extraction(self):
        with (self.corpus / "fichiers" / "honoraires-2026.xlsx").open("ab") as f:
            f.write(b"\0")
        self.assertTrue(any("a change depuis l'extraction" in e for e in self.erreurs()))

    def test_extraction_manquante(self):
        (self.corpus / "extractions" / "fiche-epis-dor.txt").unlink()
        self.assertTrue(any("manquant" in e for e in self.erreurs()))

    def test_extraction_modifiee(self):
        with (self.corpus / "extractions" / "fiche-epis-dor.txt").open("a", encoding="utf-8") as f:
            f.write("texte ajoute")
        self.assertTrue(any("l'extraction a change" in e for e in self.erreurs()))

    def test_faux_docx(self):
        (self.corpus / "fichiers" / "fiche-phare.docx").write_bytes(b"pas un docx")
        self.assertTrue(any("vrai fichier docx" in e for e in self.erreurs()))

    def test_document_degrade_qui_a_une_couche_texte(self):
        propre = self.corpus / "fichiers" / "devis-vehicule-epis.pdf"
        shutil.copy(propre, self.corpus / "fichiers" / "lettre-mission-epis-dor.pdf")
        self.assertTrue(any("sans couche texte" in e for e in self.erreurs()))

    def test_trace_de_machine_dans_un_fichier(self):
        with (self.corpus / "fichiers" / "mail-kerloch-2026-03.pdf").open("ab") as f:
            f.write(b"/home/quelquun/doc.pdf")
        self.assertTrue(any("trace d'une machine" in e for e in self.erreurs()))

    def test_mot_interdit_dans_un_fichier_binaire(self):
        docs = d.charger_documents("expert-comptable", self.racine)
        with (self.corpus / "fichiers" / "fiche-phare.docx").open("ab") as f:
            f.write("MotSecret".encode("utf-16-le"))
        erreurs = d.verifier_fichiers("expert-comptable", docs, self.racine, mots_interdits=["motsecret"])
        self.assertTrue(any("mot interdit" in e for e in erreurs))

    def test_variante_docling_alteree(self):
        with (self.corpus / "extractions-docling" / "fiche-epis-dor.txt").open("a", encoding="utf-8") as f:
            f.write("texte ajoute")
        self.assertTrue(any("extraction docling" in e and "a change depuis le manifeste" in e for e in self.erreurs_variante()))

    def test_variante_docling_vide(self):
        (self.corpus / "extractions-docling" / "fiche-phare.txt").write_text("", encoding="utf-8")
        self.assertTrue(any("vide" in e for e in self.erreurs_variante()))

    def test_variante_docling_sans_manifeste(self):
        (self.corpus / "MANIFESTE-docling.json").unlink()
        self.assertTrue(any("ensemble" in e for e in self.erreurs_variante()))

    def test_variante_docling_fichier_modifie(self):
        with (self.corpus / "fichiers" / "honoraires-2026.xlsx").open("ab") as f:
            f.write(b"\0")
        self.assertTrue(any("extraction docling" in e and "a change depuis l'extraction" in e for e in self.erreurs_variante()))

    def erreurs_variante(self):
        return d.verifier_variante_extraction("expert-comptable", "docling", self.racine)

    def test_document_sans_format(self):
        formats = json.loads((self.corpus / "formats.json").read_text(encoding="utf-8"))
        del formats["fiche-phare"]
        (self.corpus / "formats.json").write_text(json.dumps(formats), encoding="utf-8")
        self.assertTrue(any("n'a pas de format" in e for e in self.erreurs()))

    def test_format_requis_absent(self):
        formats = json.loads((self.corpus / "formats.json").read_text(encoding="utf-8"))
        formats["justificatifs-epis-2026-01"]["format"] = "xlsx"
        formats["honoraires-2025"]["format"] = "xlsx"
        (self.corpus / "formats.json").write_text(json.dumps(formats), encoding="utf-8")
        self.assertTrue(any("formats absents" in e and "xls" in e for e in self.erreurs()))

    def test_fec_avec_une_colonne_en_moins(self):
        chemin = self.corpus / "fichiers" / "fec-epis-dor-2025.txt"
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        lignes[5] = "\t".join(lignes[5].split("\t")[:-1])
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        self.assertTrue(any("colonnes au lieu de 18" in e for e in self.erreurs()))

    def test_fec_dont_un_montant_a_change(self):
        chemin = self.corpus / "fichiers" / "fec-epis-dor-2025.txt"
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        cols = lignes[10].split("\t")
        cols[11] = "999999,99"
        lignes[10] = "\t".join(cols)
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        erreurs = self.erreurs()
        self.assertTrue(any("soldes par compte" in e or "desequilibrees" in e for e in erreurs), erreurs)

    def test_fec_incoherent_avec_la_balance(self):
        source = self.corpus / "sources" / "balance-epis-2025.md"
        source.write_text(source.read_text(encoding="utf-8").replace("198 400,00", "198 401,00"), encoding="utf-8")
        self.assertTrue(any("la balance" in e for e in self.erreurs()))


if __name__ == "__main__":
    unittest.main()
