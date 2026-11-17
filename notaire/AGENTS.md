# Consignes propres au benchmark notaires

À lire après [`../AGENTS.md`](../AGENTS.md). **Ce dossier est un squelette : n'y ajoutez ni tâche ni
corpus sans l'accord explicite du mainteneur**, parce qu'aucun notaire n'a encore relu le périmètre.

Quand le travail démarrera :

- **Actes clairement fictifs** : en-tête « DOCUMENT FICTIF » dans chaque acte, personnes et biens
  inventés, adresses inexistantes, numéros SIREN invalides, aucune référence cadastrale réelle.
- **Sources publiques seulement** : code civil, autres codes, jurisprudence publiée. Citer l'article ou
  la décision. Un numéro d'article dont vous n'êtes pas sûr va dans `incertitude`.
- **Mêmes champs de validation** que le dossier `expert-comptable/` : `a_valider_par_pro: true` et
  `statut_validation`.
- **Prudence d'abord** : privilégier des tâches où le comportement attendu est de renvoyer à la lecture
  de l'acte ou à une vérification, plutôt que de trancher un point de droit.
- Ne jamais coller un acte réel dans une conversation avec un agent, même « pour s'inspirer du format ».
