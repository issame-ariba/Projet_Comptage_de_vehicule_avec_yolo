²# Compte rendu · TP1 : une API de prédiction pour MaintAI

**Groupe :** G1 ·  **Membres :** Abderrahmane Sbaii  ·  **Date :** 28/10/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP1.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
3 failed, 10 passed, 1 warning in 2.72s
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

Au premier lancement, trois tests de l’API échouaient :
- `test_predict_returns_probability` : la réponse était 422 alors que le test attendait 200.
- `test_high_risk_reading_raises_alert` : le résultat ne contenait pas le champ `alert`, ce qui causait `KeyError: 'alert'`.
- `test_503_when_model_missing` : la réponse était 422 au lieu du code 503 attendu.

La sortie disponible ne donne pas les noms des quatre tests qui réussissaient déjà. Il faudrait lancer `python -m pytest -v tests/test_api.py` pour les identifier précisément.

L’option `extra="forbid"` demande à Pydantic de refuser les champs qui ne sont pas déclarés dans le schéma. Les tests qui attendent 422 peuvent donc réussir uniquement parce que la requête contient un champ supplémentaire. Cela ne prouve pas nécessairement que la règle de validation visée par le test est bien appliquée : le code 422 peut être provoqué par une autre erreur dans la requête.

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | `float` | -40 °C | 150 °C | Ces limites couvrent une plage de températures très large pour un moteur et permettent de rejeter des valeurs saisies par erreur ou peu réalistes. |
| `vibration_mm_s` | `float` | 0 mm/s | 100 mm/s | La vibration ne peut pas être négative. La borne supérieure sert à bloquer les mesures extrêmes ou incohérentes. |
| `load_pct` | `float` | 0 % | 100 % | La charge est exprimée en pourcentage ; elle va donc de 0 % à 100 %. |
| `runtime_hours` | `float` | 0 h | 100000 h | Le nombre d’heures est forcément positif ou nul ; la limite haute évite d’accepter une durée excessivement grande. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
Le résultat intermédiaire exact après la seule modification de schemas.py n’apparaît pas dans les sorties conservées.
```

Les logs transmis ne contiennent pas la sortie obtenue immédiatement après la modification de `schemas.py` seulement, donc je ne peux pas recopier ce résultat exact. Au départ, trois tests échouaient et les réponses 422 montraient que la requête était refusée pendant la validation. C’est une indication utile : le schéma contrôle bien les données entrantes, mais il faut ensuite vérifier que les autres erreurs sont corrigées et que chaque test passe pour la bonne raison.

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

Le code 503 signifie que le service ne peut pas répondre pour le moment, car le modèle requis n’est pas disponible. Le code 500 est plus général et correspond à une erreur interne inattendue.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?

Le chargement du modèle demande du temps et des ressources. En le chargeant au lancement de l’application, les requêtes suivantes peuvent réutiliser le modèle déjà en mémoire au lieu de le recharger à chaque fois.

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
13 passed, 1 warning in 2.01s
```

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health` | À vérifier avec l’API MaintAI | Corps JSON à relever dans `/docs` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | À vérifier avec l’API MaintAI | Corps JSON à relever dans `/docs` |
| `POST /v1/predict` avec une température de 500 | À vérifier avec l’API MaintAI | Corps JSON à relever dans `/docs` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | À vérifier avec l’API MaintAI | Corps JSON à relever dans `/docs` |

On peut retrouver les limites dans `/docs`, en ouvrant `POST /v1/predict` puis le schéma du corps de la requête. Les champs y sont décrits avec leur type et les contraintes de validation.

## 6. Questions de compréhension

1. REST et FastAPI : quelle est la différence ?
   REST décrit une façon d’organiser les échanges entre un client et une API. FastAPI est un outil Python qui sert à programmer cette API.
2. Le schéma Pydantic sert à trois choses. Lesquelles ?
   Il vérifie la forme et le type des données, contrôle les limites définies dans les champs et aide FastAPI à afficher les données attendues dans la documentation automatique.
3. Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?
   `localhost` correspond à la machine où tourne l’application ; `8000` correspond au port du serveur ; `/v1/predict` est l’adresse de la route qui effectue la prédiction.
4. Pourquoi `/v1` dans l'adresse ?
   Cette partie indique la première version de l’API. Si l’API évolue plus tard, on pourra distinguer les routes de la nouvelle version.
5. Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?
   `maintai.api.main` indique le module à importer ; après les deux-points, `app` indique l’objet FastAPI que le serveur Uvicorn doit lancer.

## 7. Le rendu Git

- Lien de la pull request : À compléter avec le lien GitHub réel.
- Le tag `tp1` existe sur GitHub : oui.
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  À renseigner selon la relecture réelle. Exemple de commentaire possible : « Les validations sont compréhensibles et le traitement du cas où le modèle est absent est prévu. Les tests automatisés sont tous verts. »

## 8. Ce qui reste flou

Je dois encore lancer les requêtes de l’API MaintAI pour noter les vrais codes HTTP et les corps JSON, puis ajouter le lien de la pull request et vérifier les informations du tag et de la relecture GitHub.
