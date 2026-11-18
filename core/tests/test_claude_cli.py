import json
import unittest

from core import claude_cli as c
from core import fournisseurs as f
from core.client import ErreurClient

OUTIL = {"type": "function", "function": {"name": "lire", "description": "Lit un document.", "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}}}}}


def sortie(texte, **kw):
    return {"result": texte, "stop_reason": "end_turn", "usage": {"input_tokens": 2, "cache_creation_input_tokens": 600, "cache_read_input_tokens": 50, "output_tokens": 30}, **kw}


class Invite(unittest.TestCase):
    def test_echange_simple_transmis_tel_quel(self):
        s, m = c.construire_invite([{"role": "system", "content": "S"}, {"role": "user", "content": "Q"}])
        self.assertEqual((s, m), ("S", "Q"))

    def test_conversation_rejouee_en_transcription(self):
        _, m = c.construire_invite([
            {"role": "system", "content": "S"}, {"role": "user", "content": "Q"},
            {"role": "assistant", "content": "R1"}, {"role": "user", "content": "Suite"}])
        self.assertIn("[Utilisateur]\nQ", m)
        self.assertIn("[Assistant]\nR1", m)
        self.assertTrue(m.endswith("Écris uniquement le prochain tour de l'assistant."))

    def test_appels_et_resultats_d_outils_dans_la_transcription(self):
        _, m = c.construire_invite([
            {"role": "system", "content": "S"}, {"role": "user", "content": "Q"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "appel_0", "type": "function", "function": {"name": "lire", "arguments": '{"doc_id": "x"}'}}]},
            {"role": "tool", "tool_call_id": "appel_0", "content": '{"ok": true}'}])
        self.assertIn('<appel>{"name": "lire", "arguments": {"doc_id": "x"}}</appel>', m)
        self.assertIn("[Résultat de l'outil, appel appel_0]", m)


class Appels(unittest.TestCase):
    def test_lecture_de_deux_appels_et_du_texte(self):
        texte, appels = c.lire_appels('Je regarde.\n<appel>{"name": "lire", "arguments": {"doc_id": "a"}}</appel>\n<appel>{"name": "lire", "arguments": {"doc_id": "b"}}</appel>', 3)
        self.assertEqual(texte, "Je regarde.")
        self.assertEqual([a["id"] for a in appels], ["appel_3", "appel_4"])
        self.assertEqual(json.loads(appels[1]["arguments"]), {"doc_id": "b"})

    def test_json_invalide_reste_dans_le_texte_et_n_est_pas_un_appel(self):
        texte, appels = c.lire_appels('<appel>{pas du json}</appel>')
        self.assertEqual(appels, [])
        self.assertIn("pas du json", texte)

    def test_arguments_non_objet_refuses(self):
        _, appels = c.lire_appels('<appel>{"name": "lire", "arguments": [1]}</appel>')
        self.assertEqual(appels, [])


class Client(unittest.TestCase):
    def client(self, reponses):
        vus = []
        def lanceur(systeme, message, modele, effort, max_tokens, delai):
            vus.append((systeme, message, modele, effort, max_tokens))
            r = reponses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r
        cl = c.ClientClaudeCli("claude-sonnet-5-5", {"effort": "high"}, lanceur=lanceur, tentatives=2)
        return cl, vus

    def test_reponse_texte_et_tokens(self):
        cl, vus = self.client([sortie("Bonjour")])
        rep = cl.completer([{"role": "system", "content": "S"}, {"role": "user", "content": "Q"}], max_tokens=32768)
        self.assertEqual((rep.texte, rep.fin, rep.tokens_prompt, rep.tokens_completion), ("Bonjour", "stop", 652, 30))
        self.assertEqual(vus[0], ("S" + c.NEUTRALISATION_DATE, "Q", "claude-sonnet-5-5", "high", 32768))
        self.assertIn("date du jour", vus[0][0])

    def test_coupure_au_plafond(self):
        cl, _ = self.client([sortie("abc", stop_reason="max_tokens")])
        self.assertEqual(cl.completer([{"role": "user", "content": "Q"}]).fin, "length")

    def test_outils_decrits_dans_le_systeme_et_appels_emules(self):
        cl, vus = self.client([sortie('<appel>{"name": "lire", "arguments": {"doc_id": "a"}}</appel>')])
        rep = cl.completer([{"role": "system", "content": "S"}, {"role": "user", "content": "Q"}], outils=[OUTIL])
        self.assertIn("- lire : Lit un document.", vus[0][0])
        self.assertEqual((rep.fin, rep.appels_outils[0]["name"]), ("tool_calls", "lire"))

    def test_sans_outils_les_blocs_appel_ne_sont_pas_interpretes(self):
        cl, _ = self.client([sortie('<appel>{"name": "lire", "arguments": {}}</appel>')])
        self.assertEqual(cl.completer([{"role": "user", "content": "Q"}]).appels_outils, [])

    def test_une_panne_est_rejouee_une_fois(self):
        cl, vus = self.client([ErreurClient("panne"), sortie("ok")])
        cl.completer([{"role": "user", "content": "Q"}])
        self.assertEqual(len(vus), 2)

    def test_echec_definitif_remonte(self):
        cl, _ = self.client([ErreurClient("a"), ErreurClient("b")])
        with self.assertRaises(ErreurClient):
            cl.completer([{"role": "user", "content": "Q"}])

    def test_erreur_signalee_par_le_cli(self):
        cl, _ = self.client([sortie("Not logged in", is_error=True), sortie("Not logged in", is_error=True)])
        with self.assertRaises(ErreurClient):
            cl.completer([{"role": "user", "content": "Q"}])


class Creation(unittest.TestCase):
    def test_fournisseur_claude_cli(self):
        from unittest import mock
        with mock.patch("core.fournisseurs.shutil.which", return_value="/usr/bin/claude"):
            cl = f.creer_client({"fournisseur": "claude_cli", "modele_api": "claude-sonnet-5-5"}, env={})
        self.assertIsInstance(cl, c.ClientClaudeCli)
        with mock.patch("core.fournisseurs.shutil.which", return_value=None), self.assertRaises(ErreurClient):
            f.creer_client({"fournisseur": "claude_cli", "modele_api": "x"}, env={})


class Isolation(unittest.TestCase):
    def test_le_cli_est_lance_sans_outil_dans_un_dossier_vide_et_sans_variables_secretes(self):
        from unittest import mock
        import os
        vu = {}
        def faux(cmd, **kw):
            vu.update(cmd=cmd, cwd=kw["cwd"], env=kw["env"], vide=os.listdir(kw["cwd"]))
            return mock.Mock(returncode=0, stdout=json.dumps(sortie("ok")), stderr="")
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "secret", "BENCH_API_KEY": "secret"}), mock.patch("core.claude_cli.subprocess.run", faux):
            c.lancer_cli("S", "Q", "claude-sonnet-5-5", "high", 1000, 10)
        self.assertEqual(vu["vide"], [])
        self.assertNotIn("sover", vu["cwd"].lower())
        self.assertEqual(vu["cmd"][vu["cmd"].index("--tools") + 1], "")
        for drapeau in ("--no-session-persistence", "--disable-slash-commands", "--strict-mcp-config"):
            self.assertIn(drapeau, vu["cmd"])
        self.assertNotIn("ANTHROPIC_API_KEY", vu["env"])
        self.assertNotIn("BENCH_API_KEY", vu["env"])


if __name__ == "__main__":
    unittest.main()


class Releve(unittest.TestCase):
    def test_un_resultat_via_cli_est_non_comparable(self):
        from core import catalogue, lancer
        from core.tests.test_lancer import JEUX
        entree = {**catalogue.charger("claude-sonnet-5-5-etalon"), "fournisseur": "claude_cli"}
        releve = lancer.construire_releve({"metier": "expert-comptable", "max_tokens": 1, "passes": 1, "blocs": []}, entree, {}, JEUX)
        self.assertFalse(releve["comparable_aux_resultats_publies"])
        self.assertIn("claude -p", releve["raisons_non_comparable"][0])
