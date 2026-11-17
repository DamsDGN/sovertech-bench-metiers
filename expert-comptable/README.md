# Benchmark experts-comptables

**Statut : première version en préparation. Aucun résultat publié. Toutes les réponses de référence sont
« à valider par un professionnel ».**

## À qui s'adresse ce benchmark

Aux cabinets d'expertise comptable qui se demandent si un assistant IA **installé chez eux** (sur leur
propre matériel, sans envoyer de dossier à un service extérieur) peut les aider sur des tâches
courantes, et lequel choisir.

Il ne remplace pas votre jugement : il mesure ce qu'un modèle sait faire **sur des situations
représentatives**, avec les mêmes questions pour tous, pour que la comparaison soit honnête.

## Le cabinet fictif

Toutes les épreuves se déroulent dans un cabinet **inventé**, le **Cabinet Aubépine & Associés**
(Lorient), avec cinq clients inventés : une boulangerie, une menuiserie, une société civile immobilière,
une consultante indépendante et une association. Ses procédures internes, ses grilles d'honoraires, ses
fiches clients et ses notes de réunion sont dans [`corpus/`](corpus/README.md).

Rien n'y est réel : ni les noms, ni les numéros SIREN (volontairement invalides), ni les montants. Vous
pouvez tout lire sans risque et vous reconnaître dans les situations sans reconnaître un client.

## Les trois épreuves

### 1. Discuter : [`chat/`](chat/README.md)

20 situations de conversation, des plus simples aux plus complexes : rédiger un courriel de relance, expliquer la TVA collectée
à un dirigeant, choisir un compte du plan comptable, **calculer le résultat d'une balance, repérer l'opération bancaire sans justificatif,
répondre à une cliente qui conteste ses honoraires, dresser les actions de clôture d'un dossier** à partir de plusieurs documents.

On regarde notamment : le **français**, le **respect des consignes** (nombre de mots, format imposé), et
surtout deux comportements qui comptent dans un cabinet :

- **Savoir dire « je ne sais pas »** quand l'information manque (le numéro de téléphone d'une cliente
  qui n'est dans aucun dossier) ;
- **Ne pas inventer** un chiffre ou une référence.

### 2. Chercher dans les dossiers : [`rag/`](rag/README.md)

23 questions sur les documents du cabinet fictif. L'assistant doit retrouver le bon passage, répondre
**à partir de ce passage seulement** et citer le document. Pour que l'épreuve soit réaliste, le corpus
contient des pièges que vous connaissez bien :

- des **versions obsolètes** d'une procédure ou d'une grille d'honoraires (laquelle est en vigueur ?) ;
- des **informations contradictoires** (le devis dit un montant, la facture un autre) ;
- des **questions sans réponse** dans les documents, ou **à moitié sans réponse** : la bonne réponse est de le dire.

On sépare deux choses : *l'assistant a-t-il retrouvé le bon document ?* et *a-t-il bien répondu à partir
de ce qu'il a retrouvé ?* Ainsi, on sait si un mauvais résultat vient de la recherche ou du modèle.

### 3. Agir : [`agentique/`](agentique/README.md)

20 tâches où l'assistant dispose d'outils factices : chercher dans les documents, lire un document,
extraire des champs, écrire dans un tableau de suivi, **préparer un courriel sans l'envoyer**. Les
tâches demandent plusieurs étapes (par exemple : trouver les dates de clôture, calculer les dates de
relance, les inscrire dans le tableau).

On vérifie **le résultat final** (le tableau contient-il les bonnes valeurs ?), la justesse des appels,
le nombre d'étapes, la **reprise après une panne d'outil**, et qu'il **n'a jamais fait ce qui était
interdit** (envoyer un courriel, lire un document confidentiel, obéir à une instruction cachée dans un courriel reçu).

## Comment on note

| Ce qu'on vérifie | Comment | Peut-on le rejouer chez soi ? |
|---|---|---|
| Un montant, une date, un compte, un format, un nombre de mots | Contrôle **automatique** | Oui, résultat identique |
| Retrouver le bon document | Calcul automatique (le bon document est-il dans les premiers résultats ?) | Oui |
| Citer une source qui existe et qui soutient la réponse | Contrôle automatique | Oui |
| Qualité du français, clarté, prudence | Un **modèle juge** (Claude, en session, à l'aveugle) sur une grille publique, avec un échantillon relu par un humain | **Non** : dépend d'une session de notation. Le rapport affiche ces notes **séparément** |
| L'état final d'un tableau, l'absence d'action interdite | Contrôle automatique | Oui |

Chaque épreuve est lancée **5 fois** et on publie la moyenne **et la dispersion** : si deux modèles
sont dans la marge d'erreur, le rapport dit « pas de différence démontrée ».

On mesure aussi la **vitesse** (mots par seconde, temps avant le début de la réponse), la **mémoire
graphique** utilisée et le **coût par tâche**, qui comptent quand on dimensionne un matériel.

## Ce que les résultats disent, et ne disent pas

**Ils disent** : comment chaque modèle se comporte sur ces situations inventées, à cette date, avec
cette configuration.

**Ils ne disent pas** :

- qu'un modèle est fiable pour **vos** dossiers : il faut toujours le tester sur votre propre
  environnement, avec des données qui restent chez vous ;
- que la **justesse métier** est établie : tant qu'une réponse de référence est « à valider », le
  score correspondant est provisoire ;
- qu'un écart de quelques points compte : avec 20 tâches environ par épreuve, de petits écarts sont du
  bruit.

## Les modèles testés

Des modèles « ouverts », de 12 à 35 milliards de paramètres, qui tiennent sur **une carte graphique de
48 Go**, dans un format compact nommé **NVFP4**. La liste et les dépôts exacts sont dans
[`docs/PLAN.md`](../docs/PLAN.md), section 4. Vous pouvez en ajouter un (voir
[`docs/REPRODUIRE.md`](../docs/REPRODUIRE.md)).

## Relire ou corriger

**Vous êtes expert-comptable ?** Chaque épreuve a un fichier `TACHES.md` qui présente chaque tâche
et sa réponse attendue en langage courant. Une relecture de vingt minutes par épreuve est précieuse.
Voir [`CONTRIBUTING.md`](../CONTRIBUTING.md) : **toute erreur signalée est la bienvenue**.

## Pour les techniciens

Format des fichiers, contrôles et conventions : [`AGENTS.md`](AGENTS.md) (ce dossier) et
[`../AGENTS.md`](../AGENTS.md) (général).
