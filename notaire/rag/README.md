# Épreuve « Chercher dans les dossiers »

**Question posée : l'assistant retrouve-t-il le bon document, répond-il à partir de lui seulement, cite-t-il
sa source, et dit-il quand le dossier ne contient pas la réponse ?**

Statut : première version. **14 questions**, toutes « à valider par un professionnel ». Aucun résultat publié.

## Comment ça se passe

Un moteur de recherche simple et **déterministe** (le même pour tous les modèles) retrouve les six passages
les plus proches de la question dans les 25 documents de l'étude fictive. Le modèle répond avec ces seuls
extraits. On sépare donc **la recherche** (le bon document est-il dans les six premiers ?) de **la réponse** (le
modèle a-t-il bien utilisé ce qu'on lui a donné ?).

## Les types de questions

| Type | Nombre | Exemple |
|---|---|---|
| **Réponse directe** | 6 | Le prix de vente de l'appartement du dossier D-2026-014 ; la date limite de dépôt de la déclaration de succession |
| **Version obsolète** | 2 | Combien de jours avant la signature convoque-t-on les parties ? (la procédure remplacée dit 8, celle en vigueur dit 15) ; le tarif d'une copie authentique en 2026 (pas celui de 2025) |
| **Plusieurs documents** | 2 | Le prêt accordé couvre-t-il la condition suspensive ? (avant-contrat **et** courriel de la banque) ; la fin du délai de rétractation (fiche **et** procédure) |
| **Contradiction** | 1 | Qui envoie les convocations : la procédure et la note de réunion se contredisent, la plus récente l'emporte |
| **Sans réponse** | 2 | Les émoluments du notaire pour un dossier ; le téléphone d'une vendeuse : aucun document ne les contient |
| **Réponse partielle** | 1 | Les droits de succession : le décompte donne la part de chacun, mais ni l'assurance-vie ni les donations antérieures ne sont connues |

Répartition par difficulté : **6 simples, 6 moyennes, 2 complexes**.

## Un exemple complet

> **Question** : « Qui envoie les convocations à la signature : le clerc en charge du dossier ou un autre
> service ? »
>
> **Bonne réponse** : la procédure (5 janvier 2026) dit les clercs, mais la note de réunion du 9 février 2026,
> plus récente, confie les convocations à Anouk Derrien à partir du 16 février. La procédure n'est pas encore
> mise à jour.

## Comment c'est noté

Contrôles automatiques : le bon document est-il retrouvé (rappel et rang) ? la réponse contient-elle la bonne
valeur ? évite-t-elle la valeur obsolète ? cite-t-elle un document qui existe ? s'abstient-elle quand il le
faut ? Un modèle juge note le reste, **séparément**, sur [`grille.md`](grille.md).

## Ce que ces résultats disent et ne disent pas

- 14 questions : de petits écarts sont du bruit.
- Une question est toujours **atteignable** : les tests vérifient que le bon document est dans les six
  premiers résultats pour chaque question, pour que l'épreuve mesure le modèle et non le moteur de recherche.
- La justesse juridique des textes publics du corpus est à reconfirmer (voir leur champ `incertitude`).

## Pour les techniciens

Données : [`questions.jsonl`](questions.jsonl). Champs : `question`, `documents_attendus`, `documents_pieges`,
`type_question`, `reference`, `verifications`, `elements_documents` (doivent figurer dans le texte extrait),
`valeurs_obsoletes`, `abstention_attendue`. Voir
[`../../expert-comptable/rag/README.md`](../../expert-comptable/rag/README.md). Version lisible :
`python3 -m core.export_lisible notaire`.
