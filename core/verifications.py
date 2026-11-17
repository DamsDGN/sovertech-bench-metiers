import re

_ESPACES = "   "

TYPES = {
    "contient_un_de": {"valeurs"},
    "ne_contient_aucun": {"valeurs"},
    "mots_max": {"max"},
    "puces": {"exact"},
    "liste_numerotee": {"exact"},
    "reponse_exacte": {"valeurs"},
    "aucun_nombre_a_n_chiffres": {"n"},
    "tableau_markdown": {"colonnes", "lignes"},
    "abstention": {"attendue"},
}

_MARQUES_ABSTENTION = (
    "je ne sais pas",
    "je ne dispose pas",
    "je n'ai pas cette information",
    "je n'ai pas l'information",
    "ne figure pas",
    "ne figurent pas",
    "n'est pas indiqu",
    "ne sont pas indiqu",
    "n'est pas mentionn",
    "ne sont pas mentionn",
    "n'est pas précis",
    "n'apparaît pas",
    "n'apparait pas",
    "aucune information",
    "pas d'information",
    "ne contiennent pas",
    "ne contient pas",
    "ne permettent pas",
    "ne permet pas",
    "impossible de",
    "je ne peux pas",
    "ne donnent pas",
    "ne donne pas",
    "ne précisent pas",
    "ne précise pas",
    "ne mentionne pas",
    "ne mentionnent pas",
    "n'indique pas",
    "n'indiquent pas",
    "aucun numéro",
    "n'a pas été communiqué",
    "n'a été communiqué",
    "pas communiqué",
    "non communiqué",
    "non renseigné",
    "pas renseigné",
)


def champs_obligatoires(type_verif: str) -> set:
    return set(TYPES[type_verif])


def _normaliser(texte: str) -> str:
    for c in _ESPACES:
        texte = texte.replace(c, " ")
    return re.sub(r"[ \t]+", " ", texte).lower()


def _contient_un_de(verif, reponse):
    r = _normaliser(reponse)
    return any(_normaliser(v) in r for v in verif["valeurs"])


def _ne_contient_aucun(verif, reponse):
    r = _normaliser(reponse)
    return not any(_normaliser(v) in r for v in verif["valeurs"])


def _mots_max(verif, reponse):
    return len(reponse.split()) <= verif["max"]


def _compter_lignes(reponse, motif):
    return sum(1 for l in reponse.splitlines() if re.match(motif, l.strip()))


def _puces(verif, reponse):
    return _compter_lignes(reponse, r"^[-*•]\s+\S") == verif["exact"]


def _liste_numerotee(verif, reponse):
    return _compter_lignes(reponse, r"^\d+[.)]\s+\S") == verif["exact"]


def _reponse_exacte(verif, reponse):
    r = re.sub(r"^[\s«»\"'“”]+|[\s«»\"'“”.!]+$", "", reponse.strip()).lower()
    return r in {_normaliser(v) for v in verif["valeurs"]}


def _aucun_nombre_a_n_chiffres(verif, reponse):
    r = reponse
    for c in _ESPACES + " ":
        r = re.sub(r"(?<=\d)" + re.escape(c) + r"(?=\d)", "", r)
    return re.search(r"(?<!\d)\d{%d}(?!\d)" % verif["n"], r) is None


def _tableau_markdown(verif, reponse):
    lignes = [l.strip() for l in reponse.splitlines() if l.strip().startswith("|")]
    donnees = [l for l in lignes if not re.fullmatch(r"\|[\s:|-]+\|?", l)]
    if len(donnees) < 2:
        return False
    colonnes = {len(l.strip("|").split("|")) for l in donnees}
    return colonnes == {verif["colonnes"]} and len(donnees) - 1 == verif["lignes"]


def _abstention(verif, reponse):
    r = _normaliser(reponse)
    detectee = any(m in r for m in _MARQUES_ABSTENTION)
    return detectee == verif["attendue"]


_EVALUATEURS = {
    "contient_un_de": _contient_un_de,
    "ne_contient_aucun": _ne_contient_aucun,
    "mots_max": _mots_max,
    "puces": _puces,
    "liste_numerotee": _liste_numerotee,
    "reponse_exacte": _reponse_exacte,
    "aucun_nombre_a_n_chiffres": _aucun_nombre_a_n_chiffres,
    "tableau_markdown": _tableau_markdown,
    "abstention": _abstention,
}


def evaluer(verif: dict, reponse: str) -> bool:
    type_verif = verif.get("type")
    if type_verif not in _EVALUATEURS:
        raise ValueError(f"type de verification inconnu : {type_verif!r}")
    return _EVALUATEURS[type_verif](verif, reponse)


def evaluer_toutes(verifs: list, reponse: str) -> list:
    return [(v, evaluer(v, reponse)) for v in verifs]


normaliser = _normaliser
