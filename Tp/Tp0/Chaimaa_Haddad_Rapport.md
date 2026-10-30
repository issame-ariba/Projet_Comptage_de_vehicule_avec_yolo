# TP0 : MaintAI
**Nom :** Chaimaa HADDAD · **Groupe :** G3

---

## Le problème
Dans un contexte manufacturier, prédire les pannes de machines industrielles à partir des relevés télémétriques de capteurs (température, vibrations, charge nominale et heures de fonctionnement).
L'enjeu métier est asymétrique : rater une panne paralyse la production pendant toute une journée, alors qu'une fausse alerte coûte seulement une heure d'inspection par un agent de maintenance.

---

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| Baseline (majoritaire) | 0.824 | 0.000 | 0.000 |
| Régression logistique | 0.889 | 0.574 | 0.737 |
| Modèle entraîné MaintAI | 0.904 | 0.750 | 0.622 |

---

## Mon choix, et pourquoi
Le modèle MaintAI calibré est le meilleur compromis opérationnel :
1. Il dépasse largement la baseline dont le rappel est de 0 (incapacité totale à détecter les pannes) ;
2. Il privilégie le rappel afin de minimiser les faux négatifs (pannes non anticipées) ;
3. Il conserve une précision acceptable de 62,2 %, ce qui évite de saturer l'équipe technique avec des fausses alertes abusives.

---

## Le critère (rappel >= 0,75) est-il atteint ?
Le critère d'acceptation énoncé dans le polycopié est : $\text{rappel} \ge 0,75$ et $\text{précision} \ge 0,50$.
Avec un rappel obtenu de 0,750 et une précision de 0,622, le critère d'acceptation est validé. En comparaison, la régression logistique naïve non calibrée plafonnait à un rappel insuffisant de 0,574.

---

## Ce qui reste flou
La détection de dérive de distribution (data drift) au fil des mois lorsque les capteurs s'usent ou se dérèglent progressivement.
