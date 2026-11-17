import datetime
import json
import re
from pathlib import Path

from . import verifications as vf

RACINE = Path(__file__).resolve().parent.parent
BORNES_V0 = (15, 24)
JOURS_RELANCE = 45
JOURS_RETRACTATION = 10
JOURS_CONVOCATION = 15
JOURS_ALERTE_SUCCESSION = 60

STATUTS_DOC = {"en_vigueur", "obsolete"}
TYPES_DOC = {"procedure", "fiche_client", "note", "facture", "devis", "tarif", "charte", "texte_public", "interne",
             "lettre_mission", "piece_comptable", "courriel", "fec",
             "fiche_dossier", "acte", "avant_contrat", "etat_civil", "releve_foncier", "decompte", "statuts", "procuration"}
USAGES_PAR_DEFAUT = ["chat", "rag", "agentique"]
COLONNES_FEC = ["JournalCode", "JournalLib", "EcritureNum", "EcritureDate", "CompteNum", "CompteLib", "CompAuxNum", "CompAuxLib",
                "PieceRef", "PieceDate", "EcritureLib", "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise"]
NIVEAUX = {"simple", "moyen", "complexe"}
GRAVITES = ("faible", "moyenne", "elevee", "critique")
TYPES_RAG = {"reponse_directe", "version_obsolete", "contradiction", "sans_reponse", "plusieurs_documents",
             "reponse_partielle"}
OUTILS = {"rechercher", "lire", "lire_tableau", "extraire_champs", "ecrire_tableau", "rediger_mail", "envoyer_mail", "interroger_fec"}
CHAMPS_VALIDATION = {"relu_par", "date", "commentaire"}

_COURRIEL = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")
_IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,}")
_TELEPHONE = re.compile(r"(?<!\d)(?:\+33|0033|0)\s?[1-9](?:[\s.-]?\d{2}){4}(?!\d)")
_NEUF_CHIFFRES = re.compile(r"(?<!\d)\d{3} ?\d{3} ?\d{3}(?!\d)")
_NUMERO_SECU = re.compile(r"(?<!\d)[12] ?\d{2} ?(?:0[1-9]|1[0-2]) ?\d{2} ?\d{3} ?\d{3} ?\d{2}(?!\d)")


def luhn_valide(numero: str) -> bool:
    chiffres = [int(c) for c in numero if c.isdigit()]
    if not chiffres:
        return False
    total = 0
    for i, c in enumerate(reversed(chiffres)):
        if i % 2 == 1:
            c *= 2
            if c > 9:
                c -= 9
        total += c
    return total % 10 == 0


def lire_mots_interdits(chemin: Path) -> list:
    if not chemin.exists():
        return []
    lignes = (l.strip() for l in chemin.read_text(encoding="utf-8").splitlines())
    return [l for l in lignes if l and not l.startswith("#")]


def parser_document(texte: str):
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        raise ValueError("entete absente (premiere ligne attendue : ---)")
    meta = {}
    for i in range(1, len(lignes)):
        if lignes[i].strip() == "---":
            return meta, "\n".join(lignes[i + 1:])
        if ":" in lignes[i]:
            cle, valeur = lignes[i].split(":", 1)
            meta[cle.strip()] = valeur.strip()
    raise ValueError("entete non terminee")


def charger_jsonl(chemin: Path) -> list:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def lire_fec(chemin: Path) -> list:
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    en_tete = lignes[0].split("\t")
    return [dict(zip(en_tete, l.split("\t"))) for l in lignes[1:] if l.strip()]


MOTEURS_EXTRACTION = {"tika": "extractions", "docling": "extractions-docling"}


def charger_documents(metier: str, racine: Path = RACINE, extraction: str = "tika") -> dict:
    if extraction not in MOTEURS_EXTRACTION:
        raise ValueError(f"moteur d'extraction inconnu : {extraction!r} (attendus : {sorted(MOTEURS_EXTRACTION)})")
    base = racine / metier
    corpus = base / "corpus"
    formats = json.loads((corpus / "formats.json").read_text(encoding="utf-8")) if (corpus / "formats.json").exists() else {}
    documents = {}
    for f in sorted((corpus / "sources").glob("*.md")):
        meta, corps_source = parser_document(f.read_text(encoding="utf-8"))
        id_ = meta.get("id", f.stem)
        spec = formats.get(id_, {})
        texte_extrait = corpus / MOTEURS_EXTRACTION[extraction] / f"{id_}.txt"
        doc = {"meta": meta, "corps_source": corps_source, "fichier": f.name, "format": spec.get("format"),
               "degradation": spec.get("degradation"), "usage": spec.get("usage", USAGES_PAR_DEFAUT),
               "corps": texte_extrait.read_text(encoding="utf-8") if texte_extrait.exists() else corps_source}
        if meta.get("type") == "fec":
            doc["donnees"] = lire_fec(corpus / "fichiers" / f"{id_}.{spec['format']}")
        documents[id_] = doc
    return documents


def charger_metier(metier: str, racine: Path = RACINE, extraction: str = "tika") -> dict:
    base = racine / metier
    documents = charger_documents(metier, racine, extraction)
    env = base / "agentique" / "environnement" / "etat_initial.json"
    return {
        "documents": documents,
        "chat": charger_jsonl(base / "chat" / "taches.jsonl"),
        "rag": charger_jsonl(base / "rag" / "questions.jsonl"),
        "agentique": charger_jsonl(base / "agentique" / "taches.jsonl"),
        "environnement": json.loads(env.read_text(encoding="utf-8")),
    }


def verifier_documents(docs: dict, mots_interdits=()) -> list:
    erreurs = []
    for id_, d in docs.items():
        meta, corps = d["meta"], d.get("corps_source", d["corps"])
        nom = f"document {id_}"
        for champ in ("id", "titre", "type", "date", "statut"):
            if not meta.get(champ):
                erreurs.append(f"{nom} : champ {champ} manquant")
        if meta.get("id") and meta["id"] != id_:
            erreurs.append(f"{nom} : id different de la cle")
        if "fichier" in d and meta.get("id") and d["fichier"] != meta["id"] + ".md":
            erreurs.append(f"{nom} : le nom de fichier doit etre {meta['id']}.md")
        if meta.get("type") and meta["type"] not in TYPES_DOC:
            erreurs.append(f"{nom} : type {meta['type']!r} inconnu")
        if meta.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
            erreurs.append(f"{nom} : date au format AAAA-MM-JJ attendue")
        statut = meta.get("statut")
        if statut and statut not in STATUTS_DOC:
            erreurs.append(f"{nom} : statut {statut!r} inconnu")
        if statut == "obsolete":
            cible = meta.get("remplace_par")
            if not cible:
                erreurs.append(f"{nom} : obsolete sans remplace_par")
            elif cible not in docs:
                erreurs.append(f"{nom} : remplace_par {cible!r} n'existe pas")
            elif docs[cible]["meta"].get("statut") != "en_vigueur":
                erreurs.append(f"{nom} : le remplacant {cible!r} doit etre en vigueur")
        if meta.get("type") == "texte_public":
            if not meta.get("source_publique"):
                erreurs.append(f"{nom} : texte_public sans source_publique")
        elif "DOCUMENT FICTIF" not in corps:
            erreurs.append(f"{nom} : la mention DOCUMENT FICTIF est obligatoire")
        if meta.get("type") == "fiche_client":
            siren = re.sub(r"\s", "", meta.get("siren", ""))
            if siren.isdigit() and luhn_valide(siren):
                erreurs.append(f"{nom} : SIREN valide, il doit etre fictif (invalide au controle de Luhn)")
        texte = corps + "\n" + "\n".join(str(v) for v in meta.values())
        for m in _COURRIEL.finditer(texte):
            if not m.group(1).lower().endswith(".example"):
                erreurs.append(f"{nom} : courriel hors domaine .example ({m.group(0)})")
        if _IBAN.search(texte):
            erreurs.append(f"{nom} : IBAN interdit")
        if _TELEPHONE.search(texte):
            erreurs.append(f"{nom} : numero de telephone interdit")
        if _NUMERO_SECU.search(texte):
            erreurs.append(f"{nom} : numero de securite sociale interdit")
        for m in _NEUF_CHIFFRES.finditer(texte):
            if luhn_valide(m.group(0)):
                erreurs.append(f"{nom} : nombre a 9 chiffres valide au controle de Luhn ({m.group(0)})")
        bas = texte.lower()
        for mot in mots_interdits:
            if mot.lower() in bas:
                erreurs.append(f"{nom} : mot interdit present")
    return erreurs


def _commun(t, prefixe, vus, erreurs):
    id_ = t.get("id", "?")
    nom = f"{prefixe} {id_}"
    if not re.fullmatch(prefixe_motif(prefixe), str(id_)):
        erreurs.append(f"{nom} : identifiant mal forme")
    if id_ in vus:
        erreurs.append(f"{nom} : identifiant en double")
    vus.add(id_)
    if t.get("niveau") not in NIVEAUX:
        erreurs.append(f"{nom} : niveau {t.get('niveau')!r} inconnu")
    if not t.get("theme"):
        erreurs.append(f"{nom} : theme manquant")
    if t.get("gravite") not in GRAVITES:
        erreurs.append(f"{nom} : gravite {t.get('gravite')!r} inconnue (attendues : {', '.join(GRAVITES)})")
    if not isinstance(t.get("a_valider_par_pro"), bool):
        erreurs.append(f"{nom} : a_valider_par_pro doit etre un booleen")
    sv = t.get("statut_validation")
    if not isinstance(sv, dict) or set(sv) != CHAMPS_VALIDATION:
        erreurs.append(f"{nom} : statut_validation doit avoir les champs {sorted(CHAMPS_VALIDATION)}")
    elif t.get("a_valider_par_pro") is False and not (sv.get("relu_par") and sv.get("date")):
        erreurs.append(f"{nom} : validee sans relu_par et date")
    if not isinstance(t.get("source_publique"), list):
        erreurs.append(f"{nom} : source_publique doit etre une liste")
    if t.get("incertitude") is not None and not isinstance(t["incertitude"], str):
        erreurs.append(f"{nom} : incertitude doit etre None ou un texte")
    return nom


def prefixe_motif(prefixe):
    return {"chat": r"CH-\d{2}", "rag": r"RG-\d{2}", "agentique": r"AG-\d{2}"}[prefixe]


def _bornes(taches, bornes, prefixe, erreurs):
    if not bornes[0] <= len(taches) <= bornes[1]:
        erreurs.append(f"{prefixe} : nombre de taches {len(taches)} hors des bornes {bornes}")


def _verifier_verifications(t, nom, erreurs):
    verifs = t.get("verifications", [])
    valides = True
    for v in verifs:
        type_v = v.get("type")
        if type_v not in vf.TYPES:
            erreurs.append(f"{nom} : verification {type_v!r} inconnue")
            valides = False
            continue
        manquants = vf.champs_obligatoires(type_v) - set(v)
        if manquants:
            erreurs.append(f"{nom} : verification {type_v} sans {sorted(manquants)[0]}")
            valides = False
    if valides and t.get("reponse_modele"):
        for v, ok in vf.evaluer_toutes(verifs, t["reponse_modele"]):
            if not ok:
                erreurs.append(f"{nom} : la reponse_modele echoue a la verification {v['type']}")
    if valides and t.get("reponse_fautive") is not None:
        if all(ok for _, ok in vf.evaluer_toutes(verifs, t["reponse_fautive"])):
            erreurs.append(f"{nom} : la reponse_fautive passe toutes les verifications")


def verifier_taches_chat(taches, docs, bornes=BORNES_V0) -> list:
    erreurs, vus = [], set()
    _bornes(taches, bornes, "chat", erreurs)
    for t in taches:
        nom = _commun(t, "chat", vus, erreurs)
        for champ in ("consigne", "reference", "reponse_modele"):
            if not t.get(champ):
                erreurs.append(f"{nom} : {champ} manquant")
        for doc_id in t.get("contexte", []):
            if doc_id not in docs:
                erreurs.append(f"{nom} : document de contexte {doc_id!r} inexistant")
        suite = t.get("suite", [])
        if not isinstance(suite, list) or not all(isinstance(x, str) and x.strip() for x in suite):
            erreurs.append(f"{nom} : suite doit etre une liste de messages non vides")
        verifs = t.get("verifications", [])
        if not verifs and not t.get("criteres_juge"):
            erreurs.append(f"{nom} : ni verifications ni criteres_juge")
        _verifier_verifications(t, nom, erreurs)
        if t.get("abstention_attendue") is True and not any(
                v.get("type") == "abstention" and v.get("attendue") is True for v in verifs):
            erreurs.append(f"{nom} : abstention_attendue exige la verification abstention")
    return erreurs


def verifier_questions_rag(questions, docs, bornes=BORNES_V0) -> list:
    erreurs, vus = [], set()
    _bornes(questions, bornes, "rag", erreurs)
    for q in questions:
        nom = _commun(q, "rag", vus, erreurs)
        type_q = q.get("type_question")
        if type_q not in TYPES_RAG:
            erreurs.append(f"{nom} : type_question {type_q!r} inconnu")
        for champ in ("question", "reference", "reponse_modele"):
            if not q.get(champ):
                erreurs.append(f"{nom} : {champ} manquant")
        _verifier_verifications(q, nom, erreurs)
        if q.get("abstention_attendue") is True and not any(
                v.get("type") == "abstention" and v.get("attendue") is True for v in q.get("verifications", [])):
            erreurs.append(f"{nom} : une question avec abstention attendue exige la verification abstention")
        attendus = q.get("documents_attendus", [])
        for doc_id in attendus + q.get("documents_pieges", []):
            if doc_id not in docs:
                erreurs.append(f"{nom} : document {doc_id!r} inexistant")
        for doc_id in attendus:
            if doc_id in docs and docs[doc_id]["meta"].get("statut") != "en_vigueur":
                erreurs.append(f"{nom} : le document attendu {doc_id!r} doit etre en vigueur")
        if q.get("abstention_attendue") != (type_q in ("sans_reponse", "reponse_partielle")):
            erreurs.append(f"{nom} : abstention_attendue doit valoir vrai si et seulement si sans_reponse ou reponse_partielle")
        if type_q == "sans_reponse":
            if attendus:
                erreurs.append(f"{nom} : sans_reponse ne doit citer aucun document attendu")
        else:
            if not attendus:
                erreurs.append(f"{nom} : aucun document attendu")
            if not q.get("verifications"):
                erreurs.append(f"{nom} : verifications vides")
        if type_q in ("contradiction", "plusieurs_documents") and len(attendus) < 2:
            erreurs.append(f"{nom} : {type_q} demande au moins deux documents attendus")
        if type_q == "version_obsolete":
            pieges = [p for p in q.get("documents_pieges", []) if p in docs and docs[p]["meta"].get("statut") == "obsolete"]
            if not pieges or not q.get("valeurs_obsoletes"):
                erreurs.append(f"{nom} : version_obsolete exige un document piege obsolete et valeurs_obsoletes")
        texte = vf.normaliser("\n".join(docs[i]["corps"] for i in attendus if i in docs))
        for element in q.get("elements_documents", []):
            if vf.normaliser(element) not in texte:
                erreurs.append(f"{nom} : l'element {element!r} n'est pas dans les documents attendus")
    return erreurs


def _jours_apres(date_jj_mm_aaaa: str, jours: int) -> str:
    return _jours_avant(date_jj_mm_aaaa, -jours)


def _jours_avant(date_jj_mm_aaaa: str, jours: int) -> str:
    j, m, a = (int(x) for x in date_jj_mm_aaaa.split("/"))
    return (datetime.date(a, m, j) - datetime.timedelta(days=jours)).strftime("%d/%m/%Y")


def _valeurs_fiche(meta: dict) -> dict:
    cloture = f"{meta['cloture_jour_mois']}/{meta['exercice_en_cours']}"
    return {
        "Date de clôture": cloture,
        "Date de relance": _jours_avant(cloture, JOURS_RELANCE),
        "Forfait HT": meta["forfait_annuel_ht"],
    }


def faits_fec(docs: dict) -> dict:
    """Valeurs attendues dans les cellules de synthese, recalculees depuis le FEC (analyse independante du generateur)."""
    rows = next((d["donnees"] for d in docs.values() if d.get("donnees")), [])
    if not rows:
        return {}
    m = lambda x: 0 if not x else int(x.replace(",", ""))
    eur = lambda c: f"{c // 100},{abs(c) % 100:02d}"
    pieces = {}
    for r in rows:
        if r["JournalCode"] == "AC" and r["CompteNum"] == "607":
            pieces.setdefault(r["PieceRef"], set()).add(r["EcritureNum"])
    doubles = sorted(p for p, e in pieces.items() if len(e) > 1)
    return {
        "Total des ventes 2025 (compte 707)": eur(sum(m(r["Credit"]) - m(r["Debit"]) for r in rows if r["CompteNum"] == "707")),
        "Solde du compte d'attente 471": eur(sum(m(r["Debit"]) - m(r["Credit"]) for r in rows if r["CompteNum"] == "471")),
        "Facture saisie en double (référence de pièce)": doubles[0] if len(doubles) == 1 else None,
    }


def _controle_notaire(docs: dict):
    """Dates derivees des fiches de dossier : fin du delai de retractation, convocation a la signature."""
    fiches = {d["meta"]["dossier"]: d["meta"] for d in docs.values()
              if d["meta"].get("type") == "fiche_dossier" and d["meta"].get("dossier")}

    def valeur_attendue(tab, ligne, colonne):
        if tab == "suivi_dossiers" and ligne in fiches:
            m = fiches[ligne]
            if colonne == "Fin du délai de rétractation" and m.get("date_premiere_presentation"):
                v = _jours_apres(m["date_premiere_presentation"], JOURS_RETRACTATION)
                return v, f"la fiche donne {v!r} ({JOURS_RETRACTATION} jours apres la premiere presentation)"
            if colonne == "Date de convocation" and m.get("date_signature_prevue"):
                v = _jours_avant(m["date_signature_prevue"], JOURS_CONVOCATION)
                return v, f"la fiche donne {v!r} ({JOURS_CONVOCATION} jours avant la signature)"
            if colonne == "Alerte déclaration de succession" and m.get("date_limite_declaration"):
                v = _jours_avant(m["date_limite_declaration"], JOURS_ALERTE_SUCCESSION)
                return v, f"la fiche donne {v!r} ({JOURS_ALERTE_SUCCESSION} jours avant la date limite de declaration)"
            if colonne == "Nature de l'acte" and m.get("nature_acte"):
                return m["nature_acte"], f"la fiche donne {m['nature_acte']!r}"
            if colonne == "Date de signature prévue" and m.get("date_signature_prevue"):
                return m["date_signature_prevue"], f"la fiche donne {m['date_signature_prevue']!r}"
        return None
    return valeur_attendue


def _controle_expert_comptable(docs: dict):
    """Cellules attendues recalculees depuis les documents : renvoie (valeur attendue, explication) ou None."""
    fiches = {d["meta"]["client"]: d["meta"] for d in docs.values()
              if d["meta"].get("type") == "fiche_client" and d["meta"].get("client")}
    fec = faits_fec(docs)

    def valeur_attendue(tab, ligne, colonne):
        if tab == "synthese" and ligne in fec:
            return fec[ligne], f"le FEC donne {fec[ligne]!r}"
        if tab == "synthese" and ligne == "Total des forfaits annuels HT":
            total = str(sum(int(f["forfait_annuel_ht"]) for f in fiches.values()))
            return total, f"les fiches donnent {total!r}"
        if tab == "suivi_cloture" and ligne in fiches and colonne in _valeurs_fiche(fiches[ligne]):
            attendu = _valeurs_fiche(fiches[ligne])[colonne]
            motif = f" ({JOURS_RELANCE} jours avant la cloture)" if colonne == "Date de relance" else ""
            return attendu, f"la fiche donne {attendu!r}{motif}"
        return None
    return valeur_attendue


CONTROLES_METIER = {"expert-comptable": _controle_expert_comptable, "notaire": _controle_notaire}


def verifier_taches_agentique(taches, docs, env, bornes=BORNES_V0, controle=None) -> list:
    erreurs, vus = [], set()
    _bornes(taches, bornes, "agentique", erreurs)
    controle = controle or _controle_expert_comptable(docs)
    tableaux = env.get("tableaux", {})
    interdits = set(env.get("documents_interdits", []))
    texte_total = "\n".join(d["corps"] + " " + " ".join(d["meta"].values()) for d in docs.values())
    for t in taches:
        nom = _commun(t, "agentique", vus, erreurs)
        if not t.get("consigne"):
            erreurs.append(f"{nom} : consigne manquante")
        if not isinstance(t.get("etapes_max"), int) or t["etapes_max"] <= 0:
            erreurs.append(f"{nom} : etapes_max doit etre un entier positif")
        for o in t.get("outils_attendus", []):
            if o not in OUTILS:
                erreurs.append(f"{nom} : outil attendu {o!r} inconnu")
        for a in t.get("actions_interdites", []):
            if a == "envoyer_mail":
                continue
            kind, _, cible = a.partition(":")
            if kind == "lire" and (cible in interdits or cible in docs):
                continue
            if kind == "ecrire" and cible in tableaux:
                continue
            erreurs.append(f"{nom} : action interdite {a!r} inconnue")
        for p in t.get("pannes", []):
            if p.get("outil") not in OUTILS:
                erreurs.append(f"{nom} : panne sur l'outil {p.get('outil')!r} inconnu")
            if not isinstance(p.get("echecs"), int) or p["echecs"] <= 0:
                erreurs.append(f"{nom} : panne sans nombre d'echecs positif")
        etat = t.get("etat_final_attendu", {})
        if etat.get("envois") != 0:
            erreurs.append(f"{nom} : etat_final_attendu.envois doit valoir 0")
        for tab, lignes in etat.get("tableaux", {}).items():
            if tab not in tableaux:
                erreurs.append(f"{nom} : tableau {tab!r} inexistant")
                continue
            for ligne, cellules in lignes.items():
                if ligne not in tableaux[tab]["lignes"]:
                    erreurs.append(f"{nom} : ligne {ligne!r} inexistante dans {tab}")
                    continue
                for colonne, valeur in cellules.items():
                    if colonne not in tableaux[tab]["colonnes"]:
                        erreurs.append(f"{nom} : colonne {colonne!r} inexistante dans {tab}")
                    elif colonne not in tableaux[tab]["colonnes_modifiables"]:
                        erreurs.append(f"{nom} : colonne {colonne!r} non modifiable dans {tab}")
                    else:
                        attendu = controle(tab, ligne, colonne)
                        if attendu is not None and valeur != attendu[0]:
                            erreurs.append(f"{nom} : {ligne}/{colonne} vaut {valeur!r}, {attendu[1]}")
        for b in etat.get("brouillons", []):
            for cle in ("objet_ne_contient", "corps_ne_contient"):
                if cle in b and not (isinstance(b[cle], list) and all(isinstance(x, str) and x for x in b[cle])):
                    erreurs.append(f"{nom} : {cle} doit etre une liste de textes non vides")
            if b.get("destinataire") and b["destinataire"] not in texte_total:
                erreurs.append(f"{nom} : destinataire {b['destinataire']!r} absent du corpus")
        msg = t.get("message_final_attendu")
        if msg is not None:
            for v in msg.get("verifications", []):
                if v.get("type") not in vf.TYPES:
                    erreurs.append(f"{nom} : verification du message final {v.get('type')!r} inconnue")
    return erreurs


SIGNATURES = {"docx": b"PK", "xlsx": b"PK", "doc": bytes.fromhex("D0CF11E0"), "xls": bytes.fromhex("D0CF11E0"), "pdf": b"%PDF"}
FORMATS_REQUIS = {"csv", "xls", "xlsx", "doc", "docx", "pdf", "txt"}


def _sha256(octets: bytes) -> str:
    import hashlib
    return hashlib.sha256(octets).hexdigest()


def _montants_balance(corps_source: str) -> dict:
    sortie = {}
    for l in corps_source.splitlines():
        cellules = [c.strip() for c in l.strip().strip("|").split("|")]
        if l.startswith("|") and len(cellules) == 4 and cellules[0].isdigit():
            nombre = lambda x: int(x.replace(" ", "").replace(",", "")) if x else 0
            sortie[cellules[0]] = nombre(cellules[2]) - nombre(cellules[3])
    return sortie


def verifier_fec(metier: str, id_: str, docs: dict, racine: Path = RACINE) -> list:
    corpus = racine / metier / "corpus"
    spec = json.loads((corpus / "formats.json").read_text(encoding="utf-8"))[id_]
    chemin = corpus / "fichiers" / f"{id_}.{spec['format']}"
    erreurs, nom = [], f"FEC {id_}"
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    if lignes[0].split("\t") != COLONNES_FEC:
        return [f"{nom} : l'en-tete n'a pas les 18 colonnes attendues dans l'ordre"]
    for i, l in enumerate(lignes[1:], start=2):
        if len(l.split("\t")) != 18:
            erreurs.append(f"{nom} : ligne {i} avec {len(l.split(chr(9)))} colonnes au lieu de 18")
    rows = lire_fec(chemin)
    for r in rows:
        for champ in ("EcritureDate", "PieceDate", "ValidDate"):
            if r[champ] and not re.fullmatch(r"2025\d{4}", r[champ]):
                erreurs.append(f"{nom} : {champ} {r[champ]!r} hors format ou hors exercice ({r['EcritureNum']})")
    montant = lambda x: 0 if not x else int(x.replace(",", ""))
    soldes, ecritures = {}, {}
    for r in rows:
        soldes[r["CompteNum"]] = soldes.get(r["CompteNum"], 0) + montant(r["Debit"]) - montant(r["Credit"])
        e = ecritures.setdefault(r["EcritureNum"], 0)
        ecritures[r["EcritureNum"]] = e + montant(r["Debit"]) - montant(r["Credit"])
    verites = json.loads((corpus / f"{id_}.verites.json").read_text(encoding="utf-8"))
    if {c: v for c, v in verites["solde_par_compte_cents"].items()} != soldes:
        erreurs.append(f"{nom} : les soldes par compte ne correspondent pas a {id_}.verites.json")
    desequilibrees = {n: v for n, v in ecritures.items() if v}
    if desequilibrees != {n: v for n, v in verites["ecritures_desequilibrees"].items()}:
        erreurs.append(f"{nom} : ecritures desequilibrees differentes des verites ({desequilibrees})")
    if len(ecritures) != verites["nombre_ecritures"] or len(rows) != verites["nombre_lignes"]:
        erreurs.append(f"{nom} : nombre de lignes ou d'ecritures different des verites")
    for source_id, doc in docs.items():
        if source_id.startswith("balance-") and id_.split("-")[-1] in source_id:
            for compte, solde in _montants_balance(doc["corps_source"]).items():
                if abs(soldes.get(compte, 0)) != abs(solde):
                    erreurs.append(f"{nom} : le compte {compte} vaut {soldes.get(compte, 0)} centimes, la balance {source_id} donne {solde}")
    return erreurs


def verifier_variante_extraction(metier: str, moteur: str, racine: Path = RACINE) -> list:
    corpus = racine / metier / "corpus"
    manifeste_chemin = corpus / f"MANIFESTE-{moteur}.json"
    dossier = corpus / MOTEURS_EXTRACTION[moteur]
    if not manifeste_chemin.exists() and not dossier.exists():
        return []
    if not manifeste_chemin.exists() or not dossier.exists():
        return [f"extraction {moteur} : dossier et manifeste doivent exister ensemble"]
    erreurs = []
    manifeste = json.loads(manifeste_chemin.read_text(encoding="utf-8"))["documents"]
    formats = {k for k in json.loads((corpus / "formats.json").read_text(encoding="utf-8")) if not k.startswith("_")}
    for id_ in sorted(formats - set(manifeste)):
        erreurs.append(f"extraction {moteur} : {id_} absent du manifeste")
    for id_, entree in sorted(manifeste.items()):
        chemin = dossier / f"{id_}.txt"
        fichier = corpus / "fichiers" / entree["fichier"]
        if not chemin.exists():
            erreurs.append(f"extraction {moteur} : texte de {id_} manquant")
            continue
        if chemin.stat().st_size == 0:
            erreurs.append(f"extraction {moteur} : texte de {id_} vide")
        if entree["sha256_extraction"] != _sha256(chemin.read_bytes()):
            erreurs.append(f"extraction {moteur} : le texte de {id_} a change depuis le manifeste")
        if fichier.exists() and entree["sha256_fichier"] != _sha256(fichier.read_bytes()):
            erreurs.append(f"extraction {moteur} : le fichier {id_} a change depuis l'extraction (relancer outils/extraire_corpus.py {moteur})")
    return erreurs


TRACES_DE_MACHINE = (b"/home/", b"C:\\Users\\", b"/Users/", b"\\Users\\")


def verifier_fichiers(metier: str, docs: dict, racine: Path = RACINE, mots_interdits=()) -> list:
    corpus = racine / metier / "corpus"
    erreurs = []
    formats = {k: v for k, v in json.loads((corpus / "formats.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
    manifeste = json.loads((corpus / "MANIFESTE.json").read_text(encoding="utf-8"))["documents"]
    for id_ in set(docs) - set(formats):
        erreurs.append(f"corpus : {id_} n'a pas de format dans formats.json")
    for id_ in set(formats) - set(docs):
        erreurs.append(f"corpus : formats.json cite {id_}, qui n'a pas de source")
    for id_, spec in sorted(formats.items()):
        nom = f"fichier {id_}"
        fichier = corpus / "fichiers" / f"{id_}.{spec['format']}"
        extraction = corpus / "extractions" / f"{id_}.txt"
        if not fichier.exists() or not extraction.exists():
            erreurs.append(f"{nom} : fichier ou extraction manquant")
            continue
        octets = fichier.read_bytes()
        bas = octets.lower()
        for trace in TRACES_DE_MACHINE:
            if trace.lower() in bas:
                erreurs.append(f"{nom} : trace d'une machine ou d'un utilisateur dans les metadonnees ({trace.decode()})")
        for mot in mots_interdits:
            if mot.lower().encode("utf-8") in bas or mot.lower().encode("utf-16-le") in bas:
                erreurs.append(f"{nom} : mot interdit present dans le fichier")
        signature = SIGNATURES.get(spec["format"])
        if signature and not octets.startswith(signature):
            erreurs.append(f"{nom} : le contenu n'est pas un vrai fichier {spec['format']}")
        if spec.get("degradation"):
            if spec["format"] != "pdf" or b"/Font" in octets or b"/Image" not in octets:
                erreurs.append(f"{nom} : un document degrade doit etre un PDF image seule, sans couche texte")
        entree = manifeste.get(id_)
        if not entree:
            erreurs.append(f"{nom} : absent du manifeste d'extraction")
        else:
            if entree["sha256_fichier"] != _sha256(octets):
                erreurs.append(f"{nom} : le fichier a change depuis l'extraction (relancer outils/extraire_corpus.py)")
            if entree["sha256_extraction"] != _sha256(extraction.read_bytes()):
                erreurs.append(f"{nom} : l'extraction a change depuis le manifeste")
    exigences = json.loads((corpus / "formats.json").read_text(encoding="utf-8")).get("_exigences", {})
    requis = set(exigences.get("formats", FORMATS_REQUIS))
    utilises = {s["format"] for s in formats.values()}
    if requis - utilises:
        erreurs.append(f"corpus : formats absents {sorted(requis - utilises)}")
    if sum(1 for s in formats.values() if s.get("degradation")) < exigences.get("documents_degrades_min", 2):
        erreurs.append(f"corpus : au moins {exigences.get('documents_degrades_min', 2)} documents degrades sont attendus")
    if not any(s["format"] == "pdf" and not s.get("degradation") for s in formats.values()):
        erreurs.append("corpus : au moins un PDF propre est attendu")
    for id_, doc in docs.items():
        if doc["meta"].get("type") == "fec" and id_ in formats and (corpus / "fichiers" / f"{id_}.{formats[id_]['format']}").exists():
            erreurs += verifier_fec(metier, id_, docs, racine)
    return erreurs


def verifier_metier(metier: str, racine: Path = RACINE) -> list:
    jeux = charger_metier(metier, racine)
    mots = lire_mots_interdits(racine / ".mots-interdits.txt")
    docs = jeux["documents"]
    exigences = json.loads((racine / metier / "corpus" / "formats.json").read_text(encoding="utf-8")).get("_exigences", {})
    bornes = tuple(exigences.get("bornes_taches", BORNES_V0))
    fabrique = CONTROLES_METIER.get(metier)
    controle = fabrique(docs) if fabrique else None
    return (
        verifier_fichiers(metier, docs, racine, mots)
        + verifier_variante_extraction(metier, "docling", racine)
        + verifier_documents(docs, mots)
        + verifier_taches_chat(jeux["chat"], docs, bornes)
        + verifier_questions_rag(jeux["rag"], docs, bornes)
        + verifier_taches_agentique(jeux["agentique"], docs, jeux["environnement"], bornes, controle)
    )
