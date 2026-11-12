# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** 5eme IADATA G1  ·  **Membres :** Abderrahmane Sbaii …  ·  **Date :** 11/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
5 failed, 18 passed, 1 warning
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

- `tests/test_client.py` (3 tests) : `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict`. La méthode `predict` du starter ne fait que lever cette exception.
- `tests/test_ui.py` (2 tests) : les assertions échouent, car la page n'affiche encore que les messages `st.info` des TODO. Il n'y a ni indicateur dans l'onglet « Données », ni probabilité dans l'onglet « Prédiction ».

Les 18 autres tests (API, sécurité, modèle, hérités du TP2) passent.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "...\maintai-starter-tp3\ui\app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

Python cherche les modules dans une liste de dossiers (`sys.path`), et cette liste dépend de la façon de lancer le programme. `streamlit run ui/app.py` y ajoute le dossier du script, `ui/`, où il n'y a pas de dossier `maintai`. `python -m streamlit ...` ajoute en plus le dossier courant, c'est-à-dire la racine du projet, qui contient `maintai/`. L'import réussit donc. Le TP4 règlera le problème pour de bon avec `pip install -e .`.

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
    # 1. Trois indicateurs côte à côte (le premier est le nombre de relevés, lu par le test)
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")  # moyenne de 0/1 = part de pannes
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")

    # 2. Choix de la variable
    variable = st.selectbox("Variable", FEATURES)

    # 3. Taux de panne par tranche de la variable
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True).failure.mean()
    taux.index = [round(i.mid, 1) for i in taux.index]  # milieu de tranche, en nombre
    taux.index.name = variable
    st.subheader(f"Taux de panne par tranche de {variable}")
    st.bar_chart(taux)

    # 4. Nuage température / vibration, coloré par panne (« oui / non » plutôt que 0 / 1)
    nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
    st.subheader("Température et vibration")
    st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6 % |
| Température moyenne | 59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente avec la vibration. Il est faible dans les tranches de vibration basses, puis monte nettement dans les tranches hautes. Une machine qui vibre beaucoup tombe donc plus souvent en panne. Les étiquettes des barres sont des nombres (le milieu de chaque tranche), donc les tranches restent dans l'ordre croissant.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Au chargement de la page, `relance` s'affiche une première fois dans le terminal de Streamlit (pas dans la page). Il s'affiche de nouveau à chaque changement de la liste déroulante et à chaque clic sur « Prédire ». En revanche, déplacer un curseur du formulaire n'affiche rien : les curseurs sont dans `st.form`, qui ne relance le script qu'au clic sur le bouton. Cela montre qu'à chaque interaction, Streamlit réexécute **tout** le script `ui/app.py`, de la première à la dernière ligne, avec les nouvelles valeurs des widgets, puis renvoie la nouvelle page. `st.form` sert justement à regrouper plusieurs saisies en une seule relance.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Puisque tout le script est relancé à chaque clic, `pd.read_csv` relirait le fichier de 5000 lignes à chaque interaction. `@st.cache_data` garde en mémoire le résultat de `charger(path)` pour un même argument : le CSV est lu une seule fois, et les relances suivantes réutilisent le DataFrame déjà chargé. La page reste rapide.

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
    def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        # En-tête de la clé, seulement si une clé est donnée (None ou "" : pas d'en-tête)
        headers = {"X-API-Key": self.api_key} if self.api_key else {}

        # self.http (et non httpx.post) : vrai client ou TestClient des tests ; json= convertit en JSON
        r = self.http.post("/v1/predict", json=reading, headers=headers)

        # L'API a répondu mais a refusé (401, 422, 503...) : on lève APIError avec le "detail"
        if r.status_code != 200:
            try:
                detail = r.json().get("detail")
            except ValueError:  # corps qui n'est pas du JSON
                detail = r.text
            raise APIError(r.status_code, detail)

        # Succès : {"failure_probability": ..., "alert": ..., "threshold": ..., "model_version": ...}
        return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 23 passed, 1 warning in 16.86s ========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | « Probabilité de panne : 95 % », puis un bandeau rouge « ALERTE : risque de panne, planifiez une intervention. » |
| valeurs par défaut, fausse clé | bandeau jaune « Erreur 401 : Clé API absente ou invalide. » |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | bandeau rouge « API injoignable à l'adresse http://127.0.0.1:8000 : vérifiez que uvicorn est lancé. » |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

CORS est une règle appliquée **par le navigateur** : il bloque le JavaScript d'une page quand il appelle une autre origine non autorisée. Avec Streamlit, le navigateur ne parle qu'au serveur Streamlit (port 8501). C'est le serveur Streamlit, en Python, qui appelle l'API avec `httpx` dans `MaintaiClient`. Cette requête va de serveur à serveur, sans navigateur, donc la règle CORS ne s'applique pas. L'API, elle, vérifie toujours la clé : la sécurité vient de `X-API-Key`, pas de CORS.

## 5. Questions de compréhension

1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?
   Dans le TP2, c'est **le navigateur** : le `fetch` du JavaScript de `web/index.html` part de la page servie sur le port 5500, d'où le contrôle CORS. Dans Streamlit, c'est **le serveur Streamlit en Python** (`MaintaiClient.predict`, avec `httpx`). Le navigateur ne fait qu'afficher la page que ce serveur lui renvoie.
2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?
   Le test passe à `MaintaiClient` le `TestClient` de FastAPI par le paramètre `http=` (`MaintaiClient(api_key="test-key", http=client)`). Le `TestClient` a la même interface qu'un `httpx.Client`, mais il envoie la requête directement à l'objet `app` en mémoire, sans réseau ni serveur. Le code de `predict` est exactement le même, d'où l'importance d'appeler `self.http.post` et non `httpx.post`.
3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?
   Pour une **démonstration**, je choisirais Streamlit : tout est en Python, les graphiques sont prêts en une ligne, et la démo tient en une séance. On renonce à une interface personnalisée, ce qui est acceptable pour montrer le modèle. Pour l'**application d'un technicien**, je choisirais une page HTML + JavaScript. On contrôle entièrement l'interface (gros boutons, affichage sur tablette ou téléphone sur le terrain) et la page est légère, servie comme de simples fichiers statiques. Streamlit, lui, relance tout le script côté serveur à chaque clic et maintient une session par utilisateur. Il faut alors gérer CORS, ce que Streamlit évitait.

## 6. Le rendu Git

- Lien de la pull request : …
- Le tag `tp3` existe sur GitHub : oui
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? non (ils sont exclus par le `.gitignore`)

## 7. Ce qui reste flou

- Pourquoi `sys.path` change selon qu'on lance `streamlit run` ou `python -m streamlit run`, et ce que `pip install -e .` modifie exactement (TP4).
- Comment Streamlit gère plusieurs utilisateurs en même temps, puisque chaque clic relance le script côté serveur : est-ce adapté à une équipe entière de techniciens ?