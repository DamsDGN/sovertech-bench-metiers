# Grille du modèle juge : épreuve « Discuter »

Le juge ne note **que** ce que les contrôles automatiques ne peuvent pas vérifier. Il reçoit l'énoncé, la
réponse à noter et le critère, **sans connaître le modèle qui a répondu** ni l'identifiant de la tâche.

## Échelle (par critère)

| Note | Signification |
|---|---|
| **2** | Le critère est pleinement satisfait. |
| **1** | Le critère est partiellement satisfait (défaut mineur, imprécision sans conséquence). |
| **0** | Le critère n'est pas satisfait, ou la réponse est fausse, inventée ou dangereuse sur ce point. |

## Règles pour le juge

1. **Noter le critère, pas le style général.** Une réponse élégante qui rate le critère obtient 0.
2. **Ne pas récompenser la longueur.** Une réponse plus longue n'est pas meilleure.
3. **Vérifier avant de croire.** Une affirmation chiffrée ou réglementaire sans appui dans l'énoncé est
   suspecte : elle ne mérite 2 que si elle est correcte et vérifiable.
4. **Une invention vaut 0** sur tout critère de fiabilité ou de prudence, même si le reste est bon.
5. **Le juge peut répondre « incertain »** s'il ne peut pas trancher : la tâche est alors relue par un
   humain.
6. Le juge **ne note jamais la justesse métier d'un point marqué « à valider »** comme établie : il le
   signale dans son commentaire.

## Biais connus des modèles juges (à garder en tête)

- Préférence pour les **réponses longues** et très structurées.
- Indulgence envers un **style assuré** même quand le fond est faux.
- Sensibilité à l'**ordre de présentation** des réponses.
- Favoritisme possible pour **le style de sa propre famille de modèles**.

Ces biais sont réduits par l'anonymisation, le mélange des réponses et la relecture humaine d'un
échantillon, mais pas supprimés. Le rapport indique le modèle juge, sa version et l'accord mesuré avec
l'humain.

## Critères par tâche

Les critères de chaque tâche sont dans [`TACHES.md`](TACHES.md), sous « Critères du juge ».
