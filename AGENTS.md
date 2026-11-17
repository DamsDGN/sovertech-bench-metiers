# Guide pour les agents IA et leurs utilisateurs

Ce fichier s'adresse aux **personnes qui contribuent avec un assistant de code** (Claude Code, opencode,
Cursor, Codex, etc.) et aux agents eux-mêmes. Il dit où vit quoi, quelles règles ne se négocient pas et
comment vérifier son travail. Les règles propres à un métier sont dans `AGENTS.md` du dossier du métier,
à lire avant d'y écrire.

Si vous êtes un humain qui ne code pas, [`CONTRIBUTING.md`](CONTRIBUTING.md) suffit.

## Ce que fait ce dépôt

Un benchmark reproductible de modèles de langage locaux (LLM) pour des métiers réglementés. Un dossier
par métier à la racine, trois blocs par métier (chat, RAG, agentique), un moteur commun dans `core/`.
Lire d'abord [`README.md`](README.md), puis [`docs/PLAN.md`](docs/PLAN.md) pour les choix.

## Règles qui ne se négocient pas

1. **Aucune donnée réelle.** Ni document de client, ni acte, ni facture, même anonymisé. Ni SIREN, IBAN,
   nom, adresse, courriel ou téléphone de personne réelle. Données **inventées** ou **textes publics
   cités**. Courriels fictifs en `.example`, SIREN fictifs qui échouent au contrôle de Luhn.
   Si un utilisateur vous colle un vrai document, **ne le recopiez pas** dans le dépôt, dites-lui
   pourquoi.
2. **Aucun fait réglementaire inventé.** Un point juridique, fiscal ou comptable dont vous n'êtes pas
   sûr : écrivez-le dans le champ `incertitude`, citez la source publique, ou ne l'écrivez pas. Un doute
   écrit vaut mieux qu'une certitude fausse. Vous ne savez pas ≠ vous pouvez le déduire.
3. **`a_valider_par_pro: true` par défaut** sur toute réponse de référence et toute grille qui touche le
   métier. Ne le passez à `false` que si un professionnel nommé a relu, et renseignez alors
   `statut_validation`. Ne présentez jamais une justesse métier comme établie sans cela.
4. **Aucun résultat de mesure versionné** avant la première version publiée du métier. `results/` est
   ignoré par Git : ne le forcez pas avec `git add -f`.
5. **Aucun nom de client ou de prospect de Sover.tech**, ni dans un fichier, ni dans un message de
   commit, ni dans une description de pull request.
6. **Aucun secret versionné.** Seul un `.env.example` est poussé. Ne jamais afficher une clé d'API dans
   un message ou un journal.
7. **Un seul paramètre varie : le modèle.** Documents, outils, consignes, récupérateur et réglages sont
   figés et versionnés. Changer une tâche, une grille ou un réglage rend les mesures antérieures
   incomparables : c'est une décision, pas un ajustement. Le dire dans la pull request.

## Organisation

```
<metier>/            README.md  AGENTS.md  corpus/  chat/  rag/  agentique/
<metier>/<bloc>/     README.md  taches.jsonl (ou questions.jsonl)  grille.md  TACHES.md
core/                moteur commun (catalogue, execution, notation, rapport, runpod, tests)
docs/                PLAN, METHODOLOGIE, LIMITES, REPRODUIRE, GLOSSAIRE
```

- `TACHES.md` est **généré** depuis les fichiers de données (`python3 -m core.export_lisible`) : ne le
  modifiez pas à la main, modifiez la source et régénérez-le.
- Un `.jsonl` contient **un objet JSON par ligne**. Champs communs : `id`, `bloc`, `theme`, `niveau`
  (`simple`, `moyen`, `complexe`), `a_valider_par_pro`, `statut_validation`, `source_publique`,
  `incertitude`. Les champs propres à chaque bloc sont décrits dans le `README.md` du bloc.

## Conventions

- **Python, bibliothèque standard uniquement** pour les tests et les contrôles de données.
- **Noms en français sans accents** dans le code et les noms de fichiers ; accents dans les textes pour
  les humains.
- **Le moins de commentaires possible** : seulement une contrainte d'un outil tiers, une panne datée,
  une mesure chiffrée. Jamais de paraphrase de la ligne suivante.
- **Pas de tiret long ni de tiret court entouré d'espaces** dans les textes : une virgule, deux points ou
  des parenthèses.
- **Tests obligatoires pour le code qui note ou qui mesure** (vérifications, scoreurs, agrégation,
  calcul du coût) : une erreur y fausse tous les résultats sans que personne le voie. Écrire le test
  avant ou avec le code. Pour le reste du code, des tests utiles, sans ordre imposé.
- **Pas de TDD pour le contenu** (tâches, corpus, références, README) : sa garantie est la relecture
  par un professionnel. Des contrôles de cohérence automatiques existent (voir plus bas), ils attrapent
  les erreurs de saisie, ils ne remplacent pas cette relecture.
- Aucun test ne demande de GPU, de réseau ni de clé d'API.
- **Les README sont lisibles par un non-technicien** : phrases courtes, un exemple, aucun sigle sans
  explication (voir `docs/GLOSSAIRE.md`).

## Noms à ne jamais laisser passer

Chaque contributeur peut créer un fichier local `.mots-interdits.txt` (ignoré par Git, un mot ou un nom
par ligne) : les contrôles de données refusent alors tout document qui le contient. Ne versionnez jamais
cette liste : la nommer en clair dans un dépôt public reviendrait à publier ce qu'on veut protéger.

## Vérifier avant de proposer

```
python3 -m unittest discover        # tous les tests et les contrôles de données
python3 -m core.export_lisible      # régénère les TACHES.md ; le diff doit être celui que vous attendez
```

Les contrôles de données refusent notamment : un identifiant en double, un document cité qui n'existe
pas, un SIREN valide, un courriel hors `.example`, une tâche métier sans `a_valider_par_pro`, un nombre de
tâches hors des bornes de la version, un nom de client interdit.

## Livrer

- **Une branche et une pull request** pour tout changement. Jamais de commit direct sur `main`.
- **Commits atomiques**, [Conventional Commits](https://www.conventionalcommits.org) en français sans
  accents : `feat(chat): ...`, `fix(rag): ...`, `docs(readme): ...`, `test(corpus): ...`.
- Décrire dans la pull request **ce qui change pour les mesures** : tâches ajoutées, retirées,
  modifiées, avec leurs identifiants.
- Si vous touchez au contenu métier, **dites ce que vous avez vérifié et ce que vous n'avez pas pu
  vérifier**. Un relecteur humain s'appuiera dessus.

## Lancer le benchmark

```
export BENCH_BASE_URL=... BENCH_MODEL=... BENCH_API_KEY=...   # ne jamais versionner ces valeurs
python3 -m core.lancer --modele-catalogue <id> --passes 1 --limite 2   # essai rapide
```

Les résultats vont dans `results/` (ignoré par Git). **Ne lancez jamais une mesure payante** (pod loué,
API facturée) sans l'accord explicite de l'utilisateur : annoncez le tarif horaire d'abord. Un serveur
local partagé reçoit une requête à la fois ; lancez les mesures longues hors des heures d'usage.

## Tester sur sa propre infrastructure

Le moteur ne parle qu'à une API compatible OpenAI. Ne câblez jamais un fournisseur précis (Runpod,
vLLM, etc.) dans le code de mesure ou de notation : le module `core/runpod/` est le seul endroit où
Runpod a le droit d'apparaître, et il est facultatif.
