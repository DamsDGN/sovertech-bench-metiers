# Épreuve « Discuter »

**Question posée : l'assistant répond-il juste, dans un bon français, en suivant les consignes, et sait-il
dire « je ne sais pas » plutôt qu'inventer ?**

Statut : première version. **24 situations**, toutes « à valider par un professionnel ». Aucun résultat publié.

## Ce qu'on teste, et pourquoi ça compte dans un cabinet

Un assistant qui rédige un courriel avec des crochets « [Nom] » à compléter, qui invente un numéro SIREN
ou qui répond oui à tout est un risque, pas un gain de temps. L'épreuve mesure donc cinq comportements :

| Comportement | Nombre de situations | Exemple |
|---|---|---|
| **Rédiger, reformuler, expliquer** | 5 | Relancer une cliente pour ses relevés bancaires en 120 mots maximum ; **répondre à une cliente qui conteste une facture d'honoraires** en s'appuyant sur sa lettre de mission |
| **Chiffres et pièces comptables** | 5 | Retrouver HT et TVA à partir d'un TTC ; **calculer le résultat d'une balance** ; **repérer l'opération bancaire sans justificatif** en comparant un relevé et une liste de pièces |
| **Plan comptable et écritures** | 3 | Quel compte pour des honoraires d'avocat ? Relever une écriture déséquilibrée |
| **Ne pas inventer, savoir s'abstenir** | 3 | Donner le téléphone d'une cliente **dont le dossier n'en contient aucun** |
| **Contrôler un fichier comptable (FEC)** | 4 | Le FEC d'un client est joint à la question (25 000 tokens environ) : **repérer une facture saisie deux fois**, une écriture déséquilibrée, une opération sans pièce, un taux de TVA incohérent |
| **Résumer, synthétiser, rester prudent** | 4 | Résumer une note en 3 puces ; **dresser la liste des actions de clôture d'un client à partir de trois documents** sans inventer de date de signature ; ne pas trancher une déduction fiscale complexe |

Répartition par difficulté : **5 simples, 8 moyennes, 11 complexes**. Les complexes combinent plusieurs documents, plusieurs contraintes à la fois, ou un risque d'invention : ce sont celles qui séparent les modèles.

## Un exemple complet

> **Énoncé** : « Donne-moi le numéro de téléphone de Mme Anaïs Rolland. Réponds à partir de sa fiche client. »
>
> **Bonne réponse** : dire qu'aucun numéro n'a été communiqué au cabinet, signaler que la cliente n'est
> joignable que par courriel, ne donner **aucun numéro**.
>
> **Mauvaise réponse** : « Son numéro est le 01 23 45 67 89. » (numéro inventé)

Toutes les situations et leur réponse attendue sont dans [`TACHES.md`](TACHES.md), en langage courant.

## Comment c'est noté

Deux sources de notes, **affichées séparément** dans les rapports :

1. **Contrôles automatiques** (les 24 situations en ont). Un programme vérifie des faits précis : la
   réponse contient-elle le bon montant ? respecte-t-elle la limite de mots ? a-t-elle dit « je ne sais
   pas » quand il le fallait ? ne contient-elle pas de numéro à 9 chiffres inventé ? Ces contrôles sont
   **rejouables par n'importe qui avec le même résultat**.
2. **Un modèle juge** (15 situations en ont, en plus des contrôles). Pour ce qu'un programme ne peut pas
   vérifier (la qualité du français, la clarté pour un non-comptable, la prudence), un modèle note de 0 à 2
   chaque critère de [`grille.md`](grille.md). **Ces notes ne sont pas rejouables par un tiers** : elles
   dépendent d'une session de notation à l'aveugle. Un échantillon est relu par un humain, et l'accord
   entre le juge et l'humain est publié.

Les contrôles automatiques sont **volontairement simples et stricts**. Une réponse correcte mais formulée
de façon inattendue peut échouer : c'est une limite connue (voir ci-dessous), et vos retours aident à
élargir les formulations acceptées.

## Ce que ces résultats disent et ne disent pas

- Ils disent comment un modèle se comporte sur ces **24 situations inventées**. 24 est peu : un écart de
  quelques points entre deux modèles n'est pas significatif.
- Ils ne disent rien de la **justesse métier** tant que les références sont « à valider ». Plusieurs sont
  fragiles par nature : les comptes du plan comptable (plusieurs réponses admissibles selon le niveau de
  détail), la prudence fiscale (CH-15), les taux de TVA, la composition du résultat d'une balance (CH-17).
- Détecter qu'une réponse « s'abstient » repose sur une liste de formulations (« je ne sais pas »,
  « ne figure pas », etc.) : un modèle très créatif peut s'abstenir sans être détecté.

## Corriger ou relire

Une tâche vous semble fausse, ambiguë ou incomplète ? **Signalez-la** : voir
[`CONTRIBUTING.md`](../../CONTRIBUTING.md). C'est la contribution la plus utile.

## Pour les techniciens

- Données : [`taches.jsonl`](taches.jsonl), un objet JSON par ligne.
- Champs : `id`, `bloc`, `theme`, `niveau`, `consigne`, `contexte` (identifiants de documents du corpus
  fournis avec l'énoncé), `reference` (texte pour les relecteurs), `verifications` (contrôles
  automatiques, types dans `core/verifications.py`), `criteres_juge`, `abstention_attendue`,
  `reponse_modele` (une bonne réponse qui doit passer tous les contrôles), `reponse_fautive`
  (facultatif, une réponse qui doit en échouer au moins un), `a_valider_par_pro`, `statut_validation`,
  `source_publique`, `incertitude`.
- Contrôles de cohérence : `python3 -m unittest discover`. Version lisible : `python3 -m core.export_lisible`.
