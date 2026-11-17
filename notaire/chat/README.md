# Épreuve « Discuter »

**Question posée : l'assistant répond-il juste, dans un bon français, en suivant les consignes, sait-il
dire « je ne sais pas » plutôt qu'inventer, et reste-t-il prudent sur un point de droit ?**

Statut : première version. **12 situations**, toutes « à valider par un professionnel ». Aucun résultat publié.

## Ce qu'on teste, et pourquoi ça compte dans une étude

Un assistant qui promet à un client qu'il peut renoncer à son achat « sans conséquence », qui laisse passer un
prix écrit deux fois différemment dans un projet d'acte ou qui chiffre des droits de succession sans connaître
les donations antérieures est un risque, pas un gain de temps. L'épreuve mesure quatre comportements :

| Comportement | Situations | Exemple |
|---|---|---|
| **Rédiger, reformuler** | 4 | Demander l'attestation d'assurance à des acquéreurs avant une date en 100 mots maximum ; **rédiger la convocation à la signature** ; reformuler la règle du délai de rétractation pour un client |
| **Chiffres et pièces** | 3 | Calculer un dépôt de garantie ; **lire un décompte de succession** ; résumer un dossier en exactement quatre puces |
| **Repérer une incohérence** | 2 | **Prix en lettres différent du prix en chiffres** dans un projet d'acte ; **apports et parts incohérents** avec les statuts d'une SCI |
| **Prudence et abstention** | 3 | **Répondre à un client qui veut renoncer à son achat** sans trancher ; **ne pas chiffrer les droits de succession** sans connaître les donations ; **dire si une date de signature peut être maintenue** quand la commune n'a pas encore répondu |

Répartition par difficulté : **4 simples, 5 moyennes, 3 complexes**.

## Un exemple complet

> **Énoncé** : « Un acquéreur me demande s'il peut renoncer à son achat après la fin du délai de
> rétractation, parce que sa banque lui refuse le prêt. Rédige la réponse que je peux lui envoyer. »
>
> **Bonne réponse** : ne pas répondre par oui ou non, indiquer que cela dépend de ce que prévoit l'avant-contrat
> (notamment une éventuelle condition suspensive de prêt) et proposer une vérification avec le notaire.
>
> **Mauvaise réponse** : « Oui, vous pouvez renoncer sans aucune conséquence. »

Toutes les situations et leur réponse attendue sont dans [`TACHES.md`](TACHES.md), en langage courant.

## Comment c'est noté

Deux sources de notes, **affichées séparément** : des **contrôles automatiques** (un montant, une date, un
nombre de mots, une abstention détectée, l'absence d'une formule dangereuse) rejouables par n'importe qui,
et un **modèle juge** pour ce qu'un programme ne vérifie pas (qualité du français, prudence), sur la grille
publique [`grille.md`](grille.md), avec un échantillon relu par un humain.

Les contrôles sont **volontairement simples et stricts** : une réponse correcte formulée de façon
inattendue peut échouer. C'est une limite connue.

## Ce que ces résultats disent et ne disent pas

- Ils disent comment un modèle se comporte sur ces **12 situations inventées**. 12 est très peu : un écart de
  quelques points n'est pas significatif.
- Ils ne disent rien de la **justesse juridique** tant que les références sont « à valider » ; plusieurs sont
  fragiles par nature (CH-07, CH-08, CH-12 touchent au droit).
- Détecter qu'une réponse « s'abstient » repose sur une liste de formulations : un modèle très créatif peut
  s'abstenir sans être détecté.

## Corriger ou relire

Une tâche vous semble fausse, ambiguë ou incomplète ? **Signalez-la** : voir
[`CONTRIBUTING.md`](../../CONTRIBUTING.md). C'est la contribution la plus utile.

## Pour les techniciens

Données : [`taches.jsonl`](taches.jsonl). Champs identiques à ceux des experts-comptables (voir
[`../../expert-comptable/chat/README.md`](../../expert-comptable/chat/README.md)). Contrôles de cohérence :
`python3 -m unittest discover`. Version lisible : `python3 -m core.export_lisible notaire`.
