# TP0 : MaintAI
**Nom :** Abderrahmane Sbaii · **Groupe :** G1

## Le problème
Prédire une panne à partir de 4 capteurs (température, vibration, charge, heures de fonctionnement) ; une panne manquée arrête une ligne.

## Résultats sur le jeu de test
| Modèle | Accuracy | Rappel | Précision |
|---|---|---|---|
| baseline | 0.824 | 0.000 | 0.000 |
| régression logistique (seuil 0,5) | 0.889 | 0.574 | 0.737 |
| régression logistique (seuil 0,25) | 0.862 | 0.795 | 0.579 |

Données : 5 000 machines, dont 1 000 en test (tirage aléatoire stratifié). Il y a 176 pannes dans le test, soit environ 18 %.

## Mon choix, et pourquoi
Je garde la **régression logistique**, mais je baisse le **seuil de décision de 0,5 à 0,25** : une machine est signalée dès que la probabilité de panne dépasse 25 %.
- Avec le seuil par défaut, le modèle rate 75 pannes sur 176 (rappel 0,574). C'est trop grave, puisque chaque panne manquée arrête une ligne.
- J'ai choisi le seuil 0,25 **sur une validation** (25 % des données d'entraînement), sans regarder le test. C'est le premier seuil qui y donne un rappel ≥ 0,75 (0,771).
- Sur le test, ce seuil détecte 140 pannes sur 176 : il n'en manque plus que 36, au lieu de 75.
- Le prix à payer, ce sont des fausses alertes : 102 au lieu de 36. La précision descend à 0,579, mais plus de la moitié des alertes restent de vraies pannes.
- La baseline a pourtant 82,4 % d'accuracy sans trouver une seule panne : c'est pour ça que je juge les modèles sur le rappel et pas sur l'accuracy.

D'après les coefficients du modèle, c'est la **vibration** qui signale le plus une panne. Viennent ensuite la température, la charge et les heures de fonctionnement.

## Le critère (rappel ≥ 0,75) est-il atteint ?
**Oui** : rappel de 0,795 sur le jeu de test (1 000 machines), avec le seuil 0,25. Avec le seuil par défaut (0,5), le critère n'est **pas** atteint (0,574).

## Ce qui reste flou
- **Combien coûte une fausse alerte ?** Avec 102 interventions inutiles, il faudrait savoir si l'équipe de maintenance peut toutes les absorber.
- **La validation est petite** (environ 1 000 machines) : le seuil exact pourrait varier un peu avec un autre tirage. Une validation croisée serait plus solide.
- **Je n'ai essayé qu'une régression logistique.** Un modèle non linéaire (gradient boosting, par exemple), avec un seuil réglé de la même façon, ferait peut-être mieux.
- **Quel délai avant la panne ?** Les données ne disent pas combien de temps à l'avance on prédit, ni si les mesures sont datées. Si elles le sont, il faudrait un découpage chronologique.
