# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI
**Groupe :** (Ton groupe) . **Membres :** Abderrahmane Sbaii . **Date :** 04/11/2026

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| `{"vibration_mm_s": 6.1, "load_pct": 85}` | champ manquant | 422 | 422 |
| `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 250, "runtime_hours": 15000}` | valeur absurde | 422 | 422 |
| `{"temperature_c": "chaud", "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000}` | texte au lieu d'un nombre | 422 | 422 |
| `{"temperature_c": 72.5, "vibration_mm_s": 6.1, "load_pct": 85, "runtime_hours": 15000, "champ_secret": 12}` | champ en trop | 422 | 200 |
| `POST /v1/route_inconnue` | mauvaise route | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?
Oui, pour le "champ en trop". J'avais prévu une erreur 422, mais j'ai obtenu 200. Pourquoi ? Parce que FastAPI (Pydantic) ignore simplement les champs supplémentaires par défaut, il ne bloque pas la requête.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :
```text
=========================== 18 passed in 0.15s ===========================

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

Il sert à exécuter une même fonction de test plusieurs fois avec des données différentes. pytest compte 5 tests pour notre fonction, car nous lui avons fourni une liste de 5 cas de requêtes refusées. Il lance la fonction une fois par cas de la liste[cite: 3].

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff check . lit le code sans l'exécuter pour trouver les problèmes de style ou les erreurs de syntaxe (comme un import inutile). 
python -m pytest exécute le code pour vérifier qu'il fait ce qui est attendu (que les tests passent).

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
========================= 2 failed, 16 passed in 0.18s =========================

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Les deux tests qui échouent sont ceux qui essaient d'appeler l'API sans clé et avec une fausse clé. Au lieu de recevoir une erreur 401 (accès refusé), ils reçoivent un code 200 (succès) car la sécurité n'est pas encore mise en place.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    expected_key = settings.api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API serveur non configurée.",
        )

    if x_api_key is None or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante ou invalide.",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(
    prefix="/v1",
    dependencies=[Depends(require_api_key)]
)
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Il y a toujours 2 tests qui échouent. Pourquoi ? Parce que la fonction de vérification existe, mais rien ne l'appelle encore : le routeur n'est pas protégé.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
=========================== 18 passed in 0.16s ===========================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status":"ok","model_loaded":true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail":"Clé API manquante ou invalide."}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail":"Clé API manquante ou invalide."}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability":0.12,"alert":false}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail":"Clé API manquante ou invalide."}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], ...}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Parce que l'API vérifie les conditions en série, l'une après l'autre. Elle vérifie d'abord la clé API. Sans clé, elle bloque la requête immédiatement avec une erreur 401, sans même regarder les données envoyées[cite: 5]. Avec la bonne clé, elle passe à l'étape suivante, analyse les données, voit que 500 °C dépasse le maximum autorisé, et renvoie donc une erreur 422 (données invalides).

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

J'obtiens le code 500 (Internal Server Error)[cite: 7]. Ce n'est pas 401 car notre code dans `security.py` vérifie d'abord si le serveur lui-même possède une clé configurée[cite: 7]. Sans le fichier `.env`, la variable de la clé serveur est vide (`None`)[cite: 7]. Le code déclenche donc une erreur 500 pour signaler ce problème de configuration interne, avant même de comparer la clé transmise par le client[cite: 7].

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
(collez ici)
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | Alerte ! Probabilité : 94.8% |
| 500 °C, bonne clé | Erreur 422 : La température dépasse la valeur maximale autorisée. |
| relevé normal, fausse clé | Erreur 401 : Clé API manquante ou invalide. |



**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche une erreur d'API injoignable ou bloquée par CORS[cite: 23]. La console (F12) affiche une erreur CORS explicite indiquant que l'en-tête "Access-Control-Allow-Origin" est absent pour l'origine "http://localhost:5501".

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

Parce que CORS est une règle de sécurité propre au navigateur web, destinée à protéger l'utilisateur[cite: 20]. `curl.exe` n'est pas un navigateur web et n'applique pas les restrictions CORS, il transmet simplement la requête HTTP et la clé API[cite: 20].

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

Sans headers=HEADERS, 4 tests échouent car ils reçoivent le code 401 (au lieu de 422) à cause de l'absence de clé API. 
Le seul cas qui passe quand même est le cas 5 (la mauvaise route /v1/predicte), car le contrôle de la route (404) s'effectue avant le contrôle de la clé API (401) dans l'ordre des vérifications de l'API[cite: 18].

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
============================== 23 passed in 4.12s ==============================
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   401 vs 422 : Le code 401 (Unauthorized) signifie que l'authentification a échoué (clé API absente ou invalide). Le code 422 (Unprocessable Entity) indique que l'authentification est valide, mais que les données envoyées dans le corps de la requête ne respectent pas le schéma Pydantic (valeurs absurdes, types incorrects, champs manquants).

   401 vs 403 : Le 401 indique que l'utilisateur n'est pas authentifié (il ne s'est pas identifié). Le 403 (Forbidden) indique que l'utilisateur est authentifié mais qu'il n'a pas les droits nécessaires pour effectuer l'action.

2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   La clé n'est pas dans le code pour éviter qu'elle ne se retrouve définitivement dans l'historique public de GitHub.   .env contient la vraie clé secrète de l'application et n'est jamais commité.   .env.example contient la structure avec de fausses valeurs pour indiquer quoi configurer, et il est commité sur Git. 

3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Parce qu'une URL est enregistrée partout (dans les journaux du serveur, l'historique du navigateur ou les caches). Transmettre la clé dans un en-tête HTTP (X-API-Key) est beaucoup plus sécurisé.

4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
  secrets.compare_digest effectue une comparaison en temps constant, ce qui protège contre les attaques par analyse temporelle (timing attacks). Un opérateur == s'arrête au premier caractère faux, ce qui permettrait à un attaquant de deviner la clé en mesurant le temps de réponse.

5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est définie par la combinaison d'un schéma (protocole), d'un domaine et d'un port.

 Non, elles ne sont pas de la même origine car leurs ports diffèrent (5500 vs 8000).

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui 
- `git status` avant le commit : le fichier `.env` apparaissait-il ?  non
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  Relu par Abderrahmane Sbaii :« Tout est parfait, les 23 tests passent et la sécurité CORS fonctionne correctement.»

## 9. Ce qui reste flou
Rien ne reste flou ; la mise en place de la clé API, la gestion du fichier `.env`, le filtrage CORS et les tests unitaires avec Pytest ont été bien compris et testés avec succès.
