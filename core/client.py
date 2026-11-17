import http.client
import json
import re
import ssl
import time
import urllib.parse
from dataclasses import dataclass, field


class ErreurClient(Exception):
    pass


@dataclass
class Reponse:
    texte: str = ""
    raisonnement: str = ""
    appels_outils: list = field(default_factory=list)
    fin: str | None = None
    tokens_prompt: int | None = None
    tokens_completion: int | None = None
    ttft: float | None = None
    duree: float = 0.0

    @property
    def debit(self):
        if not self.tokens_completion or self.ttft is None:
            return None
        decodage = self.duree - self.ttft
        return self.tokens_completion / decodage if decodage > 0 else None


_REFLEXION = re.compile(r"<think>.*?</think>", re.S)


def nettoyer_reponse(texte: str) -> str:
    texte = _REFLEXION.sub("", texte)
    if "<think>" in texte:
        texte = texte.split("<think>")[0]
    return texte.strip()


def lire_flux(lignes, t0: float, horloge=time.monotonic) -> Reponse:
    rep = Reponse()
    appels = {}
    for brut in lignes:
        ligne = brut.decode("utf-8") if isinstance(brut, bytes) else brut
        ligne = ligne.strip()
        if not ligne.startswith("data:"):
            continue
        charge = ligne[5:].strip()
        if charge == "[DONE]":
            break
        evt = json.loads(charge)
        if evt.get("usage"):
            rep.tokens_prompt = evt["usage"].get("prompt_tokens")
            rep.tokens_completion = evt["usage"].get("completion_tokens")
        for choix in evt.get("choices", []):
            delta = choix.get("delta", {})
            contenu = delta.get("content")
            raisonnement = delta.get("reasoning_content") or delta.get("reasoning")
            if (contenu or raisonnement or delta.get("tool_calls")) and rep.ttft is None:
                rep.ttft = horloge() - t0
            if contenu:
                rep.texte += contenu
            if raisonnement:
                rep.raisonnement += raisonnement
            for tc in delta.get("tool_calls") or []:
                a = appels.setdefault(tc.get("index", 0), {"id": None, "name": "", "arguments": ""})
                if tc.get("id"):
                    a["id"] = tc["id"]
                f = tc.get("function") or {}
                if f.get("name"):
                    a["name"] += f["name"]
                if f.get("arguments"):
                    a["arguments"] += f["arguments"]
            if choix.get("finish_reason"):
                rep.fin = choix["finish_reason"]
    rep.appels_outils = [appels[i] for i in sorted(appels)]
    for i, a in enumerate(rep.appels_outils):
        a["id"] = a["id"] or f"appel_{i}"
    rep.texte = nettoyer_reponse(rep.texte)
    rep.duree = horloge() - t0
    return rep


class Client:
    def __init__(self, base_url: str, modele: str, cle: str | None = None, ca_cert: str | None = None,
                 delai: float = 900, tentatives: int = 3):
        u = urllib.parse.urlparse(base_url)
        self.https = u.scheme == "https"
        self.hote, self.port = u.hostname, u.port or (443 if self.https else 80)
        self.prefixe = u.path.rstrip("/")
        self.modele, self.cle, self.delai, self.tentatives = modele, cle, delai, tentatives
        self.contexte = ssl.create_default_context(cafile=ca_cert) if self.https else None

    def _connexion(self):
        if self.https:
            return http.client.HTTPSConnection(self.hote, self.port, timeout=self.delai, context=self.contexte)
        return http.client.HTTPConnection(self.hote, self.port, timeout=self.delai)

    def _entetes(self):
        e = {"Content-Type": "application/json"}
        if self.cle:
            e["Authorization"] = f"Bearer {self.cle}"
        return e

    def charge_utile(self, messages, outils=None, echantillonnage=None, max_tokens=None) -> dict:
        charge = {"model": self.modele, "messages": messages, "stream": True,
                  "stream_options": {"include_usage": True}}
        charge.update(echantillonnage or {})
        if max_tokens:
            charge["max_tokens"] = max_tokens
        if outils:
            charge["tools"] = outils
            charge["tool_choice"] = "auto"
        return charge

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None) -> Reponse:
        corps = json.dumps(self.charge_utile(messages, outils, echantillonnage, max_tokens))
        derniere = None
        for essai in range(self.tentatives):
            t0 = time.monotonic()
            conn = self._connexion()
            try:
                conn.request("POST", self.prefixe + "/chat/completions", body=corps, headers=self._entetes())
                r = conn.getresponse()
                if r.status >= 500 or r.status == 429:
                    derniere = f"HTTP {r.status}"
                elif r.status != 200:
                    raise ErreurClient(f"HTTP {r.status} : {r.read(300).decode('utf-8', 'replace')}")
                else:
                    return lire_flux(r, t0)
            except (OSError, http.client.HTTPException) as e:
                derniere = f"{type(e).__name__}"
            finally:
                conn.close()
            time.sleep(2 * (essai + 1))
        raise ErreurClient(f"echec apres {self.tentatives} tentatives ({derniere})")

    def infos_serveur(self) -> dict:
        conn = self._connexion()
        try:
            conn.request("GET", self.prefixe + "/models", headers=self._entetes())
            r = conn.getresponse()
            donnees = json.loads(r.read())
            m = (donnees.get("data") or [{}])[0]
            return {"modele_servi": m.get("root"), "alias": m.get("id"), "contexte_max": m.get("max_model_len")}
        except (OSError, ValueError, http.client.HTTPException):
            return {}
        finally:
            conn.close()
