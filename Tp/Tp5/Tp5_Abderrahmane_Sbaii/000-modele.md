# ADR 004 : Choix du modèle et du seuil de décision pour MaintAI

Date : 25/11/2026 · Auteurs : Abderrahmane Sbaii

## Contexte
Nous devons choisir le modèle de prédiction de pannes et son seuil de décision à déployer en production pour MaintAI. Dans un contexte industriel, une panne non détectée (faux négatif) entraîne un arrêt de production coûteux, alors qu'une fausse alerte (faux positif) coûte seulement une vérification préventive par un technicien.

## Options étudiées
1. **Régression logistique par défaut (`threshold = 0.3`, `C = 1.0`) :** bonne précision (`0.653`) et bonne accuracy (`0.908`), mais un `recall` insuffisant (`0.691`) qui laisse passer trop de pannes réelles.
2. **Régression logistique régularisée (`C = 0.01`, `threshold = 0.3`) :** performances identiques au modèle par défaut (`recall = 0.691`, `precision = 0.653`), sans gain sur la détection des pannes.
3. **Forêt aléatoire (`--model forest`) :** modèle plus complexe et plus lent, avec un `recall` de `0.728` et une `precision` de `0.562`, moins performant que la régression logistique ajustée.
4. **Régression logistique avec seuil abaissé (`--threshold 0.2`) :** meilleur `recall` de tous les essais (`0.838`), modèle léger et interprétable, au prix d'une baisse de `precision` (`0.543`).

## Décision
Nous retenons la **régression logistique avec un seuil de décision à `0.2`** (`python -m maintai.train --threshold 0.2`), correspondant au run MLflow `resilient-lynx-315` (`run_id` : `a6ba66068c53462195f2d48`, entraîné sur les données `v1` d'empreinte `data_md5` : `73e0b7cb3c6f795c70c3ddf970b99c15`). Ce choix maximise le `recall` (`0.838`) pour répondre à la contrainte métier critique : éviter les pannes non détectées.

## Conséquences
* **Ce que cela facilite :** détection de près de 84 % des pannes avant qu'elles ne surviennent et déploiement d'un modèle simple, rapide et facile à maintenir.
* **Ce que cela rend plus difficile :** la baisse de `precision` (`0.543`) génère davantage de fausses alertes, ce qui demande plus d'interventions de contrôle aux équipes de maintenance.
* **Ce qu'il faudra surveiller :** le taux de fausses alertes en production et l'évolution du `recall` dans le temps (dérive des données des capteurs) afin de réentraîner le modèle sur de nouvelles versions DVC si nécessaire.# ADR 004 : Choix du modèle et du seuil de décision pour MaintAI

Date : 25/11/2026 · Auteurs : Abderrahmane Sbaii

## Contexte
Nous devons choisir le modèle de prédiction de pannes et son seuil de décision à déployer en production pour MaintAI. Dans un contexte industriel, une panne non détectée (faux négatif) entraîne un arrêt de production coûteux, alors qu'une fausse alerte (faux positif) coûte seulement une vérification préventive par un technicien.

## Options étudiées
1. **Régression logistique par défaut (`threshold = 0.3`, `C = 1.0`) :** bonne précision (`0.653`) et bonne accuracy (`0.908`), mais un `recall` insuffisant (`0.691`) qui laisse passer trop de pannes réelles.
2. **Régression logistique régularisée (`C = 0.01`, `threshold = 0.3`) :** performances identiques au modèle par défaut (`recall = 0.691`, `precision = 0.653`), sans gain sur la détection des pannes.
3. **Forêt aléatoire (`--model forest`) :** modèle plus complexe et plus lent, avec un `recall` de `0.728` et une `precision` de `0.562`, moins performant que la régression logistique ajustée.
4. **Régression logistique avec seuil abaissé (`--threshold 0.2`) :** meilleur `recall` de tous les essais (`0.838`), modèle léger et interprétable, au prix d'une baisse de `precision` (`0.543`).

## Décision
Nous retenons la **régression logistique avec un seuil de décision à `0.2`** (`python -m maintai.train --threshold 0.2`), correspondant au run MLflow `resilient-lynx-315` (`run_id` : `a6ba66068c53462195f2d48`, entraîné sur les données `v1` d'empreinte `data_md5` : `73e0b7cb3c6f795c70c3ddf970b99c15`). Ce choix maximise le `recall` (`0.838`) pour répondre à la contrainte métier critique : éviter les pannes non détectées.

## Conséquences
* **Ce que cela facilite :** détection de près de 84 % des pannes avant qu'elles ne surviennent et déploiement d'un modèle simple, rapide et facile à maintenir.
* **Ce que cela rend plus difficile :** la baisse de `precision` (`0.543`) génère davantage de fausses alertes, ce qui demande plus d'interventions de contrôle aux équipes de maintenance.
* **Ce qu'il faudra surveiller :** le taux de fausses alertes en production et l'évolution du `recall` dans le temps (dérive des données des capteurs) afin de réentraîner le modèle sur de nouvelles versions DVC si nécessaire.