# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G1 · **Membre :** Issam Ariba · **Date :** 11/11/2026

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```text
4 failed, 19 passed in 21.82s
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

Deux parties du projet n'étaient pas encore terminées à ce stade :

- `tests/test_client.py` : les trois tests échouaient parce que la méthode `MaintaiClient.predict()` contenait encore `raise NotImplementedError("TP3 sprint 2 : MaintaiClient.predict")`.
- `tests/test_ui.py` : un test échouait parce que la partie prédiction de l'interface Streamlit affichait encore le message provisoire du Sprint 2 au lieu du résultat attendu.

Les autres tests passaient. Ces erreurs correspondaient aux fonctionnalités qui devaient être réalisées pendant le Sprint 2.

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

La commande directe `streamlit run ui/app.py` n'a pas de résultat de terminal conservé dans les éléments communiqués. Le lancement qui a été confirmé est celui effectué avec `python -m streamlit run ui/app.py`.

Lors du premier démarrage de l'application, une erreur de fichier manquant a été rencontrée :

```text
FileNotFoundError: [Errno 2] No such file or directory:
'C:\Users\pc\Downloads\TP3\maintai-starter-tp3\data\sensors.csv'
```

Le dossier `data` ne contenait alors que `.gitkeep`. Après la mise à disposition du fichier de données attendu, l'onglet « Données » s'est affiché correctement.

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

La commande `python -m streamlit run ui/app.py` lance Streamlit avec le Python de l'environnement actif. Comme l'environnement virtuel `.venv` est activé, cette commande utilise les bibliothèques installées dans cet environnement. La commande `streamlit run` seule dépend de la résolution de l'exécutable `streamlit` dans le PATH de Windows ; elle peut donc ne pas utiliser le bon environnement ou ne pas être reconnue.

La commande qui a fonctionné est :

```powershell
python -m streamlit run ui/app.py
```

Le terminal a affiché :

```text
Uvicorn server started on :::8501

You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://172.21.71.28:8501
```

L'application était accessible à l'adresse `http://localhost:8501`.

## 3. Sprint 1 : l'onglet « Données »

Code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
# Chargement du jeu de données
df = charger(get_settings().data_path)

# 1. Affichage des trois indicateurs
c1, c2, c3 = st.columns(3)

# Nombre total de relevés
c1.metric("Nombre de relevés", len(df))

# Calcul et affichage du taux de panne
taux_panne = df["failure"].mean()
c2.metric("Taux de panne", f"{taux_panne:.1%}")

# Calcul et affichage de la température moyenne
temperature_moyenne = df["temperature_c"].mean()
c3.metric("Température moyenne", f"{temperature_moyenne:.1f} °C")

# 2. Sélection de la variable à analyser
variable = st.selectbox(
    "Choisir une variable à analyser",
    FEATURES
)

# 3. Découpage de la variable en dix intervalles
tranches = pd.cut(df[variable], bins=10)

# Calcul du taux de panne dans chaque intervalle
taux_par_tranche = df.groupby(
    tranches,
    observed=True
)["failure"].mean()

# Utilisation du milieu de chaque intervalle comme étiquette
taux_par_tranche.index = [
    round(interval.mid, 2)
    for interval in taux_par_tranche.index
]

# Affichage du graphique en barres
st.subheader(f"Taux de panne selon {variable}")
st.bar_chart(taux_par_tranche)

# 4. Préparation des catégories pour le nuage de points
df_graph = df.copy()
df_graph["panne"] = df_graph["failure"].map({
    0: "Non",
    1: "Oui"
})

# Affichage du nuage de points température / vibration
st.subheader("Relation entre température et vibration")
st.scatter_chart(
    df_graph,
    x="temperature_c",
    y="vibration_mm_s",
    color="panne"
)
```

| Indicateur | Valeur affichée |
|---|---:|
| Relevés | 5 000 |
| Taux de panne | 13,6 % |
| Température moyenne | 59,8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le graphique obtenu montre que le taux de panne augmente avec le niveau de vibration. Il est très faible pour les premières tranches, puis il augmente progressivement. Dans les dernières tranches, à partir d'environ 12 mm/s sur le graphique, le taux affiché atteint 100 %. Cela indique que les vibrations élevées sont fortement associées au risque de panne dans ce jeu de données.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

Lorsqu'un utilisateur interagit avec un widget Streamlit, comme un curseur, Streamlit réexécute le script de haut en bas. Le message `relance` placé au début du fichier doit donc réapparaître dans le terminal à chaque réexécution. Cette expérience illustre le fonctionnement réactif de Streamlit. La sortie exacte du terminal pour cette manipulation n'a pas été communiquée.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

`@st.cache_data` mémorise le résultat du chargement du fichier CSV. Lorsque la fonction est appelée à nouveau avec le même chemin et que les données en cache sont toujours valides, Streamlit réutilise le résultat au lieu de relire le fichier. Cela évite les chargements répétitifs et améliore les performances de l'application.

## 4. Sprint 2 : l'onglet « Prédiction »

Méthode `predict` (`maintai/client.py`) :

```python
def predict(self, reading: dict) -> dict:
    """Envoie un relevé ; lève APIError si l'API refuse,
    httpx.HTTPError si elle est injoignable."""

    # Préparer les en-têtes HTTP.
    headers = {}

    # Ajouter la clé API uniquement si elle est renseignée.
    if self.api_key:
        headers["X-API-Key"] = self.api_key

    # Envoyer les données du relevé à l'API au format JSON.
    # self.http est utilisé afin de permettre l'injection d'un client de test.
    r = self.http.post(
        "/v1/predict",
        json=reading,
        headers=headers
    )

    # Si le code HTTP n'est pas 200, lever une erreur API.
    if r.status_code != 200:
        raise APIError(
            r.status_code,
            r.json().get("detail")
        )

    # Retourner la réponse JSON lorsque la requête réussit.
    return r.json()
```

Dernière ligne de `python -m pytest` à la fin du Sprint 2 :

```text
23 passed, 1 warning in 11.91s
```

Les 23 tests passent. Un avertissement de dépréciation Starlette/httpx est affiché, mais il ne provoque aucun échec.

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| Valeurs par défaut, bonne clé | Probabilité de panne : **95 %**. Message : **« ALERTE : risque de panne détecté ! »** |
| Valeurs par défaut, fausse clé | **Erreur API 401 : Clé API absente ou invalide** |
| API arrêtée (Ctrl+C dans le terminal d'Uvicorn) | **API injoignable : [WinError 10061] Aucune connexion n’a pu être établie car l’ordinateur cible l’a expressément refusée** |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

La requête vers l'API est envoyée par le code Python de Streamlit avec `MaintaiClient` et HTTPX. Elle n'est pas envoyée directement par le navigateur avec JavaScript. CORS est une restriction appliquée par les navigateurs aux requêtes entre origines différentes. La communication réalisée directement entre le processus Python de Streamlit et l'API n'est donc pas bloquée par cette restriction CORS.

## 5. Questions de compréhension

**1. Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**

Dans la page web du TP2, le JavaScript exécuté dans le navigateur envoie la requête à l'API, par exemple avec `fetch()`. Dans Streamlit, la requête est envoyée côté Python par la classe `MaintaiClient`, qui utilise HTTPX et `self.http.post()`.

**2. Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'Uvicorn ?**

Les tests fournissent directement à `MaintaiClient` un client HTTP de test grâce au paramètre `http`. Ce client communique avec l'application FastAPI de test sans démarrer un serveur Uvicorn ni ouvrir un port réseau. Les tests peuvent ainsi vérifier les réponses de l'API de façon automatisée.

**3. Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**

Pour une démonstration à un client, je choisirais une page HTML + JavaScript si je souhaite une interface très personnalisée, une présentation soignée et un contrôle précis de l'expérience utilisateur.

Pour un technicien de maintenance, je choisirais Streamlit pour ce prototype, car il permet de consulter facilement les indicateurs, les graphiques et les prédictions dans une interface interactive. Il permet également de développer rapidement une interface Python sans devoir programmer beaucoup de code frontend. Le choix définitif dépendrait des besoins de déploiement, de sécurité et d'utilisation sur le terrain.

## 6. Le rendu Git

- **Lien de la Pull Request :** non communiqué dans les informations disponibles.
- **Le tag `tp3` existe sur GitHub :** à confirmer avec `git tag` puis `git push origin --tags`.
- **`git status` avant le commit :** résultat non communiqué. Il faut vérifier que `.env`, les fichiers CSV de `data/` et les modèles du dossier `models/` ne sont pas suivis par Git. Ces fichiers ne doivent pas être publiés sur GitHub.

Commandes de vérification à exécuter depuis la racine du projet :

```powershell
git status
git branch
git tag
```

## 7. Ce qui reste flou

Les points à approfondir sont :
- le fonctionnement du cache Streamlit et la réexécution du script après une interaction ;
- la différence entre une erreur HTTP renvoyée par l'API (`401`) et une erreur de connexion lorsque l'API est arrêtée (`WinError 10061`) ;
- la différence entre les requêtes navigateur soumises aux règles CORS et les requêtes envoyées directement par un client Python ;
- les dernières étapes de livraison Git : vérification de `git status`, création de la Pull Request et création/push du tag `tp3`.

---

**Bilan du TP3 :** l'interface Streamlit de MaintAI permet d'explorer 5 000 relevés de maintenance, de visualiser le taux de panne selon une variable et la relation entre température et vibration, puis d'envoyer un relevé à l'API pour obtenir une prédiction. Les trois scénarios de prédiction ont été vérifiés : clé correcte, clé incorrecte et API indisponible. À la fin du Sprint 2, les tests automatisés affichent **23 passed**.
