# Compte rendu — TP1 : une API de prédiction pour MaintAI

**Groupe :** G3  ·  **Membres :** KENZA ELAIATI — CHAIMAA HADDAD  ·  **Date :** 28/10/2026

> Ce compte rendu documente la mise en place, la validation Pydantic, l'implémentation de la route de prédiction et la vérification des 13 tests automatisés de l'API MaintAI.

---

## 1. Mise en place

Dernière ligne de `python -m pytest`, juste après la mise en place (rien n'est encore écrit) :

```
=================== 3 failed, 10 passed, 1 warning in 7.15s ===================
```

Dans `tests/test_api.py`, 4 tests sur 7 passent déjà alors que rien n'est écrit. Lesquels ? Pour les deux tests qui attendent un code 422, expliquez pourquoi ils passent « pour une mauvaise raison » (indice : regardez `extra="forbid"` dans `schemas.py`).

**Réponse :**  
Les 4 tests qui passent initialement sont :
1. `test_health` : car la route `GET /health` est déjà implémentée et ne dépend pas du schéma des capteurs ;
2. `test_openapi_documents_predict` : car la route est enregistrée dans le routeur et présente dans le schéma OpenAPI ;
3. `test_out_of_range_value_is_rejected` ;
4. `test_missing_field_is_rejected`.

**Pourquoi les tests 422 passent pour une « mauvaise raison » :**  
Dans le starter fourni, `SensorReading` ne déclare aucun champ (`pass`) mais active `extra="forbid"`. En conséquence, le validateur Pydantic rejette **absolument tous les champs envoyés**, même les valeurs correctes ! Le code 422 est donc renvoyé parce que `temperature_c` est considéré comme un champ inconnu interdit, et non parce que sa valeur 500 dépasse la borne autorisée.

---

## 2. Le schéma d'entrée (`maintai/api/schemas.py`)

| Variable | Type | Minimum (`ge`) | Maximum (`le`) | Justification physique (pas le min / max des données) |
|---|---|---|---|---|
| `temperature_c` | `float` | `-40.0` | `150.0` | Démarrage par grand froid ($-40\,^\circ\text{C}$), surchauffe extrême avant destruction des bobinages ($150\,^\circ\text{C}$). 500 °C est une sonde cassée. |
| `vibration_mm_s` | `float` | `0.0` | `50.0` | Vitesse vibratoire toujours $\ge 0$. Norme ISO 10816 : zone critique à partir de 20 mm/s, rupture mécanique vers 50 mm/s. |
| `load_pct` | `float` | `0.0` | `120.0` | Charge positive non nulle. Les moteurs acceptent une surcharge temporaire (facteur de service de 115 % à 120 %) avant déclenchement. |
| `runtime_hours` | `float` | `0.0` | `100000.0` | Heures cumulées positives. 100 000 h équivaut à 11 ans d'exploitation continue jour et nuit, durée limite d'un équipement industriel. |

Après avoir écrit `schemas.py` seul, que donne `python -m pytest`, et quel est le message d'erreur des tests qui échouent ? Pourquoi est-ce un bon signe ?

```
FAILED tests/test_api.py::test_predict_returns_probability - NotImplementedError
FAILED tests/test_api.py::test_high_risk_reading_raises_alert - NotImplementedError
FAILED tests/test_api.py::test_503_when_model_missing - NotImplementedError
=================== 3 failed, 10 passed, 1 warning in 6.79s ===================
```

**Pourquoi c'est un bon signe :**  
L'erreur n'est plus un refus de validation 422 ! Cela prouve que le schéma Pydantic accepte désormais les relevés valides, qui traversent la couche de validation et parviennent avec succès jusqu'au corps de la fonction `predict()`, où ils butent sur le `raise NotImplementedError` prévu avant écriture.

---

## 3. La fonction `predict()` (`maintai/api/main.py`)

Votre code :

```python
@router.post("/predict", response_model=PredictionOut)
def predict(reading: SensorReading) -> PredictionOut:
    """Reçoit un relevé de capteurs validé et renvoie l'estimation du risque de panne."""
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle absent. Entraînez d'abord le modèle avec python -m maintai.train",
        )
    result = predictor.predict(reading.model_dump())
    return PredictionOut(**result)
```

Pourquoi répondre **503** et pas 500 quand le modèle manque ?  
**Réponse :**  
Le code HTTP **500 (Internal Server Error)** signale un bug inattendu, une exception non gérée ou un crash dans le code de l'API.  
Le code HTTP **503 (Service Unavailable)** signifie que l'API fonctionne normalement, mais qu'une dépendance indispensable (ici le modèle `model.joblib`) n'est pas encore prête ou déployée. Cela indique clairement aux équipes d'exploitation que le service est temporairement indisponible et qu'il faut entraîner le modèle, sans polluer les alertes de bugs de l'application.

Pourquoi le modèle est-il chargé **une seule fois**, au démarrage, et pas à chaque requête ?  
**Réponse :**  
Désérialiser un modèle scikit-learn avec `joblib.load()` nécessite des lectures disques et une allocation mémoire coûteuses (plusieurs dizaines de millisecondes par appel). Charger le modèle à chaque requête multiplierait par 100 le temps de réponse et saturerait le serveur en cas de fort trafic. Grâce au cycle de vie `lifespan`, le modèle reste chargé en mémoire vive (RAM) et répond à chaque requête en quelques millisecondes seulement.

---

## 4. Les tests

Dernière ligne de `python -m pytest` à la fin du TP :

```
======================== 13 passed, 1 warning in 3.68s ========================
```

---

## 5. L'API en marche

Après `python -m maintai.dataset` et `python -m maintai.train`, lancez `uvicorn maintai.api.main:app --reload`, puis envoyez ces requêtes depuis `/docs` (ou avec `curl.exe`).

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---:|---|
| `GET /health` | **200** | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict` avec `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | **200** | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "2026-10-28T10:11:42Z"}` |
| `POST /v1/predict` avec une température de 500 | **422** | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500.0, "ctx": {"le": 150.0}}]}` |
| `POST /v1/predicte` (faute de frappe dans l'adresse) | **404** | `{"detail": "Not Found"}` |

Dans `/docs`, où voit-on les bornes que vous avez choisies ?  
**Réponse :**  
Dans `/docs` (Swagger UI), les bornes sont visibles :
1. Dans la documentation de la route `POST /v1/predict`, en ouvrant l'onglet **Request Body** > **Schema** : chaque champ affiche ses contraintes (`>= -40`, `<= 150`, etc.) ;
2. Tout en bas de la page sous la rubrique **Schemas**, en déroulant le composant `SensorReading`.

---

## 6. Questions de compréhension

1. **REST et FastAPI : quelle est la différence ?**  
   *REST* est un style architectural standardisé pour concevoir des services web (utilisation des méthodes HTTP GET/POST, URL claires représentant des ressources, codes de statut standards, format JSON). *FastAPI* est le framework Python moderne permettant d'implémenter concrètement une telle API avec validation de types automatique et génération de documentation.

2. **Le schéma Pydantic sert à trois choses. Lesquelles ?**  
   - **Valider :** Vérifie le type et les bornes des données reçues avant d'exécuter la fonction (renvoie 422 si invalide) ;
   - **Documenter :** Génère automatiquement la spécification OpenAPI et l'interface interactive `/docs` ;
   - **Typage Python :** Convertit le JSON entrant en un objet Python manipulable en toute sécurité (`reading.model_dump()`).

3. **Dans `http://localhost:8000/v1/predict`, que désignent `localhost`, `8000` et `/v1/predict` ?**  
   - `localhost` : la machine hôte elle-même (adresse 127.0.0.1) ;
   - `8000` : le numéro de port réseau sur lequel le serveur uvicorn écoute les requêtes ;
   - `/v1/predict` : la route de l'application (`/v1` étant la version de l'API et `/predict` l'action de prédiction).

4. **Pourquoi `/v1` dans l'adresse ?**  
   Le préfixe `/v1` permet de versionner l'API. Si de nouvelles fonctionnalités ou des ruptures de contrat apparaissent plus tard (ex: ajout de nouveaux capteurs obligatoires), on pourra déployer `/v2` sans casser les applications clientes existantes qui consomment encore `/v1`.

5. **Dans la commande `uvicorn maintai.api.main:app`, que désignent `maintai.api.main` et `app` ?**  
   - `maintai.api.main` : le chemin d'import Python désignant le fichier `maintai/api/main.py` ;
   - `app` : l'objet variable `app = FastAPI()` instancié dans ce fichier.

---

## 7. Le rendu Git

- **Branche de travail :** `tp1`
- **Lien de la pull request :** `https://github.com/mon-groupe/maintai/pull/1`
- **Le tag `tp1` existe sur GitHub :** oui
- **Qui a relu la pull request, et quel commentaire a-t-il laissé ?**  
  *Relecteur :* CHAIMAA HADDAD (relue pour KENZA ELAIATI)  
  *Commentaire :* « Code validé : les 13 tests passent avec succès, les bornes physiques de l'ADR 002 sont cohérentes avec la réalité industrielle d'un moteur, et l'API renvoie bien 503 en l'absence du modèle. Prêt pour fusion sur main. »

---

## 8. Ce qui reste flou
Comment orchestrer la mise à jour à chaud d'un modèle en production sans redémarrer le serveur uvicorn (par exemple via un rechargement déclenché par un webhook ou une tâche de fond périodique).
