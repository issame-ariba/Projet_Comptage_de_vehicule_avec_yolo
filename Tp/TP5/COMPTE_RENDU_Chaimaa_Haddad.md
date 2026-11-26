# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** Binôme  ·  **Membres :** KENZA ELAIATI — CHAIMAA HADDAD  ·  **Date :** 26/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
5 failed, 27 passed in ...s
```

Quels tests échouent, et pourquoi ?

Les 5 tests de `tests/test_tracking.py` (`test_training_creates_a_run`, `test_run_records_metrics`, `test_run_records_data_version`, `test_run_stores_the_model`, `test_options_change_the_run`) échouent car `log_run` dans `maintai/tracking.py` n'est pas encore implémentée (elle renvoie `""` sans rien enregistrer dans MLflow).

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

Avant `pip install -e .`, le package `maintai` pointait vers `TP4` (version `0.2.0`). Après `pip install -e .` dans `TP5`, il pointe vers `TP5` en mode éditable (version `0.3.0`).

## 2. Sprint 1 : MLflow

Votre fonction `log_run` (`maintai/tracking.py`) :

```python
def log_run(params: dict, metrics: dict, model, X_example, data_path: Path) -> str:
    """Enregistre un entraînement : paramètres, version des données, métriques et modèle. Renvoie l'id du run."""
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("data_md5", file_md5(data_path))
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_example,
            skops_trusted_types=TRUSTED_TYPES,
        )
        return run.info.run_id
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
32 passed, 22 warnings in 64.79s (0:01:04)
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.75 | 0.622 | 0.904 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train --C 10 --threshold 0.3` | 0.75 | 0.618 | 0.903 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Nous choisissons `python -m maintai.train --threshold 0.2` (run `a2ef7bf0f31d41e6b1548c85371c1e83`), car il obtient le meilleur **recall** (`0.838`), détectant ainsi le plus grand nombre de pannes réelles. La forêt aléatoire (`recall = 0.728`, `precision = 0.562`) n'est pas meilleure ici que la régression logistique.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

La version indiquée dans le `requirements.txt` du modèle MLflow est `scikit-learn==1.8.0`. Cela règle le problème de reproductibilité du TP4 : chaque modèle enregistré embarque automatiquement les versions exactes des bibliothèques utilisées lors de son entraînement, évitant les incompatibilités au chargement (`joblib`/`pickle`).

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les métadonnées dans `mlflow.db` et les artefacts (modèles, fichiers associés) dans `mlruns/` dans le dossier courant (`TP/TP5`). Non, ces fichiers ne vont pas dans Git (ils sont exclus par `.gitignore`), car ils sont volumineux, binaires et spécifiques aux expérimentations locales.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```yaml
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

La valeur `md5` dans `data/sensors.csv.dvc` (`73e0b7cb3c6f795c70c3ddf970b99c15`) est exactement identique au paramètre `data_md5` enregistré dans les runs MLflow sur la v1. Cela relie de façon fiable chaque modèle entraîné à la version exacte des données utilisée.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

`data/sensors.csv` est un fichier de données potentiellement très volumineux qui évolue souvent ; Git est conçu pour le code source, pas pour stocker des fichiers de données volumineux (dont chaque version resterait dans l'historique pour toujours). En revanche, `data/sensors.csv.dvc` est un petit fichier texte de 5 lignes (un « reçu » contenant l'empreinte md5 et la taille), parfaitement adapté à Git.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data\sensors.csv.dvc:
	changed outs:
		modified:           data\sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `71af41c Données v1` | `73e0b7cb` | 5000 |
| v2 | `48da9cf Données v2` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout 71af41c -- data/sensors.csv.dvc` et `dvc checkout`, `data/sensors.csv` contient **5000** lignes. Après retour à la v2 (`git checkout HEAD -- data/sensors.csv.dvc` et `dvc checkout`), il contient à nouveau **8000** lignes.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC télécharge le fichier depuis le stockage distant configuré (`%USERPROFILE%\dvc-stockage`) correspondant au `.dvc` courant (`1 file fetched and 1 file added`), restaure le cache local et recrée `data/sensors.csv` avec ses 8000 lignes.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 (`50f99429...`) | `73e0b7cb` | 4000 | 0.75 | 0.622 |
| v2 (`471b0a7b...`) | `93fdeef2` | 6400 | 0.741 | 0.65 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non, on ne peut pas conclure directement que le modèle v2 est meilleur (d'autant que son `recall` est légèrement plus bas : `0.741` contre `0.75`, malgré une meilleure précision `0.65`). Il faut être prudent car le jeu de test n'est pas le même entre la v1 (20 % de 5000 lignes, `seed=42`) et la v2 (20 % de 8000 lignes, `seed=7`, taux de panne différent : 12,8 % contre 13,6 %). Pour comparer équitablement deux modèles, il faut les évaluer sur un **même jeu de test**.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

Fait dans [docs/adr/004-choix-du-modele.md](docs/adr/004-choix-du-modele.md) : modèle `logreg` (`C=1.0`, `threshold=0.2`), run `a2ef7bf0f31d41e6b1548c85371c1e83`, `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   - **Git** versionne le code source, la configuration, la documentation et les petits fichiers `.dvc` (reçus).
   - **DVC** versionne les fichiers de données (hors Git, dans un cache et un stockage distant) via leur empreinte md5.
   - **MLflow** versionne les expériences d'entraînement : paramètres, métriques, `data_md5` des données, modèle sérialisé et versions exactes des bibliothèques (`requirements.txt`).
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   Le stockage est un chemin local sur le PC (`%USERPROFILE%\dvc-stockage`), qui ne fonctionnerait pas sur les machines des coéquipiers ; `--local` l'écrit dans `.dvc/config.local` qui est ignoré par Git. Pour partager les données en équipe, il faudrait configurer un stockage distant partagé (S3, Google Drive, serveur SSH/HTTP ou DagsHub) sans `--local` dans `.dvc/config`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   - Le **code** : dans **Git** (et le wheel du TP4).
   - Les **données** : dans **DVC** (le reçu `.dvc` dans Git, le fichier dans le stockage).
   - Le **modèle et ses dépendances** : dans **MLflow** (un run identifié par son `run_id` et son `requirements.txt`).

## 7. Le rendu Git

- Lien de la pull request : (à compléter après création de la PR sur GitHub)
- Le tag `tp5` existe sur GitHub : oui / non (à créer après fusion : `git tag tp5 && git push --tags`)
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? **non** (tous exclus par `.gitignore` et `.dvc/.gitignore`).

## 8. Ce qui reste flou

Rien de bloquant ; le lien entre `data_md5` dans MLflow, `.dvc` dans Git et `dvc pull` pour la reproductibilité est clair.
