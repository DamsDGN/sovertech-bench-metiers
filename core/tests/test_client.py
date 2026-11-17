import http.server
import json
import threading
import unittest

from core import catalogue
from core import client as c


def evt(delta=None, fin=None, usage=None):
    d = {"choices": [{"delta": delta or {}, "finish_reason": fin}]}
    if usage:
        d["usage"] = usage
    return "data: " + json.dumps(d)


class LireFlux(unittest.TestCase):
    def horloge(self):
        self.t += 1.0
        return self.t

    def setUp(self):
        self.t = 0.0

    def test_texte_ttft_et_usage(self):
        lignes = [evt({"role": "assistant"}), evt({"content": "Bon"}), evt({"content": "jour"}),
                  evt(fin="stop"), evt(usage={"prompt_tokens": 10, "completion_tokens": 4}), "data: [DONE]"]
        r = c.lire_flux(lignes, 0.0, self.horloge)
        self.assertEqual(r.texte, "Bonjour")
        self.assertEqual(r.fin, "stop")
        self.assertEqual((r.tokens_prompt, r.tokens_completion), (10, 4))
        self.assertEqual(r.ttft, 1.0)
        self.assertGreater(r.duree, r.ttft)
        self.assertIsNotNone(r.debit)

    def test_raisonnement_separe_de_la_reponse(self):
        lignes = [evt({"reasoning_content": "je reflechis"}), evt({"content": "Reponse"}), "data: [DONE]"]
        r = c.lire_flux(lignes, 0.0, self.horloge)
        self.assertEqual((r.raisonnement, r.texte), ("je reflechis", "Reponse"))

    def test_balises_think_retirees(self):
        lignes = [evt({"content": "<think>brouillon</think>Oui."}), "data: [DONE]"]
        self.assertEqual(c.lire_flux(lignes, 0.0, self.horloge).texte, "Oui.")

    def test_appels_d_outils_reassembles(self):
        lignes = [
            evt({"tool_calls": [{"index": 0, "id": "a1", "function": {"name": "lire", "arguments": '{"doc'}}]}),
            evt({"tool_calls": [{"index": 0, "function": {"arguments": '_id": "x"}'}}]}),
            evt({"tool_calls": [{"index": 1, "function": {"name": "rechercher", "arguments": "{}"}}]}),
            evt(fin="tool_calls"), "data: [DONE]"]
        r = c.lire_flux(lignes, 0.0, self.horloge)
        self.assertEqual([a["name"] for a in r.appels_outils], ["lire", "rechercher"])
        self.assertEqual(json.loads(r.appels_outils[0]["arguments"]), {"doc_id": "x"})
        self.assertEqual(r.appels_outils[0]["id"], "a1")
        self.assertTrue(r.appels_outils[1]["id"])

    def test_lignes_ignorees(self):
        r = c.lire_flux([": keep-alive", "", evt({"content": "ok"}), "data: [DONE]"], 0.0, self.horloge)
        self.assertEqual(r.texte, "ok")


class ChargeUtile(unittest.TestCase):
    def test_reglages_et_outils(self):
        cl = c.Client("http://localhost:1/v1", "m")
        p = cl.charge_utile([{"role": "user", "content": "x"}], outils=[{"type": "function"}],
                            echantillonnage={"temperature": 1.0, "top_k": 64}, max_tokens=100)
        self.assertEqual((p["temperature"], p["top_k"], p["max_tokens"], p["tool_choice"]), (1.0, 64, 100, "auto"))
        self.assertTrue(p["stream"])

    def test_sans_outils_pas_de_tool_choice(self):
        p = c.Client("http://localhost:1/v1", "m").charge_utile([], None, None, None)
        self.assertNotIn("tools", p)
        self.assertNotIn("max_tokens", p)


class ServeurLocal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a): pass
            def do_POST(self):
                n = int(self.headers["Content-Length"])
                self.server.dernier = json.loads(self.rfile.read(n))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                for l in [evt({"content": "Salut"}), evt(fin="stop", usage={"prompt_tokens": 3, "completion_tokens": 1}), "data: [DONE]"]:
                    self.wfile.write((l + "\n\n").encode())
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"data": [{"id": "alias", "root": "depot/modele", "max_model_len": 4096}]}).encode())
        cls.srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_address[1]}/v1"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_completer(self):
        r = c.Client(self.url, "alias", cle="secret").completer([{"role": "user", "content": "hi"}])
        self.assertEqual(r.texte, "Salut")
        self.assertEqual(self.srv.dernier["model"], "alias")

    def test_infos_serveur(self):
        self.assertEqual(c.Client(self.url, "alias").infos_serveur(),
                         {"modele_servi": "depot/modele", "alias": "alias", "contexte_max": 4096})


class Catalogue(unittest.TestCase):
    def test_le_catalogue_est_valide(self):
        self.assertEqual(catalogue.verifier(), [])

    def test_charger(self):
        e = catalogue.charger("gemma-4-12b-nvfp4-redhatai")
        self.assertEqual(e["quantification"], "NVFP4")
        self.assertEqual(e["echantillonnage"]["top_k"], 64)

    def test_modele_inconnu(self):
        with self.assertRaises(KeyError):
            catalogue.charger("inconnu")


if __name__ == "__main__":
    unittest.main()
