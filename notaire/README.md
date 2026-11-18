# Benchmark notaires

**Statut : première version en préparation. Aucun résultat publié. Toutes les réponses de référence sont
« à valider par un professionnel » : nous ne sommes pas notaires.**

## À qui s'adresse ce benchmark

Aux études notariales qui se demandent si un assistant IA **installé chez elles** (sur leur propre
matériel, sans envoyer un dossier à un service extérieur) peut les aider sur des tâches courantes, et
lequel choisir.

Il ne remplace ni votre jugement ni votre responsabilité : il mesure ce qu'un modèle sait faire **sur des
situations représentatives**, avec les mêmes questions pour tous, pour que la comparaison soit honnête.

## L'étude fictive

Toutes les épreuves se déroulent dans une étude **inventée**, l'**Étude Bruyère & Associés** (Quimper),
avec quatre dossiers inventés : la vente d'un appartement, la vente d'une maison avec procuration, une
succession et la constitution d'une société civile immobilière. Ses procédures, sa grille de frais, ses
fiches de dossier, ses pièces et ses notes de réunion sont dans [`corpus/`](corpus/README.md).

Rien n'y est réel : ni les noms, ni les adresses, ni les montants, ni les biens. Les documents existent dans
leurs **vrais formats** (Word récents et anciens, Excel récents et anciens, CSV, PDF propres, et **PDF
dégradés** : deux scans et une photo prise de travers, lus par reconnaissance de caractères).

**Aucun acte réel, même anonymisé, n'est utilisé ni accepté.**

## Une règle propre au notariat : prudence d'abord

Une réponse fausse sur un point de droit n'a pas la même portée qu'une erreur de relance. Les épreuves
mesurent donc en particulier la capacité de l'assistant à :

- **relever les faits d'un dossier** (un prix, une date, un montant) sans les déformer ;
- **repérer une incohérence** entre deux pièces (un prix écrit autrement en lettres et en chiffres, un
  prêt accordé inférieur à celui que la condition suspensive prévoit) ;
- **ne pas trancher un point de droit** à la place du notaire : renvoyer à la lecture de l'acte ou à une
  vérification, plutôt que promettre ou affirmer ;
- **dire « je ne sais pas »** quand le dossier ne le dit pas (les droits de succession quand les
  donations antérieures ne sont pas connues).

## Ce que la deuxième série a durci (17/11/2026)

Une première mesure sur un modèle de taille modeste a donné des scores élevés. 19 tâches et 9 documents s'ajoutent, toutes **déduites du corpus** :
prorata de taxe foncière, **état hypothécaire** (inscriptions, mainlevées, somme nette du vendeur), **origine de propriété** comparée au titre,
**identité et régime matrimonial** comparés entre pièces, **comparaison de deux versions d'un projet d'acte**, **origine des fonds** d'un apport, et quatre épreuves
transversales : conversation à plusieurs tours, **cloisonnement entre dossiers**, instruction cachée dans un PDF scanné, demande de précision avant d'agir.

## Les trois épreuves

### 1. Discuter : [`chat/`](chat/README.md)

19 situations de conversation : rédiger une convocation ou un courriel, reformuler une règle pour un
client, repérer une incohérence dans un projet d'acte ou dans un tableau d'apports, résumer un dossier,
et **répondre prudemment** à un client qui demande s'il peut renoncer à son achat.

### 2. Chercher dans les dossiers : [`rag/`](rag/README.md)

20 questions sur les documents de l'étude. L'assistant doit retrouver le bon passage, répondre **à partir
de ce passage seulement** et citer le document. Les pièges sont ceux d'une étude : une **procédure
remplacée** (8 jours ou 15 jours avant la signature ?), une **grille de frais périmée**, deux documents
qui **se contredisent** (qui envoie les convocations ?), des questions **sans réponse** dans le dossier.

### 3. Agir : [`agentique/`](agentique/README.md)

18 tâches où l'assistant dispose d'outils factices : chercher, lire un document, extraire des champs,
écrire dans un tableau de suivi, **préparer un courriel sans l'envoyer**. Par exemple : calculer et
inscrire les dates de convocation de plusieurs dossiers selon la procédure en vigueur.

On vérifie **le résultat final**, la reprise après une panne d'outil, et qu'il **n'a jamais fait ce qui était
interdit** : envoyer un courriel, lire la grille de rémunération confidentielle, obéir à une instruction
cachée dans un courriel reçu d'un héritier.

## Comment on note

Comme pour les [experts-comptables](../expert-comptable/README.md) : des **contrôles automatiques
rejouables** (un montant, une date, un format, l'état final d'un tableau, l'absence d'action interdite) et,
pour ce qu'un programme ne peut pas vérifier, un modèle juge **affiché séparément** avec sa grille publique.
Chaque épreuve est lancée plusieurs fois (5 passes visées, 2 pour les premiers résultats publiés) ; on publie la moyenne et la dispersion.

Chaque tâche porte une **gravité proposée** (faible à critique, voir [`docs/GRAVITE.md`](../docs/GRAVITE.md)) : une erreur sur
un délai ou sur un montant de prêt ne pèse pas comme une erreur de ton. Cette proposition est à valider par un notaire.

## Ce que les résultats disent, et ne disent pas

**Ils disent** : comment chaque modèle se comporte sur ces situations inventées, à cette date, avec cette
configuration.

**Ils ne disent pas** :

- qu'un modèle est fiable pour **vos** dossiers : il faut toujours le tester dans votre environnement,
  avec des données qui restent chez vous ;
- que la **justesse juridique** est établie : tant qu'une référence est « à valider », le score est
  provisoire. Les textes publics du corpus (délai de rétractation, délais en matière de succession, droit
  de préemption) sont **résumés avec leur source et un champ d'incertitude** : à reconfirmer ;
- qu'un écart de quelques points compte : avec 18 à 20 tâches par épreuve, de petits écarts sont du bruit.
  **Ce benchmark est plus petit que celui des experts-comptables** (57 tâches contre 91) : c'est une v0.

## Limites connues de cette première version

- **Jeu de tâches modeste** : 57 au total, quatre dossiers.
- **Extraction du texte** : seul le moteur Apache Tika est mesuré, pas la variante Docling.
- **Pas de relecture professionnelle** à ce jour.
- Plusieurs règles du corpus sont des **conventions internes de l'étude fictive** (convocation 15 jours avant
  la signature, alerte 60 jours avant l'échéance de déclaration, calcul de la fin du délai de rétractation par
  ajout de 10 jours à la date de remise) : elles ne prétendent pas décrire la pratique notariale.

## Pour avancer, il faut un notaire

Nous ne sommes pas notaires. **Si c'est vous, ou si vous connaissez quelqu'un, écrivez-nous** (voir
[`CONTRIBUTING.md`](../CONTRIBUTING.md)) : chaque épreuve a un fichier `TACHES.md` qui présente chaque tâche
et sa réponse attendue en langage courant. Une relecture de vingt minutes par épreuve est précieuse.

## Pour les techniciens

Format des fichiers, contrôles et conventions : [`AGENTS.md`](AGENTS.md) (ce dossier) et
[`../AGENTS.md`](../AGENTS.md) (général).
