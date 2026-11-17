# Glossaire en langage clair

Ce glossaire explique, sans jargon, les mots techniques employés dans les README. Si un mot manque,
signalez-le : un README doit rester compréhensible sans lui.

**Agent / agentique.** Un assistant qui ne se contente pas de répondre : il **enchaîne des actions** avec
des outils (chercher un document, remplir un tableau, préparer un courriel) pour atteindre un but.
L'épreuve « Agir » mesure s'il le fait juste, sans excès, et sans faire ce qui est interdit.

**Chat.** La conversation avec l'assistant : on pose une question ou une consigne, il répond. L'épreuve
« Discuter » mesure la qualité de ces réponses.

**Corpus.** L'ensemble des documents sur lesquels portent les questions. Ici : les documents d'un cabinet
**inventé** (procédures, fiches clients, notes) et quelques textes publics.

**Écart-type / dispersion.** Une épreuve n'a pas toujours le même résultat si on la rejoue : le modèle
varie un peu. L'écart-type mesure cette variation. Si l'écart entre deux modèles est plus petit que leur
variation, la différence **n'est pas démontrée**.

**GPU / carte graphique.** Le composant qui fait tourner les modèles d'IA. Sa mémoire (VRAM, en Go)
limite la taille du modèle qu'on peut installer. Ici : **48 Go**.

**Hallucination.** Quand un assistant **invente** une information (un chiffre, une référence) avec
aplomb. Plusieurs tâches la détectent.

**LLM (modèle de langage).** Le « moteur » d'un assistant comme ChatGPT. Un LLM **local** tourne sur votre
matériel, sans envoyer vos données à l'extérieur.

**Modèle juge.** Pour les critères qu'un programme ne sait pas vérifier (qualité du français, clarté),
un autre modèle note les réponses selon une grille publique. Il a des biais (il préfère par exemple les
réponses longues), donc nous les indiquons et un humain relit un échantillon.

**NVFP4.** Un format qui rend un modèle **plus compact** (environ le quart de sa taille d'origine) pour
qu'il tienne sur une carte graphique plus modeste, au prix d'une petite perte de précision. Tous les
modèles testés ici sont dans ce format, pour que la comparaison soit équitable.

**Paramètres (« 27 milliards de paramètres »).** La taille d'un modèle. Plus il y en a, plus le modèle
est en général capable, et plus il demande de mémoire.

**Plafond de génération.** Le nombre maximal de mots-morceaux (« tokens ») qu'un modèle peut produire pour une
réponse. Les modèles qui « réfléchissent » avant de répondre comptent cette réflexion dedans : avec un plafond trop
bas, ils s'arrêtent avant d'écrire la réponse. Nous fixons le même plafond pour tous (32768).

**Quantification.** Le procédé qui rend un modèle plus compact (voir NVFP4).

**RAG.** Pour « génération augmentée par la recherche » : l'assistant **cherche d'abord** les passages
utiles dans vos documents, **puis** répond en s'appuyant dessus. L'épreuve « Chercher dans vos dossiers »
mesure les deux temps séparément : a-t-il retrouvé le bon passage ? a-t-il bien répondu à partir de lui ?

**Retriever (récupérateur).** La partie du RAG qui retrouve les passages. Elle est **la même pour tous les
modèles**, pour que seul le modèle varie.

**Runpod.** Un service de location de cartes graphiques. Sover.tech l'utilise pour lancer ses mesures,
mais le benchmark fonctionne aussi sur votre propre matériel.

**TTFT (temps avant la première réponse).** Le délai entre l'envoi de la question et l'apparition du
premier mot de la réponse. Il compte pour le confort d'usage.

**vLLM.** Un logiciel qui sert un modèle sur un ordinateur pour que d'autres programmes puissent lui
parler. C'est ce que Sover.tech utilise. D'autres existent, le benchmark les accepte.

**« À valider par un professionnel ».** Mention portée par toute réponse de référence qui touche au
métier tant qu'un expert-comptable ou un notaire ne l'a pas relue.
