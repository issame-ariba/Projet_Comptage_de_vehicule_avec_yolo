"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.
 
Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""
import httpx
import pandas as pd
import streamlit as st
 
from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings
 
st.set_page_config(page_title="MaintAI", page_icon="🔧")
st.title("MaintAI · prédiction de panne")
 
 
@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lu une seule fois : Streamlit relance tout le script à chaque clic
    return pd.read_csv(path)
 
 
with st.sidebar:
    url = st.text_input("URL de l'API", "http://localhost:8000")
    cle = st.text_input("Clé API", type="password")
 
onglet_donnees, onglet_prediction = st.tabs(["Données", "Prédiction"])
 
# Sprint 1 : explorer les données
with onglet_donnees:
    df = charger(get_settings().data_path)
 
    # 1. Trois indicateurs côte à côte : st.columns(3) découpe la largeur en 3 colonnes,
    #    et chaque colonne a sa propre méthode .metric(libellé, valeur).
    #    L'ordre compte : le test lit le PREMIER indicateur et attend le nombre de relevés.
    c1, c2, c3 = st.columns(3)
    c1.metric("Relevés", len(df))
    # failure vaut 0 ou 1 : sa moyenne est donc la part de pannes (ex. 0.205).
    # Le format :.1% multiplie par 100 et ajoute « % » (0.205 -> "20.5%").
    c2.metric("Taux de panne", f"{df.failure.mean():.1%}")
    c3.metric("Température moyenne", f"{df.temperature_c.mean():.1f} °C")
 
    # 2. Liste déroulante : `variable` vaut le nom de colonne choisi (ex. "vibration_mm_s").
    #    Changer de choix relance le script, et les graphiques ci-dessous se recalculent.
    variable = st.selectbox("Variable", FEATURES)
 
    # 3. Taux de panne par tranche de la variable choisie.
    #    pd.cut découpe l'étendue de la variable en 10 intervalles de même largeur
    #    et range chaque relevé dans l'un d'eux.
    tranches = pd.cut(df[variable], bins=10)
    # Pour chaque tranche, la moyenne de failure = le taux de panne dans cette tranche.
    # observed=True : on ne garde que les tranches qui contiennent réellement des relevés.
    taux = df.groupby(tranches, observed=True).failure.mean()
    # L'index contient des intervalles (ex. (4.2, 8.4]) que le graphique ne sait pas ordonner.
    # On les remplace par leur milieu, arrondi, en gardant des NOMBRES (pas du texte) :
    # l'axe des abscisses reste ainsi trié dans l'ordre croissant.
    taux.index = [round(i.mid, 1) for i in taux.index]
    taux.index.name = variable
    st.subheader(f"Taux de panne par tranche de {variable}")
    st.bar_chart(taux)  # l'index en abscisse, le taux en ordonnée
 
    # 4. Nuage de points température / vibration, coloré selon la panne.
    #    color= attend le NOM d'une colonne. Avec 0 / 1, Streamlit ferait un dégradé ;
    #    une colonne texte « oui / non » donne deux couleurs nettes et une légende lisible.
    #    assign() renvoie une copie : on ne modifie pas le DataFrame mis en cache.
    nuage = df.assign(panne=df.failure.map({0: "non", 1: "oui"}))
    st.subheader("Température et vibration")
    st.scatter_chart(nuage, x="temperature_c", y="vibration_mm_s", color="panne")
 
 
# Sprint 2 : demander une prédiction à l'API
with onglet_prediction:
    with st.form("releve"):
        releve = {
            "temperature_c": st.slider("Température (°C)", -40.0, 150.0, 72.0),
            "vibration_mm_s": st.slider("Vibration (mm/s)", 0.0, 50.0, 6.0),
            "load_pct": st.slider("Charge (%)", 0.0, 100.0, 85.0),
            "runtime_hours": st.number_input("Heures de fonctionnement", 0, 100_000, 15000),
        }
        envoye = st.form_submit_button("Prédire")
 
    # envoye ne vaut True que pendant la relance provoquée par le bouton « Prédire »
    if envoye:
        # try / except / except / else : trois issues possibles, un affichage chacune.
        try:
            # 1. Le client reçoit l'URL et la clé saisies dans la barre latérale.
            resultat = MaintaiClient(url, api_key=cle).predict(releve)
        except APIError as e:
            # 2a. L'API a répondu mais a refusé (401 fausse clé, 422 relevé invalide, 503...) :
            #     message jaune avec le code et l'explication renvoyée par l'API.
            st.warning(f"Erreur {e.status_code} : {e.detail}")
        except httpx.HTTPError:
            # 2b. Aucune réponse : serveur arrêté, mauvaise URL ou délai dépassé.
            #     L'ordre des except compte : APIError d'abord, l'erreur réseau ensuite.
            st.error(f"API injoignable à l'adresse {url} : vérifiez que uvicorn est lancé.")
        else:
            # 3. Réponse 200 : la probabilité (entre 0 et 1) devient un pourcentage entier.
            pct = round(resultat["failure_probability"] * 100)
            st.metric("Probabilité de panne", f"{pct} %")
            # La décision d'alerte vient de l'API (elle connaît le seuil), on ne la recalcule pas.
            if resultat["alert"]:
                st.error("ALERTE : risque de panne, planifiez une intervention.")
            else:
                st.success("Fonctionnement normal")
 
