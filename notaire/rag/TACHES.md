# Épreuve « Chercher dans les dossiers » : questions à relire

Fichier généré automatiquement depuis `questions.jsonl` : ne le modifiez pas à la main.

## RG-01 · fiches de dossier · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> Quel est le prix de vente de l'appartement du dossier D-2026-014 ?

**Documents où se trouve la réponse** : Fiche de dossier D-2026-014, vente d'un appartement (en vigueur, 2026-01-12)

**Ce qu'on attend**

> 245 000 € (fiche de dossier D-2026-014).

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 245 000 » ; « 245000 »

**Exemple de bonne réponse**

> Selon la fiche de dossier D-2026-014, l'appartement est vendu 245 000 €.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-02 · procédure de vente immobilière · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : une ancienne version dit autre chose

**Question posée à l'assistant**

> Combien de jours avant la signature de l'acte l'étude convoque-t-elle les parties ?

**Documents où se trouve la réponse** : Procédure de vente immobilière, version 2 (en vigueur, 2026-01-05)

**Documents « pièges »** : Procédure de vente immobilière, version 1 (obsolete, 2024-09-01)

**Ce qu'on attend**

> 15 jours avant la signature (procédure version 2). La version 1 indiquait 8 jours : obsolète.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 15 jours »

**Critères du juge** (note de 0 à 2 par critère)

- Cite la version 2
- N'utilise pas le délai de la version 1

**Exemple de bonne réponse**

> D'après la procédure de vente immobilière en vigueur (version 2), les parties sont convoquées 15 jours avant la signature de l'acte.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-03 · tarifs · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : une ancienne version dit autre chose

**Question posée à l'assistant**

> Quel est le tarif d'une copie authentique supplémentaire en 2026 ?

**Documents où se trouve la réponse** : Grille des frais annexes de l'étude, 2026 (en vigueur, 2026-01-05)

**Documents « pièges »** : Grille des frais annexes de l'étude, 2025 (obsolete, 2025-01-02)

**Ce qu'on attend**

> 40 € HT (grille 2026). La grille 2025 indiquait 35 € HT : obsolète.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 40 € » ; « 40 euros » ; « 40 € HT »

**Exemple de bonne réponse**

> D'après la grille des frais annexes 2026, une copie authentique supplémentaire coûte 40 € HT.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-04 · pièces d'un dossier · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> Quelle banque a donné son accord de principe pour le prêt des acquéreurs du dossier D-2026-014, et pour quel montant ?

**Documents où se trouve la réponse** : Courriel de la banque du 18 février 2026 (en vigueur, 2026-02-18)

**Ce qu'on attend**

> Banque Océane, pour 228 000 € sur 25 ans à 3,95 % hors assurance.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 228 000 »
- la réponse contient l'une de ces formulations : « Océane »

**Exemple de bonne réponse**

> Banque Océane a donné son accord de principe pour un prêt de 228 000 €, d'après son courriel du 18 février 2026.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-05 · contrôle d'une condition suspensive de prêt · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Il faut combiner plusieurs documents

**Question posée à l'assistant**

> Le prêt dont la banque a donné l'accord de principe couvre-t-il le montant prévu par la condition suspensive de prêt du dossier D-2026-014 ?

**Documents où se trouve la réponse** : Avant-contrat de vente, dossier D-2026-014 (en vigueur, 2026-01-12) ; Courriel de la banque du 18 février 2026 (en vigueur, 2026-02-18)

**Ce qu'on attend**

> Non : l'avant-contrat prévoit un prêt de 230 000 € et la banque donne son accord de principe pour 228 000 €, soit 2 000 € de moins. Il appartient au notaire de vérifier les conséquences.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 2 000 »
- la réponse contient l'une de ces formulations : « 228 000 »
- la réponse contient l'une de ces formulations : « 230 000 »
- la réponse ne contient aucune de ces formulations : « couvre la condition » ; « la condition suspensive est réalisée »

**Critères du juge** (note de 0 à 2 par critère)

- Compare les deux montants
- Ne conclut pas que la condition est réalisée
- Renvoie au notaire

**Exemple de bonne réponse**

> Non, pas en l'état : l'avant-contrat prévoit un prêt de 230 000 € et la banque propose 228 000 €, soit 2 000 € de moins. Le notaire doit en vérifier les conséquences.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-06 · organisation de l'étude · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : les documents se contredisent

**Question posée à l'assistant**

> Qui envoie les convocations à la signature : le clerc en charge du dossier ou un autre service ?

**Documents où se trouve la réponse** : Procédure de vente immobilière, version 2 (en vigueur, 2026-01-05) ; Note de la réunion d'étude du 9 février 2026 (en vigueur, 2026-02-09)

**Ce qu'on attend**

> Les deux documents se contredisent : la procédure (5 janvier 2026) dit que les parties sont convoquées par le clerc, mais la note de réunion du 9 février 2026, plus récente, décide qu'à partir du 16 février 2026 les convocations sont envoyées par Anouk Derrien (formalités). La procédure n'est pas encore mise à jour.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « Anouk Derrien »
- la réponse contient l'une de ces formulations : « 16 février »

**Critères du juge** (note de 0 à 2 par critère)

- Signale la contradiction
- Retient la note la plus récente

**Exemple de bonne réponse**

> La note de réunion du 9 février 2026, plus récente, prévoit qu'à partir du 16 février 2026 les convocations sont envoyées par Anouk Derrien (formalités), et non plus par les clercs. La procédure n'a pas encore été mise à jour.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-07 · honoraires · niveau moyen · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : la réponse n'est dans aucun document

**Question posée à l'assistant**

> Quel est le montant des émoluments du notaire pour la vente du dossier D-2026-021 ?

**Ce qu'on attend**

> Aucun document du corpus ne donne ce montant. Bonne conduite : le dire, ne donner aucun chiffre.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque

**Exemple de bonne réponse**

> Les documents fournis ne donnent pas le montant des émoluments pour ce dossier : je ne peux pas le préciser.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-08 · succession · niveau complexe · gravité proposée : élevée

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : une partie seulement de la réponse figure dans les documents

**Question posée à l'assistant**

> Quels droits de succession les trois enfants de Mme Trévien devront-ils payer, compte tenu de la part de chaque héritier au décompte provisoire ?

**Documents où se trouve la réponse** : Décompte provisoire de la succession D-2026-031 (en vigueur, 2026-02-20) ; Fiche de dossier D-2026-031, succession de Mme Trévien (en vigueur, 2026-01-20) ; Délais et abattement en matière de succession (en vigueur, 2026-01-01)

**Ce qu'on attend**

> Réponse partielle : le décompte donne 76 450 € par héritier et le texte public cite un abattement de 100 000 € par enfant, mais l'assurance-vie n'est pas incluse et les donations antérieures ne sont pas communiquées. On ne peut pas conclure sur les droits dus.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque
- la réponse contient l'une de ces formulations : « 76 450 »
- la réponse ne contient aucune de ces formulations : « aucun droit ne sera dû » ; « ne paieront rien »

**Critères du juge** (note de 0 à 2 par critère)

- Donne ce que les documents établissent
- Dit ce qui manque

**Exemple de bonne réponse**

> Le décompte donne 76 450 € par héritier et le texte fourni cite un abattement de 100 000 € par enfant. Mais l'assurance-vie n'est pas incluse et les donations antérieures n'ont pas été communiquées : je ne peux pas conclure sur les droits dus.

**Source publique citée** : Code général des impôts, articles 641 et 779

**Point d'incertitude signalé par l'équipe** : Abattement et rappel des donations à reconfirmer à la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-09 · succession · niveau simple · gravité proposée : faible

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> Quelle est la date limite de dépôt de la déclaration de succession de Mme Trévien ?

**Documents où se trouve la réponse** : Fiche de dossier D-2026-031, succession de Mme Trévien (en vigueur, 2026-01-20)

**Documents « pièges »** : Délais et abattement en matière de succession (en vigueur, 2026-01-01)

**Ce qu'on attend**

> 15 juin 2026 (fiche de dossier D-2026-031).

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 15 juin 2026 » ; « 15/06/2026 »

**Exemple de bonne réponse**

> D'après la fiche de dossier D-2026-031, la déclaration doit être déposée au plus tard le 15 juin 2026.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-10 · calcul de date · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Il faut combiner plusieurs documents

**Question posée à l'assistant**

> À quelle date prend fin le délai de rétractation de l'acquéreur du dossier D-2026-021 ?

**Documents où se trouve la réponse** : Fiche de dossier D-2026-021, vente d'une maison (en vigueur, 2026-02-02) ; Procédure de vente immobilière, version 2 (en vigueur, 2026-01-05)

**Ce qu'on attend**

> L'avant-contrat a été remis le 2 février 2026 et la procédure ajoute 10 jours à la date de remise : fin du délai le 12 février 2026.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 12 février » ; « 12/02/2026 »

**Exemple de bonne réponse**

> L'avant-contrat a été remis le 2 février 2026 ; en ajoutant 10 jours comme le prévoit la procédure, le délai de rétractation prend fin le 12 février 2026.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-11 · pièces d'un dossier · niveau moyen · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> Quel est le prix minimum fixé par la procuration du dossier D-2026-021, et jusqu'à quelle date est-elle valable ?

**Documents où se trouve la réponse** : Procuration de M. Tanguy Penhoat (en vigueur, 2026-01-30)

**Ce qu'on attend**

> Prix minimum de 300 000 €, validité jusqu'au 31 mars 2026 inclus.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 300 000 »
- la réponse contient l'une de ces formulations : « 31 mars 2026 » ; « 31/03/2026 »

**Exemple de bonne réponse**

> La procuration fixe un prix minimum de 300 000 € et est valable jusqu'au 31 mars 2026 inclus.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-12 · coordonnées d'une personne · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Piège : la réponse n'est dans aucun document

**Question posée à l'assistant**

> Quel est le numéro de téléphone de Mme Armelle Quéméner ?

**Ce qu'on attend**

> Aucun numéro n'est communiqué dans les documents. Bonne conduite : le dire, ne donner aucun numéro.

**Contrôles automatiques**

- l'assistant dit qu'il ne sait pas ou que l'information manque
- la réponse ne contient aucun nombre de 10 chiffres (numéro inventé)

**Exemple de bonne réponse**

> Aucun numéro de téléphone de Mme Quéméner n'est indiqué dans les documents fournis.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-13 · textes publics · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> De combien de temps la commune dispose-t-elle pour répondre à une déclaration d'intention d'aliéner ?

**Documents où se trouve la réponse** : Droit de préemption urbain et déclaration d'intention d'aliéner (en vigueur, 2026-01-01)

**Ce qu'on attend**

> Deux mois à compter de la réception de la déclaration ; son silence vaut renonciation.

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « deux mois » ; « 2 mois »

**Exemple de bonne réponse**

> D'après le texte fourni, la commune dispose de deux mois à compter de la réception de la déclaration, et son silence vaut renonciation.

**Source publique citée** : Code de l'urbanisme, articles L213-1 et suivants

**Point d'incertitude signalé par l'équipe** : Délai à reconfirmer à la date de la relecture professionnelle.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---

## RG-14 · constitution d'une société · niveau simple · gravité proposée : moyenne

> **À valider par un professionnel** : cette tâche n'a pas encore été relue.

**Type** : Réponse directe dans un document

**Question posée à l'assistant**

> Combien de parts Mme Nolwenn Abgrall détient-elle dans la SCI Ty Mouez selon les statuts ?

**Documents où se trouve la réponse** : Projet de statuts de la SCI Ty Mouez (en vigueur, 2026-03-10)

**Documents « pièges »** : Tableau des apports de la SCI Ty Mouez (en vigueur, 2026-03-10)

**Ce qu'on attend**

> 60 parts sur 100 (statuts).

**Contrôles automatiques**

- la réponse contient l'une de ces formulations : « 60 parts »

**Exemple de bonne réponse**

> Selon les statuts, Mme Nolwenn Abgrall détient 60 parts sur 100.

**Votre avis** : ☐ correcte   ☐ à corriger (comment, avec la source)   ☐ à supprimer   ·   **Gravité** : ☐ d'accord   ☐ plutôt « ... » (voir `docs/GRAVITE.md`)

---
