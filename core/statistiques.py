import math
import random

GRAINE = 20261117
REPLIQUES = 10000
MINIMUM_TACHES = 8


def moyenne(valeurs):
    return sum(valeurs) / len(valeurs)


def _percentile(trie: list, p: float) -> float:
    position = p * (len(trie) - 1)
    bas, haut = math.floor(position), math.ceil(position)
    return trie[bas] + (trie[haut] - trie[bas]) * (position - bas)


def ic_moyenne(valeurs: list, replications: int = REPLIQUES, graine: int = GRAINE):
    """Moyenne et intervalle de confiance a 95 % par rééchantillonnage des valeurs (ici : des taches)."""
    if not valeurs:
        return None, None, None
    m = moyenne(valeurs)
    if len(valeurs) < 2:
        return m, None, None
    hasard = random.Random(graine)
    n = len(valeurs)
    moyennes = sorted(sum(valeurs[hasard.randrange(n)] for _ in range(n)) / n for _ in range(replications))
    return m, _percentile(moyennes, 0.025), _percentile(moyennes, 0.975)


def test_des_signes(a_mieux: int, b_mieux: int) -> float:
    """Valeur p bilaterale exacte : parmi les taches qui different, B l'emporte-t-elle plus souvent que le hasard ?"""
    n = a_mieux + b_mieux
    if n == 0:
        return 1.0
    k = min(a_mieux, b_mieux)
    p = 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, p)


def comparaison_appariee(taux_a: dict, taux_b: dict, replications: int = REPLIQUES, graine: int = GRAINE) -> dict:
    """Compare deux mesures tache par tache (taux de réussite sur les passes) : difference moyenne B moins A,
    intervalle a 95 % sur les taches, et test des signes. Seules les taches presentes des deux cotes comptent."""
    communes = sorted(set(taux_a) & set(taux_b))
    diffs = [taux_b[t] - taux_a[t] for t in communes]
    b_mieux = sum(1 for x in diffs if x > 1e-9)
    a_mieux = sum(1 for x in diffs if x < -1e-9)
    moy, bas, haut = ic_moyenne(diffs, replications, graine)
    trop_peu = len(communes) < MINIMUM_TACHES
    demontree = (not trop_peu) and bas is not None and (bas > 0 or haut < 0)
    return {"n": len(communes), "difference": moy, "ic_bas": bas, "ic_haut": haut, "a_mieux": a_mieux, "b_mieux": b_mieux,
            "egales": len(communes) - a_mieux - b_mieux, "p_signes": test_des_signes(a_mieux, b_mieux),
            "demontree": demontree, "trop_peu": trop_peu}
