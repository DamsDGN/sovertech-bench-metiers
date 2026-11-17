import re

BANDEAU = "DOCUMENT FICTIF"


def lire_source(chemin):
    texte = chemin.read_text(encoding="utf-8").splitlines()
    meta, i = {}, 0
    if texte and texte[0].strip() == "---":
        i = 1
        while texte[i].strip() != "---":
            if ":" in texte[i]:
                k, v = texte[i].split(":", 1)
                meta[k.strip()] = v.strip()
            i += 1
        i += 1
    return meta, blocs(texte[i:])


def _cellules(ligne):
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def blocs(lignes):
    sortie, i = [], 0
    while i < len(lignes):
        l = lignes[i].rstrip()
        if not l.strip():
            i += 1
        elif l.startswith("# "):
            sortie.append(("h1", l[2:].strip())); i += 1
        elif l.startswith("## "):
            sortie.append(("h2", l[3:].strip())); i += 1
        elif l.startswith("|"):
            lot = []
            while i < len(lignes) and lignes[i].startswith("|"):
                lot.append(lignes[i]); i += 1
            rangees = [_cellules(x) for x in lot if not re.fullmatch(r"\|[\s:|-]+\|?", x.strip())]
            sortie.append(("table", rangees))
        elif re.match(r"^[-*] ", l):
            lot = []
            while i < len(lignes) and re.match(r"^[-*] ", lignes[i]):
                lot.append(lignes[i][2:].strip()); i += 1
            sortie.append(("ul", lot))
        elif re.match(r"^\d+\. ", l):
            lot = []
            while i < len(lignes) and re.match(r"^\d+\. ", lignes[i]):
                lot.append(re.sub(r"^\d+\. ", "", lignes[i]).strip()); i += 1
            sortie.append(("ol", lot))
        else:
            sortie.append(("p", l.strip())); i += 1
    return sortie


def sans_gras(texte):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", texte)


def vers_reportlab(texte):
    t = texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def segments_gras(texte):
    morceaux = re.split(r"(\*\*.+?\*\*)", texte)
    return [(m[2:-2], True) if m.startswith("**") and m.endswith("**") else (m, False) for m in morceaux if m]


def sans_euro(texte):
    return re.sub(r"\s*€\s*$", "", texte).strip()
