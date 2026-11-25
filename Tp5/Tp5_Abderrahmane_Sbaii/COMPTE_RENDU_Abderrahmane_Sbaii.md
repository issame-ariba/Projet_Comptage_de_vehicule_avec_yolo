# Compte rendu · TP5 : suivre les entraînements (MLflow) et versionner les données (DVC)

**Groupe :** …  ·  **Membres :** Abderrahmane Sbaii, …  ·  **Date :** 25/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP5.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP5`)

Dernière ligne de `python -m pytest` après `pip install -r requirements.txt` et `pip install -e .` :

```
========================= 5 failed, 27 passed in 14.32s =========================
```

Quels tests échouent, et pourquoi ?

Les 5 tests du fichier `tests/test_tracking.py` échouent car la fonction `log_run` dans `maintai/tracking.py` est encore vide (elle renvoie simplement `""`) et n'enregistre pas encore les paramètres, métriques, `data_md5` et modèles dans MLflow.

Avant `pip install -e .`, où pointait le package `maintai` installé dans l'environnement ? Et après ?

* **Avant `pip install -e .` :** il pointait vers le dossier du **TP4** (ou n'était pas trouvé dans le nouvel environnement `.venv` du TP5).
* **Après `pip install -e .` :** il pointe en mode éditable vers le dossier courant **`D:\telechargement_data\TP5\TP5`**.

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
========================= 32 passed, 4 warnings in 48.12s =========================
```

Vos runs (au moins quatre), relevés dans `mlflow ui` (mode « Model training ») :

| Commande | recall | precision | accuracy |
|---|---|---|---|
| `python -m maintai.train` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --C 0.01` | 0.691 | 0.653 | 0.908 |
| `python -m maintai.train --threshold 0.2` | 0.838 | 0.543 | 0.882 |
| `python -m maintai.train --model forest` | 0.728 | 0.562 | 0.886 |
| `python -m maintai.train` (sur données v2) | 0.741 | 0.650 | 0.916 |

Quel run choisiriez-vous pour MaintAI, et pourquoi ? (Rappel : une panne manquée coûte plus cher qu'une fausse alerte.)

Je choisis le run **`python -m maintai.train --threshold 0.2`** (`resilient-lynx-315`) car il obtient le **meilleur `recall` (`0.838`)**. Comme une panne manquée coûte beaucoup plus cher qu'une fausse alerte, il est prioritaire de détecter un maximum de pannes réelles, même si la `precision` baisse (`0.543`), ce qui entraîne un peu plus de vérifications préventives.

Dans `mlflow ui`, ouvrez le modèle d'un run. Quelle version de scikit-learn est indiquée dans son `requirements.txt` ? Quel problème du TP4 cela règle-t-il ?

La version indiquée est **`scikit-learn==1.8.0`**. Cela règle le problème de **reproductibilité** du TP4 : au TP4, le modèle était sauvegardé seul (`model.joblib`) sans les versions exactes des bibliothèques, ce qui pouvait provoquer des erreurs ou des comportements différents lors du rechargement futur du modèle.

Où MLflow enregistre-t-il les runs sur votre disque ? Ces fichiers vont-ils dans Git ? Pourquoi ?

MLflow enregistre les paramètres, métriques et tags dans le fichier SQLite **`mlflow.db`**, et les modèles/artefacts dans le dossier **`mlruns/`** à la racine de `TP5`. Ces fichiers **ne vont pas dans Git** (ils sont exclus par `.gitignore`) car ils sont volumineux, binaires et générés localement à chaque test ou entraînement.

## 3. Sprint 2 : DVC

Contenu de `data/sensors.csv.dvc` après `dvc add data/sensors.csv` :

```
outs:
- md5: 73e0b7cb3c6f795c70c3ddf970b99c15
  size: 126815
  hash: md5
  path: sensors.csv
```

Comparez la valeur `md5` de ce fichier au paramètre `data_md5` de votre dernier run MLflow. Que constatez-vous ?

Les deux valeurs sont **strictement identiques** (`73e0b7cb3c6f795c70c3ddf970b99c15` pour la v1, et `93fdeef2...` pour la v2). Cela permet de relier chaque run MLflow à la version exacte des données utilisées lors de l'entraînement.

Pourquoi `data/sensors.csv` ne va pas dans Git, alors que `data/sensors.csv.dvc` y va ?

Git gère mal les fichiers de données volumineux et alourdit l'historique du dépôt à chaque modification. DVC garde le fichier réel (`sensors.csv`) dans son cache/stockage externe et ne place dans Git qu'un petit reçu texte (`sensors.csv.dvc` de 98 octets) contenant l'empreinte `md5`.

Après `python -m maintai.dataset --n 8000 --seed 7`, que dit `dvc status` ?

```
data/sensors.csv.dvc:
        changed outs:
                modified:           data/sensors.csv
```

| Version | Commit Git (`git log --oneline`) | md5 (8 premiers caractères) | Nombre de lignes |
|---|---|---|---|
| v1 | `e9592eb` | `73e0b7cb` | 5000 |
| v2 | `8315a9c` | `93fdeef2` | 8000 |

Revenez à la v1 (`git checkout <commit> -- data/sensors.csv.dvc`, puis `dvc checkout`). Combien de lignes contient `data/sensors.csv` ? Puis revenez à la v2.

Après `git checkout e9592eb -- data/sensors.csv.dvc` et `dvc checkout`, le fichier `data/sensors.csv` contient de nouveau **5000 lignes**. Après le retour sur `HEAD` et `dvc checkout`, il contient de nouveau **8000 lignes**.

Supprimez `data/sensors.csv` et le dossier `.dvc/cache`, puis lancez `dvc pull`. Que se passe-t-il ?

DVC affiche `1 file fetched and 1 file added` : il télécharge automatiquement le fichier correspondant au reçu `sensors.csv.dvc` depuis le stockage distant (`%USERPROFILE%\dvc-stockage`) vers le cache `.dvc\cache`, puis restaure `data\sensors.csv` dans le dossier du projet.

## 4. Relier modèle et données

Entraînez un modèle sur la v2. Dans `mlflow ui`, comparez ce run à celui de la v1 avec les mêmes réglages :

| Run | data_md5 (8 caractères) | n_train | recall | precision |
|---|---|---|---|---|
| v1 | `73e0b7cb` | 4000 | 0.691 | 0.653 |
| v2 | `93fdeef2` | 6400 | 0.741 | 0.650 |

Peut-on dire que le modèle v2 est « meilleur » ? Pourquoi faut-il être prudent en comparant deux runs entraînés sur des données différentes ?

Non, on ne peut pas conclure directement que le modèle v2 est meilleur. Les deux modèles n'ont pas été évalués sur le **même jeu de test** (1000 lignes pour la v1 contre 1600 lignes générées avec `seed=7` pour la v2). Pour comparer deux modèles de manière rigoureuse, il faut toujours les évaluer sur un jeu de test identique.

## 5. Décision : l'ADR 004

Dans `docs/adr/004-choix-du-modele.md` : le modèle et le seuil retenus, à partir de votre tableau MLflow. Indiquez l'identifiant du run et le `data_md5` de la version des données utilisée.

Voir le fichier `docs/adr/004-choix-du-modele.md`.

## 6. Questions de compréhension

1. Quelle différence entre Git, DVC et MLflow ? Que versionne chacun ?
   * **Git** versionne le **code source** (`maintai/*.py`, `tests/`) et les petits reçus `.dvc`.
   * **DVC** versionne les **fichiers de données** (`data/sensors.csv`) via leur empreinte `md5` dans un stockage externe.
   * **MLflow** versionne les **entraînements (runs)** : hyperparamètres, métriques, modèle entraîné et versions exactes des bibliothèques (`requirements.txt`).
2. Pourquoi le stockage DVC est-il ajouté avec `--local` dans ce TP ? Que faudrait-il pour que tout le groupe partage les mêmes données ?
   L'option `--local` écrit le chemin dans `.dvc/config.local` (ignoré par Git) car il s'agit d'un dossier local propre à mon ordinateur (`C:\Users\sbaii\dvc-stockage`). Pour partager les données en équipe, il faudrait configurer un **stockage distant partagé** (Amazon S3, Google Drive, Azure Blob ou serveur SSH) sans `--local` dans `.dvc/config`.
3. Livrer un modèle, c'est trois choses (TP4). Lesquelles, et où sont-elles maintenant ?
   * **Le code :** dans **Git** (et le package wheel du TP4).
   * **Les données :** dans **DVC** (le reçu `.dvc` dans Git et le fichier réel dans le stockage DVC).
   * **Le modèle et ses versions exactes :** dans **MLflow** (chaque run contient l'artefact `model.skops` et son `requirements.txt`).

## 7. Le rendu Git

- Lien de la pull request : …
- Le tag `tp5` existe sur GitHub : oui
- `git status` avant le commit : `mlflow.db`, `mlruns/`, `data/sensors.csv` ou `.dvc/cache` apparaissaient-ils ? non

## 8. Ce qui reste flou

Rien de particulier : l'articulation entre Git (code), DVC (empreinte des données) et MLflow (suivi des runs et reproductibilité) est claire grâce au lien assuré par `data_md5`.
## 9. Bonus : Optimisation par Grid Search (30 runs maximum)

### 9.1. Méthode utilisée
Pour automatiser la recherche des meilleurs réglages sans dépasser un budget de **30 entraînements**, nous avons mis en place une **recherche par grille (*Grid Search*)** pilotée par un script Python (`grid_search.py`). 
* **Principe :** le script génère toutes les combinaisons d'hyperparamètres définies, les limite strictement à 30 essais maximum, puis appelle `python -m maintai.train` pour chaque combinaison.
* **Traçabilité :** chaque essai est automatiquement enregistré comme un run distinct dans **MLflow**, ce qui permet de comparer toutes les métriques dans une seule interface.

### 9.2. Hyperparamètres explorés et validation rapide (*Flash Test*)
* **Hyperparamètres testés :**
  * **Régularisation `C` :** `[0.001, 0.01, 0.1, 1.0, 10.0]` (et valeurs intermédiaires `[0.005, 0.05, 0.5, 2.0, 5.0]`) pour contrôler la complexité de la régression logistique.
  * **Seuil de décision `threshold` :** `[0.15, 0.18, 0.20, 0.22, 0.25, 0.30]` pour ajuster la sensibilité de détection des pannes.
  * **Budget total :** $5 \times 3 + 5 \times 3 = 30$ combinaisons testées.
* **Validation rapide (*Flash Test*) :**
  * Avant de lancer les 30 entraînements complets, un *flash test* sur **2 combinaisons** (`configs_to_run[:2]`) a été exécuté pour vérifier en moins de 30 secondes que les arguments CLI étaient valides, que `log_run` enregistrait bien chaque essai dans `mlflow.db` et qu'aucune erreur n'interrompait la boucle.

### 9.3. Code du script (`grid_search.py`)

```python
import subprocess
import sys

# Grille 1 : 5 valeurs de C x 3 seuils = 15 runs
c_values_1 = [0.001, 0.01, 0.1, 1.0, 10.0]
thresholds_1 = [0.15, 0.20, 0.25]

# Grille 2 : 5 valeurs intermédiaires de C x 3 seuils = 15 runs
c_values_2 = [0.005, 0.05, 0.5, 2.0, 5.0]
thresholds_2 = [0.18, 0.22, 0.30]

configs = []
for c in c_values_1:
    for th in thresholds_1:
        configs.append(["--C", str(c), "--threshold", str(th)])

for c in c_values_2:
    for th in thresholds_2:
        configs.append(["--C", str(c), "--threshold", str(th)])

# Plafond strict à 30 runs maximum
configs_to_run = configs[:30]

for i, args in enumerate(configs_to_run, start=1):
    cmd = [sys.executable, "-m", "maintai.train"] + args
    print(f"[{i}/{len(configs_to_run)}] Exécution : {' '.join(cmd)}")
    subprocess.run(cmd, check=True)