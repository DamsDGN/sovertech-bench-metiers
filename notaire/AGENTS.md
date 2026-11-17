# Consignes propres au benchmark notaires

À lire après [`../AGENTS.md`](../AGENTS.md), avant d'écrire dans ce dossier. **Aucun notaire n'a relu ce
benchmark** : tout y est « à valider par un professionnel », et aucun résultat ne doit en être publié
avant une relecture.

## L'étude fictive est la seule source de situations

Étude Bruyère & Associés, Quimper, quatre dossiers inventés (`corpus/`). Toute nouvelle tâche s'appuie
sur ce corpus ou sur un **texte public cité**. Ne créez pas un « nouveau dossier » dans une tâche :
ajoutez sa fiche au corpus, avec les mêmes garde-fous que les autres.

Garde-fous du corpus (contrôlés par les tests) :

- mention « DOCUMENT FICTIF » dans chaque document, sauf les textes publics ;
- courriels en `.example`, aucun IBAN, aucun numéro de téléphone, **aucun numéro de sécurité sociale** ;
- personnes, biens et adresses inventés (« résidence fictive », « hameau fictif ») ; **aucune référence
  cadastrale réelle** ;
- aucun acte réel, **même anonymisé ou « pour s'inspirer du format »** : ne collez jamais un acte réel dans une
  conversation avec un agent ;
- chaque document porte `statut` (`en_vigueur`, `obsolete`) et, s'il est remplacé, `remplace_par`.

## Sources publiques admises

Code civil, Code de la construction et de l'habitation, Code de l'urbanisme, Code général des impôts,
jurisprudence publiée, textes sur Légifrance. **Citez l'article.** Si vous ne pouvez pas retrouver le
numéro exact d'un article ou un montant à jour, **écrivez-le dans `incertitude`** plutôt que de le deviner.

## Conventions internes de l'étude fictive

Certaines règles du corpus sont des **choix de l'étude inventée**, pas du droit : convocation 15 jours avant
la signature, alerte 60 jours avant l'échéance de la déclaration de succession, fin du délai de rétractation
calculée par ajout de 10 jours à la date de remise. Elles sont dans les procédures du corpus et recalculées
par `core/donnees.py` (`_controle_notaire`). Ne les présentez jamais comme la pratique du notariat.

Les dates dérivées doivent tomber **un jour ouvré** (la procédure renvoie au notaire tout délai tombant un
week-end) : un test le vérifie.

## Prudence d'abord

Privilégiez les tâches où le comportement attendu est de **relever un fait, signaler un écart ou renvoyer
au notaire**, plutôt que de trancher un point de droit. Une référence ne contient pas de conclusion
juridique : elle décrit ce que les documents établissent et ce qu'il faut vérifier.

## Pièges voulus, à ne pas « réparer »

La procédure remplacée (`proc-avant-contrat-v1`), la grille de frais 2025, la contradiction procédure /
note de réunion (convocations), le prix écrit autrement en lettres et en chiffres (`projet-acte-d021`), le
tableau des apports incohérent (`tableau-apports-d040`), le prêt accordé inférieur à la condition suspensive
(`courriel-banque-d014`), la déclaration d'intention d'aliéner sans réponse (`fiche-dossier-d021`), la grille de
rémunération confidentielle et le courriel à instruction cachée (`mail-heritier-d031`) sont **des épreuves**,
pas des erreurs du corpus. Les corriger change les mesures : signalez-le dans la pull request.

## Fabriquer le corpus

```bash
. .venv/bin/activate                                          # dépendances de outils/requirements.txt
python3 outils/generer_corpus.py --metier notaire             # sources Markdown -> vrais fichiers
python3 outils/extraire_corpus.py tika --metier notaire       # texte figé (Docker, image Apache Tika)
python3 -m core.export_lisible notaire                        # TACHES.md lisibles
python3 -m unittest discover                                  # contrôles de cohérence
```

## Blocs

Mêmes champs que pour les experts-comptables (voir [`../expert-comptable/AGENTS.md`](../expert-comptable/AGENTS.md)).
Les consignes données aux modèles sont dans `prompts.json` ; les bornes du nombre de tâches et les
exigences du corpus sont dans `corpus/formats.json` (`_exigences`).
