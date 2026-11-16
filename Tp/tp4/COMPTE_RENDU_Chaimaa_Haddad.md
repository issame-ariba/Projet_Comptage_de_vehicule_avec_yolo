# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** Groupe MaintAI  ·  **Membres :** Chaïma Haddad  ·  **Date :** 12/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
FAILED tests/test_package.py::test_installed_version_matches_the_code - AssertionError: assert '0.2.0' == '0.1.0'
FAILED tests/test_cli.py::test_cli_predict - FileNotFoundError: [Errno 2] No such file or directory: 'maintai-predict'
```

Quels sont les deux tests qui échouent, et pourquoi ?

1. `test_installed_version_matches_the_code` : échoue car le package `maintai` n'a pas encore été installé en mode éditable avec `pip install -e .` pour faire correspondre les métadonnées de version installée (`importlib.metadata.version("maintai")`) avec le code source.
2. `test_cli.py` : échoue car la commande CLI de console `maintai-predict` n'est pas encore enregistrée comme point d'entrée exécutable dans l'environnement.

---

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "pydantic>=2.6",
    "pydantic-settings>=2.0",
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.4",
    "joblib>=1.3",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

- `pytest` est un outil de développement et de test, non requis pour l'exécution du code en production par un utilisateur du package. Il est placé dans les dépendances optionnelles `[project.optional-dependencies] dev = [...]`.
- `fastapi` et `uvicorn` ne sont nécessaires que si l'utilisateur souhaite démarrer le serveur API HTTP. Le package principal et son CLI n'en ont pas besoin directement, ils sont donc isolés dans l'extra `api = ["fastapi", "uvicorn"]`.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: MaintAI : prédiction de panne à partir de relevés de capteurs industriels.
Location: C:\Users\user\AppData\Roaming\Python\Python314\site-packages
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
27 passed, 1 warning in 6.02s
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

- `maintai-predict 72 6 85 15000` affiche :
  `Probabilité de panne : 95 % (ALERTE)`
- `python -c "import maintai; print(maintai.__file__)"` affiche :
  `C:\Users\user\Downloads\solution_deux_seances (3)\solution_deux_seances\S4\TP\TP4\maintai\__init__.py`
- Python trouve le code directement dans notre dossier source de travail grâce au mode éditable (`pip install -e .`), qui crée un lien `.pth` / loader pointant vers le dossier local sans copier les fichiers dans `site-packages`.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

- Oui, le changement est immédiatement visible. En installation éditable, Python exécute les fichiers réels situés dans le dossier source du dépôt sans avoir besoin de refaire `pip install`.

---

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        11/12/2026   4:57 AM          11648 maintai-0.2.0-py3-none-any.whl
-a----        11/12/2026   4:57 AM          12247 maintai-0.2.0.tar.gz
```

Contenu du wheel (`tar -tf dist\maintai-0.2.0-py3-none-any.whl`). Le modèle, les tests et `ui/` y sont-ils ? Pourquoi ?

```
maintai/__init__.py
maintai/cli.py
maintai/client.py
maintai/config.py
maintai/data.py
maintai/dataset.py
maintai/predict.py
maintai/train.py
maintai/api/__init__.py
maintai/api/main.py
maintai/api/schemas.py
maintai/api/security.py
maintai-0.2.0.dist-info/METADATA
maintai-0.2.0.dist-info/WHEEL
maintai-0.2.0.dist-info/entry_points.txt
maintai-0.2.0.dist-info/top_level.txt
maintai-0.2.0.dist-info/RECORD
```

Le modèle (`models/`), les tests (`tests/`) et l'interface (`ui/`) ne sont **pas** dans le wheel :
- Le wheel ne contient que le code du package importable Python `maintai/`.
- Les modèles sont des artefacts volumineux et générés (non versionnés dans la distribution logicielle standard).
- Les tests et l'UI Streamlit sont du code d'accompagnement et non des modules internes de la bibliothèque `maintai`.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | `FileNotFoundError: Modèle non trouvé (modèle absent dans le répertoire par défaut)` |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | `Probabilité de panne : 95 % (ALERTE)` |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)` (sans avertissement de version) |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

L'avertissement provient de `joblib` / `scikit-learn` quand la version de `scikit-learn` utilisée pour charger le modèle est différente de celle utilisée lors de l'entraînement (`fit`).
Dans `models/model_info.json`, c'est la clé `"sklearn_version": "1.8.0"` qui documente précisément la version exacte avec laquelle le pipeline a été sérialisé.

---

## 4. Questions de compréhension

1. **Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?**
   `pyproject.toml` spécifie les dépendances abstraites et minimales nécessaires au fonctionnement du package pour n'importe quel utilisateur ou bibliothèque qui l'installe. `requirements.txt` sert à figer (pinner) un environnement d'exécution complet et reproductible pour le déploiement ou l'environnement de développement.

2. **Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?**
   `pip install -e .` installe en mode développement (editable) : les modifications apportées au code source local sont immédiatement actives. Le wheel `.whl` est une archive autonome statique : il copie les fichiers compilés/figés dans `site-packages`.

3. **Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?**
   Un point d'entrée associe une commande en ligne de commande à une fonction Python exécutable (ex: `maintai.cli:main`). Lors de l'installation, pip crée un exécutable wrapper (`maintai-predict.exe` sous Windows) dans le dossier `Scripts` de l'environnement Python actif (`%USERPROFILE%\AppData\Roaming\Python\Python314\Scripts` ou `.venv/Scripts`).

---

## 5. Le rendu Git

- Lien de la pull request : (à compléter lors de l'ouverture de la PR sur GitHub)
- Le tag `tp4` existe sur GitHub : oui
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? non (ignorés via `.gitignore`)

---

## 6. Ce qui reste flou

Tout est clair. L'architecture modulaire, le packaging avec `pyproject.toml`, l'exposition d'un CLI et l'isolation des dépendances de test/API sont maîtrisés.
