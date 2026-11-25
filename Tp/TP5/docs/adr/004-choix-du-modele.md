# ADR 004 : Choix du modèle et du seuil de décision pour MaintAI

Date : 26/11/2026 · Auteurs : KENZA ELAIATI — CHAIMAA HADDAD

## Contexte
MaintAI doit prédire les pannes de machines industrielles à partir de relevés de capteurs (`temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`). La contrainte métier principale est qu'une panne manquée (faux négatif) entraîne un arrêt imprévu et coûteux, beaucoup plus pénalisant qu'une inspection préventive inutile (fausse alerte). Il faut donc arbitrer entre le modèle, sa régularisation et son seuil d'alerte à partir des runs enregistrés dans MLflow.

## Options étudiées
Comparaison des runs sur les données v1 (`data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`, `n_train = 4000`) et v2 (`data_md5 = 93fdeef2cac1893c4f720c16457eea75`, `n_train = 6400`) :

1. **Régression logistique par défaut (`--model logreg`, `C=1.0`, `threshold=0.3`)** — Run `50f99429019f4428bbac0c2c65d02cab` :
   - Avantages : bon équilibre (`recall = 0.750`, `precision = 0.622`, `accuracy = 0.904`), modèle simple et rapide.
   - Inconvénients : laisse passer 25 % des pannes sur le jeu de test.
2. **Régression logistique fortement régularisée (`--C 0.01`, `threshold=0.3`)** — Run `be9cedfc23994193bca8e41dd6ca34c3` :
   - Avantages : meilleure précision (`0.653`) et meilleure accuracy (`0.908`).
   - Inconvénients : recall plus faible (`0.691`), trop de pannes manquées.
3. **Régression logistique avec seuil abaissé (`--model logreg`, `C=1.0`, `threshold=0.2`)** — Run `a2ef7bf0f31d41e6b1548c85371c1e83` :
   - Avantages : meilleur recall de tous les essais (`0.838`), soit la plus grande proportion de pannes détectées.
   - Inconvénients : précision plus basse (`0.543`), ce qui génère plus de fausses alertes.
4. **Forêt aléatoire (`--model forest`, `threshold=0.3`)** — Run `e662629562e04ca78ae4fd829d677edc` :
   - Avantages : capture des relations non linéaires.
   - Inconvénients : moins bon recall (`0.728`) et moins bonne précision (`0.562`) que la régression logistique par défaut, tout en étant plus lourde à sérialiser (`skops_trusted_types`).

## Décision
Nous retenons la **régression logistique avec `C=1.0` et un seuil de décision abaissé à `0.2`** :
- **Run MLflow :** `a2ef7bf0f31d41e6b1548c85371c1e83`
- **Version des données (`data_md5`) :** `73e0b7cb3c6f795c70c3ddf970b99c15`
- **Métriques :** `recall = 0.838`, `precision = 0.543`, `accuracy = 0.882`

Ce choix répond directement à la contrainte métier : maximiser la détection des pannes (`recall = 83,8 %`) afin de limiter le risque de panne critique non anticipée.

## Conséquences
- **Ce que cela facilite :** réduction du nombre de pannes manquées en production, déploiement léger grâce à la régression logistique et traçabilité complète via MLflow (`run_id`) et DVC (`data_md5`).
- **Ce que nous acceptons en échange :** une précision de `0.543` (environ 46 % des alertes sont des fausses alertes), impliquant davantage de vérifications de maintenance préventive.
- **Ce qu'il faudra surveiller :** la dérive des données en production, le taux de fausses alertes toléré par les techniciens, et la ré-évaluation du modèle sur de nouvelles données réelles (comme la v2, en veillant à comparer sur un jeu de test commun).

