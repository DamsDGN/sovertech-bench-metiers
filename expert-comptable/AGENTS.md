# Consignes propres au benchmark experts-comptables

À lire après [`../AGENTS.md`](../AGENTS.md), avant d'écrire dans ce dossier.

## Le cabinet fictif est la seule source de situations

Cabinet Aubépine & Associés, Lorient, cinq clients inventés (`corpus/`). Toute nouvelle tâche s'appuie
sur ce corpus ou sur un **texte public cité**. Ne créez pas un « nouveau client » dans une tâche : ajoutez
sa fiche au corpus, avec les mêmes garde-fous que les autres.

Garde-fous du corpus (contrôlés par les tests) :

- SIREN fictifs **invalides** au contrôle de Luhn ;
- courriels en `.example` ;
- aucun IBAN, aucun numéro de téléphone réaliste ;
- chaque document porte `statut` (`en_vigueur`, `obsolete`) et, s'il est remplacé, `remplace_par`.

## Sources publiques admises

Plan comptable général (règlement ANC n° 2014-03), Code de commerce, Code général des impôts, Bulletin
officiel des finances publiques (BOFiP), textes sur Légifrance. **Citez l'article ou le règlement.** Si
vous ne pouvez pas retrouver le numéro exact d'un article, **écrivez-le dans `incertitude`** plutôt que
de le deviner.

Ne reprenez pas de contenu protégé (manuels, commentaires d'éditeurs) : reformulez une règle publique
avec sa source.

## Ce qu'on ne met pas dans une référence

- Un taux, un seuil, un plafond ou une date limite **qui change selon l'année ou l'activité** sans date
  de validité (`date_reference_reglementaire`) et source.
- Un conseil fiscal personnalisé présenté comme certain. Pour les tâches de prudence, la référence décrit
  le **comportement attendu** (renvoyer à une vérification, ne pas affirmer), pas une réponse tranchée.
- Une valeur que le corpus ne contient pas, pour une tâche où la bonne réponse est de **s'abstenir**.

## Pièges voulus, à ne pas « réparer »

Les versions obsolètes (`proc-cloture-v1`, `honoraires-2025`, `charte-delais-v1`), la contradiction
devis / facture, les questions sans réponse, le document confidentiel `rh-remunerations-2026` et le courriel
à instruction cachée `mail-kerloch-2026-03` sont **des épreuves**, pas des erreurs du corpus. Les
supprimer ou les corriger change les mesures : signalez-le dans la pull request.

## Blocs

- **Chaque tâche porte une `gravite`** (`faible`, `moyenne`, `elevee`, `critique`), définie dans `docs/GRAVITE.md`. C'est
  une proposition de l'équipe, à valider par un professionnel : ne la présentez pas comme établie.
- Chaque bloc mêle **tâches simples et complexes** (de l'ordre d'un quart à un tiers de complexes) et reste
  représentatif du travail d'un cabinet : une tâche qu'aucun cabinet ne ferait n'a pas sa place. Classer
  honnêtement : une tâche à réponse unique reste « simple », même si son énoncé est long.
- `chat/taches.jsonl` : champs `consigne`, `contexte`, `reference`, `verifications`, `criteres_juge`.
- `rag/questions.jsonl` : champs `question`, `documents_attendus`, `type_question` (`reponse_directe`,
  `version_obsolete`, `contradiction`, `sans_reponse`, `reponse_partielle`, `plusieurs_documents`), `reference`,
  `valeurs_obsoletes`.
- `agentique/taches.jsonl` : champs `consigne`, `etat_final_attendu`, `actions_interdites`,
  `etapes_max`, `pannes`. L'environnement simulé est dans `agentique/environnement/`.

Le détail de chaque champ est dans le `README.md` du bloc.
