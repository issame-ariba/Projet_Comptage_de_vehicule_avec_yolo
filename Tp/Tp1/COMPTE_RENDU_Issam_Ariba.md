# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1  ·  **Membres :** Issam Ariba  ·  **Date :** 28/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 2.72s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Les trois tests qui échouaient au départ étaient :
- `test_predict_returns_probability` : attendu 200, obtenu 422.
- `test_high_risk_reading_raises_alert` : la réponse ne contenait pas la clé `alert` (`KeyError: 'alert'`).
- `test_503_when_model_missing` : attendu 503, obtenu 422.

Les noms exacts des quatre tests qui passaient dès le début ne sont pas visibles dans les sorties que j’ai envoyées. Avec `extra="forbid"`, Pydantic refuse les champs supplémentaires. Ainsi, un test qui attend 422 peut réussir simplement parce qu’un champ inconnu est présent, et non parce que la validation attendue par le test fonctionne correctement.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | `float` | -40 | 150 | Une température moteur peut être très basse ou très élevée ; ces limites rejettent les valeurs extrêmes ou peu plausibles. |
| `vibration_mm_s` | `float` | 0 | 100 | Une vibration ne peut pas être négative ; 100 mm/s est une limite haute pour rejeter les valeurs anormales ou erronées. |
| `load_pct` | `float` | 0 | 100 | Le pourcentage de charge est compris entre 0 % et 100 %. |
| `runtime_hours` | `float` | 0 | 100000 | Le temps de fonctionnement ne peut pas être négatif ; la limite supérieure rejette les valeurs démesurées. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
Résultat intermédiaire exact non conservé dans les sorties envoyées.
```

Les sorties disponibles ne permettent pas de connaître exactement le résultat obtenu après avoir modifié uniquement `schemas.py`. Avant les corrections, les tests affichaient `3 failed, 10 passed, 1 warning in 2.72s`. Le code 422 indique que la requête a été rejetée pendant la validation des données, avant que la prédiction se déroule normalement. C’est utile pour repérer un problème de format ou de validation, mais il faut vérifier que chaque test passe ou échoue pour la bonne raison.

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
predictor = state.get("predictor")
if predictor is None:
    raise HTTPException(
        status_code=503,
        detail="Modèle de prédiction indisponible.",
    )
result = predictor.predict(reading.model_dump())
return PredictionOut(**result)
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?

Le code 503 signifie que le service est temporairement indisponible parce que le modèle nécessaire à la prédiction manque. Le code 500 est plutôt utilisé pour une erreur interne inattendue du serveur.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Le chargement du modèle peut prendre du temps. En le chargeant au démarrage, l’API peut le réutiliser pour les requêtes suivantes, ce qui évite de refaire ce travail à chaque demande et améliore les temps de réponse.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 2.01s
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | À tester dans `/docs` | Réponse exacte non fournie |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | À tester dans `/docs` | Réponse exacte non fournie |
| `POST /v1/predict` avec une température de 500 | À tester dans `/docs` | Réponse exacte non fournie |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | À tester dans `/docs` | Réponse exacte non fournie |

Dans `/docs`, les bornes apparaissent dans la documentation de `POST /v1/predict`, dans le schéma du corps de la requête. On peut y voir les types des champs et leurs contraintes minimales et maximales.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST est un style d’architecture pour organiser les échanges avec une API. FastAPI est un framework Python qui permet de créer une API web.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Il vérifie les types des données reçues, contrôle les contraintes comme les minimums et maximums, et permet à FastAPI de générer la documentation des données attendues.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` désigne l’ordinateur local, `8000` est le port du serveur et `/v1/predict` est le chemin de la route de prédiction.
4. Pourquoi `/v1` dans l'adresse ?
   `/v1` indique la version 1 de l’API et permet de distinguer cette version d’éventuelles versions futures.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` est le module Python qui contient l’API, et `app` est l’objet FastAPI que Uvicorn doit démarrer.

## 7. Le rendu Git

- Lien de la pull request : À compléter avec le lien réel sur GitHub.
- Le tag `tp1` existe sur GitHub : oui .
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  À compléter avec le nom et le commentaire réels du relecteur.

## 8. Ce qui reste flou

Je dois encore vérifier les réponses réelles de l’API MaintAI dans `/docs`, les informations de la pull request GitHub, les quatre tests qui passaient dès le début et le résultat exact obtenu après la modification de `schemas.py` seule.
