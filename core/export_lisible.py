import sys
from pathlib import Path

from . import donnees as d

LIBELLES_GRAVITE = {"faible": "faible", "moyenne": "moyenne", "elevee": "élevée", "critique": "critique"}

TYPES_RAG = {
    "reponse_directe": "Réponse directe dans un document",
    "version_obsolete": "Piège : une ancienne version dit autre chose",
    "contradiction": "Piège : les documents se contredisent",
    "sans_reponse": "Piège : la réponse n'est dans aucun document",
    "plusieurs_documents": "Il faut combiner plusieurs documents",
    "reponse_partielle": "Piège : une partie seulement de la réponse figure dans les documents",
}


THEMES = {
    "controle_condition_suspensive": "contrôle d'une condition suspensive de prêt",
    "coordonnees": "coordonnées d'une personne",
    "fiches_dossiers": "fiches de dossier",
    "organisation_etude": "organisation de l'étude",
    "pieces_dossier": "pièces d'un dossier",
    "procedure_vente": "procédure de vente immobilière",
    "prudence_juridique": "prudence sur un point de droit",
    "societes": "constitution d'une société",
    "succession": "succession",
    "suivi_et_procedure": "suivi d'un dossier selon la procédure",
    "tarifs": "tarifs",
    "abstention": "savoir dire qu'on ne sait pas",
    "agregation_fiches": "regrouper des informations de plusieurs fiches",
    "analyse_balance": "lecture d'une balance",
    "injection_dans_document": "instruction cachée dans un document",
    "pieces_contradictoires": "pièces contradictoires",
    "rapprochement_bancaire": "rapprochement bancaire",
    "rapprochement_et_brouillon": "rapprochement bancaire puis courriel",
    "reponse_client": "répondre à un client mécontent",
    "relance_et_honoraires": "relances et honoraires de relance",
    "reponse_partielle": "réponse partielle",
    "suivi_multi_clients": "suivi de plusieurs clients",
    "synthese_multi_documents": "synthèse de plusieurs documents",
    "tarifs_et_calcul": "tarifs et calcul",
    "action_interdite_envoi": "action interdite : envoyer un courriel",
    "brouillon_courriel": "préparer un courriel sans l'envoyer",
    "calcul": "calcul",
    "calcul_date": "calcul de date",
    "calcul_et_version": "calcul et version en vigueur",
    "calcul_multi_documents": "calcul à partir de plusieurs documents",
    "consigne_stricte": "respect d'une consigne stricte",
    "contradiction": "documents contradictoires",
    "controle_fec": "contrôle d'un fichier des écritures comptables (FEC)",
    "controle_fec_et_courriel": "contrôle du FEC puis courriel",
    "interrogation_fec": "interrogation du FEC",
    "delais_clients": "délais de réponse aux clients",
    "detection_erreur": "détection d'une erreur",
    "document_confidentiel": "document confidentiel à ne pas consulter",
    "ecritures_multiples": "plusieurs écritures dans un tableau",
    "fiches_clients": "fiches clients",
    "filtre_et_ecritures": "filtrer puis écrire",
    "honoraires": "honoraires",
    "information_absente": "information absente",
    "invention": "ne pas inventer",
    "lecture_donnees": "lecture de données",
    "pedagogie": "pédagogie",
    "plan_comptable": "plan comptable",
    "procedure_cloture": "procédure de clôture",
    "prudence_reglementaire": "prudence sur un point réglementaire",
    "recherche_et_ecriture": "chercher puis écrire",
    "redaction_courriel": "rédaction d'un courriel",
    "redaction_courrier": "rédaction d'un courrier",
    "reformulation": "reformulation",
    "relance_pieces": "relance des pièces manquantes",
    "reprise_apres_panne": "reprise après une panne d'outil",
    "resume": "résumé",
    "sans_reponse": "question sans réponse",
    "tache_complete": "tâche complète en plusieurs étapes",
    "textes_publics": "textes publics",
    "version_en_vigueur": "version en vigueur",
}


def decrire_verification(v: dict) -> str:
    t = v["type"]
    if t == "contient_un_de":
        return "la réponse contient l'une de ces formulations : " + " ; ".join(f"« {x} »" for x in v["valeurs"])
    if t == "ne_contient_aucun":
        return "la réponse ne contient aucune de ces formulations : " + " ; ".join(f"« {x} »" for x in v["valeurs"])
    if t == "mots_max":
        return f"la réponse fait au plus {v['max']} mots"
    if t == "puces":
        return f"la réponse comporte exactement {v['exact']} puces"
    if t == "liste_numerotee":
        return f"la réponse comporte une liste numérotée d'exactement {v['exact']} éléments"
    if t == "reponse_exacte":
        return "la réponse tient dans un seul mot : " + " ou ".join(f"« {x} »" for x in v["valeurs"])
    if t == "aucun_nombre_a_n_chiffres":
        return f"la réponse ne contient aucun nombre de {v['n']} chiffres (numéro inventé)"
    if t == "tableau_markdown":
        return f"la réponse est un tableau de {v['colonnes']} colonnes et {v['lignes']} lignes"
    if t == "abstention":
        return ("l'assistant dit qu'il ne sait pas ou que l'information manque" if v["attendue"]
                else "l'assistant répond au lieu de s'abstenir")
    raise ValueError(t)


def _entete(t: dict) -> list:
    lignes = [f"## {t['id']} · {THEMES.get(t['theme'], t['theme'])} · niveau {t['niveau']} · gravité proposée : {LIBELLES_GRAVITE[t['gravite']]}", ""]
    if t.get("a_valider_par_pro"):
        lignes.append("> **À valider par un professionnel** : cette tâche n'a pas encore été relue.")
    else:
        sv = t["statut_validation"]
        lignes.append(f"> Relue par {sv['relu_par']} le {sv['date']}. {sv.get('commentaire') or ''}".rstrip())
    lignes.append("")
    return lignes


def _pied(t: dict) -> list:
    lignes = []
    if t.get("source_publique"):
        lignes += ["**Source publique citée** : " + " ; ".join(t["source_publique"]), ""]
    if t.get("incertitude"):
        lignes += [f"**Point d'incertitude signalé par l'équipe** : {t['incertitude']}", ""]
    lignes += ["**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)", "", "---", ""]
    return lignes


def _verifs(t: dict) -> list:
    lignes = []
    if t.get("verifications"):
        lignes += ["**Contrôles automatiques**", ""] + [f"- {decrire_verification(v)}" for v in t["verifications"]] + [""]
    if t.get("criteres_juge"):
        lignes += ["**Critères du juge** (note de 0 à 2 par critère)", ""] + [f"- {c}" for c in t["criteres_juge"]] + [""]
    return lignes


def _citation(texte: str) -> list:
    return [f"> {l}" if l else ">" for l in texte.splitlines()] + [""]


def _titre(docs, id_):
    m = docs[id_]["meta"]
    return f"{m['titre']} ({m['statut'].replace('_', ' ')}, {m['date']})"


def exporter_chat(taches, docs) -> str:
    sortie = ["# Épreuve « Discuter » : tâches à relire", "",
              "Fichier généré automatiquement depuis `taches.jsonl` : ne le modifiez pas à la main. "
              "Pour chaque tâche, dites si elle est correcte, à corriger ou à supprimer "
              "(voir `CONTRIBUTING.md`).", ""]
    for t in taches:
        sortie += _entete(t) + ["**Énoncé posé à l'assistant**", ""] + _citation(t["consigne"])
        if t["contexte"]:
            sortie += ["**Documents fournis avec l'énoncé** : " + " ; ".join(_titre(docs, i) for i in t["contexte"]), ""]
        sortie += ["**Ce qu'on attend**", ""] + _citation(t["reference"]) + _verifs(t)
        sortie += ["**Exemple de bonne réponse**", ""] + _citation(t["reponse_modele"]) + _pied(t)
    return "\n".join(sortie)


def exporter_rag(questions, docs) -> str:
    sortie = ["# Épreuve « Chercher dans les dossiers » : questions à relire", "",
              "Fichier généré automatiquement depuis `questions.jsonl` : ne le modifiez pas à la main.", ""]
    for q in questions:
        sortie += _entete(q) + [f"**Type** : {TYPES_RAG[q['type_question']]}", "",
                                "**Question posée à l'assistant**", ""] + _citation(q["question"])
        if q["documents_attendus"]:
            sortie += ["**Documents où se trouve la réponse** : " + " ; ".join(_titre(docs, i) for i in q["documents_attendus"]), ""]
        if q["documents_pieges"]:
            sortie += ["**Documents « pièges »** : " + " ; ".join(_titre(docs, i) for i in q["documents_pieges"]), ""]
        sortie += ["**Ce qu'on attend**", ""] + _citation(q["reference"]) + _verifs(q)
        sortie += ["**Exemple de bonne réponse**", ""] + _citation(q["reponse_modele"]) + _pied(q)
    return "\n".join(sortie)


def _actions(a: str) -> str:
    if a == "envoyer_mail":
        return "envoyer un courriel (seuls les brouillons sont permis)"
    kind, _, cible = a.partition(":")
    return {"lire": f"consulter le document confidentiel « {cible} »", "ecrire": f"écrire dans le tableau « {cible} »"}[kind]


def exporter_agentique(taches, docs) -> str:
    sortie = ["# Épreuve « Agir » : tâches à relire", "",
              "Fichier généré automatiquement depuis `taches.jsonl` : ne le modifiez pas à la main.", ""]
    for t in taches:
        sortie += _entete(t) + ["**Consigne donnée à l'assistant**", ""] + _citation(t["consigne"])
        sortie += ["**Ce qu'on attend**", ""] + _citation(t["reference"])
        sortie += ["**État final vérifié automatiquement**", ""]
        etat = t["etat_final_attendu"]
        cellules = [f"- tableau « {tab} », ligne « {l} », colonne « {c} » : « {v} »"
                    for tab, lignes in etat["tableaux"].items() for l, cs in lignes.items() for c, v in cs.items()]
        sortie += cellules or ["- aucune cellule ne doit être modifiée"]
        for b in etat["brouillons"]:
            parties = [f"adressé à {b['destinataire']}"]
            if b["objet_contient"]:
                parties.append("objet mentionnant " + " / ".join(f"« {x} »" for x in b["objet_contient"]))
            if b["corps_contient"]:
                parties.append("texte mentionnant " + " / ".join(f"« {x} »" for x in b["corps_contient"]))
            sortie.append("- un brouillon de courriel " + ", ".join(parties))
        sortie += ["- aucun autre brouillon, aucun courriel envoyé", "- toute autre cellule reste inchangée", ""]
        if t.get("message_final_attendu"):
            sortie += ["**Réponse finale de l'assistant** : "
                       + " ; ".join(decrire_verification(v) for v in t["message_final_attendu"]["verifications"]), ""]
        sortie += ["**Actions interdites** (une seule suffit à pénaliser la tâche) : "
                   + " ; ".join(_actions(a) for a in t["actions_interdites"]), ""]
        if t["pannes"]:
            sortie += ["**Panne simulée** : " + " ; ".join(
                f"l'outil « {p['outil']} » échoue {p['echecs']} fois" + (f" sur « {p['document']} »" if p.get("document") else "")
                for p in t["pannes"]) + ". L'assistant doit réessayer ou contourner.", ""]
        sortie += [f"**Nombre d'étapes maximal avant pénalité** : {t['etapes_max']}", ""] + _pied(t)
    return "\n".join(sortie)


def generer(metier: str, racine: Path = d.RACINE) -> dict:
    jeux = d.charger_metier(metier, racine)
    docs = jeux["documents"]
    base = racine / metier
    return {
        base / "chat" / "TACHES.md": exporter_chat(jeux["chat"], docs),
        base / "rag" / "TACHES.md": exporter_rag(jeux["rag"], docs),
        base / "agentique" / "TACHES.md": exporter_agentique(jeux["agentique"], docs),
    }


def main(argv=None):
    metier = (argv or sys.argv[1:] or ["expert-comptable"])[0]
    for chemin, texte in generer(metier).items():
        chemin.write_text(texte, encoding="utf-8")
        print(f"écrit : {chemin.relative_to(d.RACINE)}")


if __name__ == "__main__":
    main()
