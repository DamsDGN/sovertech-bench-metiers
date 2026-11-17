# Plan : benchmark de LLM locaux pour experts-comptables et notaires

Statut : **proposition du 17/11/2026, à valider par Damien avant tout code.**
Ce plan est le livrable 1 de la session v0. Il dit ce qu'on construit, dans quel ordre, avec quels
choix, et ce qu'on ne sait pas encore.

## 1. Décisions déjà prises

| Sujet | Décision |
|---|---|
| Dépôt | **Nouveau dépôt public dès le début** : GitHub `DamsDGN/sovertech-bench-metiers` (décision du 17/11/2026, construction « en public »). Conditions : voir §1 bis. |
| Banc interne | Sover.tech garde un banc interne privé de sélection de modèles, qui reste intact. Ce dépôt-ci est indépendant. |
| Structure | Monorepo : un moteur commun (`core/`) et **un dossier par métier à la racine** (`expert-comptable/`, `notaire/`), chacun avec son `README.md`. |
| Portabilité | Sover.tech lance ses mesures avec vLLM sur Runpod, mais **chacun peut rejouer le benchmark sur sa propre infrastructure** (API compatible OpenAI). Voir §5 bis. |
| Blocs | Trois par profession : chat, RAG, agentique. |
| Données | 100 % synthétiques ou publiques. Aucun document de client, même anonymisé. |
| Licences | Apache 2.0 pour le code, CC BY 4.0 pour les jeux de données fictifs. |
| Posture publique | Corrections et signalements bienvenus, écrits en tête de chaque README et dans `CONTRIBUTING.md`. Elle complète la validation par un professionnel, elle ne la remplace pas. |
| Lisibilité | Un `README.md` par benchmark (6) et par profession (2), écrit pour un expert-comptable non technicien. Le jargon va dans `docs/` et dans un glossaire en langage clair. |
| Périmètre modèles | Modèles de 12 à 35 milliards de paramètres qui tiennent sur **48 Go de VRAM**, **uniquement en NVFP4**, publiés par nvidia, RedHatAI ou unsloth : **7 en v0** (§4). |
| v0 | Domaine expert-comptable seul. Le dossier notaire existe en squelette, sans tâches. |

## 1 bis. Conditions d'un dépôt public dès le premier commit

Tout ce qui est poussé est lisible par tous, y compris les brouillons. Donc, avant le premier push :

1. `README.md` racine, `LICENSE` (Apache 2.0), `LICENSE-DATA` (CC BY 4.0) et `CONTRIBUTING.md` sont
   en place, avec l'avertissement « projet en construction, références métier non validées par un
   professionnel, corrections et signalements bienvenus ».
2. **Aucun résultat de mesure n'est versionné avant `comptable-v1`.** `results/` est ignoré par Git
   jusqu'à la première version publiée : un chiffre public sur des références non validées nuirait
   à la crédibilité du projet.
3. **Aucune donnée réelle, aucun nom de client ou de prospect**, ni dans les documents ni dans les
   messages de commit. Un test automatique contrôle le corpus (§7) ; ce plan est relu dans ce sens.
4. Chaque tâche non relue porte `a_valider_par_pro: true` **dans le fichier lui-même**, visible de
   tous, pas seulement dans le rapport.
5. Aucun secret versionné (clé Runpod, jeton Hugging Face). Seul un `.env.example` est poussé.
6. Tout passe par une branche et une pull request, y compris pour Damien : l'historique public
   montre les relectures.

## 2. Relation avec le banc interne

Sover.tech utilise déjà un banc interne, privé, qui mesure débit, TTFT, appels d'outils et relève la
configuration de chaque passe (version de vLLM, révision des poids, matériel, sans secrets).

Ce dépôt est indépendant : il n'importe rien du banc interne. Les briques utiles sont **réécrites ici**,
avec leurs propres tests : client OpenAI compatible en streaming avec mesure du TTFT, relevé de
rejouabilité, masquage des secrets, journal de passe reprenable. Le protocole de notation à l'aveugle
est repris dans son principe (§6), pas dans son code.

## 3. Structure cible

```
sovertech-bench-metiers/
  README.md                 présentation du projet, lisible hors métier tech
  AGENTS.md                 guide des contributeurs qui travaillent avec un agent IA
  CONTRIBUTING.md           règle « aucune donnée réelle », processus de validation par des pros
  LICENSE                   Apache 2.0 (code)
  LICENSE-DATA              CC BY 4.0 (jeux de données fictifs)
  expert-comptable/         un dossier par métier, à la racine
    README.md               ce que fait le benchmark, en langage clair
    AGENTS.md               consignes propres au métier
    corpus/                 cabinet fictif : fiches clients, procédures, textes publics
    chat/                   README.md, taches.jsonl, grille.md, TACHES.md (version lisible)
    rag/                    README.md, questions.jsonl, grille.md, TACHES.md
    agentique/              README.md, taches.jsonl, grille.md, environnement/, TACHES.md
  notaire/                  squelette en v0 : README.md et AGENTS.md, pas de tâches
  core/                     moteur commun
    catalogue/              un fichier par modèle : dépôt HF, quantification, réglages
    execution/              client OpenAI compatible, reprise, mesures
    notation/               scoreurs automatiques, agrégation (moyenne, écart-type)
    rapport/                génération du rapport
    runpod/                 lancement sur Runpod (facultatif, voir §5 bis)
    tests/
  docs/                     PLAN, méthodologie, limites, reproduire, glossaire
  results/                  résultats bruts, ignorés par Git avant comptable-v1
```

Versions publiées : étiquettes Git `comptable-v1`, `notaire-v1`. Une version fige les tâches, les
grilles, les prompts, le retriever et les réglages. Changer l'un d'eux crée une nouvelle version.

Chaque dossier de métier et chaque bloc a un `README.md` écrit pour un professionnel non technicien :
ce qu'on teste, pourquoi ça compte dans un cabinet ou une étude, un exemple, comment on note, ce que le
résultat veut dire et ne veut pas dire, comment signaler une erreur. Un `TACHES.md` lisible, généré
depuis les fichiers de données, permet à un professionnel de relire chaque tâche sans ouvrir de JSON.

Conventions reprises du banc interne de Sover.tech : `unittest` de la bibliothèque standard, aucun test
ne demande de GPU, de réseau ni de clé ; **tests obligatoires pour le code qui note ou qui mesure**,
pas de TDD pour le contenu, dont la garantie est la relecture par un professionnel ; code et noms de fichiers en
français sans accents ; peu de commentaires ; commits Conventional Commits ; branches et pull requests.

## 4. Catalogue de modèles (NVFP4 uniquement)

**Décision du 17/11/2026 : tous les benchmarks utilisent le format NVFP4, et lui seul.** Aucune
comparaison de quantifications en v0 : un écart de note ne mélange donc jamais modèle et format.

**Règle de sélection** : un modèle est retenu s'il existe en NVFP4 publié par **nvidia, RedHatAI ou
unsloth**, s'il pèse entre 12 et 35 milliards de paramètres au total (MoE compris), s'il tient sur une
carte de 48 Go avec un cache de contexte de 32 000 tokens, et si vLLM le sert (balises `vllm`,
`compressed-tensors` ou `modelopt`, architecture connue). Les tailles sont **estimées** (~0,6 octet par
paramètre en NVFP4, soit 16 à 22 Go de poids) : le chargement réel les confirme et le pic de VRAM est
relevé dans chaque résultat. Je n'ai pas encore lancé ces dépôts : la compatibilité vLLM est déduite des
balises, pas testée.

**Source d'un modèle quand plusieurs éditeurs publient un NVFP4** : ce sont des quantifications
différentes, donc des mesures différentes. On en prend **une seule par modèle**, par ordre de priorité
nvidia, puis RedHatAI, puis unsloth. NVIDIA fabrique le format et l'optimise pour Blackwell. Exceptions
justifiées dans le catalogue : Qwen 3.8 27B vient de RedHatAI (modèle déjà retenu par Sover.tech pour son catalogue),
Muse-Glimmer vient de RedHatAI (seul dépôt balisé `vllm`).

| # | Modèle | Dépôt NVFP4 retenu | Particularité |
|---|---|---|---|
| 1 | Qwen 3.8 27B | `RedHatAI/Qwen3.8-27B-NVFP4` | Apache 2.0 |
| 2 | Qwen 3.6 35B A3B | `nvidia/Qwen3.6-35B-A3B-NVFP4` | Apache 2.0, déjà mesuré en FP8 par Sover.tech |
| 3 | Gemma 4 26B A4B | `RedHatAI/gemma-4-26B-A4B-it-NVFP4` | Apache 2.0, aucun NVFP4 chez nvidia |
| 4 | Gemma 4 31B | `RedHatAI/gemma-4-31B-it-NVFP4` | Apache 2.0, pas encore mesuré par Sover.tech |
| 5 | Nemotron 3.5 Lightning 30B-A3B (NVIDIA) | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4` | **licence « other »** à lire avant publication ; ne pas prendre les variantes DSpark et DFlash (décodage spéculatif) |
| 6 | Muse-Glimmer 30B (Meta) | `RedHatAI/Muse-Glimmer-30B-NVFP4` | Apache 2.0 ; **support vLLM à confirmer au chargement** |
| 7 | Ministral 3 14B Instruct (Mistral) | `RedHatAI/Ministral-3-14B-Instruct-2512-NVFP4` | Apache 2.0, le plus récent des Mistral qui tiennent sur 48 Go ; dépôt balisé `compressed-tensors`, sans balise `vllm` : à confirmer au chargement |

**Candidats NVFP4 disponibles, non retenus d'office** (à confirmer par Damien) : Mistral Small 3.2 24B
(`RedHatAI/Mistral-Small-3.2-24B-Instruct-2506-NVFP4`, juin 2025), Qwen 3.6 27B
(`nvidia/Qwen3.6-27B-NVFP4`), Gemma 4 12B (`RedHatAI/gemma-4-12B-it-NVFP4`), Nemotron 3 Nano 30B-A3B
(`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4`, remplacé par la version 3.5).

**Hors périmètre faute de NVFP4 chez ces trois éditeurs** : gpt-oss-20b (format natif MXFP4, pas NVFP4).

**Erreur corrigée le 17/11/2026** : une première recherche concluait à l'absence de NVFP4 Mistral. Elle
était tronquée à 40 résultats triés par date et avait manqué les dépôts RedHatAI de février 2026 et
d'octobre 2025. Une recherche ciblée par nom les trouve. Le catalogue se construit donc par recherche
nominative, jamais par une liste triée et tronquée.

**Hors périmètre faute de place sur 48 Go** : gpt-oss-120b, DeepSeek V4.1 Flash et V4 Pro (~763
milliards de paramètres), Mistral Small 4 (119 milliards), Mistral Medium 3.5 (128 milliards), Mistral
Large 4, Qwen 3.8 2.4T. Chacun reste dans le catalogue avec la raison écrite.

**Pas de version non quantifiée** : en BF16 ces modèles pèsent de 54 à 72 Go et ne tiennent pas, sauf
quelques petits. L'expérience « effet de la quantification » (BF16, FP8, NVFP4) sur un ou deux modèles
est un lot ultérieur, sur une autre carte.

Un modèle dont le chargement ou le parseur d'outils échoue est **signalé comme tel dans le rapport**
et non retiré en silence : « Muse-Glimmer : non évalué, vLLM ne le sert pas à la date du test » est un
résultat.

## 4 bis. Étalons cloud (valeurs de référence)

Les prospects demandent si une IA locale tiendra la comparaison avec les IA cloud. Le benchmark mesure donc
aussi, **sur exactement les mêmes tâches et les mêmes prompts**, quelques modèles cloud « étalons » :
**Claude Sonnet 5.5** et **Claude Opus 5.5** (Anthropic), et un modèle d'OpenAI à choisir.

- Ils sont dans le catalogue avec la catégorie `etalon_cloud`, **hors de la règle NVFP4** : ils ne sont pas
  des candidats à installer chez un client, ils situent l'écart.
- **Réglages = ceux de l'éditeur** : aucun réglage d'échantillonnage n'est envoyé (ces modèles les refusent),
  le niveau d'effort est celui par défaut de l'éditeur, écrit dans le fichier du catalogue.
- **Mesure facturée à l'usage** : le lanceur **exige un plafond** (`--budget-usd`) et s'arrête à une tâche
  près quand il est atteint. Le coût réel par tâche est calculé à partir des tokens facturés et des prix
  relevés sur la page officielle de l'éditeur (date de relevé écrite dans le catalogue).
- **Un étalon est daté** : l'API de l'éditeur peut changer le modèle sans préavis. Les cinq passes d'un étalon
  se font le même jour.
- **Données** : le corpus est fictif et public, l'envoyer à une API cloud ne divulgue rien. Ce n'est vrai que
  pour ce benchmark : **ne jamais envoyer de données de client à une API cloud** avec ces outils.
- **Biais du juge** : si Claude note les épreuves (voir §6) et que Claude est aussi mesuré, il y a un conflit
  d'intérêts. Les scores automatiques n'en souffrent pas ; les scores jugés des étalons Claude sont signalés
  comme tels dans le rapport.
- Pas de repli automatique d'un modèle à un autre (la fonction de repli de l'API fausserait la mesure) : un
  refus du modèle est enregistré comme tel.

## 5. Moteur d'inférence : vLLM (Ollama pour les essais locaux)

**Choix : vLLM sur Runpod pour toutes les mesures publiées.**

- C'est ce que Sover.tech déploie chez le client : on mesure ce qui sera livré.
- Les poids NVFP4 se servent directement. Ollama passe surtout par GGUF, donc par une autre
  quantification : l'écart de note mélangerait modèle et format.
- vLLM expose le débit, le TTFT, le cache de préfixe et le parseur d'outils par modèle. Le banc
  existant l'a déjà éprouvé sur ces cartes.
- Ollama garde un rôle : lancer le moteur en local pour tester le code sans GPU loué.

Contrepartie assumée : les parseurs d'outils diffèrent selon la famille (`gemma4`, `qwen3_xml`, etc.),
donc une part de l'écart agentique vient de cette couche. Le rapport le dit.

**Runpod** : un pod à la fois, une carte de 48 Go **de génération Blackwell**, parce que le NVFP4 n'a de
sens qu'avec le FP4 natif (la RTX PRO 5000 48 Go, déjà utilisée par Sover.tech pour ses campagnes de charge, en est une). Sur Ampere ou
Ada (A40, L40S) il tournerait sans le gain de débit et fausserait les mesures de performance. Le prix horaire est relevé et affiché avant chaque création de pod, et rien
ne se lance sans l'accord de Damien, comme sur le banc interne. L'image vLLM, sa version exacte, le SHA de
révision de chaque modèle et la ligne de commande sont épinglés dans le relevé de rejouabilité.

## 5 bis. Portabilité : le benchmark ne dépend pas de Runpod

**Principe (17/11/2026)** : Sover.tech lance ses mesures avec vLLM sur Runpod, mais **toute personne
doit pouvoir rejouer le benchmark sur sa propre infrastructure**. Runpod est notre façon de louer des
cartes, pas une dépendance du benchmark.

- **Le moteur ne parle qu'à une API compatible OpenAI** (`/v1/chat/completions`, appels d'outils
  compris). vLLM, SGLang, llama.cpp en mode serveur, Ollama en mode `/v1`, ou un autre serveur maison
  conviennent. Réglages par ligne de commande ou variables d'environnement : adresse, modèle, clé.
- **Le module `core/runpod/` est facultatif** : il crée le pod, y lance vLLM et le détruit. Sans lui,
  on lance le benchmark contre l'adresse de son choix. Aucun test ni aucune étape de notation n'en
  dépend.
- **Mesures qui demandent l'infra, rendues facultatives** : le pic de VRAM vient de `nvidia-smi` ou des
  métriques de vLLM si elles sont joignables, sinon le champ reste vide avec sa raison écrite (jamais
  une valeur inventée). Le coût par tâche demande un **tarif horaire fourni par l'utilisateur**
  (`--prix-horaire`) ; sans lui, le rapport donne le temps de GPU et pas de coût.
- **Un résultat porte son contexte** : serveur, version, modèle servi, quantification déclarée, matériel
  si connu. Un résultat obtenu avec une autre quantification que le NVFP4 (autre carte, autre format)
  est enregistré et **marqué « non comparable » aux résultats publiés**, sans être refusé.
- **Le catalogue sert deux usages** : liste des modèles que Sover.tech publie (avec leur dépôt NVFP4),
  et modèle d'un fichier que chacun peut copier pour tester le sien.
- **Guide `docs/REPRODUIRE.md`** : deux parcours, « sur Runpod comme Sover.tech » et « sur mon infra »,
  avec le matériel minimal, les commandes et ce qu'on peut attendre du budget.

## 6. Méthode de mesure

**Ce qui varie : le modèle, et rien d'autre.** Documents, outils, prompts, retriever et paramètres sont
figés et versionnés. Un seul réglage échappe à la règle « identique pour tous » : l'**échantillonnage**.

- **Décision du 17/11/2026 (Q2)** : chaque modèle tourne aux réglages recommandés par son
  éditeur (température, top_p, top_k), écrits en clair dans son fichier de catalogue et versionnés.
  C'est ce que fait le banc interne, parce que c'est ainsi qu'il sera servi au client, et que
  certains modèles (Qwen en mode raisonnement) se dégradent en décodage glouton. Le coût : un écart de
  note mélange modèle et réglage. L'alternative est un réglage commun, plus « iso » mais moins réaliste.
- **5 passes par test**. On enregistre moyenne, écart-type, minimum, maximum et le nombre de passes.
  Pas de graine imposée (même raison que ci-dessus). Un écart entre deux modèles n'est annoncé que s'il
  dépasse la dispersion observée ; sinon le rapport écrit « non discriminant ».
- **Mesures systématiques** : débit (tokens/s), TTFT, temps par tâche, pic de VRAM (`nvidia-smi`,
  échantillonné pendant la passe), **coût par tâche** = temps de GPU consommé par la tâche × tarif
  horaire du pod. Le coût exclut le chargement du modèle, qui est rapporté à part.
- **Budget GPU** : environ 55 tâches × 5 passes ≈ 275 générations par modèle, ×7 ≈ 1 925 au total.
  Estimation brute ~15 h de GPU, soit **~30 h à budgéter** après doublement de l'estimation brute (règle de prudence de Sover.tech),
  hors rechargement et incidents. Le tarif horaire exact est à relever avant lancement.
  Corriger une tâche ou une grille après la première lecture oblige à **relancer** tous les modèles.

### Bloc chat

Qualité du français, respect des consignes, refus quand l'information manque, invention de faits.

- **Automatique d'abord** : longueur, format demandé, présence de mentions obligatoires, détection des
  chiffres ou références absents du contexte fourni, abstention (« je ne peux pas répondre ») quand
  la tâche est construite sans réponse possible.
- **Modèle juge sinon**, avec une grille écrite par critère et une échelle courte. Le rapport indique le
  modèle juge, sa version, et ses biais connus : préférence pour les réponses longues, favoritisme pour
  son propre style, sensibilité à l'ordre. Le juge n'est **jamais** un modèle du catalogue testé.
- **Décision du 17/11/2026 : le juge est Claude, en session, à l'aveugle** (protocole du banc interne de
  Sover.tech). Conséquences écrites dans `docs/LIMITES.md` : la notation du bloc chat **n'est pas
  rejouable par un tiers** (elle dépend d'une session humaine), contrairement aux vérifications
  automatiques, au RAG chiffré et à l'agentique, qui le sont. Pour rester défendable :
  1. la grille de notation est publique et versionnée ;
  2. le lot soumis au juge est anonymisé et mélangé : ni nom de modèle ni identifiant de tâche, et
     le juge ne reçoit **que** ce fichier, hors du dépôt ;
  3. chaque note porte sa provenance (`juge`, version du modèle, `note_le`) dans le résultat ;
  4. l'échantillon relu par un humain sert à publier l'accord juge / humain ;
  5. le rapport affiche séparément les scores **automatiques** (rejouables) et les scores **jugés**
     (non rejouables), pour que le lecteur sache lesquels il peut reproduire.
- **Échantillon relu par un humain** pour mesurer l'accord juge / humain (proposition : 20 % des
  réponses jugées, tirées au hasard, accord publié). Damien relit la langue et les consignes ; le
  fond métier relève d'un professionnel (§7).

### Bloc RAG

On sépare **récupération** et **génération**.

- **Même retriever pour tous** : modèle d'embedding, découpage, top-k, re-classement éventuel, tous
  figés et épinglés (choix de l'embedder à faire et à vérifier sur du français, pas encore arrêté).
- **Récupération** : le bon passage est-il dans les k premiers ? Rappel@k et rang réciproque moyen,
  calculés **sans modèle**, parce que chaque question a ses passages attendus déclarés.
- **Génération** : fidélité aux extraits (aucune affirmation hors passages fournis), citation de la
  source (l'identifiant du passage cité existe et soutient la phrase : vérifiable par programme),
  « je ne sais pas » quand la réponse n'y est pas.
- **Pièges dans le corpus** : questions **sans réponse**, passages **contradictoires**, **versions
  obsolètes** d'un même document (la bonne réponse est la version en vigueur, avec sa date).

### Bloc agentique

- **Environnement simulé** et déterministe, outils factices : `rechercher`, `lire`,
  `extraire_champs`, `ecrire_tableau`, `rediger_mail` (rédige, **n'envoie jamais**).
- **Tâches à plusieurs étapes**, notées **automatiquement sur l'état final** : le tableau contient-il
  les bonnes valeurs, le brouillon de mail existe-t-il et dit-il ce qu'il faut.
- **Critères** : état final, justesse des appels d'outils (bons arguments), nombre d'étapes (efficacité),
  reprise après erreur (outil factice qui échoue une fois), **absence d'action interdite** (écrire hors
  de la plage autorisée, lire un dossier hors périmètre, tenter d'envoyer le mail).

### Réutiliser ou non : Inspect AI, promptfoo, Ragas

Étude faite sur la documentation publique et la presse ; je n'ai **pas encore** exécuté ces outils, donc
la décision d'Inspect AI passe par un essai de une demi-journée avant engagement.

| Outil | Ce que c'est | Décision proposée |
|---|---|---|
| **Inspect AI** (UK AISI) | Cadre Python : jeu de tâches, « solveurs » (dont boucle d'agent avec outils), « scoreurs », journaux ; licence MIT d'après la plupart des sources (une source dit Apache 2.0 : **à vérifier dans le dépôt officiel**) | **À adopter pour le bloc agentique et si l'essai est concluant, pour la définition des tâches, les 5 passes et les journaux.** Il couvre exactement ce qu'on veut coder (boucle d'outils, notation sur état final). `core/mesures` garde TTFT, débit, VRAM, coût, qu'il ne fournit pas à ma connaissance. |
| **promptfoo** | Outil Node/YAML de test de prompts et de red-teaming ; MIT ; **racheté par OpenAI en mars 2026**, promesse de rester ouvert, clôture de l'opération non confirmée | **Écarté.** Chaîne Node dans un dépôt Python, peu adapté à la notation sur état d'un environnement simulé, et propriétaire en train de changer chez un acteur dont les modèles figurent au catalogue. |
| **Ragas** | Bibliothèque Python de mesure RAG, Apache 2.0 ; fidélité, pertinence, précision et rappel du contexte, presque toutes par modèle juge ; sources secondaires uniquement, **docs officielles à lire** | **Non adopté comme socle.** Le rappel et la précision de récupération se calculent sans juge puisque nos passages attendus sont déclarés. Pour la fidélité, on code des vérifications déterministes, et Ragas sert de **recoupement sur un échantillon**, avec ses prompts en anglais par défaut à traduire. |

## 7. Données et validation métier

- **Aucun fait réglementaire inventé.** Chaque tâche qui dépend d'une règle juridique, fiscale ou
  comptable porte un champ `source_publique` (Légifrance, BOFiP, plan comptable général publié, etc.)
  et une date de validité (« en vigueur au JJ/MM/AAAA »).
- **Champ explicite `a_valider_par_pro`**, `true` par défaut, sur toute réponse de référence et toute
  grille qui touche le métier, avec `statut_validation` (`non_relu`, `relu_par`, `date`, `commentaire`).
  Le rapport affiche la part de tâches validées à côté de chaque score métier, et **ne présente jamais**
  une justesse métier comme établie tant que la validation manque.
- **Corpus fictif du cabinet** : cabinet, clients et pièces inventés (noms, SIREN et montants fictifs
  et cohérents entre eux), mélangés à des textes publics. Un test automatique refuse un SIREN ou un
  IBAN qui passerait pour réel, et tout motif de données personnelles.
- **Notaire** : sources publiques (code civil, jurisprudence publiée) et actes clairement fictifs.
  Squelette seulement en v0.
- **Contribution** : ticket « erreur dans une référence » (tâche, source, correction proposée). Un
  professionnel relecteur est crédité dans l'historique de validation.

## 8. Livrables et commits (un commit par étape)

1. `docs(plan)` : ce plan, une fois validé.
2. `chore(depot)` : squelette, licences, `README.md`, `CONTRIBUTING.md`, `AGENTS.md`.
3. `feat(core)` : catalogue de modèles (schéma + 7 fichiers) et son test de cohérence.
4. `feat(core)` : exécution minimale (client, mesures, journal reprenable), avec tests.
5. `feat(core)` : relevé de rejouabilité, avec tests.
6. `feat(domaine)` : corpus fictif du cabinet et son contrôle automatique de données.
7. `feat(chat)` : 15 à 20 tâches, grilles, README du bloc.
8. `feat(rag)` : corpus indexé, retriever figé, 15 à 20 tâches, README du bloc.
9. `feat(agentique)` : environnement simulé, 15 à 20 tâches, README du bloc.
10. `feat(notation)` : scoreurs, juge, agrégation sur 5 passes.
11. `feat(rapport)` : génération du rapport avec limites et part de références validées.
12. `docs` : méthodologie, limites, guide de reproduction, glossaire.
13. Script de lancement Runpod (essai à sec, puis passe réelle sur accord de Damien).

Les tests couvrent le moteur, la notation, le corpus et le rapport. Aucun ne demande de GPU, de réseau
ou de clé.

## 9. Ce que les premiers résultats pourront dire, et ce qu'ils ne diront pas

Avec 15 à 20 tâches par bloc et 5 passes, les écarts fins entre deux modèles voisins seront souvent dans
le bruit : le rapport donnera la dispersion et dira « non discriminant » quand c'est le cas. Les
résultats sont valables pour **ce corpus fictif**, ces prompts, ces quantifications et ces versions de
vLLM, à ces dates. Ils ne disent rien d'un cabinet réel, ni de la justesse métier tant que
`a_valider_par_pro` reste vrai.

## 10. Questions ouvertes

- **Q1. Quel modèle juge ?** Tranchée le 17/11/2026 : **Claude en session, à l'aveugle** (§6, bloc chat).
- **Q2. Échantillonnage** : tranchée le 17/11/2026, **réglages recommandés par l'éditeur, modèle par modèle** (§6).
- **Q3. Qui valide le métier ?** Un relecteur existe, mais **plus tard** (réponse du 17/11/2026). La v0
  avance donc avec toutes les références en `a_valider_par_pro: true`. Conséquence : aucun résultat
  de justesse métier n'est présenté comme établi, et `comptable-v1` n'est publié avec ses résultats
  qu'après cette relecture (§1 bis, point 2).
- **Q4. Nom du dépôt** : tranchée, `sovertech-bench-metiers` (créé sur GitHub par Damien).
- **Q5. Inspect AI** : essai d'une demi-journée en début d'étape 4, décision documentée ensuite.
- **Q6. Muse-Glimmer et Nemotron** : support vLLM et licence à confirmer ; sinon ils sortent du lot
  avec la raison écrite.
- **Q7. Candidats NVFP4 non retenus d'office** : ajouter Mistral Small 3.2 24B, Qwen 3.6 27B, Gemma 4
  12B, Nemotron 3 Nano ?
- **Q8. Visibilité du dépôt GitHub** : tranchée le 17/11/2026, **public dès le début** (§1 bis).
