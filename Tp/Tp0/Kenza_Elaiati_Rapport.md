# TP0 : MaintAI
**Nom :** Kenza ELAIATI · **Groupe :** G3

---

## Le problème
L'usine souhaite anticiper les défaillances de ses équipements à partir de 4 capteurs physiques : la température du moteur (`temperature_c`), la vitesse de vibration (`vibration_mm_s`), le taux de charge (`load_pct`) et le nombre d'heures d'exploitation (`runtime_hours`).
L'objectif est d'aider les équipes de maintenance à cibler chaque matin les machines prioritaires. Une panne manquée entraîne l'arrêt complet d'une ligne de fabrication pendant 24 heures (coût financier majeur), tandis qu'une fausse alerte ne consomme qu'une heure d'inspection technique.

---

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline (classe majoritaire) | 0.824 | 0.000 | 0.000 |
| Régression logistique | 0.889 | 0.574 | 0.737 |
| Modèle entraîné MaintAI | 0.904 | 0.750 | 0.622 |

---

## Mon choix, et pourquoi
En maintenance prédictive, le **rappel (`recall`)** est la métrique prioritaire parce que le coût d'une panne manquée (une journée d'arrêt d'usine) est incomparablement plus destructeur qu'une fausse alerte (une heure d'inspection préventive).
La baseline obtient une accuracy flatteuse de 82,4 % uniquement parce que 82,4 % des relevés sont sains, mais son rappel est strictement nul (0,000) car elle ne détecte aucune panne.
Le modèle avec seuil optimisé à 0,3 permet d'atteindre un rappel de 0,750, ce qui garantit que 75 % des pannes potentielles sont interceptées avant l'incident.

---

## Le critère (rappel >= 0,75) est-il atteint ?
Oui, avec le modèle final calibré au seuil de probabilité 0,3, le rappel atteint exactement **0,750**, ce qui remplit le critère d'acceptation fixé par le polycopié. En revanche, avec la régression logistique standard au seuil par défaut de 0,5 (rappel de 0,574), le critère n'était pas atteint.

---

## Ce qui reste flou
Comment ajuster dynamiquement le seuil de décision (0,3) lorsque le coût relatif d'un arrêt de ligne varie selon les périodes de production haute ou basse.
