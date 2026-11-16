# Compte rendu · TP4 : MaintAI devient un package Python

**Groupe :** G1 ·  **Membres :** Abderrahmane Sbaii  ·  **Date :** 14/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP4.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP4`, avec son propre `.venv`)

Dernière ligne de `python -m pytest` juste après `pip install -r requirements.txt` :

```
====== 2 failed, 25 passed in 14.88s ======
```

Quels sont les deux tests qui échouent, et pourquoi ?

Les deux tests qui échouent sont `test_installed_version_matches_the_code` et `test_command_is_declared` dans `tests/test_package.py`. Ils échouent parce que le package `maintai` n'est pas encore installé dans le `.venv`.

## 2. Sprint 1 : `pyproject.toml` et `pip install -e .`

Vos sections `dependencies` et `[project.scripts]` :

```toml
dependencies = [
    "pandas>=2.2",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "pydantic-settings>=2.0",
    "httpx>=0.27",
]

[project.scripts]
maintai-predict = "maintai.cli:main"
```

Pourquoi `pytest` et `fastapi` ne sont-ils pas dans `dependencies` ?

Ils sont déjà déclarés dans les groupes optionnels (`dev` et `api`) sous `[project.optional-dependencies]`. Un utilisateur qui veut uniquement lancer la commande `maintai-predict` n'a pas besoin des outils de test ou du serveur API.

Sortie de `pip show maintai` (les quatre premières lignes) :

```
Name: maintai
Version: 0.2.0
Summary: Outil de prédiction de panne pour la maintenance prédictive
Home-page:
```

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
====== 27 passed in 9.94s ======
```

Placez-vous dans un autre dossier (`cd %TEMP%`) et lancez `maintai-predict 72 6 85 15000`, puis `python -c "import maintai; print(maintai.__file__)"`. Qu'affichent ces deux commandes ? Où Python trouve-t-il le code de `maintai` ?

La commande `maintai-predict` affiche `Probabilité de panne : 95 % (ALERTE)`. La commande Python affiche le chemin `C:\Users\sbaii\Downloads\TP4\maintai-starter-tp4\maintai\__init__.py`. Python trouve le code partout grâce au lien créé dans `.venv\Lib\site-packages` lors de l'exécution de `pip install -e .`.

Modifiez le message affiché par `maintai/cli.py`, puis relancez `maintai-predict` sans réinstaller. Le changement est-il visible ? Pourquoi ?

Oui, le changement est visible immédiatement sans réinstaller. L'option `-e` (*editable*) crée un lien direct vers le dossier du code au lieu de copier les fichiers.

## 3. Sprint 2 : construire et installer le wheel

Sortie de `dir dist` après `python -m build` :

```
maintai-0.2.0-py3-none-any.whl
maintai-0.2.0.tar.gz
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

Non, le modèle (`models/`), les tests (`tests/`) et `ui/` ne sont pas dans le wheel. Seul le dossier `maintai/` et ses métadonnées (`dist-info`) sont inclus, car `pyproject.toml` contient la règle `include = ["maintai*"]`.

Dans un environnement neuf (`%TEMP%\essai`), installez le wheel et lancez `maintai-predict` :

| Étape | Ce qui s'affiche |
|---|---|
| sans `MAINTAI_MODELS_DIR` | Erreur : modèle introuvable (le dossier `models/` n'est pas dans le wheel) |
| avec `MAINTAI_MODELS_DIR` vers vos `models` | `Probabilité de panne : 95 % (ALERTE)` + avertissement `InconsistentVersionWarning` |
| après `pip install scikit-learn==1.8.0` | `Probabilité de panne : 95 % (ALERTE)` (affichage propre, sans avertissement) |

D'où vient l'avertissement `InconsistentVersionWarning` ? Quelle ligne de `models/model_info.json` permet de le comprendre ?

Cet avertissement vient du fait que le modèle a été écrit avec une version de `scikit-learn` différente de celle installée dans le nouvel environnement. Dans `models/model_info.json`, la ligne qui précise la version de `scikit-learn` permet de connaître la version exacte utilisée lors de l'entraînement.

## 4. Questions de compréhension

1. Quelle différence entre `requirements.txt` et la liste `dependencies` de `pyproject.toml` ?
   `pyproject.toml` utilise `>=` (« au moins ») pour que le package puisse s'installer facilement à côté d'autres bibliothèques. `requirements.txt` utilise `==` (« exactement ») pour bloquer les versions exactes nécessaires pour relire le modèle sans erreur.
2. Quelle différence entre `pip install -e .` et `pip install dist\maintai-0.2.0-py3-none-any.whl` ?
   `pip install -e .` fait une installation éditable (un lien vers le dossier du code) utilisée pour développer et voir les changements tout de suite. L'installation du fichier `.whl` (wheel) installe une copie figée du code pour livrer le projet à quelqu'un d'autre.
3. Qu'est-ce qu'un « point d'entrée » (`[project.scripts]`) ? Où pip crée-t-il le fichier `maintai-predict.exe` ?
   Un point d'entrée relie une commande du terminal (`maintai-predict`) à une fonction précise du code (`main` dans `maintai/cli.py`). `pip` crée le fichier `maintai-predict.exe` dans le dossier `.venv\Scripts\`.

## 5. Le rendu Git

- Lien de la pull request : …
- Le tag `tp4` existe sur GitHub : oui
- `git status` avant le commit : `dist/`, `build/` ou `maintai.egg-info/` apparaissaient-ils ? non

## 6. Ce qui reste flou

Rien à signaler, tout est clair.