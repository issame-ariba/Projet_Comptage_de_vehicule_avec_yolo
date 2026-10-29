# TP0 : CantineAI
**Nom :** Issam Ariba · **Groupe :** G1

## Le problème
Prédire, la veille à 10 h, le nombre de repas à commander pour le lendemain, à partir du menu, de la météo, du calendrier (examens, sorties, veille de vacances) et du nombre d'inscrits. Un repas en trop est jeté (≈ 15 DH perdus) ; un repas manquant, c'est un élève sans déjeuner.

## Résultats sur le jeu de test
Découpage chronologique : 272 jours d'entraînement, 68 jours de test (25/02/2026 → 19/06/2026).

| Modèle | MAE (repas) | RMSE | R² |
|---|---|---|---|
| baseline (moyenne) | 70.271 | 88.416 | -0.151 |
| méthode actuelle « semaine précédente »* | 79.0 | — | — |
| **ridge** | **22.623** | **28.545** | **0.880** |
| gradient boosting | 28.218 | 35.433 | 0.815 |
| random forest | 31.447 | 41.402 | 0.748 |
| arbre de décision | 42.010 | 54.766 | 0.558 |

\* calculée sur les 58 jours de test où `repas_semaine_precedente` est connue.

## Mon choix, et pourquoi
Je retiens **Ridge** : c'est le modèle qui a la plus petite MAE (22,6 repas d'erreur par jour en moyenne). La MAE est la métrique principale parce qu'elle se lit directement en repas en trop ou manquants, donc en DH perdus ou en élèves sans repas.
Ridge divise l'erreur par 3 par rapport à la baseline (70,3 → 22,6, soit −68 %) et par 3,5 par rapport à la méthode actuelle du gestionnaire (79 → 23). C'est aussi le modèle le plus simple et le plus lisible des quatre. Ses coefficients montrent que le mercredi (−60), le menu poisson (−48), les examens (−34) et la veille de vacances (−26) font baisser la fréquentation, et que le vendredi couscous la fait monter (+45).

## Le critère (MAE ≤ 30 repas, et meilleure que la méthode « semaine précédente ») est-il atteint ?
**Oui.** La MAE de Ridge est de 22,6 repas sur les 68 jours de test chronologiques, sous le seuil de 30. Elle est aussi bien meilleure que la méthode actuelle (79 repas).

## Ce qui reste flou
- **Les données sont synthétiques** : les performances sur une vraie cantine seront probablement moins bonnes.
- **Le jeu de test est petit** : 68 jours, une seule fin d'année scolaire.
- **La MAE traite les deux erreurs pareil**, alors qu'un repas manquant coûte plus cher qu'un repas jeté. Faut-il ajouter une marge de sécurité, ou prédire un quantile plutôt que la moyenne ?
- **Couscous et vendredi sont confondus** (le couscous est toujours servi le vendredi) : le modèle ne peut pas séparer leurs deux effets.
- **Les jours de reprise après les vacances** n'ont pas de `repas_semaine_precedente` (la valeur est remplacée par la médiane), et les événements rares (sorties) sont peu représentés.
