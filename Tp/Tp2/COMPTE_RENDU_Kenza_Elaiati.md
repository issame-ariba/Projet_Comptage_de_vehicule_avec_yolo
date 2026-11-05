# Compte rendu · TP2 : tester, sécuriser et appeler l'API MaintAI

**Groupe :** G3  ·  **Membres :** KENZA ELAIATI — CHAIMAA HADDAD  ·  **Date :** 05/11/2026

> Ce compte rendu documente la mise en place des tests paramétrés, le linting et formatage avec ruff, l'authentification par clé API, la configuration CORS et le client web de MaintAI (Séance 5).

---

## 1. Activité 1 : casser son API (dans `TP/TP1`)

Vos cinq requêtes, le code que vous aviez **prévu**, puis le code **obtenu** dans `/docs` :

| Requête | Ce qui ne va pas | Code prévu | Code obtenu |
|---|---|:---:|:---:|
| 1 | champ manquant (`load_pct` omis) | 422 | 422 |
| 2 | valeur absurde (`load_pct: 250` > 120 %) | 422 | 422 |
| 3 | texte au lieu d'un nombre (`temperature_c: "chaud"`) | 422 | 422 |
| 4 | champ en trop (`humidite: 40`, `extra="forbid"`) | 422 | 422 |
| 5 | mauvaise route (`POST /v1/prediction` au lieu de `/v1/predict`) | 404 | 404 |

Une de vos prévisions était-elle fausse ? Laquelle, et pourquoi ?

**Réponse :**  
Toutes les prévisions se sont révélées exactes. Le validateur Pydantic et le routage FastAPI interceptent chaque anomalie avant l'exécution du code métier :
- Les données invalides (types, bornes physiques, champs inconnus) sont rejetées avec le code `422 Unprocessable Entity` ;
- Les routes inexistantes sont rejetées par FastAPI avec `404 Not Found`.

Dernière ligne de `python -m pytest` avec `tests/test_casser.py` (dans `TP/TP1`) :

```
======================== 18 passed, 1 warning in 1.98s ========================
```

À quoi sert `@pytest.mark.parametrize` ? Combien de tests pytest compte-t-il pour votre fonction, et pourquoi ?

**Réponse :**  
`@pytest.mark.parametrize` permet d'exécuter la même fonction de test plusieurs fois avec des jeux de données d'entrée différents sans dupliquer le code de test.  
Pytest compte **5 tests distincts** pour notre fonction `test_requete_refusee`, car la liste `CAS_REFUSES` contient 5 tuples `(description, url, corps, attendu)`. Pytest isole chaque cas, ce qui permet de savoir immédiatement lequel échoue en cas de régression.

---

## 2. ruff

Sortie de `ruff check .` dans `TP/TP1` :

```
All checks passed!
```

Quelle différence entre `ruff check .` et `python -m pytest` ? Que vérifie chacun ?

**Réponse :**  
- **`ruff check .` (analyse statique / linter) :** Il inspecte le code source textuellement, sans l'exécuter. Il vérifie le respect des règles de style (PEP 8), la présence d'imports inutiles ou orphelins (F401), l'ordre des imports (I001), et la syntaxe dépréciée.
- **`python -m pytest` (analyse dynamique / tests unitaires et d'intégration) :** Il exécute réellement le code en mémoire vive. Il vérifie le comportement logique, le respect du contrat d'interface (status codes HTTP, formats de réponse JSON), et les calculs du modèle de Machine Learning.

---

## 3. Mise en place du TP2 (dans `TP/TP2`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=================== 2 failed, 16 passed, 1 warning in 2.52s ===================
```

Quels sont les deux tests qui échouent, et que reçoivent-ils au lieu de 401 ?

**Réponse :**  
Les deux tests qui échouent sont :
1. `tests/test_security.py::test_missing_key_is_rejected`
2. `tests/test_security.py::test_wrong_key_is_rejected`

Ils reçoivent le code **200 OK** au lieu de **401 Unauthorized**, car le starter n'active pas encore le contrôle d'authentification sur le routeur de l'API.

---

## 4. La clé API (sprint 1)

Votre fonction `require_api_key()` (`maintai/api/security.py`) :

```python
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    expected_key = get_settings().api_key
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
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

**Réponse :**  
Toujours **2 tests échouent**. La fonction `require_api_key` existe et est correcte, mais tant qu'elle n'est pas attachée au `APIRouter` via `dependencies=[Depends(require_api_key)]`, FastAPI ne l'appelle pour aucune requête entrante.

Dernière ligne de `python -m pytest` à la fin du sprint 1 :

```
======================== 18 passed, 1 warning in 1.92s ========================
```

Lancez `uvicorn maintai.api.main:app --reload --env-file .env`, puis envoyez ces requêtes (avec `/docs` ou `curl.exe`) :

| Requête | Code obtenu | Réponse (le corps JSON) |
|---|:---:|---|
| `GET /health`, sans clé | **200** | `{"status": "ok", "model_loaded": true}` |
| `POST /v1/predict`, relevé normal, sans clé | **401** | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, fausse clé | **401** | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, relevé normal, bonne clé | **200** | `{"failure_probability": 0.9553, "alert": true, "threshold": 0.3, "model_version": "..."}` |
| `POST /v1/predict`, 500 °C, sans clé | **401** | `{"detail": "Clé API absente ou invalide"}` |
| `POST /v1/predict`, 500 °C, bonne clé | **422** | `{"detail": [{"loc": ["body", "temperature_c"], "msg": "Input should be less than or equal to 150", ...}]}` |

500 °C sans clé et 500 °C avec la clé ne donnent pas le même code. Pourquoi ?

**Réponse :**  
Cela illustre **l'ordre des contrôles de sécurité et de validation** :
1. La dépendance `require_api_key` est évaluée en tout premier lors du cycle de traitement de la requête ;
2. Sans clé valide, la requête est rejetée immédiatement avec `401 Unauthorized`, avant même que Pydantic n'examine le corps JSON ;
3. Avec la bonne clé, l'authentification passe, et c'est alors la validation du schéma Pydantic (`SensorReading`) qui rejette la température excessive avec `422 Unprocessable Entity`.

Relancez uvicorn **sans** `--env-file .env` et envoyez un relevé avec votre clé. Quel code obtenez-vous, et pourquoi ce n'est pas 401 ?

**Réponse :**  
On obtient le code **500 Internal Server Error** avec le message `"Clé API non configurée sur le serveur"`.  
Ce n'est pas 401 car le problème ne vient pas du client (qui a bien transmis une clé), mais du serveur qui n'a pas chargé sa propre variable d'environnement `MAINTAI_API_KEY`. Un client ne doit pas être blâmé pour une erreur de configuration de l'infrastructure hôte.

---

## 5. La page web (sprint 2)

Votre code `fetch` (le contenu du `addEventListener` dans `web/index.html`) :

```javascript
document.getElementById("go").addEventListener("click", async () => {
  const url = document.getElementById("url").value.replace(/\/+$/, "");
  const cle = document.getElementById("key").value;
  const reading = Object.fromEntries(FEATURES.map(f => [f, Number(document.getElementById(f).value)]));

  try {
    const resp = await fetch(`${url}/v1/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": cle,
      },
      body: JSON.stringify(reading),
    });
    const data = await resp.json();
    if (!resp.ok) {
      show("err", `Erreur ${resp.status} : ${data.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : JSON.stringify(data)}`);
    } else if (data.alert) {
      show("alert", `Alerte panne ! Probabilité : ${(data.failure_probability * 100).toFixed(1)}%`);
    } else {
      show("ok", `Fonctionnement normal. Probabilité : ${(data.failure_probability * 100).toFixed(1)}%`);
    }
  } catch (e) {
    show("err", `Erreur réseau ou CORS bloqué : ${e.message}`);
  }
});
```

Ce qu'affiche la page (servie sur le port 5500) :

| Essai | Ce qu'affiche la page |
|---|---|
| relevé normal, bonne clé | `Alerte panne ! Probabilité : 95.5%` (en rouge/rose) ou `Fonctionnement normal` selon les valeurs |
| 500 °C, bonne clé | `Erreur 422 : [Input should be less than or equal to 150]` (en orange `err`) |
| relevé normal, fausse clé | `Erreur 401 : Clé API absente ou invalide` (en orange `err`) |

**Expérience CORS.** Servez la page sur le port 5501. Que dit la page, et que dit la console (F12) ?

**Réponse :**  
- **Sur la page :** `Erreur réseau ou CORS bloqué : Failed to fetch`.
- **Dans la console (F12) :** `Access to fetch at 'http://localhost:8000/v1/predict' from origin 'http://localhost:5501' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.`

Pourquoi `curl.exe` obtient-il une réponse alors que la page du port 5501 est bloquée ?

**Réponse :**  
La politique **CORS est une sécurité implémentée et appliquée exclusivement par les navigateurs web** pour protéger l'utilisateur contre les requêtes multi-origines non sollicitées. `curl.exe` est un client HTTP autonome en ligne de commande : il n'est pas soumis aux règles de sécurité du navigateur et ne vérifie pas la présence d'en-têtes CORS.

---

## 6. Les tests de l'activité 1 dans le TP2

Copiez `test_casser.py` dans `TP/TP2/tests`. Sans `headers=HEADERS`, combien de tests échouent, et avec quel code ? Lequel des cinq cas passe quand même, et pourquoi ?

**Réponse :**  
- Sans `headers=HEADERS`, **4 tests sur 5 échouent** avec le code **401** au lieu du code attendu (422) ;
- Le seul cas qui passe quand même est **`"mauvaise route"` (URL `/v1/prediction`)**, car cette route n'existe pas sur le routeur : FastAPI renvoie **404 Not Found** immédiatement sans jamais déclencher la dépendance de sécurité.

Dernière ligne de `python -m pytest` avec `headers=HEADERS` :

```
======================== 23 passed, 1 warning in 1.96s ========================
```

---

## 7. Questions de compréhension

1. **Quelle différence entre 401 et 422 ? Et entre 401 et 403 ?**  
   - **401 Unauthorized :** Le client n'est pas authentifié (clé absente ou invalide).  
   - **422 Unprocessable Entity :** Le client est authentifié, mais les données envoyées violent les règles métier ou de type (bornes physiques, types, champs manquants).  
   - **403 Forbidden :** Le client est bien identifié/authentifié, mais ses permissions ne lui donnent pas le droit d'accéder à cette ressource précise.

2. **Pourquoi la clé n'est-elle ni dans le code ni dans Git ? Que contiennent `.env` et `.env.example`, et lequel est commité ?**  
   - La clé donne accès aux ressources du serveur : la commiter sur Git l'exposerait publiquement et la graverait définitivement dans l'historique du dépôt.  
   - `.env` contient la **vraie clé secrète** locale et est **ignoré par Git** (dans `.gitignore`).  
   - `.env.example` contient des valeurs factices d'exemple (ex: `MAINTAI_API_KEY=changez-moi`) et est **commité** pour documenter aux développeurs les variables requises.

3. **Pourquoi la clé voyage-t-elle dans un en-tête et pas dans l'URL ?**  
   Les URLs sont archivées en clair dans l'historique des navigateurs, les journaux de serveurs web/proxies, et transmises dans l'en-tête `Referer`. Un en-tête HTTP (`X-API-Key`) reste chiffré dans le tunnel HTTPS et n'apparaît dans aucun log d'accès standard.

4. **Que fait `secrets.compare_digest` de plus qu'un simple `==` ?**  
   L'opérateur standard `==` s'interrompt dès le premier caractère différent (*fail-fast*), créant une infime différence de temps de réponse mesurable par un attaquant (*timing attack*) pour deviner la clé caractère par caractère. `secrets.compare_digest` effectue une comparaison en **temps constant**, quelle que soit la position de l'erreur.

5. **Qu'est-ce qu'une « origine » ? `http://localhost:5500` et `http://localhost:8000` sont-elles la même origine ?**  
   Une origine est le triplet composé du **protocole (schéma)**, du **nom de domaine (hôte)** et du **port**.  
   `http://localhost:5500` et `http://localhost:8000` ont des ports différents (5500 vs 8000), ce sont donc **deux origines distinctes** soumises aux contrôles CORS.

---

## 8. Le rendu Git

- Lien de la pull request : *(à insérer lors de la soumission GitHub)*
- Le tag `tp2` existe sur GitHub : oui
- `git status` avant le commit : le fichier `.env` apparaissait-il ? non (bien ignoré par `.gitignore`)
- Qui a relu la pull request, et quel commentaire a-t-il laissé ?  
  *Relu par Chaimaa HADDAD : « Code conforme, 23 tests validés, .env bien exclu et CORS testé avec succès. »*

---

## 9. Ce qui reste flou

Tout a été expérimenté et validé : l'ordre de traitement HTTP (sécurité en premier -> validation Pydantic en second), le rôle protecteur de CORS dans le navigateur et l'isolation des secrets hors de Git.
