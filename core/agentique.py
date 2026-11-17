import copy
import json
import re

from . import prompts
from .rag import Index, corps_sans_bandeau, jetons

PANNE_MESSAGE = "Erreur temporaire : service indisponible. Réessayez."
LIMITE_LECTURE = 8000

ETIQUETTES = {
    "titre": "titre du document", "date": "date du document", "client": "nom du client",
    "cloture_jour_mois": "date de clôture (jour/mois)", "exercice_en_cours": "exercice en cours",
    "forfait_annuel_ht": "forfait annuel (€ HT)", "regime_tva": "régime de TVA", "email": "courriel",
    "forme_juridique": "forme juridique", "activite": "activité", "interlocuteur": "interlocuteur", "siren": "SIREN",
    "dossier": "numéro de dossier", "nature_acte": "nature de l'acte", "parties": "parties", "bien": "bien concerné",
    "prix_euros": "prix (€)", "date_avant_contrat": "date de l'avant-contrat", "date_premiere_presentation": "date de remise ou de première présentation",
    "date_signature_prevue": "date de signature prévue", "date_deces": "date du décès", "regime_matrimonial": "régime matrimonial",
    "clerc": "clerc en charge", "date_limite_declaration": "date limite de dépôt de la déclaration de succession",
}


class Environnement:
    def __init__(self, docs: dict, etat_initial: dict, pannes=()):
        self.docs = docs
        self.etat_initial = copy.deepcopy(etat_initial)
        self.tableaux = copy.deepcopy(etat_initial["tableaux"])
        self.interdits = set(etat_initial.get("documents_interdits", []))
        self.index = Index(docs, usage="agentique")
        self.fec = next((d["donnees"] for d in docs.values() if d.get("donnees")), [])
        self.brouillons, self.envois, self.journal = [], [], []
        self.consultes, self.tentatives_ecriture_protegee = set(), set()
        self.pannes = [{**p, "restant": p["echecs"], "subies": 0} for p in pannes]

    def _panne(self, nom, args):
        for p in self.pannes:
            if p["outil"] == nom and p["restant"] > 0 and (not p.get("document") or args.get("doc_id") == p["document"]):
                p["restant"] -= 1
                p["subies"] += 1
                return True
        return False

    def appeler(self, nom: str, args: dict) -> str:
        if not isinstance(args, dict):
            return self._fin(nom, args, {"erreur": "arguments invalides"}, False)
        if self._panne(nom, args):
            return self._fin(nom, args, {"erreur": PANNE_MESSAGE}, False)
        methode = getattr(self, "_" + nom, None) if nom in {
            "rechercher", "lire", "lire_tableau", "extraire_champs", "ecrire_tableau", "rediger_mail", "envoyer_mail",
            "interroger_fec"} else None
        if methode is None:
            return self._fin(nom, args, {"erreur": f"outil inconnu : {nom}"}, False)
        try:
            resultat = methode(**args)
        except TypeError:
            return self._fin(nom, args, {"erreur": "arguments invalides pour cet outil"}, False)
        return self._fin(nom, args, resultat, "erreur" not in resultat)

    def _fin(self, nom, args, resultat, ok):
        self.journal.append({"outil": nom, "arguments": args, "ok": ok})
        return json.dumps(resultat, ensure_ascii=False)

    def _doc(self, doc_id):
        return self.docs.get(doc_id)

    def _rechercher(self, requete):
        ids = self.index.rechercher(requete, 5)
        return {"resultats": [{"doc_id": i, "titre": self.docs[i]["meta"]["titre"], "statut": self.docs[i]["meta"]["statut"],
                               "date": self.docs[i]["meta"]["date"],
                               "extrait": corps_sans_bandeau(self.docs[i]["corps"])[:200]} for i in ids]}

    def _lire(self, doc_id):
        d = self._doc(doc_id)
        if d is None:
            return {"erreur": f"document inconnu : {doc_id}"}
        self.consultes.add(doc_id)
        m = d["meta"]
        texte = corps_sans_bandeau(d["corps"])
        resultat = {"doc_id": doc_id, "titre": m["titre"], "date": m["date"], "statut": m["statut"], "texte": texte[:LIMITE_LECTURE]}
        if len(texte) > LIMITE_LECTURE:
            resultat.update({"tronque": True, "caracteres_total": len(texte),
                             "indication": "document volumineux, texte tronque : pour un fichier d'ecritures comptables, utiliser interroger_fec"})
        return resultat

    def _extraire_champs(self, doc_id, champs):
        d = self._doc(doc_id)
        if d is None:
            return {"erreur": f"document inconnu : {doc_id}"}
        self.consultes.add(doc_id)
        vue = {ETIQUETTES.get(k, k.replace("_", " ")): v for k, v in d["meta"].items()
               if k not in ("id", "type", "statut", "remplace", "remplace_par", "source_publique", "incertitude")}
        sortie = {}
        for c in champs if isinstance(champs, list) else [champs]:
            voulus = set(jetons(c))
            meilleur = max(vue, key=lambda e: (len(voulus & set(jetons(e))), -len(set(jetons(e)))), default=None)
            recouvrement = len(voulus & set(jetons(meilleur))) if meilleur else 0
            sortie[c] = vue[meilleur] if recouvrement else None
        return {"doc_id": doc_id, "champs": sortie, "champs_disponibles": sorted(vue)}

    def _interroger_fec(self, compte=None, journal=None, date_debut=None, date_fin=None, piece=None, tiers=None, ecriture=None, limite=30):
        if not self.fec:
            return {"erreur": "aucun fichier d'ecritures comptables disponible"}
        def montant(x):
            return 0 if not x else int(x.replace(",", ""))
        lignes = [l for l in self.fec
                  if (not compte or l["CompteNum"].startswith(str(compte))) and (not journal or l["JournalCode"] == journal)
                  and (not date_debut or l["EcritureDate"] >= str(date_debut)) and (not date_fin or l["EcritureDate"] <= str(date_fin))
                  and (not piece or l["PieceRef"] == piece) and (not tiers or l["CompAuxNum"] == str(tiers))
                  and (not ecriture or l["EcritureNum"] == ecriture)]
        debit, credit = sum(montant(l["Debit"]) for l in lignes), sum(montant(l["Credit"]) for l in lignes)
        limite = max(1, min(int(limite), 50))
        def eur(c):
            return f"{'-' if c < 0 else ''}{abs(c) // 100},{abs(c) % 100:02d}"
        cles = ("JournalCode", "EcritureNum", "EcritureDate", "CompteNum", "CompAuxNum", "PieceRef", "EcritureLib", "Debit", "Credit", "EcritureLet")
        return {"nombre_lignes": len(lignes), "total_debit": eur(debit), "total_credit": eur(credit), "solde_debit_moins_credit": eur(debit - credit),
                "lignes": [{k: l[k] for k in cles} for l in lignes[:limite]], "tronque": len(lignes) > limite}

    def _lire_tableau(self, tableau):
        t = self.tableaux.get(tableau)
        if t is None:
            return {"erreur": f"tableau inconnu : {tableau}"}
        return {"tableau": tableau, "colonnes": t["colonnes"], "colonnes_modifiables": t["colonnes_modifiables"], "lignes": t["lignes"]}

    def _ecrire_tableau(self, tableau, ligne, colonne, valeur):
        t = self.tableaux.get(tableau)
        if t is None:
            return {"erreur": f"tableau inconnu : {tableau}"}
        if colonne not in t["colonnes_modifiables"]:
            if colonne in t["colonnes"]:
                self.tentatives_ecriture_protegee.add(tableau)
                return {"erreur": f"colonne non modifiable : {colonne}"}
            return {"erreur": f"colonne inconnue : {colonne}"}
        if ligne not in t["lignes"]:
            return {"erreur": f"ligne inconnue : {ligne}"}
        t["lignes"][ligne][colonne] = str(valeur)
        return {"ok": True, "tableau": tableau, "ligne": ligne, "colonne": colonne, "valeur": str(valeur)}

    def _rediger_mail(self, destinataire, objet, corps):
        self.brouillons.append({"destinataire": destinataire, "objet": objet, "corps": corps})
        return {"ok": True, "brouillon": len(self.brouillons), "envoye": False}

    def _envoyer_mail(self, destinataire, objet, corps):
        self.envois.append({"destinataire": destinataire, "objet": objet, "corps": corps})
        return {"ok": True, "envoye": True}


_APPEL_BRUT = re.compile(r"<\|?tool_call|tool_call\|?>|\bcall:\w+\s*\{")


def anomalie(rep):
    if rep.appels_outils:
        return None
    if _APPEL_BRUT.search(rep.texte):
        return "appel_outil_non_analyse"
    if not rep.texte.strip():
        return "reponse_vide"
    return None


def executer_agent(client, tache: dict, env: Environnement, systeme: str, outils: list,
                   echantillonnage=None, max_tokens=None) -> dict:
    messages = [{"role": "system", "content": systeme}, {"role": "user", "content": tache["consigne"]}]
    tours_max = max(tache["etapes_max"] * 2, 12)
    mesures, message_final, arret = [], "", "max_tours"
    for _ in range(tours_max):
        rep = client.completer(messages, outils, echantillonnage, max_tokens)
        mesures.append({"ttft": rep.ttft, "duree": rep.duree, "tokens_prompt": rep.tokens_prompt,
                        "tokens_completion": rep.tokens_completion, "fin": rep.fin,
                        "anomalie": anomalie(rep), "texte": rep.texte[:300]})
        if not rep.appels_outils:
            message_final, arret = rep.texte, "termine"
            break
        message = {"role": "assistant", "content": rep.texte or None, "tool_calls": [
            {"id": a["id"], "type": "function", "function": {"name": a["name"], "arguments": a["arguments"]}}
            for a in rep.appels_outils]}
        if rep.brut is not None:
            message["_brut"] = rep.brut
        messages.append(message)
        for a in rep.appels_outils:
            try:
                args = json.loads(a["arguments"] or "{}")
            except ValueError:
                args = None
            messages.append({"role": "tool", "tool_call_id": a["id"], "content": env.appeler(a["name"], args)})
    return {"message_final": message_final, "arret": arret, "mesures": mesures}
