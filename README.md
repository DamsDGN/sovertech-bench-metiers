# Bench LLM métiers

**Une intelligence artificielle installée dans votre cabinet ou votre étude est-elle assez bonne pour
vous aider au quotidien ? Ce projet permet de le mesurer, publiquement et en toute transparence.**

> **Projet en construction.** Les premiers résultats sont publiés sur
> [sover.tech/professions-reglementees](https://sover.tech/professions-reglementees/#resultats), pour **quatre assistants**
> (Gemma 4 12B, Qwen 3.8 27B et Qwen 3.6 35B A3B en local, Claude Sonnet 5.5 comme valeur de référence en ligne), en
> **2 passes** par épreuve. Ce sont des résultats préliminaires. Les réponses de référence
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
| Experts-comptables | [`expert-comptable/`](expert-comptable/README.md) | Première version durcie : 91 tâches, 37 documents en vrais formats |
| Notaires | [`notaire/`](notaire/README.md) | Première version durcie : 57 tâches, 34 documents, **aucun notaire ne l'a relue** |

Chaque dossier contient un `README.md` qui explique, **sans jargon**, ce que le benchmark de ce métier
teste, comment il note, et ce que ses résultats veulent dire ou ne veulent pas dire.

## Ce qui rend ce projet fiable (et ce qui ne l'est pas encore)

- **Aucune donnée réelle, jamais.** Les cabinets, clients, dossiers et actes sont **inventés**.
  Quand nous nous appuyons sur le droit ou la comptabilité, ce sont des **textes publics**, cités.
- **Un seul paramètre change : le modèle.** Mêmes documents, mêmes consignes, mêmes outils, mêmes
  réglages pour tous. Chaque épreuve est lancée **plusieurs fois** (5 passes visées, 2 pour les premiers résultats publiés) et on publie la moyenne et la dispersion.
- **Une note n'est pas une vérité.** Une partie est calculée automatiquement (la date est-elle
  juste ?). Une autre est donnée par un modèle « juge », dont nous indiquons les biais, et un échantillon
  est relu par un humain pour vérifier le juge.
- **Nous ne sommes ni experts-comptables ni notaires.** Toute réponse de référence qui touche au
  métier est marquée **« à valider par un professionnel »** tant qu'elle n'a pas été relue. Un résultat
  de justesse métier n'est jamais présenté comme établi sans cette validation.
- **Toutes les erreurs ne se valent pas.** Chaque tâche porte une **gravité** (faible, moyenne, élevée, critique), et
  les rapports publient le **taux d'échec sur les tâches graves** à côté du score global : un modèle qui réussit 90 %
  des tâches mais se trompe sur les plus graves n'est pas présenté comme fiable (voir [`docs/GRAVITE.md`](docs/GRAVITE.md)).
- **Une incertitude honnête.** Rejouer plusieurs fois les mêmes tâches mesure la variabilité du modèle, pas le fait que
  l'on n'ait testé qu'un échantillon de situations. Les écarts entre modèles sont donc comparés **tâche par tâche**,
  avec un intervalle de confiance : deux modèles ne sont départagés que si cet intervalle exclut zéro.
- **Les limites sont écrites** dans chaque publication : nombre de tâches, nombre de passes, méthode de
  notation.
- **Pour la recherche dans les dossiers, le moteur de recherche est le même pour tous et il est simple.** On
  mesure donc comment le modèle exploite des passages déjà retrouvés, pas la performance d'une solution
  documentaire complète (lecture des scans, index, classement des résultats). Ce second sujet est un autre
  benchmark, qui n'existe pas encore.

## Qui est derrière ce projet, et ce que ça change

Sover.tech **vend des assistants IA installés chez ses clients** : nous avons un intérêt à ce que l'IA locale
paraisse crédible. Nous ne nous présentons donc pas comme « indépendants ». Pour limiter le biais :
les épreuves, les références et les contrôles sont publics et rejouables ; les notes automatiques sont séparées
de celles du modèle juge ; le juge est un modèle (Claude), qui est aussi l'un des modèles de comparaison
envisagés, ce que nous écrivons dans chaque rapport ; et un écart n'est annoncé que s'il dépasse l'incertitude.
Ces garde-fous n'effacent pas le conflit d'intérêts : lisez les résultats avec ce recul.

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
