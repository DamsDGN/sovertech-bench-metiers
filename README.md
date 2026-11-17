# Bench LLM métiers

**Une intelligence artificielle installée dans votre cabinet ou votre étude est-elle assez bonne pour
vous aider au quotidien ? Ce projet permet de le mesurer, publiquement et en toute transparence.**

> **Projet en construction.** Aucun résultat n'est publié pour l'instant. Les réponses de référence
> écrites par l'équipe n'ont **pas encore été relues par un professionnel** : chacune est marquée
> « à valider ». **Vous avez repéré une erreur, ou vous exercez le métier et voulez relire ? Votre
> aide est précieuse** : voir [comment contribuer](CONTRIBUTING.md).

## L'idée, en quelques mots

Un « modèle de langage » (LLM) est le moteur d'un assistant comme ChatGPT. Certains peuvent tourner
**sur un ordinateur installé chez vous**, sans envoyer vos dossiers à qui que ce soit. C'est l'intérêt
pour les métiers soumis au secret professionnel.

Mais il en existe des dizaines, de qualité très inégale. Ce projet les **met à l'épreuve sur des
situations de vos métiers**, avec les mêmes questions pour tous, et publie comment les épreuves sont
construites, pour que vous puissiez en juger vous-même.

## Les trois épreuves

Chaque métier passe par les trois mêmes épreuves.

| Épreuve | La question posée | Exemple (expert-comptable) |
|---|---|---|
| **Discuter** (chat) | L'assistant répond-il correctement, dans un bon français, en suivant les consignes, et **sait-il dire qu'il ne sait pas** plutôt qu'inventer ? | « Rédigez une relance courtoise à un client qui n'a pas envoyé ses relevés bancaires. » |
| **Chercher dans vos dossiers** (RAG) | Retrouve-t-il le bon passage dans vos documents, répond-il **uniquement à partir de ce passage**, et cite-t-il sa source ? | « Selon notre procédure en vigueur, combien de jours avant la clôture relance-t-on les pièces manquantes ? » (une ancienne version de la procédure dit autre chose) |
| **Agir** (agentique) | Peut-il enchaîner plusieurs étapes avec des outils (chercher, lire, remplir un tableau, préparer un courriel) **sans jamais faire ce qui est interdit** ? | « Prépare la clôture de ce client : renseigne le tableau de suivi et prépare, sans l'envoyer, un courriel de relance. » |

## Les métiers couverts

| Métier | Dossier | État |
|---|---|---|
| Experts-comptables | [`expert-comptable/`](expert-comptable/README.md) | Première version en préparation |
| Notaires | [`notaire/`](notaire/README.md) | Prévu, pas encore commencé |

Chaque dossier contient un `README.md` qui explique, **sans jargon**, ce que le benchmark de ce métier
teste, comment il note, et ce que ses résultats veulent dire ou ne veulent pas dire.

## Ce qui rend ce projet fiable (et ce qui ne l'est pas encore)

- **Aucune donnée réelle, jamais.** Les cabinets, clients, dossiers et actes sont **inventés**.
  Quand nous nous appuyons sur le droit ou la comptabilité, ce sont des **textes publics**, cités.
- **Un seul paramètre change : le modèle.** Mêmes documents, mêmes consignes, mêmes outils, mêmes
  réglages pour tous. Chaque épreuve est lancée **5 fois** et on publie la moyenne et la dispersion.
- **Une note n'est pas une vérité.** Une partie est calculée automatiquement (la date est-elle
  juste ?). Une autre est donnée par un modèle « juge », dont nous indiquons les biais, et un échantillon
  est relu par un humain pour vérifier le juge.
- **Nous ne sommes ni experts-comptables ni notaires.** Toute réponse de référence qui touche au
  métier est marquée **« à valider par un professionnel »** tant qu'elle n'a pas été relue. Un résultat
  de justesse métier n'est jamais présenté comme établi sans cette validation.
- **Les limites sont écrites** dans chaque publication : nombre de tâches, nombre de passes, méthode de
  notation.

## Vous voulez tester vous-même ?

Le benchmark **ne dépend d'aucun fournisseur**. Sover.tech le lance avec le logiciel vLLM sur des cartes
graphiques louées chez Runpod, mais vous pouvez le lancer sur **votre propre infrastructure** : il suffit
qu'un serveur de modèles compatible avec l'API d'OpenAI soit joignable. La marche à suivre est dans
[`docs/REPRODUIRE.md`](docs/REPRODUIRE.md) : Python, aucune bibliothèque à installer. Un résultat obtenu avec une autre configuration que la nôtre est
accepté, et clairement marqué comme tel.

## Pour aller plus loin

- [Le plan du projet](docs/PLAN.md) : choix techniques, modèles testés, calendrier.
- [Glossaire en langage clair](docs/GLOSSAIRE.md) : LLM, RAG, agent, quantification, etc.
- [Contribuer](CONTRIBUTING.md) : signaler une erreur, relire en tant que professionnel, ajouter une tâche.
- [Guide pour les agents IA](AGENTS.md) : si vous contribuez avec l'aide d'un assistant de code.

## Licences

- Code : [Apache 2.0](LICENSE).
- Jeux de données fictifs (corpus, questions, grilles) : [CC BY 4.0](LICENSE-DATA). Vous pouvez les
  réutiliser en citant ce projet.

Un projet de [Sover.tech](https://sover.tech), qui déploie des assistants IA locaux chez les cabinets et
les PME.
