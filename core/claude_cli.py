"""Client qui interroge Claude par le CLI `claude -p` (abonnement), sans clé d'API.

Chaque appel lance un processus neuf, depuis un dossier temporaire vide et neutre, sans aucun outil, sans
mémoire, sans hooks, sans serveur MCP, avec le prompt système du benchmark. Le modèle ne peut donc ni lire
le dépôt (réponses de référence comprises) ni agir sur la machine.

Écarts avec un appel d'API direct, à déclarer dans tout résultat obtenu ainsi :
- le CLI ajoute son propre contexte fixe (environnement : système, shell) ;
- les appels d'outils sont émulés en texte (blocs <appel>), pas par le mécanisme natif de l'API ;
- une conversation à plusieurs tours est rejouée sous forme de transcription dans un seul message ;
- le raisonnement et l'échantillonnage ne se règlent pas comme avec l'API.
"""
import json
import os
import re
import subprocess
import tempfile
import time

from .client import ErreurClient, Reponse

FIN_CLI = {"end_turn": "stop", "max_tokens": "length", "stop_sequence": "stop", "tool_use": "tool_calls"}
_APPEL = re.compile(r"<appel>\s*(.*?)\s*</appel>", re.S)
PROTOCOLE_OUTILS = (
    "\n\nTu disposes des outils ci-dessous. Pour appeler un ou plusieurs outils, écris pour chacun un bloc "
    '<appel>{"name": "nom_de_l_outil", "arguments": {...}}</appel>, puis arrête-toi : les résultats te seront '
    "rendus au tour suivant. Quand tu as terminé, réponds en texte simple, sans aucun bloc <appel>.\n\nOutils :\n"
)


def decrire_outils(outils: list) -> str:
    lignes = []
    for o in outils:
        f = o["function"]
        lignes.append(f"- {f['name']} : {f['description']}\n  paramètres (JSON Schema) : {json.dumps(f['parameters'], ensure_ascii=False)}")
    return PROTOCOLE_OUTILS + "\n".join(lignes)


def _bloc_appel(nom: str, arguments) -> str:
    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
    except ValueError:
        args = {}
    return "<appel>" + json.dumps({"name": nom, "arguments": args or {}}, ensure_ascii=False) + "</appel>"


def construire_invite(messages: list):
    """Renvoie (prompt système, message utilisateur). Un échange simple est transmis tel quel ; sinon la
    conversation est rejouée sous forme de transcription et le modèle écrit le prochain tour."""
    systeme = next((m["content"] for m in messages if m["role"] == "system"), "")
    echanges = [m for m in messages if m["role"] != "system"]
    if len(echanges) == 1 and echanges[0]["role"] == "user":
        return systeme, echanges[0]["content"]
    morceaux = []
    for m in echanges:
        if m["role"] == "user":
            morceaux.append(f"[Utilisateur]\n{m['content']}")
        elif m["role"] == "assistant":
            texte = m.get("content") or ""
            appels = "\n".join(_bloc_appel(tc["function"]["name"], tc["function"]["arguments"]) for tc in m.get("tool_calls", []))
            morceaux.append("[Assistant]\n" + "\n".join(x for x in (texte, appels) if x))
        elif m["role"] == "tool":
            morceaux.append(f"[Résultat de l'outil, appel {m['tool_call_id']}]\n{m['content']}")
    morceaux.append("Écris uniquement le prochain tour de l'assistant.")
    return systeme, "\n\n".join(morceaux)


def lire_appels(texte: str, depart: int = 0):
    """Sépare le texte libre et les blocs <appel> (JSON invalide : le bloc reste dans le texte)."""
    appels = []

    def remplacer(m):
        try:
            donnees = json.loads(m.group(1))
            nom, args = donnees["name"], donnees.get("arguments") or {}
            if not isinstance(nom, str) or not isinstance(args, dict):
                raise ValueError
        except (ValueError, KeyError, TypeError):
            return m.group(0)
        appels.append({"id": f"appel_{depart + len(appels)}", "name": nom, "arguments": json.dumps(args, ensure_ascii=False)})
        return ""
    reste = _APPEL.sub(remplacer, texte).strip()
    return reste, appels


def lancer_cli(systeme: str, message: str, modele: str, effort: str | None, max_tokens: int | None, delai: float) -> dict:
    cmd = ["claude", "-p", "--tools", "", "--system-prompt", systeme, "--model", modele,
           "--no-session-persistence", "--disable-slash-commands", "--setting-sources", "",
           "--strict-mcp-config", "--output-format", "json"]
    if effort:
        cmd += ["--effort", effort]
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "LC_ALL", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME")}
    if max_tokens:
        env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] = str(max_tokens)
    with tempfile.TemporaryDirectory(prefix="iso-") as dossier:
        try:
            r = subprocess.run(cmd, input=message, capture_output=True, text=True, timeout=delai, cwd=dossier, env=env)
        except subprocess.TimeoutExpired:
            raise ErreurClient("claude -p : delai depasse") from None
        except OSError as e:
            raise ErreurClient(f"claude -p impossible a lancer : {e}") from e
    if r.returncode != 0:
        raise ErreurClient(f"claude -p a echoue (code {r.returncode}) : {(r.stderr or r.stdout)[:200].strip()}")
    try:
        return json.loads(r.stdout)
    except ValueError:
        raise ErreurClient(f"claude -p : sortie illisible : {r.stdout[:200]}") from None


class ClientClaudeCli:
    def __init__(self, modele: str, reglages: dict | None = None, lanceur=None, delai: float = 900, tentatives: int = 2):
        self.modele, self.reglages, self.delai, self.tentatives = modele, reglages or {}, delai, tentatives
        self.lanceur = lanceur or lancer_cli
        self._appels = 0

    def infos_serveur(self) -> dict:
        return {"modele_servi": self.modele, "alias": self.modele, "contexte_max": None,
                "voie": "claude -p (abonnement), session isolee sans outils"}

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None) -> Reponse:
        systeme, message = construire_invite(messages)
        if outils:
            systeme += decrire_outils(outils)
        derniere = None
        t0 = time.monotonic()
        for essai in range(self.tentatives):
            try:
                sortie = self.lanceur(systeme, message, self.modele, self.reglages.get("effort"), max_tokens, self.delai)
                if sortie.get("is_error"):
                    raise ErreurClient(f"claude -p : {str(sortie.get('result'))[:200]}")
                break
            except ErreurClient as e:
                derniere = e
                if essai + 1 < self.tentatives:
                    time.sleep(2 * (essai + 1))
        else:
            raise derniere
        rep = Reponse(duree=time.monotonic() - t0)
        texte = sortie.get("result") or ""
        if outils:
            texte, appels = lire_appels(texte, self._appels)
            self._appels += len(appels)
            rep.appels_outils = appels
        rep.texte = texte.strip()
        rep.fin = "tool_calls" if rep.appels_outils else FIN_CLI.get(sortie.get("stop_reason"), sortie.get("stop_reason"))
        u = sortie.get("usage") or {}
        rep.tokens_prompt = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
        rep.tokens_completion = u.get("output_tokens")
        return rep
