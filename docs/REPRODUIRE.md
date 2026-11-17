# Rejouer le benchmark

**Statut : le moteur d'exécution est en cours d'écriture.** Ce guide fixe l'engagement de portabilité et
sera complété avec les commandes réelles quand le moteur sera livré.

## Principe

Le benchmark **ne dépend d'aucun fournisseur**. Il parle à une **API compatible OpenAI**
(`/v1/chat/completions`, appels d'outils compris). Sover.tech lance ses mesures avec le logiciel vLLM sur
des cartes louées chez Runpod, mais n'importe quel serveur compatible convient : vLLM, SGLang, llama.cpp en
mode serveur, Ollama en mode `/v1`, ou le vôtre.

## Deux parcours

**A. Sur votre infrastructure.** Vous disposez déjà d'un serveur de modèles. Vous indiquez son adresse, le
nom du modèle servi et, si besoin, une clé. Vous lancez les épreuves contre cette adresse.

**B. Sur Runpod, comme Sover.tech.** Le module facultatif `core/runpod/` loue une carte, y lance vLLM avec
le modèle voulu, lance le benchmark, puis détruit la machine. Il demande votre clé Runpod et affiche
**le tarif horaire avant toute création**.

## Ce qui est facultatif selon votre infrastructure

- **Mémoire graphique utilisée** : relevée si le moteur peut joindre `nvidia-smi` ou les métriques de
  vLLM. Sinon le champ reste vide, avec la raison écrite.
- **Coût par tâche** : calculé si vous fournissez le tarif horaire de votre machine. Sinon le rapport
  donne le temps de GPU, sans coût.

## Votre résultat est-il comparable au nôtre ?

Nos résultats publiés utilisent des modèles au format **NVFP4** sur une carte graphique **Blackwell** de
48 Go. Si vous utilisez un autre format ou une autre carte, votre résultat est **enregistré et accepté**,
mais **marqué « non comparable »** aux nôtres : un écart de note mélangerait l'effet du modèle et celui de
la configuration.

Chaque résultat porte son contexte : serveur et version, modèle servi, quantification déclarée, matériel si
connu, version des tâches, date.

## Ajouter votre modèle

Le dossier `core/catalogue/` contient un fichier par modèle (dépôt, quantification, réglages recommandés
par l'éditeur). Copiez-en un, adaptez-le, et lancez. Les réglages d'échantillonnage sont ceux de l'éditeur
du modèle, écrits dans le fichier.
