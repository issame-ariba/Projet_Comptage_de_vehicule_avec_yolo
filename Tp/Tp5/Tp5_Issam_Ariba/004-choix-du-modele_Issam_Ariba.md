# ADR 004 : choix du modèle et du seuil d'alerte

Date : 25/11/2026 · Auteurs : À compléter

## Contexte

MaintAI estime le risque de panne à partir de relevés de capteurs. Une panne manquée coûte plus cher qu'une fausse alerte; le recall est donc prioritaire, tout en gardant visibles les compromis sur precision et accuracy.

## Options étudiées

Les quatre entraînements réellement présents dans MLflow, tous sur le jeu v1 (`data_md5=73e0b7cb3c6f795c70c3ddf970b99c15`) :

| Modèle / paramètres | Recall | Precision | Accuracy |
|---|---:|---:|---:|
| Régression logistique, `C=1.0`, seuil `0.3` | 0.750 | 0.622 | 0.904 |
| Régression logistique, `C=0.01`, seuil `0.3` | 0.691 | 0.653 | 0.908 |
| Régression logistique, `C=1.0`, seuil `0.2` | 0.838 | 0.543 | 0.882 |
| Random forest, seuil `0.3` | 0.728 | 0.562 | 0.886 |

## Décision

Retenir à titre de choix expérimental la régression logistique `C=1.0` avec un seuil d'alerte de `0.2`, run MLflow `b1f06060805b457c9f9c95ceb6666d72`. C'est l'option au recall observé le plus élevé (`0.838`) parmi les quatre essais.

- **Run MLflow :** `b1f06060805b457c9f9c95ceb6666d72`
- **Données :** v1, 5 000 lignes
- **data_md5 :** `73e0b7cb3c6f795c70c3ddf970b99c15`
- **Recall :** 0.838
- **Precision :** 0.543
- **Accuracy :** 0.882

## Conséquences et compromis

Le seuil plus bas favorise le rappel des pannes, mais la precision et l'accuracy sont plus faibles que pour certains autres essais. Le compromis accepté est donc un volume potentiel de fausses alertes plus élevé. Les résultats proviennent de données synthétiques; le choix doit être confirmé avec des données représentatives et le coût opérationnel réel des alertes.

## Limites

L'identifiant de run et l'empreinte correspondent aux valeurs lues dans la base MLflow locale. Le dépôt de groupe `H20-sys/project` relie cette empreinte au commit v1 `f90df135d4a72f7f0a11330ec416d5727bd0a68e`. Le compte rendu/ADR déjà fusionné du groupe utilise toutefois un autre identifiant de run (`612c5b17cf2b4808900bdb562d7503e0`); les deux bases MLflow ne doivent pas être confondues.
