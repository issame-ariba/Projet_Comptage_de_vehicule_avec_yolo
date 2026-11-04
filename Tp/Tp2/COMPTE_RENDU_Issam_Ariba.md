# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :**G1  ·  **Membres :** ISSAM ARIBA ·  **Date :** 04/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP2.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---



## 1. Activité 1 : casser son API (dans `TP/TP1`)

**Vos cinq requêtes, le code que vous aviez prévu, puis le code obtenu :**

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|---|---|
| 1. `{"temperature_c": 60.0, "vibration_mm_s": 2.0, "runtime_hours": 5000}` | Le champ obligatoire `load_pct` est manquant. | 422 | 422 |
| 2. `{"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 250, "runtime_hours": 5000}` | La charge `250 %` dépasse la limite maximale autorisée de `100 %`. | 422 | 422 |
| 3. `{"temperature_c": "chaud", "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}` | La température contient du texte au lieu d'un nombre. | 422 | 422 |
| 4. `{"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000, "pression": 20}` | Le champ supplémentaire `pression` n'est pas autorisé. | 422 | 422 |
| 5. `POST /v1/unknown` | La route demandée n'existe pas dans l'API. | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

Aucune de nos prévisions n'était fausse. Les cinq requêtes ont retourné les codes HTTP attendus. Les quatre premières requêtes ont été refusées avec le code **422**, car elles contenaient des données invalides (champ obligatoire manquant, valeur hors limites, mauvais type de donnée ou champ supplémentaire non autorisé). La cinquième requête a retourné le code **404**, car la route demandée n'existe pas dans l'API.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
19 passed, 1 warning in 2.40s
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

Le décorateur @pytest.mark.parametrize permet d'exécuter une même fonction de test plusieurs fois avec différentes données d'entrée et différents résultats attendus. Il évite de créer une fonction de test distincte pour chaque cas.

pytest compte **5 tests** pour notre fonction `test_requete_refusee` : il l'exécute une fois par ligne de la liste `CAS_REFUSES`, et nous avons cinq cas. Chaque cas apparaît sous son propre nom dans le rapport (`python -m pytest -v`), par exemple `test_requete_refusee[champ manquant-...]`.

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

ruff check . vérifie la qualité du code Python. Il détecte notamment les problèmes de style, les imports inutilisés et certaines erreurs potentielles.

python -m pytest exécute les tests automatisés pour vérifier que les fonctionnalités du projet fonctionnent correctement.

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
2 failed, 16 passed, 1 warning
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

Les deux tests de `tests/test_security.py` qui échouent sont `test_missing_key_is_rejected` (requête sans en-tête `X-API-Key`) et `test_wrong_key_is_rejected` (requête avec une fausse clé). Ils reçoivent **200** au lieu de 401 : dans le starter, la clé n'est pas encore vérifiée, donc l'API répond normalement à tout le monde.

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""

    expected_key = get_settings().api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API serveur non configurée",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
```

Votre ligne `router = ...` dans `maintai/api/main.py` :

```python
router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
```

Après avoir écrit `security.py` seul (sans toucher au router), combien de tests échouent ? Pourquoi ?

Toujours **2 tests** échouent (les deux mêmes). La fonction `require_api_key()` existe, mais aucune route ne l'appelle : tant qu'elle n'est pas ajoutée comme dépendance du router, `/v1/predict` ne vérifie pas la clé et répond encore 200.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
18 passed, 1 warning in 2.88s
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|---|---|
| `GET /health`, sans clé | 200 | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict`, relevé normal, sans clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | 200 | `{"failure_probability": 0.9475, "alert": true, "threshold": 0.3, "model_version": "2026-11-04T17:59:30Z"}` |
| `POST /v1/predict`, 500 °C, sans clé | 401 | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | 422 | `{"detail": [{"type": "less_than_equal", "loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", "input": 500, "ctx": {"le": 150.0}}]}` |

Relevé normal utilisé : `{"temperature_c": 72, "vibration_mm_s": 6, "load_pct": 85, "runtime_hours": 15000}` (les valeurs par défaut de la page web).

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

Les contrôles se font dans l'ordre : route, puis clé, puis données, puis modèle ; le premier qui échoue donne la réponse. Sans clé, la requête est arrêtée au contrôle de la clé (**401**) : l'API ne regarde même pas les données. Avec la bonne clé, la requête passe ce contrôle, puis la validation du schéma Pydantic refuse 500 °C (maximum 150 °C) : **422**.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

On obtient **500** : `{"detail": "Clé API serveur non configurée"}`. Sans `--env-file .env`, la variable `MAINTAI_API_KEY` n'est pas chargée, donc `get_settings().api_key` vaut `None`. Le client n'est pas en faute (sa clé est peut-être juste) : c'est une erreur de configuration du serveur, donc une erreur 5xx et non 401.

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));
  const url = document.getElementById("url").value.trim().replace(/\/+$/, "");
  const cle = document.getElementById("key").value;
  const adresse = url + "/v1/predict";

  try {
    const resp = await fetch(adresse, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify(reading),           // l'objet devient du texte JSON
    });
    const data = await resp.json();            // la réponse, en objet

    if (!resp.ok) {                            // 401, 422, 503...
      const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      show("err", `Erreur ${resp.status} : ${detail}`);
      return;
    }

    const pct = (data.failure_probability * 100).toFixed(1);
    if (data.alert) {
      show("alert", `ALERTE : probabilité de panne ${pct} %`);
    } else {
      show("ok", `Normal : probabilité de panne ${pct} %`);
    }
  } catch (e) {                                // API arrêtée, ou CORS qui bloque
    show("err", `API injoignable (arrêtée ou bloquée par CORS) : ${e.message}`);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | `ALERTE : probabilité de panne 94.8 %` (fond rouge : la probabilité dépasse le seuil 0,3) |
| 500 °C, bonne clé | `Erreur 422 : [{"type":"less_than_equal","loc":["body","temperature_c"],"msg":"Input should be less than or equal to 150",...}]` |
| relevé normal, fausse clé | `Erreur 401 : Clé API absente ou invalide` |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

La page affiche `API injoignable (arrêtée ou bloquée par CORS) : Failed to fetch`. La console indique que la requête vers `http://localhost:8000/v1/predict` depuis l'origine `http://localhost:5501` a été bloquée par la politique CORS : la réponse à la requête préliminaire `OPTIONS` ne contient pas l'en-tête `Access-Control-Allow-Origin`. L'API répond à cette requête `OPTIONS` par `400 Disallowed CORS origin`, car `http://localhost:5501` n'est pas dans `MAINTAI_CORS_ORIGINS`.

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

CORS est une règle appliquée par le **navigateur**, pas par l'API. C'est le navigateur qui envoie la requête `OPTIONS` (« puis-je ? ») et qui bloque la réponse si l'origine n'est pas autorisée. Il protège ainsi l'utilisateur contre une page qui utiliserait son navigateur. `curl.exe` n'est pas un navigateur : il n'a pas d'origine et ne fait aucun contrôle CORS, il envoie directement la requête. Pour lui, seule la clé API compte ; c'est pour cela que la clé reste indispensable.

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

**4 tests échouent** : les quatre cas qui attendaient 422 (champ manquant, valeur absurde, texte au lieu d'un nombre, champ en trop) reçoivent **401**, car la clé est vérifiée avant les données. Le cas **« mauvaise route »** (`POST /v1/unknown`, 404 attendu) passe quand même : la route est contrôlée en premier. Comme elle n'existe pas, `require_api_key` n'est jamais appelée et l'API répond 404.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
23 passed, 1 warning
```

## 7. Questions de compréhension

1. Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?
   **401** (Unauthorized) : l'API ne sait pas qui appelle, la clé est absente ou invalide (authentification). **422** (Unprocessable Entity) : l'appelant est accepté, mais les données envoyées ne respectent pas le schéma (champ manquant, valeur hors bornes, mauvais type). **403** (Forbidden) : l'appelant est bien identifié, mais il n'a pas le droit de faire cette action (autorisation). En résumé : 401 = « qui es-tu ? », 403 = « je sais qui tu es, mais c'est interdit ».
2. Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?
   Une clé dans le code finit sur GitHub, et une clé commitée une seule fois reste dans l'historique de Git, même si on supprime le fichier ensuite : toute personne ayant accès au dépôt pourrait l'utiliser. `.env` contient la vraie clé et les origines autorisées (`MAINTAI_API_KEY=...`, `MAINTAI_CORS_ORIGINS=...`). Il est exclu par `.gitignore` et **n'est pas commité**. `.env.example` contient les mêmes variables avec une fausse valeur (`changez-moi`) : il **est commité** et indique quoi configurer.
3. Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?
   Une URL est enregistrée partout : journaux du serveur et des proxys, historique du navigateur, favoris, en-tête `Referer`. Une clé dans l'URL serait donc copiée dans de nombreux endroits. Un en-tête (`X-API-Key`) n'apparaît ni dans la barre d'adresse ni dans ces journaux.
4. Que fait `secrets.compare_digest` de plus qu'un simple `==` ?
   `==` s'arrête au premier caractère différent : plus la clé proposée a de caractères justes au début, plus la comparaison dure longtemps. En mesurant le temps de réponse, un attaquant pourrait deviner la clé caractère par caractère (attaque temporelle). `secrets.compare_digest` compare en **temps constant**, quel que soit le nombre de caractères justes : la durée ne trahit rien.
5. Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?
   Une origine est le triplet **schéma + domaine + port** (par exemple `http` + `localhost` + `5500`). `http://localhost:5500` et `http://localhost:8000` ne sont **pas** la même origine, car le port est différent. C'est pourquoi l'API doit autoriser explicitement (CORS) la page servie sur le port 5500 pour qu'elle puisse appeler l'API sur le port 8000.

## 8. Le rendu Git

- Lien de la pull request : …
- Le tag `tp2` existe sur GitHub : oui / non
- `git status` avant le commit : le fichier `.env` apparaissait-il ? **non** (il est exclu par la ligne `.env` du `.gitignore` de `TP/TP2`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?
  …

## 9. Ce qui reste flou

- Comment gérer plusieurs clés API (une par client) et pouvoir en révoquer une sans changer celle des autres.
- Comment la clé et les origines CORS seront configurées en production (séance 8), sans fichier `.env` sur le serveur.
- Dans la page web, la clé est saisie dans le navigateur : nous ne voyons pas encore comment protéger une clé dans une vraie application web publique.
