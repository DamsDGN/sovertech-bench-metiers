# Épreuve « Chercher dans les dossiers »

**Question posée : l'assistant retrouve-t-il le bon document, répond-il uniquement à partir de ce qu'il a
trouvé, cite-t-il sa source, et dit-il « je ne sais pas » quand la réponse n'y est pas ?**

Statut : première version. **23 questions**, toutes « à valider par un professionnel ». Aucun résultat publié.

## Ce qu'on teste, et pourquoi ça compte dans un cabinet

Un assistant branché sur vos dossiers est précieux s'il s'appuie sur **la bonne version** du bon
document, et dangereux s'il complète avec ce qu'il croit savoir. Les questions portent sur le
[cabinet fictif](../corpus/README.md) et reproduisent les situations qui piègent le plus :

| Type de question | Nombre | Ce qu'on vérifie | Exemple |
|---|---|---|---|
| **Réponse directe** | 6 | L'assistant trouve et restitue l'information | « Quel est le forfait annuel de la SARL Les Épis d'Or ? » |
| **Version obsolète** | 7 | Il retient la version **en vigueur**, pas l'ancienne | « Combien de jours avant la clôture relance-t-on les pièces ? » (45 jours aujourd'hui, 30 dans l'ancienne procédure) ; calculer le coût de 4 heures de travail avec la grille 2026 |
| **Contradiction** | 1 | Il remarque que deux documents divergent et choisit le bon | Le devis dit 16 500 € HT, la facture 17 800 € HT |
| **Plusieurs documents** | 4 | Il combine plusieurs sources | **Quels clients ont droit à un point intermédiaire, et quand ?** ; **quelles relances et quelle facturation pour une cliente qui envoie ses pièces avec 35 jours de retard ?** (procédure de relance + lettre de mission) |
| **Réponse partielle** | 1 | Il donne ce qui est dans les documents et **dit ce qui manque** | Adresse postale (absente) et chiffre d'affaires (lisible dans la balance) d'un client |
| **Sans réponse** | 4 | Il **dit qu'il ne sait pas** au lieu d'inventer | « Quel est le taux horaire d'un stagiaire ? » (aucun document n'en parle) |

Répartition par difficulté : **4 simples, 12 moyennes, 7 complexes**.

## Deux étages, notés séparément

C'est le principe de cette épreuve : **savoir si un mauvais résultat vient de la recherche ou du modèle.**

1. **La recherche** (le « retriever ») : le bon document est-il parmi les premiers retrouvés ? C'est un
   calcul automatique : chaque question déclare les documents où se trouve la réponse. **Le même
   système de recherche sert à tous les modèles**, figé et versionné : seul le modèle varie.
2. **La réponse** : à partir des passages retrouvés, le modèle répond-il juste, **sans rien ajouter qui ne
   soit dans les passages**, en citant le document, et en s'abstenant quand il le faut ?

Chaque passage est présenté au modèle avec une ligne d'en-tête qui donne **le titre, la date et le statut
(en vigueur ou obsolète)** du document : c'est ce qu'un vrai gestionnaire de documents fournirait.

## Ce que lit l'assistant : du texte extrait de vrais fichiers

Les documents du cabinet fictif sont des **fichiers réels** (Word, Excel, CSV, PDF, dont un scan et une photo
sans texte). Avant la recherche, leur texte est **extrait** par un outil unique, le même pour tous les modèles
(voir [le corpus](../corpus/README.md)). La question « où est la réponse ? » inclut donc les défauts d'une
vraie extraction : un montant lu sur une facture photographiée, un tableau Excel mis à plat, un CSV aplati.

## Comment c'est noté

| Ce qu'on vérifie | Comment | Rejouable chez soi ? |
|---|---|---|
| Le bon document est retrouvé | Calcul automatique | Oui |
| La réponse contient la bonne valeur | Contrôle automatique | Oui |
| L'assistant s'abstient quand il faut (5 questions) | Contrôle automatique | Oui |
| La valeur d'une version obsolète n'est pas donnée comme réponse | Contrôle automatique | Oui |
| Le document cité existe et soutient la réponse | Contrôle automatique | Oui |
| Fidélité aux passages, qualité du raisonnement sur les contradictions | Modèle juge, voir [`grille.md`](grille.md) | **Non** |

## Un point qui peut surprendre

Pour la question « taux de TVA de la restauration sur place », **la bonne réponse est de ne pas répondre**.
Le taux existe dans la réalité, mais les documents fournis ne disent pas à quelle activité s'applique chaque
taux. On teste ici la **fidélité aux documents**, pas la culture générale : dans un cabinet, un assistant qui
répond « de mémoire » alors qu'on lui demande de s'appuyer sur le dossier est un risque.

## Ce que ces résultats disent et ne disent pas

- Ils disent comment un modèle se comporte **avec ce corpus de 25 documents (le 26e, le FEC, n'est pas proposé à la recherche documentaire)** : c'est très petit comparé à
  un vrai cabinet, où chercher la bonne pièce est plus difficile.
- Les trois **textes publics** du corpus (taux de TVA, plan comptable, conservation) sont des résumés
  rédigés par l'équipe : **ils sont à relire en priorité**.
- Avec 23 questions, un petit écart entre deux modèles n'est pas significatif.
- Le moteur de recherche est **le même pour tous et volontairement simple** : on mesure comment le modèle exploite des passages déjà retrouvés, pas une solution documentaire complète (lecture des scans, index, classement des résultats).

## Corriger ou relire

Toutes les questions et leurs réponses attendues sont dans [`TACHES.md`](TACHES.md). Une erreur, une
ambiguïté, un document qui vous paraît irréaliste : voir [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Pour les techniciens

- Données : [`questions.jsonl`](questions.jsonl).
- Champs propres : `question`, `type_question`, `documents_attendus` (identifiants, en vigueur),
  `documents_pieges` (versions obsolètes ou distracteurs), `elements_documents` (textes qui doivent figurer
  dans les documents attendus : contrôlé automatiquement), `valeurs_obsoletes` (valeurs à ne pas donner
  comme réponse), `verifications`, `reponse_modele`, `reponse_fautive`, `criteres_juge`.
- Un contrôle de cohérence vérifie que chaque `elements_documents` apparaît bien dans les documents
  attendus, que les questions « sans réponse » ne citent aucun document et exigent l'abstention, et que
  les « versions obsolètes » ont un document piège réellement obsolète.
