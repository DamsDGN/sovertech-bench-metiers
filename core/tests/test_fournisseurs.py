import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

from core import agentique as ag
from core import catalogue, lancer
from core import donnees as d
from core import fournisseurs as f
from core.client import Client, ErreurClient, Reponse
from core.tests.test_lancer import JEUX, config, lire
from core.tests.test_moteur import DOCS, OUTILS, SYSTEME, TACHES

OUTIL_OPENAI = {"type": "function", "function": {"name": "lire", "description": "Lit.", "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}}, "required": ["doc_id"]}}}


class Conversion(unittest.TestCase):
    def test_outils(self):
        self.assertEqual(f.convertir_outils([OUTIL_OPENAI]), [{"name": "lire", "description": "Lit.", "input_schema": OUTIL_OPENAI["function"]["parameters"]}])

    def test_systeme_utilisateur_et_assistant_sans_brut(self):
        systeme, msgs = f.convertir_messages([
            {"role": "system", "content": "S"}, {"role": "user", "content": "Q"},
            {"role": "assistant", "content": None, "tool_calls": [{"id": "a", "type": "function", "function": {"name": "lire", "arguments": '{"doc_id": "x"}'}}]}])
        self.assertEqual(systeme, "S")
        self.assertEqual(msgs[0], {"role": "user", "content": "Q"})
        self.assertEqual(msgs[1]["content"], [{"type": "tool_use", "id": "a", "name": "lire", "input": {"doc_id": "x"}}])

    def test_resultats_d_outils_groupes_dans_un_seul_message(self):
        _, msgs = f.convertir_messages([
            {"role": "user", "content": "Q"},
            {"role": "assistant", "content": None, "tool_calls": []},
            {"role": "tool", "tool_call_id": "a", "content": '{"ok": true}'},
            {"role": "tool", "tool_call_id": "b", "content": '{"erreur": "panne"}'}])
        derniers = msgs[-1]
        self.assertEqual(derniers["role"], "user")
        self.assertEqual([b["tool_use_id"] for b in derniers["content"]], ["a", "b"])
        self.assertNotIn("is_error", derniers["content"][0])
        self.assertTrue(derniers["content"][1]["is_error"])

    def test_la_reponse_brute_est_renvoyee_telle_quelle(self):
        brut = [{"type": "thinking", "thinking": "", "signature": "sig"}, {"type": "tool_use", "id": "a", "name": "lire", "input": {}}]
        _, msgs = f.convertir_messages([{"role": "user", "content": "Q"}, {"role": "assistant", "content": None, "tool_calls": [], "_brut": brut}])
        self.assertEqual(msgs[1]["content"], brut)


def bloc(type_, **kw):
    b = NS(type=type_, **kw)
    b.model_dump = lambda mode="json", b=b: {k: v for k, v in vars(b).items() if k != "model_dump"}
    return b


class FluxFactice:
    def __init__(self, final, erreur=None):
        self.final, self.erreur = final, erreur
    def __enter__(self):
        if self.erreur:
            raise self.erreur
        return self
    def __exit__(self, *a):
        return False
    def __iter__(self):
        return iter([NS(type="message_start"), NS(type="content_block_delta")])
    def get_final_message(self):
        return self.final


class SdkFactice:
    def __init__(self, final=None, erreur=None):
        self.appels = []
        self.messages = NS(stream=lambda **kw: self.appels.append(kw) or FluxFactice(final, erreur))


class ClientAnthropicTest(unittest.TestCase):
    def final(self, contenu, stop="end_turn"):
        return NS(content=contenu, stop_reason=stop, usage=NS(input_tokens=120, output_tokens=45))

    def test_requete_sans_echantillonnage_avec_effort(self):
        sdk = SdkFactice(self.final([bloc("text", text=" Bonjour ")]))
        c = f.ClientAnthropic("claude-opus-5-5", {"effort": "medium"}, sdk=sdk)
        r = c.completer([{"role": "system", "content": "S"}, {"role": "user", "content": "Q"}], [OUTIL_OPENAI],
                        {"temperature": 1.0, "top_k": 64}, 4096)
        p = sdk.appels[0]
        self.assertEqual((p["model"], p["system"], p["output_config"]), ("claude-opus-5-5", "S", {"effort": "medium"}))
        self.assertGreaterEqual(p["max_tokens"], 16000)
        for interdit in ("temperature", "top_k", "top_p", "thinking", "tool_choice"):
            self.assertNotIn(interdit, p)
        self.assertEqual(p["tools"][0]["name"], "lire")
        self.assertEqual((r.texte, r.fin, r.tokens_prompt, r.tokens_completion), ("Bonjour", "stop", 120, 45))
        self.assertIsNotNone(r.ttft)

    def test_appel_d_outil_et_reponse_brute(self):
        sdk = SdkFactice(self.final([bloc("thinking", thinking="", signature="s"), bloc("tool_use", id="t1", name="lire", input={"doc_id": "x"})], "tool_use"))
        r = f.ClientAnthropic("m", sdk=sdk).completer([{"role": "user", "content": "Q"}], [OUTIL_OPENAI])
        self.assertEqual(r.fin, "tool_calls")
        self.assertEqual(r.appels_outils, [{"id": "t1", "name": "lire", "arguments": '{"doc_id": "x"}'}])
        self.assertEqual(r.brut[0]["type"], "thinking")

    def test_refus_et_plafond(self):
        for stop, attendu in [("refusal", "refusal"), ("max_tokens", "length")]:
            r = f.ClientAnthropic("m", sdk=SdkFactice(self.final([], stop))).completer([{"role": "user", "content": "Q"}])
            self.assertEqual(r.fin, attendu)

    def test_erreur_de_l_api_devient_une_erreur_client(self):
        class Erreur(Exception):
            status_code = 400
        with self.assertRaises(ErreurClient) as cm:
            f.ClientAnthropic("m", sdk=SdkFactice(erreur=Erreur("requete invalide"))).completer([{"role": "user", "content": "Q"}])
        self.assertIn("HTTP 400", str(cm.exception))


class Fabrique(unittest.TestCase):
    def test_cles_obligatoires(self):
        for fournisseur, variable in (("anthropic", "ANTHROPIC_API_KEY"), ("openai", "OPENAI_API_KEY")):
            with self.assertRaises(ErreurClient) as cm:
                f.creer_client({"fournisseur": fournisseur, "modele_api": "m"}, env={})
            self.assertIn(variable, str(cm.exception))

    def test_openai_utilise_max_completion_tokens_et_n_envoie_pas_le_prive(self):
        c = f.creer_client({"fournisseur": "openai", "modele_api": "m"}, env={"OPENAI_API_KEY": "k"})
        p = c.charge_utile([{"role": "assistant", "content": "x", "_brut": [1]}], None, {}, 100)
        self.assertEqual(p["max_completion_tokens"], 100)
        self.assertNotIn("max_tokens", p)
        self.assertNotIn("_brut", p["messages"][0])
        self.assertEqual(c.hote, "api.openai.com")

    def test_local_demande_l_adresse(self):
        with self.assertRaises(ErreurClient):
            f.creer_client({"id": "x"}, env={})
        self.assertIsInstance(f.creer_client({"id": "x"}, env={"BENCH_BASE_URL": "http://h:1/v1", "BENCH_MODEL": "m"}), Client)


class CatalogueEtalons(unittest.TestCase):
    def test_etalons_valides(self):
        self.assertEqual(catalogue.verifier(), [])
        self.assertTrue(catalogue.est_etalon(catalogue.charger("claude-opus-5-5-etalon")))
        self.assertFalse(catalogue.est_etalon(catalogue.charger("gemma-4-12b-nvfp4-redhatai")))

    def test_cout(self):
        e = catalogue.charger("claude-sonnet-5-5-etalon")
        self.assertAlmostEqual(catalogue.cout_usd(e, 1_000_000, 100_000), 2.0 + 1.0)
        self.assertIsNone(catalogue.cout_usd(catalogue.charger("gemma-4-12b-nvfp4-redhatai"), 10, 10))

    def test_etalon_sans_prix_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = dict(catalogue.charger("claude-opus-5-5-etalon"), id="x")
            del e["prix_mtok"]
            (Path(tmp) / "x.json").write_text(json.dumps(e), encoding="utf-8")
            self.assertTrue(any("prix_mtok" in m for m in catalogue.verifier(Path(tmp))))


class Budget(unittest.TestCase):
    class Cher:
        def __init__(self):
            self.appels = 0
        def infos_serveur(self):
            return {"modele_servi": "claude-sonnet-5-5"}
        def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None):
            self.appels += 1
            t = next(x for x in JEUX["chat"] if messages[1]["content"].endswith(x["consigne"]))
            return Reponse(texte=t["reponse_modele"], fin="stop", ttft=0.1, duree=0.5, tokens_prompt=1_000_000, tokens_completion=0)

    def test_la_passe_s_arrete_au_plafond(self):
        with tempfile.TemporaryDirectory() as tmp:
            sortie = Path(tmp) / "s"
            client = self.Cher()
            lancer.executer(config(modele_catalogue="claude-sonnet-5-5-etalon", blocs=["chat"], limite=5, passes=1, budget_usd=3.0),
                            client, JEUX, sortie, journal=lambda *_: None)
            enrs = lire(sortie)
            self.assertEqual(len(enrs), 2)
            self.assertEqual(client.appels, 2)
            self.assertAlmostEqual(enrs[0]["cout_usd"], 2.0)
            releve = json.loads((sortie / "releve.json").read_text(encoding="utf-8"))
            self.assertEqual(releve["arret_budget"]["derniere_tache"], "CH-03")
            self.assertAlmostEqual(releve["depense_usd"], 4.0)
            self.assertTrue(releve["etalon_cloud"])
            self.assertTrue(releve["comparable_aux_resultats_publies"])
            rapport = (sortie / "rapport.md").read_text(encoding="utf-8")
            for morceau in ("Étalon cloud", "plafond de dépense atteint", "coût réel moyen par tâche"):
                self.assertIn(morceau, rapport)

    def test_la_boucle_agent_conserve_la_reponse_brute(self):
        vues = []
        tache = TACHES["AG-01"]
        class Scenario:
            def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None):
                vues.append([dict(m) for m in messages])
                if len(vues) == 1:
                    return Reponse(appels_outils=[{"id": "t1", "name": "lire_tableau", "arguments": '{"tableau": "synthese"}'}],
                                   fin="tool_calls", brut=[{"type": "thinking", "signature": "s"}], duree=0.1, ttft=0.05)
                return Reponse(texte="fini", fin="stop", duree=0.1, ttft=0.05)
        env = ag.Environnement(DOCS, JEUX["environnement"], [])
        ag.executer_agent(Scenario(), tache, env, SYSTEME, OUTILS)
        assistant = next(m for m in vues[1] if m["role"] == "assistant")
        self.assertEqual(assistant["_brut"], [{"type": "thinking", "signature": "s"}])


if __name__ == "__main__":
    unittest.main()
