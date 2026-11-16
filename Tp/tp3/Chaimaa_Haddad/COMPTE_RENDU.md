# Compte rendu · TP3 : une interface Streamlit pour MaintAI

**Groupe :** G3  ·  **Membres :** KENZA ELAIATI — CHAIMAA HADDAD  ·  **Date :** 12/11/2026

> Remplissez chaque partie dans ce fichier, puis rendez-le avec la pull request du TP3.
> Collez les sorties du terminal entre les lignes ``` (trois accents graves).

---

## 1. Mise en place (dans `TP/TP3`)

Dernière ligne de `python -m pytest` juste après la mise en place :

```
=================== 5 failed, 18 passed, 1 warning in 4.88s ===================
```

Quels fichiers de tests échouent, et quelle erreur donnent-ils ?

- `tests/test_client.py` (3 tests) : `test_client_returns_prediction`, `test_client_wrong_key_raises_401` et `test_client_bad_reading_raises_422` échouent avec `NotImplementedError: TP3 sprint 2 : MaintaiClient.predict` car la méthode `predict` du client n'est pas encore écrite.
- `tests/test_ui.py` (2 tests) : `test_ui_shows_the_data` et `test_ui_shows_the_prediction` échouent avec `IndexError: list index out of range` car les métriques Streamlit attendues (`at.metric[0]` pour le nombre de relevés et `at.metric[-1]` pour le pourcentage de probabilité) ne sont pas encore présentes dans `ui/app.py`.

---

## 2. Lancer Streamlit

Lancez d'abord `streamlit run ui/app.py`. Que s'affiche-t-il dans le navigateur ?

```
ModuleNotFoundError: No module named 'maintai'
Traceback:
File "ui/app.py", line 9, in <module>
    from maintai.client import APIError, MaintaiClient
```

Lancez ensuite `python -m streamlit run ui/app.py`. Pourquoi cette commande fonctionne-t-elle et pas la première ?

- Avec `streamlit run ui/app.py`, l'exécutable Streamlit place uniquement le dossier contenant le script (`ui/`) dans le `sys.path`. Le dossier racine du projet n'y figurant pas, Python ne peut pas résoudre le module `maintai`.
- Avec `python -m streamlit run ui/app.py`, l'interpréteur Python est démarré depuis le répertoire de travail actuel (la racine de `TP/TP3`), qui est automatiquement inséré en tête du `sys.path`. Python trouve donc immédiatement le dossier `maintai/` et charge l'application sans erreur.

---

## 3. Sprint 1 : l'onglet « Données »

Votre code de l'onglet « Données » (de `c1, c2, c3 = ...` jusqu'au nuage de points) :

```python
with onglet_donnees:
    df = charger(get_settings().data_path)
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    c2.metric("Taux de panne", f"{df['failure'].mean():.1%}")
    c3.metric("Température moyenne", f"{df['temperature_c'].mean():.1f} °C")

    variable = st.selectbox("Variable", FEATURES)
    tranches = pd.cut(df[variable], bins=10)
    taux = df.groupby(tranches, observed=True)["failure"].mean()
    taux.index = [round(interval.mid, 1) for interval in taux.index]
    st.bar_chart(taux)

    df_scatter = df.copy()
    df_scatter["Panne"] = df_scatter["failure"].map({0: "Non", 1: "Oui"})
    st.scatter_chart(df_scatter, x="temperature_c", y="vibration_mm_s", color="Panne")
```

| Indicateur | Valeur affichée |
|---|---|
| Relevés | 5000 |
| Taux de panne | 13.6% |
| Température moyenne | 59.8 °C |

Choisissez `vibration_mm_s` dans la liste. Comment évolue le taux de panne quand la vibration augmente ?

Le taux de panne augmente de façon spectaculaire avec la vitesse vibratoire : il est inférieur à 2 % pour des vibrations faibles (< 2.2 mm/s), grimpe à 32.3 % entre 4.5 et 6.7 mm/s, atteint 83.6 % entre 8.9 et 11.1 mm/s, et plafonne à 100 % au-delà de 11.1 mm/s. La vibration est le facteur le plus prédictif et critique d'une rupture mécanique imminente.

Ajoutez un `print("relance")` en haut de `ui/app.py`, puis déplacez un curseur. Que voyez-vous dans le terminal, et qu'est-ce que cela montre sur le fonctionnement de Streamlit ?

À chaque modification d'un widget ou curseur, le mot `"relance"` s'imprime à nouveau dans le terminal. Cela prouve le principe fondamental d'exécution de Streamlit : le script est **entièrement réexécuté de haut en bas** à chaque interaction utilisateur.

À quoi sert `@st.cache_data` sur la fonction `charger` ?

Il permet de mettre en mémoire cache le DataFrame pandas issu de la lecture du fichier CSV. Sans ce décorateur, le fichier `sensors.csv` serait réouvert et reparsé à chaque interaction (mouvement de curseur, sélection), ralentissant inutilement l'application. Grâce à `@st.cache_data`, le chargement disque ne s'exécute qu'une seule et unique fois.

---

## 4. Sprint 2 : l'onglet « Prédiction »

Votre méthode `predict` (`maintai/client.py`) :

```python
    def predict(self, reading: dict) -> dict:
        """Envoie un relevé ; lève APIError si l'API refuse, httpx.HTTPError si elle est injoignable."""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        r = self.http.post("/v1/predict", json=reading, headers=headers)
        if r.status_code != 200:
            try:
                detail = r.json().get("detail", r.text)
            except ValueError:
                detail = r.text
            raise APIError(r.status_code, detail)
        return r.json()
```

Dernière ligne de `python -m pytest` à la fin du sprint 2 :

```
======================== 23 passed, 1 warning in 6.14s ========================
```

Avec l'API lancée (`uvicorn maintai.api.main:app --reload --env-file .env`) :

| Essai | Ce qu'affiche Streamlit |
|---|---|
| valeurs par défaut, bonne clé | `Probabilité de panne : 96 %` et encadré rouge `ALERTE : Risque élevé de panne détecté !` |
| valeurs par défaut, fausse clé | Encadré orange d'avertissement : `Erreur 401 : Clé API absente ou invalide` |
| API arrêtée (Ctrl+C dans le terminal d'uvicorn) | Encadré rouge d'erreur : `API injoignable. Vérifiez que le serveur uvicorn tourne et que l'URL est correcte.` |

Le port 8501 n'est pas dans `MAINTAI_CORS_ORIGINS`, et pourtant la prédiction fonctionne. Pourquoi ?

Parce que la politique CORS est un mécanisme de sécurité exécuté **exclusivement à l'intérieur des navigateurs web** lors de requêtes asynchrones JavaScript (`fetch` / `XMLHttpRequest`).  
Dans l'architecture de Streamlit, ce n'est pas le navigateur du client qui contacte l'API FastAPI : c'est le **serveur Python backend de Streamlit** qui effectue l'appel via la bibliothèque Python `httpx` (`MaintaiClient`). Comme il s'agit d'un appel réseau serveur-à-serveur (sans moteur de navigateur), CORS n'intervient pas et la requête n'est pas bloquée.

---

## 5. Questions de compréhension

1. **Dans la page web du TP2, qui envoie la requête à l'API ? Et dans Streamlit ?**  
   - Dans le TP2, c'est le **navigateur web du client** qui envoie directement la requête HTTP via la fonction JavaScript `fetch()`.  
   - Dans Streamlit (TP3), c'est le **processus serveur Python de Streamlit** qui envoie la requête à FastAPI via le client `httpx` (`MaintaiClient`).

2. **Pourquoi les tests de `test_client.py` n'ont-ils pas besoin d'uvicorn ?**  
   Parce qu'ils injectent le `TestClient` de Starlette/FastAPI directement dans l'attribut `http` de `MaintaiClient` (`MaintaiClient(api_key="...", http=client)`). Les requêtes sont transmises en mémoire vive directement à l'application ASGI FastAPI sans passer par une socket réseau TCP ni par un serveur web tiers.

3. **Page HTML + JavaScript (TP2) ou Streamlit (TP3) : laquelle choisiriez-vous pour une démonstration à un client ? Et pour l'application d'un technicien de maintenance ? Pourquoi ?**  
   - **Pour une démonstration à un client :** Streamlit. Il permet d'assembler rapidement une interface interactive riche avec visualisations de données en pur Python sans complexité frontend.  
   - **Pour un technicien de maintenance :** Une page HTML/JavaScript légère ou une Progressive Web App (PWA). Elle est beaucoup plus économe en ressources serveur, réagit instantanément sans recharger un script Python à chaque clic, et offre une interface personnalisable adaptée aux tablettes ou terminaux d'atelier.

---

## 6. Le rendu Git

- Lien de la pull request : *(à insérer lors de la soumission GitHub)*
- Le tag `tp3` existe sur GitHub : oui
- `git status` avant le commit : `.env`, `data/` ou `models/` apparaissaient-ils ? non (exclus par le `.gitignore`)
