import math
import re
import unicodedata
from collections import Counter

PARAMETRES = {"methode": "bm25", "k": 6, "k1": 1.5, "b": 0.75, "decoupage": "un passage par document"}

_VIDES = set("""a au aux avec ce ces dans de des du elle en et il ils je la le les leur lui ma mais me meme mes moi
mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous
c d j l m n s t y est sont ete etre avoir a ont fait selon quel quelle quels quelles quand combien comment
pourquoi""".split())


def jetons(texte: str) -> list:
    texte = unicodedata.normalize("NFKD", texte.lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    mots = re.findall(r"[a-z0-9]+", texte)
    return [m[:-1] if len(m) > 3 and m.endswith("s") else m for m in mots if m not in _VIDES]


def corps_sans_bandeau(corps: str) -> str:
    return "\n".join(l for l in corps.splitlines() if not (len(l) < 140 and l.lstrip("*").startswith("DOCUMENT FICTIF"))).strip()


def passage(doc: dict) -> str:
    m = doc["meta"]
    return f"[Document : {m['titre']} | {m['date']} | {m['statut'].replace('_', ' ')}]\n{corps_sans_bandeau(doc['corps'])}"


class Index:
    def __init__(self, docs: dict, k1=PARAMETRES["k1"], b=PARAMETRES["b"], usage="rag"):
        self.k1, self.b = k1, b
        docs = {i: d for i, d in docs.items() if usage in d.get("usage", ["chat", "rag", "agentique"])}
        self.ids = sorted(docs)
        self.tf = {i: Counter(jetons(docs[i]["meta"]["titre"] + " " + corps_sans_bandeau(docs[i]["corps"]))) for i in self.ids}
        self.longueur = {i: sum(self.tf[i].values()) for i in self.ids}
        self.moyenne = sum(self.longueur.values()) / max(len(self.ids), 1)
        df = Counter(t for i in self.ids for t in self.tf[i])
        n = len(self.ids)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def rechercher(self, requete: str, k: int = PARAMETRES["k"]) -> list:
        termes = jetons(requete)
        notes = []
        for i in self.ids:
            s = 0.0
            for t in termes:
                f = self.tf[i].get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.longueur[i] / self.moyenne))
            if s > 0:
                notes.append((-s, i))
        return [i for _, i in sorted(notes)[:k]]


def rappel(attendus: list, recuperes: list):
    if not attendus:
        return None
    return sum(1 for a in attendus if a in recuperes) / len(attendus)


def rang_reciproque(attendus: list, recuperes: list):
    if not attendus:
        return None
    rangs = [recuperes.index(a) + 1 for a in attendus if a in recuperes]
    return 1 / min(rangs) if rangs else 0.0
