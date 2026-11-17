# Choix du moteur d'extraction : Tika et Docling mesurés

Les modèles ne lisent pas des fichiers mais du texte. Le moteur qui extrait ce texte fait partie de la chaîne,
et ses défauts sont ceux que verra un assistant branché sur de vrais dossiers. Ce document donne ce qui a été
mesuré, ce qui a été décidé, et ce qui reste à faire.

## Ce qui a été comparé

- **Apache Tika `4.2.0-1-full`**, OCR français et anglais, appelé comme le fait Open WebUI avec
  `TIKA_SERVER_VERSION=4` (`PUT /tika/json/md`, type du fichier transmis).
- **Docling `docling-serve-cpu v1.38.2`**, avec les réglages de la stack de Sover.tech (`force_ocr`, OCR
  français et anglais, tableaux en mode précis), appelé par `POST /v1/convert/file`.
- Les **26 documents du corpus du cabinet fictif** (voir `expert-comptable/corpus/README.md`), une seule passe.
- Indicateur : la part des **nombres et des identifiants de la source** (montants, dates, références,
  courriels) retrouvés dans le texte extrait. Les structures (tableaux, lignes) sont jugées à part, à la lecture.

## Ce qui a été trouvé

| Constat | Tika | Docling |
|---|---|---|
| Documents lus (sur 26) | **26** | 22 : **échec sur les 2 `.doc` et les 2 `.xls`** (formats hérités) |
| Nombres et identifiants retrouvés, documents lus par les deux | **100 %** | **100 %** |
| Word récent, Excel récent, PDF propres | texte correct, tableaux en Markdown | idem, tableaux plus aérés |
| **CSV à points-virgules** (export bancaire français) | **aplati en une seule ligne** | **tableau Markdown, 8 lignes sur 8** |
| CSV à virgules | tableau Markdown | tableau Markdown |
| Fichier au format FEC (tabulations, 18 colonnes) | tableau, 66 000 caractères | tableau, 175 000 caractères (80 000 sans les espaces de remplissage) |
| Scan de la lettre de mission | tous les faits, texte sur une seule ligne | tous les faits |
| Photo inclinée de la facture | tous les faits, **bannière abîmée** | tous les faits, bannière lisible, tableau conservé, quelques espaces perdus (« F-2026-0231du », « 21360,00 € ») |

Conclusion de la mesure : **ni l'un ni l'autre n'est supérieur partout.** Docling règle le défaut le plus gênant
de Tika (le CSV des banques françaises) et restitue mieux la structure des scans, mais **il ne lit pas les
anciens formats Word et Excel**, que les cabinets conservent longtemps. Tika lit tout, mais aplatit le CSV à
points-virgules.

## Contournements du CSV aplati dans Tika (vérifiés)

1. **Convertir le CSV avant l'indexation** : remplacer le point-virgule par une virgule (et protéger par des
   guillemets les champs qui contiennent une virgule, ce que fait toute bibliothèque CSV). Vérifié sur le relevé
   du corpus : Tika rend alors un tableau Markdown de 8 lignes. C'est le plus simple, et il garde Tika.
2. **Déposer un `.xlsx`** à la place du CSV : le tableau est conservé tel quel.
3. **Passer à Docling** : règle le CSV, mais impose de convertir au préalable les `.doc` et `.xls` (par exemple
   avec LibreOffice en ligne de commande) et coûte nettement plus de ressources.

Ce qui **ne fonctionne pas** : changer l'appel (`/tika`, `/tika/text`, `/rmeta/text`) ne règle rien pour Open
WebUI, qui impose son propre chemin ; déclarer le type `text/csv` n'y change rien non plus.

## Décision pour le benchmark

**Tika est le moteur de référence** : il lit les 26 documents et il est identique à celui de la stack déployée
(les 26 extractions versionnées ont été comparées au chemin d'Open WebUI : 0 différence). Le défaut CSV est
conservé tel quel et documenté : c'est un comportement réel.

**Docling sera une variante de comparaison** : même corpus, même tâches, même modèles, seul le moteur change, avec
une conversion préalable des `.doc` et `.xls`. Cela mesurera l'effet du moteur d'extraction sur la qualité des
réponses, ce qu'aucun indicateur d'extraction seul ne dit.

## Limites de cette mesure

Une passe, 26 documents fictifs et simples, un indicateur lexical. Les défauts de Docling que la propre étude de
Sover.tech a relevés sur de vrais documents (texte masqué sous les zones qu'il classe comme images, par exemple)
ne se retrouvent pas ici, parce que ces documents sont plus simples que des datasheets ou des devis de clients.
