# COMPTE RENDU — TP4 : MaintAI devient un package Python

**Nom et prénom :** ISSAM ARIBA  
**Groupe :** G1  
**Date :** 12/11/2026  
**Projet :** MaintAI

---

## 1. Objectif du TP

L'objectif de ce TP est de transformer le projet MaintAI en un package Python réutilisable et distribuable.

Les principales étapes sont :
- Configurer le projet avec `pyproject.toml`.
- Gérer les dépendances avec `requirements.txt`.
- Installer le package en mode développement.
- Créer une interface en ligne de commande (CLI).
- Générer les distributions `.whl` et `.tar.gz`.
- Tester l'installation dans un nouvel environnement virtuel.
- Vérifier le fonctionnement de l'application Streamlit.
- Préparer le projet pour son partage avec Git et GitHub.

## 2. Sprint 1 — Configuration du package

### 2.1 Configuration de pyproject.toml

Le fichier `pyproject.toml` permet de définir les informations du package, ses dépendances, les outils de développement et le point d'entrée de la commande CLI.

Le package possède les caractéristiques suivantes :

| Élément | Valeur |
|---|---|
| Nom | maintai |
| Version | 0.2.0 |
| Python requis | >= 3.11 |
| Build backend | setuptools |
| Commande CLI | maintai-predict |

### 2.2 Gestion des dépendances

Le fichier `requirements.txt` contient les versions précises des bibliothèques utilisées :

- NumPy
- Pandas
- Scikit-learn
- Joblib
- FastAPI
- Uvicorn
- HTTPX
- Streamlit
- Pytest
- Build

Les dépendances optionnelles sont organisées dans `pyproject.toml` en trois groupes :

- `api` : FastAPI et Uvicorn.
- `ui` : Streamlit.
- `dev` : Pytest, Ruff et Build.

### 2.3 Installation en mode développement

La commande utilisée est :

```powershell
pip install -e ".[dev,api,ui]"
```

L'installation en mode éditable permet de modifier le code source sans devoir réinstaller le package à chaque modification.

### 2.4 Vérification du package

La commande utilisée :

```powershell
pip show maintai
```

Résultat obtenu :

```text
Name: maintai
Version: 0.2.0
Summary: Package Python pour l'analyse et la prédiction des pannes de machines industrielles avec l'intelligence artificielle.
```

### 2.5 Tests automatisés

Commande :

```powershell
python -m pytest
```

Résultat final obtenu après correction :

```text
27 passed, 1 warning in 6.16s
```

Les 27 tests sont réussis. Un avertissement de dépréciation lié à Starlette et HTTPX est affiché, mais il ne bloque pas l'exécution des tests.

## 3. Sprint 2 — Construction et distribution

### 3.1 Génération des distributions

Commande exécutée :

```powershell
python -m build
```

La construction du package a réussi et a généré deux fichiers dans le dossier `dist/` :

| Fichier | Taille |
|---|---:|
| maintai-0.2.0-py3-none-any.whl | 11 690 octets |
| maintai-0.2.0.tar.gz | 12 410 octets |

Le fichier `.whl` correspond à une distribution binaire Python, tandis que le fichier `.tar.gz` contient l'archive source du package.

### 3.2 Vérification du contenu du Wheel

Commande utilisée :

```powershell
tar -tf .\dist\maintai-0.2.0-py3-none-any.whl
```

Le contenu comprend notamment :

- Les modules Python du package `maintai`.
- Le module API.
- Les fichiers de métadonnées du package.
- Les informations relatives à la commande CLI.

Le Wheel contient le code du package, mais pas les dossiers `models/`, `tests/` et `ui/`.

### 3.3 Test dans un nouvel environnement virtuel

Un nouvel environnement virtuel a été créé pour simuler l'installation chez un autre utilisateur.

Le Wheel a été installé avec :

```powershell
python -m pip install "C:\Users\pc\Downloads\TP4\maintai-starter-tp4\dist\maintai-0.2.0-py3-none-any.whl"
```

L'installation du package a réussi.

### 3.4 Gestion du modèle et des versions

Lors du premier test, le programme a affiché :

```text
Modèle introuvable
```

Cette erreur était due à l'absence du dossier du modèle dans la distribution Wheel.

Pour résoudre ce problème, la variable d'environnement suivante a été utilisée :

```powershell
$env:MAINTAI_MODELS_DIR = "C:\Users\pc\Downloads\TP4\maintai-starter-tp4\models"
```

Un avertissement `InconsistentVersionWarning` est ensuite apparu, car le modèle avait été entraîné avec Scikit-learn 1.8.0 alors que l'environnement de test utilisait une autre version.

La solution a consisté à installer la même version que celle utilisée pour entraîner le modèle :

```powershell
python -m pip install scikit-learn==1.8.0
```

Après cette correction, la prédiction a fonctionné sans avertissement de différence de version.

Le fichier `models/model_info.json` indique notamment :

```json
{
  "features": [
    "temperature_c",
    "vibration_mm_s",
    "load_pct",
    "runtime_hours"
  ],
  "target": "failure",
  "threshold": 0.3,
  "sklearn_version": "1.8.0"
}
```

### 3.5 Test de la commande CLI

Commande utilisée :

```powershell
maintai-predict 72 6 85 15000
```

Résultat observé lors du test :

```text
Diagnostic de la machine : 95 % (ALERTE)
```

La commande permet de transmettre les caractéristiques d'une machine et d'obtenir une estimation de sa probabilité de panne.

## 4. Questions et analyse

### Question 1 — Quelle est la différence entre une installation classique et une installation éditable ?

Une installation classique copie le package dans l'environnement Python. Les modifications apportées au code source ne sont pas automatiquement prises en compte.

Une installation éditable (`pip install -e`) établit un lien entre l'environnement Python et le dossier du projet. Les modifications du code source sont donc visibles immédiatement, sans réinstallation.

### Question 2 — Pourquoi créer un Wheel ?

Le Wheel (`.whl`) est un format de distribution Python qui facilite l'installation d'un package.

Il permet :
- D'installer rapidement un package.
- De distribuer le projet à d'autres utilisateurs.
- De tester le package dans un environnement indépendant.
- De séparer le code source du processus de développement.

### Question 3 — Pourquoi utiliser les versions exactes des dépendances ?

Les versions exactes permettent de reproduire le même environnement logiciel.

Elles évitent les problèmes de compatibilité entre bibliothèques, notamment lors du chargement des modèles de Machine Learning avec Joblib.

Dans notre projet, l'utilisation de Scikit-learn 1.8.0 a permis de supprimer l'avertissement lié à la différence de version entre l'entraînement et l'environnement de test.

### Question 4 — Pourquoi le modèle n'est-il pas inclus dans le Wheel ?

Le Wheel contient principalement les modules Python et les métadonnées du package.

Dans notre projet, le dossier `models/` n'est pas inclus dans le Wheel. Il faut donc fournir le modèle séparément ou l'entraîner dans le nouvel environnement.

La variable `MAINTAI_MODELS_DIR` permet d'indiquer au package l'emplacement du modèle.

## 5. Interface utilisateur Streamlit

L'application Streamlit permet de proposer une interface graphique pour exploiter les fonctionnalités du projet MaintAI.

La commande suivante permet de démarrer l'application :

```powershell
streamlit run ui/app.py
```

**Résultat :** l'application Streamlit fonctionne sans erreur.

## 6. Conclusion

Ce TP nous a permis de transformer MaintAI en un package Python structuré et réutilisable.

Nous avons appris à configurer les dépendances, installer un package en mode éditable, construire des distributions Wheel et Source, et tester leur installation dans un environnement virtuel indépendant.

Nous avons également identifié et corrigé des problèmes liés à l'emplacement du modèle et à la compatibilité des versions de Scikit-learn.

Les tests automatisés ont été exécutés avec succès : 27 tests réussis.

Le projet dispose désormais d'une structure permettant sa distribution et son utilisation dans différents environnements Python.

## 7. Git et GitHub

**État du dépôt :** à vérifier.

**Pull Request :** non renseignée.

**Tag `tp4` :** non vérifié.

