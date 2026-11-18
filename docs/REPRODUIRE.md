# Rejouer le benchmark

Le benchmark **ne dépend d'aucun fournisseur**. Il parle à une **API compatible OpenAI**
(`/v1/chat/completions`, appels d'outils compris). Sover.tech lance ses mesures publiées avec le logiciel
vLLM sur des cartes louées chez Runpod, mais n'importe quel serveur compatible convient : vLLM, SGLang,
llama.cpp en mode serveur, Ollama en mode `/v1`, ou le vôtre.

## Ce qu'il faut

- **Python 3.11 ou plus récent.** Aucune bibliothèque à installer : le moteur n'utilise que la bibliothèque
  standard.
- **Un serveur de modèle joignable** (adresse, nom du modèle servi, éventuellement une clé).
- Rien d'autre : pas de GPU sur la machine qui lance le benchmark, c'est le serveur qui en a besoin.

## Parcours A : sur votre infrastructure

1. Vérifiez que tout est en place (aucun réseau, aucun GPU) :

   ```
   python3 -m unittest discover
   ```

2. Indiquez où est votre serveur. **Ces valeurs restent sur votre machine** : ne les versionnez pas.

   ```
   export BENCH_BASE_URL=http://mon-serveur:8000/v1     # adresse de l'API
   export BENCH_MODEL=nom-du-modele-servi                # nom donné au modèle par le serveur
   export BENCH_API_KEY=...                              # facultatif
   export BENCH_CA_CERT=/chemin/vers/ca.crt              # facultatif, pour un TLS interne
   ```

3. Choisissez le modèle dans le catalogue (`core/catalogue/`, un fichier par modèle) et lancez un
   **essai rapide** : 2 tâches par épreuve, 1 passe.

   ```
   python3 -m core.lancer --modele-catalogue gemma-4-12b-nvfp4-redhatai --passes 1 --limite 2
   ```

4. Lancez la mesure complète : **5 passes**, comme la méthode le prévoit.

   ```
   python3 -m core.lancer --modele-catalogue gemma-4-12b-nvfp4-redhatai --passes 5 \
       --materiel "carte Blackwell 48 Go" --prix-horaire 1.2
   ```

Les résultats sont écrits dans `results/expert-comptable/<date>/<modèle>/` : `resultats.jsonl` (une ligne par
tâche et par passe, avec la réponse complète), `releve.json` (configuration), `rapport.md` et `resume.csv`.

### Options utiles

| Option | Effet |
|---|---|
| `--blocs chat,rag,agentique` | Ne lancer que certaines épreuves |
| `--taches CH-01,RG-02` | Ne lancer que ces tâches |
| `--metier M` | `expert-comptable` (défaut) ou `notaire` |
| `--limite N` | N tâches par épreuve (essais rapides) |
| `--passes N` | Nombre de passes (5 pour une mesure complète) |
| `--reprise` | Reprendre une passe interrompue sans refaire ce qui est fait |
| `--materiel "..."` | Décrire la machine : nécessaire pour qu'un résultat soit « comparable » |
| `--prix-horaire X` | Tarif horaire de la machine : active le coût par tâche |
| `--pause S` | Secondes entre deux tâches, pour ne pas saturer un serveur partagé |
| `--max-tokens N` | Plafond de génération, **raisonnement compris** (32768 par défaut, le même pour tous les modèles). Sur les tâches à long contexte (fichier des écritures comptables), 8192 ne suffisait pas et 16384 coupait encore des réponses. Le rapport signale les réponses coupées ; ne comparez pas deux modèles dont le plafond diffère |

Le lanceur envoie **une requête à la fois**. Si votre serveur est partagé, prévenez ses utilisateurs ou
lancez le benchmark hors des heures d'usage.

## Étalons cloud (modèles facturés à l'usage)

Les fichiers `claude-*-etalon.json` du catalogue pointent sur l'API de l'éditeur. Ils demandent une clé dans
l'environnement (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`), le paquet Python de l'éditeur
(`pip install anthropic`) et **un plafond de dépense obligatoire** :

```
python3 -m core.lancer --modele-catalogue claude-sonnet-5-5-etalon --passes 5 --budget-usd 20
```

La passe s'arrête à une tâche près quand le plafond est atteint, et le rapport le dit. Le coût réel est
calculé depuis les tokens facturés. **Le corpus du benchmark est fictif : ne l'étendez jamais avec des données
réelles avant de l'envoyer à une API cloud.**

### Interroger Claude par le CLI plutôt que par l'API

Sans clé d'API, l'étalon Anthropic peut être interrogé par le CLI `claude` (abonnement) :

```
python3 -m core.lancer --modele-catalogue claude-sonnet-5-5-etalon --via-cli --passes 1 --budget-usd 3
```

Chaque appel lance un processus neuf, dans un dossier temporaire vide, **sans aucun outil**, sans mémoire ni
configuration, avec le prompt système du benchmark : le modèle ne peut pas lire le dépôt ni les réponses de
référence. Le plafond `--budget-usd` reste exigé ; il porte sur un équivalent calculé au tarif du catalogue,
car rien n'est facturé à l'usage. Cette voie diffère d'un appel d'API direct : le CLI ajoute son propre contexte,
le CLI donne la date de la machine au modèle (une consigne ajoutée au prompt système lui demande de l'ignorer), les appels d'outils sont émulés en texte, les conversations à plusieurs tours sont rejouées sous forme de
transcription, et le raisonnement ne se règle pas comme avec l'API. La voie utilisée est
enregistrée dans le relevé (`serveur.voie`) et rappelée dans le rapport.

## Parcours B : sur Runpod, comme Sover.tech

Le module facultatif `core/runpod/` (location d'une carte, lancement de vLLM, destruction de la machine)
**n'est pas encore écrit**. D'ici là, on lance vLLM soi-même sur le pod de son choix, puis on suit le
parcours A en pointant `BENCH_BASE_URL` sur ce pod. Le tarif horaire du pod se passe avec `--prix-horaire`.

## Ce qui est facultatif selon votre infrastructure

- **Mémoire graphique utilisée** : relevée seulement si `nvidia-smi` est disponible sur la machine qui
  lance le benchmark. Sinon le champ reste vide, avec la raison écrite dans le relevé et le rapport.
- **Coût par tâche** : calculé si vous fournissez `--prix-horaire`. Sinon le rapport ne donne que les durées.

## Votre résultat est-il comparable au nôtre ?

Nos résultats publiés utilisent des modèles au format **NVFP4** sur une carte graphique **Blackwell** de
48 Go. Le relevé déclare un résultat « comparable » seulement si **le modèle servi est bien celui du
catalogue** et si **vous avez décrit votre matériel** (`--materiel`). Sinon il est **enregistré et accepté**,
mais **marqué « non comparable »** dans le rapport : un écart de note mélangerait l'effet du modèle et celui de
la configuration. La déclaration du matériel n'est pas vérifiée par le moteur : elle engage son auteur.

## Ajouter votre modèle

Copiez un fichier de `core/catalogue/`, adaptez-le (dépôt, révision, réglages d'échantillonnage de
l'éditeur du modèle, avec la source de ces réglages) et vérifiez-le avec `python3 -m unittest discover`.
Le catalogue **publié** est en NVFP4 uniquement ; pour tester un autre format, gardez votre fichier
localement : le résultat sera marqué « non comparable ».

## Reprendre le rapport

`python3 -m core.rapport results/expert-comptable/<date>/<modèle>` régénère `rapport.md` et `resume.csv` à
partir de `resultats.jsonl` et `releve.json`.
