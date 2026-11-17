# Contribuer

Merci de votre intérêt. Ce projet avance mieux avec des regards extérieurs, surtout ceux des
professionnels dont il prétend mesurer les outils.

**En cas d'erreur, tout signalement ou toute contribution est apprécié.** L'équipe n'est composée ni
d'experts-comptables ni de notaires : une réponse de référence peut être fausse, imprécise ou périmée.
Le dire est le meilleur service à rendre au projet.

## La règle absolue : aucune donnée réelle

**Ne déposez jamais** dans ce dépôt, sous aucune forme (fichier, extrait, capture, message de commit,
ticket, discussion) :

- un document d'un client ou d'un cabinet réel, **même anonymisé ou « nettoyé »** ;
- un acte, une facture, un bilan, une fiche réelle ;
- un numéro SIREN, un IBAN, un nom, une adresse, un courriel ou un téléphone de personne réelle ;
- une clé d'accès, un mot de passe, un jeton.

Pourquoi « même anonymisé » ? Parce qu'un document réel anonymisé se ré-identifie souvent, et parce que
la confiance des professionnels est ce que ce projet a de plus précieux.

**Ce qui est accepté** : des situations **inventées**, des textes **publics** (code civil, code de
commerce, plan comptable général, jurisprudence publiée, doctrine administrative) **avec leur source**.
Les courriels fictifs utilisent le domaine réservé `.example` ; les numéros SIREN fictifs sont choisis
pour échouer au contrôle de validité, afin qu'ils ne puissent appartenir à personne.

Un contrôle automatique refuse une partie des erreurs. Il ne remplace pas votre vigilance.

## Vous exercez le métier : relire une réponse de référence

C'est la contribution la plus utile. Pour chaque métier, un fichier `TACHES.md` présente chaque tâche
**dans un format lisible, sans code** : l'énoncé, la réponse attendue, la source citée, et un encadré
« à valider par un professionnel ».

1. Ouvrez le `TACHES.md` du bloc qui vous intéresse (par exemple `expert-comptable/chat/TACHES.md`).
2. Pour chaque tâche, dites : **correcte**, **à corriger** (et comment), ou **à supprimer**.
3. Envoyez-le par un [ticket « Relecture professionnelle »](../../issues/new/choose) : vous n'avez
   besoin ni de Git ni de code.

Votre relecture est consignée dans le champ `statut_validation` de la tâche : votre nom (ou le nom que
vous souhaitez voir publié), la date, et vos commentaires. Vous pouvez demander à rester anonyme.
**Une tâche n'est marquée validée que par une relecture de ce type.**

## Vous avez repéré une erreur

Ouvrez un [ticket « Erreur dans une référence »](../../issues/new/choose) en indiquant :

- la tâche (son identifiant, par exemple `CH-07`) ;
- ce qui est faux ou discutable ;
- **la source publique** qui permet de le dire (article de loi, texte réglementaire, norme) ;
- la correction que vous proposez.

Nous remercions les relecteurs dans l'historique du projet, sauf s'ils préfèrent l'anonymat.

## Vous ajoutez une tâche, un document ou un métier

1. Lisez le `README.md` du métier concerné et le [guide des agents](AGENTS.md) : il décrit le format
   des fichiers, même si vous ne travaillez pas avec un agent.
2. Toute tâche qui touche au métier est créée avec `a_valider_par_pro: true`. **Ne la passez jamais à
   `false` vous-même**, sauf si vous êtes le professionnel qui la relit et que vous l'indiquez.
3. Citez la source publique de chaque règle utilisée. En cas de doute sur un point réglementaire,
   **dites-le** dans le champ `incertitude` : mieux vaut un doute écrit qu'une certitude fausse.
4. Lancez les contrôles : `python3 -m unittest discover` doit passer.
5. Ouvrez une *pull request* depuis une branche, jamais directement sur `main`.

## Vous testez sur votre infrastructure

Voir [`docs/REPRODUIRE.md`](docs/REPRODUIRE.md). Les résultats obtenus avec une autre configuration que
celle de Sover.tech sont les bienvenus, ils sont simplement marqués comme tels.

## Licences

En contribuant, vous acceptez que votre code soit publié sous [Apache 2.0](LICENSE) et que vos jeux de
données fictifs le soient sous [CC BY 4.0](LICENSE-DATA).
