import json
import os
import time

from .client import Client, ErreurClient, Reponse

FIN_ANTHROPIC = {"end_turn": "stop", "tool_use": "tool_calls", "max_tokens": "length", "stop_sequence": "stop"}
MAX_TOKENS_ANTHROPIC = 16000


def convertir_outils(outils: list) -> list:
    return [{"name": o["function"]["name"], "description": o["function"]["description"],
             "input_schema": o["function"]["parameters"]} for o in outils]


def convertir_messages(messages: list):
    systeme, sortie = None, []
    for m in messages:
        role = m["role"]
        if role == "system":
            systeme = m["content"]
        elif role == "user":
            sortie.append({"role": "user", "content": m["content"]})
        elif role == "assistant":
            if m.get("_brut") is not None:
                contenu = m["_brut"]
            else:
                contenu = [{"type": "text", "text": m["content"]}] if m.get("content") else []
                contenu += [{"type": "tool_use", "id": tc["id"], "name": tc["function"]["name"],
                             "input": json.loads(tc["function"]["arguments"] or "{}")} for tc in m.get("tool_calls", [])]
            sortie.append({"role": "assistant", "content": contenu})
        elif role == "tool":
            bloc = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}
            if m["content"].startswith('{"erreur"'):
                bloc["is_error"] = True
            dernier = sortie[-1] if sortie else None
            if dernier and dernier["role"] == "user" and isinstance(dernier["content"], list) \
                    and dernier["content"] and dernier["content"][0].get("type") == "tool_result":
                dernier["content"].append(bloc)
            else:
                sortie.append({"role": "user", "content": [bloc]})
    return systeme, sortie


class ClientAnthropic:
    def __init__(self, modele: str, reglages: dict | None = None, sdk=None, delai: float = 900):
        if sdk is None:
            try:
                import anthropic
            except ImportError:
                raise ErreurClient("le paquet 'anthropic' est requis pour ce modele : pip install anthropic") from None
            sdk = anthropic.Anthropic(timeout=delai)
        self.sdk, self.modele, self.reglages = sdk, modele, reglages or {}

    def infos_serveur(self) -> dict:
        return {"modele_servi": self.modele, "alias": self.modele, "contexte_max": None}

    def completer(self, messages, outils=None, echantillonnage=None, max_tokens=None) -> Reponse:
        systeme, msgs = convertir_messages(messages)
        params = {"model": self.modele, "max_tokens": max(max_tokens or 0, MAX_TOKENS_ANTHROPIC), "messages": msgs}
        if systeme:
            params["system"] = systeme
        if outils:
            params["tools"] = convertir_outils(outils)
        if self.reglages.get("effort"):
            params["output_config"] = {"effort": self.reglages["effort"]}
        t0, ttft = time.monotonic(), None
        try:
            with self.sdk.messages.stream(**params) as flux:
                for evt in flux:
                    if ttft is None and getattr(evt, "type", "") == "content_block_delta":
                        ttft = time.monotonic() - t0
                final = flux.get_final_message()
        except Exception as e:
            code = getattr(e, "status_code", None)
            raise ErreurClient(f"{type(e).__name__}" + (f" (HTTP {code})" if code else "") + f" : {str(e)[:200]}") from e
        rep = Reponse(ttft=ttft, duree=time.monotonic() - t0)
        rep.brut = [b.model_dump(mode="json") for b in final.content]
        for b in final.content:
            if b.type == "text":
                rep.texte += b.text
            elif b.type == "tool_use":
                rep.appels_outils.append({"id": b.id, "name": b.name, "arguments": json.dumps(b.input, ensure_ascii=False)})
        rep.texte = rep.texte.strip()
        rep.fin = FIN_ANTHROPIC.get(final.stop_reason, final.stop_reason)
        rep.tokens_prompt = final.usage.input_tokens
        rep.tokens_completion = final.usage.output_tokens
        return rep


def creer_client(entree: dict, env=None):
    env = os.environ if env is None else env
    fournisseur = entree.get("fournisseur")
    if fournisseur == "anthropic":
        if not env.get("ANTHROPIC_API_KEY"):
            raise ErreurClient("ANTHROPIC_API_KEY absente de l'environnement")
        return ClientAnthropic(entree["modele_api"], entree.get("reglages_api"))
    if fournisseur == "openai":
        if not env.get("OPENAI_API_KEY"):
            raise ErreurClient("OPENAI_API_KEY absente de l'environnement")
        reglages = entree.get("reglages_api", {})
        return Client(reglages.get("base_url", "https://api.openai.com/v1"), entree["modele_api"], env["OPENAI_API_KEY"],
                      nom_max_tokens=reglages.get("nom_max_tokens", "max_completion_tokens"))
    base, modele = env.get("BENCH_BASE_URL"), env.get("BENCH_MODEL")
    if not base or not modele:
        raise ErreurClient("definir BENCH_BASE_URL et BENCH_MODEL (BENCH_API_KEY et BENCH_CA_CERT sont facultatifs)")
    return Client(base, modele, env.get("BENCH_API_KEY"), env.get("BENCH_CA_CERT"))
