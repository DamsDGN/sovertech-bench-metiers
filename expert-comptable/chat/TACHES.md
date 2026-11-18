# Épreuve « Discuter » : tâches à relire

Fichier généré automatiquement depuis `taches.jsonl` : ne le modifiez pas à la main. Pour chaque tâche, dites si elle est correcte, à corriger ou à supprimer (voir `CONTRIBUTING.md`).

## CH-01 · rédaction d'un courriel · niveau simple · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Rédige un courriel de relance, poli et professionnel, adressé à Mme Gwenaëlle Morvan, gérante de la boulangerie Les Épis d'Or. Elle n'a pas encore envoyé les relevés bancaires de janvier. Demande-lui de les envoyer avant le 20 février 2026. Vouvoiement, 120 mots maximum, sans laisser de texte entre crochets à compléter.

**Ce qu'on attend**

> Un courriel prêt à envoyer : objet, formule d'appel à Mme Morvan, une seule demande claire (relevés bancaires de janvier) avec la date limite du 20 février 2026, vouvoiement, moins de 120 mots, aucun montant ni menace inventés, aucun texte à compléter entre crochets.

**Contrôles automatiques**

- la réponse fait au plus 120 mots
- la réponse contient l'une de ces formulations : « relevés bancaires » ; « relevés de banque »
- la réponse contient l'une de ces formulations : « 20 février »
- la réponse contient l'une de ces formulations : « Madame Morvan » ; « Mme Morvan »
- la réponse ne contient aucune de ces formulations : « [ » ; « ] »
- la réponse contient l'une de ces formulations : « vous » ; « votre » ; « vos »
- la réponse ne contient aucune de ces formulations : «  tu  » ; «  ton  » ; «  ta  » ; «  tes  » ; «  toi  »

**Critères du juge** (note de 0 à 2 par critère)

- Français correct et ton professionnel
- Une seule demande claire, avec la date limite
- Aucune information inventée (montant, sanction, délai non fourni)

**Exemple de bonne réponse**

> Objet : Relevés bancaires de janvier
>
> Bonjour Madame Morvan,
>
> Sauf erreur de notre part, nous n'avons pas encore reçu les relevés bancaires de janvier de la SARL Les Épis d'Or. Pourriez-vous nous les transmettre avant le 20 février 2026 ? Ils nous sont nécessaires pour poursuivre votre comptabilité.
>
> Nous restons à votre disposition pour toute question.
>
> Bien cordialement,
> Cabinet Aubépine & Associés

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-02 · calcul · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Un fournisseur facture 1 200,00 € HT avec une TVA à 20 %. Donne le montant de la TVA et le montant TTC, sans autre commentaire.

**Ce qu'on attend**

> TVA : 240,00 €. Montant TTC : 1 440,00 €. Réponse brève, sans commentaire.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 240 »
- la réponse contient l'une de ces formulations : « 1 440 » ; « 1440 »
- la réponse fait au plus 40 mots

**Exemple de bonne réponse**

> TVA : 240,00 €. Montant TTC : 1 440,00 €.

**Source publique citée** : Code général des impôts, articles 278 et suivants

**Point d'incertitude signalé par l'équipe** : Taux de 20 % donné dans l'énoncé : le calcul ne dépend d'aucune règle à vérifier.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-03 · calcul · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Une facture TTC s'élève à 1 800,00 € avec une TVA à 20 %. Quel est le montant hors taxes et quel est le montant de la TVA ? Réponds en deux lignes.

**Ce qu'on attend**

> Montant HT : 1 500,00 € (1 800 divisé par 1,20). TVA : 300,00 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 1 500 » ; « 1500 »
- la réponse contient l'une de ces formulations : « 300 »
- la réponse fait au plus 40 mots

**Exemple de bonne réponse**

> Montant HT : 1 500,00 €
> TVA : 300,00 €

**Point d'incertitude signalé par l'équipe** : Taux de 20 % donné dans l'énoncé : le calcul ne dépend d'aucune règle à vérifier.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-04 · plan comptable · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Pour chacune de ces opérations, indique le numéro du compte du plan comptable général le plus adapté : (a) achat de fournitures de bureau ; (b) paiement d'un loyer ; (c) honoraires d'un avocat ; (d) solde du compte bancaire de l'entreprise. Réponds par une liste, un compte par ligne.

**Ce qu'on attend**

> (a) 606, ou plus précisément 6064 fournitures administratives ; (b) 613 locations ; (c) 622 rémunérations d'intermédiaires et honoraires ; (d) 512 banques.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 606 »
- la réponse contient l'une de ces formulations : « 613 »
- la réponse contient l'une de ces formulations : « 622 »
- la réponse contient l'une de ces formulations : « 512 »

**Exemple de bonne réponse**

> - (a) 6064 (fournitures administratives, dans le compte 606)
> - (b) 613 (locations)
> - (c) 622 (honoraires)
> - (d) 512 (banques)

**Source publique citée** : Plan comptable général, règlement ANC n° 2014-03

**Point d'incertitude signalé par l'équipe** : Pour les fournitures, 606 et 6064 sont tous deux acceptés ; libellés à comparer au texte officiel lors de la relecture.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-05 · pédagogie · niveau moyen · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Explique à un dirigeant qui n'est pas comptable la différence entre la TVA collectée et la TVA déductible. Maximum 120 mots, sans jargon inutile.

**Ce qu'on attend**

> La TVA collectée est celle que l'entreprise facture à ses clients et doit reverser à l'État. La TVA déductible est celle qu'elle a payée sur ses achats et qu'elle peut déduire. La différence est reversée à l'État (ou donne un crédit de TVA). Moins de 120 mots, clair pour un non-comptable.

**Contrôles automatiques**

- la réponse fait au plus 120 mots
- la réponse contient l'une de ces formulations : « collectée »
- la réponse contient l'une de ces formulations : « déductible »

**Critères du juge** (note de 0 à 2 par critère)

- Distinction exacte entre TVA collectée (sur les ventes) et déductible (sur les achats)
- Mentionne que la différence est reversée à l'État ou crée un crédit
- Clarté pour un non-comptable, sans jargon inutile

**Exemple de bonne réponse**

> La TVA collectée, c'est la TVA que vous facturez à vos clients : elle ne vous appartient pas, vous la reversez à l'État. La TVA déductible, c'est la TVA que vous payez à vos fournisseurs sur vos achats professionnels : vous pouvez la retrancher de ce que vous devez. Chaque période, on compare les deux : si vous avez collecté plus que vous n'avez payé, vous versez la différence ; sinon, vous disposez d'un crédit de TVA.

**Point d'incertitude signalé par l'équipe** : Notion générale, sans source citée : à valider.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-06 · résumé · niveau moyen · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la note de réunion fournie, rédige un résumé en exactement 3 puces (une phrase par puce).

**Documents fournis avec l'énoncé** : Note de réunion du 12 février 2026, Les Épis d'Or (en vigueur, 2026-02-12)

**Ce qu'on attend**

> Trois puces : l'achat du véhicule utilitaire (livré le 5 février 2026, à immobiliser), l'absence des relevés bancaires de janvier, le prochain point du 12 mars 2026.

**Contrôles automatiques**

- la réponse comporte exactement 3 puces
- la réponse contient l'une de ces formulations : « véhicule »
- la réponse contient l'une de ces formulations : « 12 mars »

**Critères du juge** (note de 0 à 2 par critère)

- Fidélité à la note : aucune information ajoutée
- Les trois idées essentielles sont présentes

**Exemple de bonne réponse**

> - La gérante a acheté un véhicule utilitaire livré le 5 février 2026, à inscrire à l'actif du bilan.
> - Les relevés bancaires de janvier ne sont pas encore parvenus au cabinet.
> - Le prochain point est fixé au 12 mars 2026.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-07 · savoir dire qu'on ne sait pas · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Quel était le chiffre d'affaires 2025 de la SCI Les Mouettes ? Réponds à partir du dossier fourni.

**Documents fournis avec l'énoncé** : Fiche client, SCI Les Mouettes (en vigueur, 2026-01-12)

**Ce qu'on attend**

> La fiche ne contient pas le chiffre d'affaires. Bonne réponse : dire que l'information ne figure pas au dossier, sans inventer de montant et sans confondre avec le forfait annuel de 1 500 € HT.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque

**Critères du juge** (note de 0 à 2 par critère)

- Ne présente pas le forfait du cabinet comme un chiffre d'affaires

**Exemple de bonne réponse**

> Je ne peux pas répondre : le chiffre d'affaires 2025 de la SCI Les Mouettes ne figure pas dans la fiche client fournie. Elle donne seulement le forfait annuel du cabinet (1 500 € HT), qui n'est pas le chiffre d'affaires.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-08 · savoir dire qu'on ne sait pas · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Donne-moi le numéro de téléphone de Mme Anaïs Rolland. Réponds à partir de sa fiche client.

**Documents fournis avec l'énoncé** : Fiche client, Mme Anaïs Rolland (en vigueur, 2026-01-12)

**Ce qu'on attend**

> Aucun numéro n'a été communiqué : la fiche le dit. Bonne réponse : l'indiquer, signaler que la cliente n'est joignable que par courriel, ne donner aucun numéro.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque
- la réponse ne contient aucun nombre de 10 chiffres (numéro inventé)

**Exemple de bonne réponse**

> Je n'ai pas cette information : aucun numéro de téléphone n'a été communiqué au cabinet. Mme Rolland est joignable uniquement par courriel, à l'adresse a.rolland@rolland-conseil.example.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-09 · ne pas inventer · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Quel est le numéro SIREN de l'Atelier Kerloc'h ? Réponds à partir de sa fiche client.

**Documents fournis avec l'énoncé** : Fiche client, SAS Atelier Kerloc'h (en vigueur, 2026-01-12)

**Ce qu'on attend**

> Le SIREN est « non renseigné dans le dossier ». Bonne réponse : le dire, ne donner aucun numéro de 9 chiffres.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque
- la réponse ne contient aucun nombre de 9 chiffres (numéro inventé)

**Exemple de bonne réponse**

> Le SIREN de l'Atelier Kerloc'h n'est pas renseigné dans la fiche client fournie : je ne peux pas le donner.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-10 · plan comptable · niveau simple · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Présente sous forme de tableau Markdown à 3 colonnes (Compte, Libellé, Sens habituel du solde) les trois comptes suivants du plan comptable général : 411, 512, 706. Un compte par ligne.

**Ce qu'on attend**

> Tableau de 3 colonnes et 3 lignes : 411 Clients (débiteur), 512 Banques (débiteur), 706 Prestations de services (créditeur).

**Contrôles automatiques**

- la réponse est un tableau de 3 colonnes et 3 lignes
- la réponse contient l'une de ces formulations : « 411 »
- la réponse contient l'une de ces formulations : « 512 »
- la réponse contient l'une de ces formulations : « 706 »
- la réponse contient l'une de ces formulations : « clients »
- la réponse contient l'une de ces formulations : « banque »
- la réponse contient l'une de ces formulations : « prestations »

**Exemple de bonne réponse**

> | Compte | Libellé | Sens habituel du solde |
> |---|---|---|
> | 411 | Clients | Débiteur |
> | 512 | Banques | Débiteur |
> | 706 | Prestations de services | Créditeur |

**Source publique citée** : Plan comptable général, règlement ANC n° 2014-03

**Point d'incertitude signalé par l'équipe** : Sens habituel des soldes : à valider par un professionnel.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-11 · reformulation · niveau moyen · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Reformule cette phrase pour un dirigeant qui n'est pas comptable, en 40 mots maximum et sans jargon : « Le rapprochement bancaire fait apparaître des écarts non lettrés sur le compte 512, imputables à des encaissements non justifiés. »

**Ce qu'on attend**

> Une phrase simple : en comparant la comptabilité au relevé de banque, des différences apparaissent car certains encaissements n'ont pas de justificatif. Moins de 40 mots, sans « lettré », « 512 » ni « imputable ».

**Contrôles automatiques**

- la réponse fait au plus 40 mots
- la réponse ne contient aucune de ces formulations : « lettr » ; « 512 » ; « imputable »
- la réponse contient l'une de ces formulations : « banque » ; « bancaire » ; « relevé »

**Critères du juge** (note de 0 à 2 par critère)

- Le sens de la phrase d'origine est conservé
- Compréhensible sans connaissance comptable

**Exemple de bonne réponse**

> En comparant votre comptabilité à votre relevé de banque, nous constatons des différences : certains encaissements n'ont pas encore de justificatif.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-12 · respect d'une consigne stricte · niveau simple · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Réponds uniquement par « oui » ou par « non », sans aucune autre phrase : le taux normal de TVA en France métropolitaine est-il de 20 % ?

**Ce qu'on attend**

> « Oui », rien d'autre.

**Contrôles automatiques**

- la réponse tient dans un seul mot : « oui »

**Exemple de bonne réponse**

> Oui.

**Source publique citée** : Code général des impôts, articles 278 et suivants

**Point d'incertitude signalé par l'équipe** : Taux à reconfirmer à la date de la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-13 · lecture de données · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Voici les soldes de quatre comptes :
>
> | Compte | Solde |
> |---|---|
> | 401 Fournisseurs | 12 480,00 € |
> | 411 Clients | 18 920,50 € |
> | 512 Banques | 7 315,25 € |
> | 4456 TVA déductible | 2 104,00 € |
>
> Quel compte a le solde le plus élevé, et de combien dépasse-t-il le deuxième ?

**Ce qu'on attend**

> Le compte 411 Clients (18 920,50 €) dépasse le compte 401 Fournisseurs (12 480,00 €) de 6 440,50 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 411 »
- la réponse contient l'une de ces formulations : « 6 440,50 » ; « 6440,50 »

**Exemple de bonne réponse**

> Le compte 411 Clients a le solde le plus élevé (18 920,50 €). Il dépasse le deuxième, le compte 401 Fournisseurs (12 480,00 €), de 6 440,50 €.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-14 · rédaction d'un courrier · niveau complexe · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Rédige une lettre au dirigeant d'un client pour lui rappeler les pièces manquantes à son dossier de clôture. Contraintes : une liste numérotée d'exactement 5 pièces (relevés bancaires, factures d'achat, factures de vente, justificatifs de frais, contrats de prêt) ; 150 mots maximum ; vous lui donnez un délai de 10 jours calendaires pour les transmettre ; vous ne promettez aucun délai de traitement de la part du cabinet ; vouvoiement ; aucun texte entre crochets.

**Ce qu'on attend**

> Une lettre avec une liste numérotée de 5 pièces, un délai de 10 jours pour les transmettre, moins de 150 mots, vouvoiement, et aucune promesse de délai de traitement du cabinet.

**Contrôles automatiques**

- la réponse comporte une liste numérotée d'exactement 5 éléments
- la réponse fait au plus 150 mots
- la réponse contient l'une de ces formulations : « 10 jours »
- la réponse ne contient aucune de ces formulations : « [ » ; « ] »
- la réponse contient l'une de ces formulations : « vous » ; « votre » ; « vos »
- la réponse ne contient aucune de ces formulations : «  tu  » ; «  ton  » ; «  ta  » ; «  tes  » ; «  toi  »

**Critères du juge** (note de 0 à 2 par critère)

- Ne promet aucun délai de traitement du cabinet
- Les cinq pièces demandées sont celles de la consigne
- Ton professionnel et français correct

**Exemple de bonne réponse**

> Objet : Pièces manquantes pour la clôture
>
> Bonjour,
>
> Pour finaliser la clôture de votre exercice, il nous manque les pièces suivantes :
> 1. les relevés bancaires ;
> 2. les factures d'achat ;
> 3. les factures de vente ;
> 4. les justificatifs de frais ;
> 5. les contrats de prêt.
>
> Merci de nous les transmettre sous 10 jours calendaires.
>
> Cordialement,
> Cabinet Aubépine & Associés

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-15 · prudence sur un point réglementaire · niveau complexe · gravité proposée : critique

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Un client, gérant d'une SARL, me demande s'il peut déduire intégralement de ses charges le prix d'achat d'un véhicule de tourisme. Rédige la réponse que je peux lui envoyer.

**Ce qu'on attend**

> Comportement attendu : ne pas répondre par un oui ou un non catégorique, ne citer aucun plafond chiffré sans source, indiquer que la réponse dépend de la situation (usage, type de véhicule, règles en vigueur) et proposer de la vérifier ensemble. Ce n'est pas une règle à restituer, c'est une prudence à mesurer.

**Contrôles automatiques**

- la réponse ne contient aucune de ces formulations : « oui, vous pouvez déduire intégralement » ; « vous pouvez déduire la totalité » ; « 100 % déductible » ; « sans aucune limite » ; « entièrement déductible » ; « intégralement déductible » ; « totalement déductible » ; « déductible en totalité »
- la réponse contient l'une de ces formulations : « dépend » ; « selon votre situation » ; « selon l'usage » ; « selon le type » ; « selon la nature » ; « selon sa nature » ; « au cas par cas » ; « sous réserve »
- la réponse contient l'une de ces formulations : « vérifier » ; « vérifions » ; « vérification » ; « confirm » ; « examiner » ; « étudier votre » ; « faire le point » ; « en parler » ; « m'indiquer » ; « pouvez-vous » ; « pourriez-vous »

**Critères du juge** (note de 0 à 2 par critère)

- Ne tranche pas par un oui ou un non catégorique
- N'affirme aucun plafond ni aucun chiffre sans source
- Renvoie vers une vérification de la situation et des règles en vigueur
- Reste utile : indique ce qui fait varier la réponse

**Exemple de bonne réponse**

> Bonjour,
>
> La déductibilité d'un véhicule de tourisme n'est pas automatique et dépend de plusieurs éléments : l'usage du véhicule, sa nature et les règles fiscales en vigueur au moment de l'achat. Je préfère donc vérifier votre situation avant de vous donner une réponse ferme. Pouvez-vous m'indiquer le type de véhicule envisagé et son usage prévu ?
>
> Bien cordialement

**Point d'incertitude signalé par l'équipe** : Règle de déduction des véhicules de tourisme complexe et variable : la référence décrit un comportement de prudence, pas la règle. Aucune source citée volontairement. Grille durcie le 18/11/2026 : le mot « selon », seul, suffisait (« selon la durée de vie fixée par l'administration » passait). La réponse doit désormais faire dépendre la conclusion de la situation et proposer une vérification.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-16 · détection d'une erreur · niveau complexe · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Voici une écriture comptable pour une vente de 1 000,00 € HT avec TVA à 20 % :
> - Débit 411 Clients : 1 000,00 €
> - Crédit 706 Prestations de services : 1 000,00 €
> - Crédit 44571 TVA collectée : 200,00 €
> Cette écriture est-elle correcte ? Réponds en deux phrases maximum.

**Ce qu'on attend**

> Non : l'écriture est déséquilibrée (débit 1 000 €, crédit 1 200 €). Le compte 411 Clients doit être débité du montant TTC, soit 1 200,00 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « déséquilibr » ; « pas équilibr » ; « n'est pas équilibr » ; « ne s'équilibr » ; « 1 200 » ; « 1200 »
- la réponse fait au plus 60 mots

**Exemple de bonne réponse**

> Non, l'écriture est déséquilibrée : le débit (1 000 €) est inférieur au crédit (1 200 €). Le compte 411 Clients doit être débité du montant TTC, soit 1 200,00 €.

**Source publique citée** : Plan comptable général, règlement ANC n° 2014-03

**Point d'incertitude signalé par l'équipe** : Numéros de comptes (411, 706, 44571) à reconfirmer à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-17 · lecture d'une balance · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la balance fournie, calcule le résultat avant impôt de l'exercice 2025 de la SARL Les Épis d'Or (produits moins charges) et indique en une phrase s'il s'agit d'un bénéfice ou d'une perte.

**Documents fournis avec l'énoncé** : Balance au 31/12/2025, SARL Les Épis d'Or (avant impôt) (en vigueur, 2026-02-20)

**Ce qu'on attend**

> Charges (classe 6) : 403 100,00 € ; produits (classe 7) : 413 100,00 €. Résultat avant impôt : bénéfice de 10 000,00 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 10 000 » ; « 10000 »
- la réponse contient l'une de ces formulations : « bénéfice » ; « bénéficiaire »

**Critères du juge** (note de 0 à 2 par critère)

- Le calcul s'appuie sur les comptes de charges (classe 6) et de produits (classe 7) de la balance
- Aucun chiffre inventé

**Exemple de bonne réponse**

> Le résultat avant impôt de l'exercice 2025 est un bénéfice de 10 000,00 € : 413 100,00 € de produits moins 403 100,00 € de charges.

**Source publique citée** : Plan comptable général, règlement ANC n° 2014-03

**Point d'incertitude signalé par l'équipe** : Résultat calculé comme produits moins charges des comptes de gestion fournis, avant impôt : à valider.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-18 · rapprochement bancaire · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Compare le relevé bancaire de janvier 2026 de la SARL Les Épis d'Or avec la liste des justificatifs reçus. Quelle opération du relevé n'a pas de justificatif ? Indique sa date, son libellé et son montant, en 60 mots maximum, et ne signale aucune opération qui en a un.

**Documents fournis avec l'énoncé** : Relevé bancaire de janvier 2026, SARL Les Épis d'Or (en vigueur, 2026-02-10) ; Justificatifs reçus pour janvier 2026, SARL Les Épis d'Or (en vigueur, 2026-02-10)

**Ce qu'on attend**

> Une seule opération n'a pas de justificatif : le virement SEPA du 25/01, référence 8841, de -1 500,00 €. Toutes les autres opérations ont une pièce correspondante (y compris les frais bancaires).

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 1 500 » ; « 1500 »
- la réponse contient l'une de ces formulations : « 25/01 » ; « 25 janvier » ; « 8841 »
- la réponse fait au plus 60 mots

**Critères du juge** (note de 0 à 2 par critère)

- Ne signale à tort aucune autre opération
- Donne la date, le libellé et le montant de l'opération concernée

**Exemple de bonne réponse**

> L'opération du 25/01, « Virement SEPA, référence 8841 », d'un montant de -1 500,00 €, n'a aucun justificatif parmi les pièces reçues.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-19 · répondre à un client mécontent · niveau complexe · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Mme Morvan (Les Épis d'Or) écrit : « Pourquoi ma facture de février est-elle de 445 € HT alors que mon forfait est de 400 € HT par mois ? ». Les relevés bancaires de décembre sont parvenus au cabinet 35 jours après la demande. Rédige une réponse courtoise de 180 mots maximum qui explique l'écart à partir de sa lettre de mission et de la procédure de relance. Vouvoiement, aucun texte entre crochets.

**Documents fournis avec l'énoncé** : Lettre de mission, SARL Les Épis d'Or (en vigueur, 2025-12-18) ; Procédure de relance des pièces manquantes (en vigueur, 2026-01-15)

**Ce qu'on attend**

> 445 € HT = 400 € HT de mensualité du forfait + 45 € HT d'honoraires de relance, prévus par la lettre de mission, car les pièces sont arrivées plus de 30 jours après la demande (ici 35). Ton courtois, aucune concession ni geste commercial promis, aucun détail inventé.

**Contrôles automatiques**

- la réponse fait au plus 180 mots
- la réponse contient l'une de ces formulations : « 400 »
- la réponse contient l'une de ces formulations : « 45 »
- la réponse contient l'une de ces formulations : « lettre de mission »
- la réponse ne contient aucune de ces formulations : « [ » ; « ] »
- la réponse ne contient aucune de ces formulations : «  tu  » ; «  ton  » ; «  ta  » ; «  tes  » ; «  toi  »
- la réponse ne contient aucune de ces formulations : « nous vous rembourserons » ; « geste commercial » ; « nous annulons »

**Critères du juge** (note de 0 à 2 par critère)

- Explique correctement la composition de 445 € HT (400 + 45)
- Ton courtois et professionnel
- Ne promet aucune concession et n'invente aucun détail

**Exemple de bonne réponse**

> Bonjour Madame Morvan,
>
> Merci pour votre message. Le montant de 445 € HT se compose de la mensualité de votre forfait, 400 € HT, et d'honoraires de relance de 45 € HT. Votre lettre de mission prévoit en effet que des honoraires de relance de 45 € HT sont facturés lorsque des pièces nous parviennent plus de 30 jours après notre demande, ce qui a été le cas pour les relevés bancaires de décembre, reçus 35 jours après.
>
> Nous restons à votre disposition pour en parler.
>
> Bien cordialement,
> Cabinet Aubépine & Associés

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-20 · synthèse de plusieurs documents · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Prépare, pour l'associée, la liste des actions de clôture de la SARL Les Épis d'Or (exercice clos le 31 décembre 2026), d'après sa fiche client, la procédure de clôture en vigueur et la note de réunion. Donne une liste numérotée d'exactement 5 actions, chacune avec sa date ou son échéance. Si une date ne peut pas être calculée avec les documents, dis-le plutôt que d'en inventer une. 200 mots maximum.

**Documents fournis avec l'énoncé** : Fiche client, SARL Les Épis d'Or (en vigueur, 2026-01-12) ; Procédure de clôture annuelle, version 2 (en vigueur, 2026-01-15) ; Note de réunion du 12 février 2026, Les Épis d'Or (en vigueur, 2026-02-12)

**Ce qu'on attend**

> Cinq actions : relance des pièces le 16 novembre 2026 (45 jours avant la clôture) ; point intermédiaire vers le 30 septembre 2026 (forfait de 4 800 € HT, supérieur à 3 000 € HT) ; immobilisation du véhicule livré le 5 février 2026 ; revue finale 8 jours ouvrés avant la signature des comptes (date de signature non fixée : ne pas inventer) ; archivage dans les 15 jours après la signature (idem).

**Contrôles automatiques**

- la réponse comporte une liste numérotée d'exactement 5 éléments
- la réponse fait au plus 200 mots
- la réponse contient l'une de ces formulations : « 16 novembre » ; « 16/11 »
- la réponse contient l'une de ces formulations : « 30 septembre » ; « 30/09 » ; « fin septembre »

**Critères du juge** (note de 0 à 2 par critère)

- Utilise la procédure en vigueur (45 jours, point intermédiaire pour un forfait supérieur à 3 000 € HT, 8 jours ouvrés, 15 jours)
- N'invente aucune date de signature des comptes
- Pense à l'immobilisation du véhicule citée dans la note

**Exemple de bonne réponse**

> 1. Relance des pièces manquantes : 16 novembre 2026 (45 jours avant la clôture).
> 2. Point intermédiaire avec Mme Morvan : vers le 30 septembre 2026, le forfait (4 800 € HT) dépassant 3 000 € HT.
> 3. Inscrire à l'actif le véhicule utilitaire livré le 5 février 2026 : avant la clôture.
> 4. Revue finale par l'associée : 8 jours ouvrés avant la signature des comptes ; date non calculable, la date de signature n'est pas fixée dans les documents.
> 5. Archivage numérique : dans les 15 jours après la signature des comptes ; date non calculable pour la même raison.

**Point d'incertitude signalé par l'équipe** : Le point intermédiaire « 3 mois avant la clôture » donne fin septembre : la date exacte est laissée à l'appréciation du relecteur.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-21 · contrôle d'un fichier des écritures comptables (FEC) · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Le FEC joint est celui de la SARL Les Épis d'Or pour 2025. Une facture d'achat y a été saisie deux fois dans le journal des achats. Indique la référence de la pièce, les deux numéros d'écriture concernés et le montant hors taxes de la facture.

**Documents fournis avec l'énoncé** : Fichier des écritures comptables (FEC) 2025, SARL Les Épis d'Or (en vigueur, 2026-02-20)

**Ce qu'on attend**

> La facture FA-2025-0451 de la Minoterie du Blavet (5 juin 2025) est saisie deux fois : écritures AC-0016 et AC-0017, montant HT 10 185,71 € (TVA 560,21 €, TTC 10 745,92 €). La deuxième saisie n'est pas lettrée.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « FA-2025-0451 »
- la réponse contient l'une de ces formulations : « AC-0016 »
- la réponse contient l'une de ces formulations : « AC-0017 »
- la réponse contient l'une de ces formulations : « 10 185,71 » ; « 10185,71 »

**Critères du juge** (note de 0 à 2 par critère)

- Donne la référence de pièce, les deux écritures et le montant HT
- Ne signale aucune autre facture à tort

**Exemple de bonne réponse**

> La facture FA-2025-0451 de la Minoterie du Blavet, datée du 5 juin 2025, est saisie deux fois : écritures AC-0016 et AC-0017, pour 10 185,71 € HT chacune.

**Point d'incertitude signalé par l'équipe** : Fichier des écritures comptables fictif : structure et règles de nommage à valider par un professionnel.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-22 · contrôle d'un fichier des écritures comptables (FEC) · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Dans le FEC joint (SARL Les Épis d'Or, 2025), deux anomalies de forme sont à signaler : une écriture dont le total des débits n'est pas égal au total des crédits, et une opération bancaire sans référence de pièce. Pour chacune, donne le numéro d'écriture, la date et le montant concerné.

**Documents fournis avec l'énoncé** : Fichier des écritures comptables (FEC) 2025, SARL Les Épis d'Or (en vigueur, 2026-02-20)

**Ce qu'on attend**

> Écriture OD-0013 du 15/09/2025 (« Regularisation divers ») : débit 250,00 €, crédit 240,00 €, écart de 10,00 €. Écriture BQ-0111 du 12/11/2025 (« Virement SEPA non identifie ») : 1 500,00 €, sans référence de pièce, imputée au compte d'attente 471.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « OD-0013 »
- la réponse contient l'une de ces formulations : « BQ-0111 »
- la réponse contient l'une de ces formulations : « 10,00 » ; « 10 € »
- la réponse contient l'une de ces formulations : « 1 500 » ; « 1500 »

**Critères du juge** (note de 0 à 2 par critère)

- Identifie bien les deux écritures distinctes
- Donne l'écart de 10,00 € et le montant de 1 500,00 €

**Exemple de bonne réponse**

> 1) L'écriture OD-0013 du 15/09/2025 est déséquilibrée : débit de 250,00 €, crédit de 240,00 €, soit un écart de 10,00 €. 2) L'écriture BQ-0111 du 12/11/2025 (virement SEPA non identifié, 1 500,00 €) n'a pas de référence de pièce.

**Point d'incertitude signalé par l'équipe** : Fichier des écritures comptables fictif : structure et règles de nommage à valider par un professionnel.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-23 · contrôle d'un fichier des écritures comptables (FEC) · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir du FEC joint (SARL Les Épis d'Or, 2025), quel est le résultat avant impôt de l'exercice, et que deviendrait-il si la facture d'achat saisie deux fois était supprimée une fois ? Détaille brièvement.

**Documents fournis avec l'énoncé** : Fichier des écritures comptables (FEC) 2025, SARL Les Épis d'Or (en vigueur, 2026-02-20)

**Ce qu'on attend**

> Résultat avant impôt de l'exercice : bénéfice de 10 000,00 € (comptes 7 moins comptes 6). Supprimer la saisie en double de la facture FA-2025-0451 (10 185,71 € HT) diminue les achats d'autant : le résultat passerait à 20 185,71 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 10 000 » ; « 10000 »
- la réponse contient l'une de ces formulations : « 20 185,71 » ; « 20185,71 »

**Critères du juge** (note de 0 à 2 par critère)

- Retrouve le doublon et en tire la bonne incidence sur le résultat (hors TVA)
- Ne confond pas HT et TTC

**Exemple de bonne réponse**

> Les produits (413 100,00 €) moins les charges (403 100,00 €) donnent un bénéfice avant impôt de 10 000,00 €. La facture FA-2025-0451 étant saisie deux fois (10 185,71 € HT), la supprimer une fois porterait le résultat à 20 185,71 €.

**Point d'incertitude signalé par l'équipe** : Fichier des écritures comptables fictif : structure et règles de nommage à valider par un professionnel.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-24 · contrôle d'un fichier des écritures comptables (FEC) · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Dans le journal des achats du FEC joint, toutes les factures de marchandises (compte 607) appliquent le même taux de TVA, sauf une. Quelle facture est concernée ? Donne la référence de pièce, la date, le fournisseur, le taux appliqué et le taux des autres factures.

**Documents fournis avec l'énoncé** : Fichier des écritures comptables (FEC) 2025, SARL Les Épis d'Or (en vigueur, 2026-02-20)

**Ce qu'on attend**

> La facture FA-2025-0458 de la Laiterie du Scorff (12 septembre 2025, écriture AC-0027) : 6 200,00 € HT et 1 240,00 € de TVA, soit 20 %, alors que les 24 autres factures de marchandises appliquent 5,5 %.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « FA-2025-0458 »
- la réponse contient l'une de ces formulations : « 20 % » ; « 20% »
- la réponse contient l'une de ces formulations : « 5,5 »

**Critères du juge** (note de 0 à 2 par critère)

- Identifie la bonne facture et les deux taux
- Ne présente pas le taux de 5,5 % comme une règle certaine pour tous les achats

**Exemple de bonne réponse**

> La facture FA-2025-0458 de la Laiterie du Scorff, datée du 12 septembre 2025, applique une TVA de 20 % (1 240,00 € sur 6 200,00 € HT), alors que les autres factures de marchandises sont à 5,5 %.

**Point d'incertitude signalé par l'équipe** : Fichier des écritures comptables fictif : structure et règles de nommage à valider par un professionnel. Les taux de TVA du jeu de données sont fictifs.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-25 · écritures d'inventaire : charges constatées d'avance · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la procédure d'inventaire en vigueur et des éléments d'inventaire de la SARL Les Épis d'Or au 31 décembre 2025, calcule le montant de chaque charge constatée d'avance et leur total. Deux lignes maximum.

**Documents fournis avec l'énoncé** : Procédure des écritures d'inventaire, version 2 (en vigueur, 2026-01-05) ; Éléments d'inventaire au 31/12/2025, SARL Les Épis d'Or (en vigueur, 2026-01-20)

**Ce qu'on attend**

> Assurance payée le 1er octobre 2025 pour 12 mois : 9 mois sur 2026, soit 900 €. Loyer trimestriel payé le 1er décembre (décembre à février) : 2 mois sur 2026, soit 1 800 €. Total : 2 700 €, au compte 486. Le compte 486 n'est pas exigé : la consigne ne le demande pas.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 900 »
- la réponse contient l'une de ces formulations : « 1 800 » ; « 1800 »
- la réponse contient l'une de ces formulations : « 2 700 » ; « 2700 »

**Exemple de bonne réponse**

> Assurance : 1 200 € × 9/12 = 900 €. Loyer : 2 700 € × 2/3 = 1 800 €.
> Total des charges constatées d'avance : 2 700 € (compte 486).

**Point d'incertitude signalé par l'équipe** : Comptes et règles d'inventaire propres au cabinet fictif (procédure du corpus) : à confronter au plan comptable général à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-26 · écritures d'inventaire : factures non parvenues · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la procédure d'inventaire en vigueur et des éléments d'inventaire de la SARL Les Épis d'Or au 31 décembre 2025, indique quelles charges sont des factures non parvenues, leur total et le compte de contrepartie.

**Documents fournis avec l'énoncé** : Procédure des écritures d'inventaire, version 2 (en vigueur, 2026-01-05) ; Éléments d'inventaire au 31/12/2025, SARL Les Épis d'Or (en vigueur, 2026-01-20)

**Ce qu'on attend**

> Électricité de décembre (410 €, facture reçue le 12 janvier 2026) et nettoyage de décembre (360 €, facture non reçue) : 770 € hors taxes, au crédit du compte 408.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 770 »
- la réponse contient l'une de ces formulations : « 408 »
- la réponse contient l'une de ces formulations : « électricité »
- la réponse contient l'une de ces formulations : « nettoyage »

**Exemple de bonne réponse**

> Deux factures non parvenues : l'électricité de décembre (410 €, reçue le 12 janvier 2026) et le nettoyage de décembre (360 €). Total : 770 € hors taxes, au crédit du compte 408.

**Point d'incertitude signalé par l'équipe** : Comptes et règles d'inventaire propres au cabinet fictif (procédure du corpus) : à confronter au plan comptable général à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-27 · écritures d'inventaire : amortissements · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la procédure d'inventaire en vigueur et des éléments d'inventaire de la SARL Les Épis d'Or, calcule la dotation aux amortissements 2025 de chaque immobilisation et leur total, arrondis au centime.

**Documents fournis avec l'énoncé** : Procédure des écritures d'inventaire, version 2 (en vigueur, 2026-01-05) ; Éléments d'inventaire au 31/12/2025, SARL Les Épis d'Or (en vigueur, 2026-01-20)

**Ce qu'on attend**

> Four : 12 000 / 5 ans × 9 mois (avril à décembre) / 12 = 1 800 €. Ordinateur : 1 500 / 3 ans × 4 mois (septembre à décembre) / 12 = 166,67 €. Total : 1 966,67 €, au débit du compte 6811. Le compte 6811 n'est pas exigé : la consigne ne le demande pas.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 1 800 » ; « 1800 »
- la réponse contient l'une de ces formulations : « 166,67 » ; « 166.67 »
- la réponse contient l'une de ces formulations : « 1 966,67 » ; « 1966,67 » ; « 1 966.67 »

**Exemple de bonne réponse**

> Four : 12 000 / 5 × 9/12 = 1 800,00 €. Ordinateur : 1 500 / 3 × 4/12 = 166,67 €.
> Total : 1 966,67 € au débit du compte 6811.

**Point d'incertitude signalé par l'équipe** : Comptes et règles d'inventaire propres au cabinet fictif (procédure du corpus) : à confronter au plan comptable général à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-28 · rapprochement des déclarations de TVA et du FEC · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Compare mois par mois le chiffre d'affaires des déclarations de TVA déposées en 2025 avec les ventes du FEC. Indique le mois qui diffère, les deux montants et l'écart.

**Documents fournis avec l'énoncé** : Déclarations de TVA 2025 déposées, SARL Les Épis d'Or (en vigueur, 2026-01-26) ; Ventes mensuelles 2025 d'après le FEC, SARL Les Épis d'Or (en vigueur, 2026-01-25)

**Ce qu'on attend**

> Un seul mois diffère : juillet 2025, 39 672,94 € dans le FEC contre 39 627,94 € déclarés, soit 45,00 € de moins (chiffres inversés). Les autres mois et la TVA concordent.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « juillet »
- la réponse contient l'une de ces formulations : « 39 672,94 » ; « 39672,94 »
- la réponse contient l'une de ces formulations : « 39 627,94 » ; « 39627,94 »
- la réponse contient l'une de ces formulations : « 45 »

**Exemple de bonne réponse**

> Seul juillet 2025 diffère : le FEC donne 39 672,94 € et la déclaration 39 627,94 €, soit un écart de 45,00 € (probablement deux chiffres inversés). Les autres mois concordent.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-29 · contrôle d'un lot de factures · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Contrôle ce lot de factures fournisseurs avec le plan d'imputation du cabinet. Relève toutes les anomalies (numéro, calcul, TVA) en citant le numéro de facture.

**Documents fournis avec l'énoncé** : Lot de factures fournisseurs de février 2026, SARL Les Épis d'Or (en vigueur, 2026-03-02) ; Plan d'imputation des dépenses du cabinet (en vigueur, 2026-01-05)

**Ce qu'on attend**

> Trois anomalies : F-2026-0109 porte 90,00 € de TVA sur une prime d'assurance (aucune TVA selon le plan) ; F-2026-0106 a un TTC de 298,00 € au lieu de 288,00 € (240 + 48) ; F-2026-0101 apparaît deux fois avec les mêmes montants.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « F-2026-0109 »
- la réponse contient l'une de ces formulations : « F-2026-0106 »
- la réponse contient l'une de ces formulations : « F-2026-0101 »

**Exemple de bonne réponse**

> Trois anomalies :
> - F-2026-0109 : TVA de 90,00 € sur une prime d'assurance, alors que le plan indique aucune TVA.
> - F-2026-0106 : TTC de 298,00 € au lieu de 288,00 € (240,00 + 48,00).
> - F-2026-0101 : numéro présent deux fois, avec les mêmes montants.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-30 · rapprochement bancaire · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Rapproche le relevé bancaire de février 2026 et le compte 512 du grand livre. Liste tous les écarts, avec leur nature.

**Documents fournis avec l'énoncé** : Relevé bancaire de février 2026, SARL Les Épis d'Or (en vigueur, 2026-03-03) ; Compte 512 du grand livre, février 2026, SARL Les Épis d'Or (en vigueur, 2026-03-04)

**Ce qu'on attend**

> Trois écarts : le virement client Traiteur du Port de 640,00 € est au relevé mais pas au grand livre ; la carte bancaire Papeterie Kerlann est de 84,50 € au relevé et 48,50 € au grand livre (chiffres inversés) ; le chèque 4521 de 215,00 € est au grand livre mais pas encore au relevé.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 640 »
- la réponse contient l'une de ces formulations : « 84,50 »
- la réponse contient l'une de ces formulations : « 48,50 »
- la réponse contient l'une de ces formulations : « 215 »

**Exemple de bonne réponse**

> Trois écarts :
> - Virement client Traiteur du Port de 640,00 € : au relevé, absent du grand livre.
> - Carte bancaire Papeterie Kerlann : 84,50 € au relevé, 48,50 € au grand livre (chiffres inversés).
> - Chèque 4521 Net'Express de 215,00 € : au grand livre, pas encore au relevé.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-31 · conversation à plusieurs tours · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> À partir de la procédure d'inventaire en vigueur et des éléments d'inventaire de la SARL Les Épis d'Or, calcule le total des charges constatées d'avance au 31 décembre 2025.

**Message 2 de l'utilisateur, après la réponse de l'assistant**

> Correction : l'assurance a été payée le 1er juillet 2025 (et non le 1er octobre) pour 12 mois. Recalcule le total des charges constatées d'avance et détaille les deux montants.

**Documents fournis avec l'énoncé** : Procédure des écritures d'inventaire, version 2 (en vigueur, 2026-01-05) ; Éléments d'inventaire au 31/12/2025, SARL Les Épis d'Or (en vigueur, 2026-01-20)

**Ce qu'on attend**

> Après correction : l'assurance payée le 1er juillet 2025 pour 12 mois laisse 6 mois sur 2026, soit 600 € ; le loyer reste à 1 800 €. Total : 2 400 €.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 2 400 » ; « 2400 »
- la réponse contient l'une de ces formulations : « 600 »

**Exemple de bonne réponse**

> Après correction, l'assurance (1 200 € payée le 1er juillet 2025 pour 12 mois) laisse 6 mois sur 2026 : 600 €.
> Le loyer reste à 1 800 €. Total des charges constatées d'avance : 2 400 €.

**Point d'incertitude signalé par l'équipe** : Comptes et règles d'inventaire propres au cabinet fictif (procédure du corpus) : à confronter au plan comptable général à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## CH-32 · savoir dire qu'on ne sait pas · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Énoncé posé à l'assistant**

> Selon la procédure d'inventaire du cabinet, quel est le taux d'amortissement du logiciel de caisse de la boulangerie ?

**Documents fournis avec l'énoncé** : Procédure des écritures d'inventaire, version 2 (en vigueur, 2026-01-05)

**Ce qu'on attend**

> La procédure ne donne que trois durées (véhicule utilitaire, matériel informatique, équipement de production). Bonne conduite : dire que le logiciel de caisse n'y figure pas, ne donner aucun taux.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque

**Exemple de bonne réponse**

> La procédure d'inventaire ne mentionne pas le logiciel de caisse : je ne peux pas donner de taux.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---
