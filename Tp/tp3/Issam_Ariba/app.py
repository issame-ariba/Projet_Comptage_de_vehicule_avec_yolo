
"""Interface Streamlit de MaintAI : explorer les données, puis demander une prédiction à l'API.

Lancement (depuis la racine du projet) : python -m streamlit run ui/app.py
"""

# Importation des bibliothèques nécessaires
import httpx
import pandas as pd
import streamlit as st

# Importation du client API, des erreurs, des variables et de la configuration
from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings


# Configuration de la page Streamlit
st.set_page_config(page_title="MaintAI", page_icon="🔧")

# Affichage du titre principal de l'application
st.title("MaintAI · prédiction de panne")


# Utilisation du cache pour éviter de recharger le fichier CSV
# à chaque interaction avec l'interface Streamlit
@st.cache_data
def charger(path) -> pd.DataFrame:
    # Lecture du fichier contenant les données de maintenance
    return pd.read_csv(path)


# Création d'une barre latérale pour configurer la connexion à l'API
with st.sidebar:
    # Champ permettant de saisir l'adresse de l'API
    url = st.text_input("URL de l'API", "http://localhost:8000")

    # Champ sécurisé permettant de saisir la clé API
    cle = st.text_input("Clé API", type="password")


# Création des deux onglets de l'application
onglet_donnees, onglet_prediction = st.tabs(
    ["Données", "Prédiction"]
)


# ==========================================================
# SPRINT 1 : EXPLORATION ET VISUALISATION DES DONNÉES
# ==========================================================

with onglet_donnees:

    # Chargement du jeu de données à partir du fichier CSV
    df = charger(get_settings().data_path)

    # ------------------------------------------------------
    # 1. AFFICHAGE DES TROIS INDICATEURS PRINCIPAUX
    # ------------------------------------------------------

    # Création de trois colonnes pour afficher les indicateurs
    c1, c2, c3 = st.columns(3)

    # Premier indicateur : nombre total de relevés
    c1.metric(
        "Nombre de relevés",
        len(df)
    )

    # Deuxième indicateur : calcul du taux de panne
    # La moyenne de failure représente la proportion de pannes
    # car 0 signifie absence de panne et 1 signifie présence de panne
    taux_panne = df["failure"].mean()

    c2.metric(
        "Taux de panne",
        f"{taux_panne:.1%}"
    )

    # Troisième indicateur : calcul de la température moyenne
    temperature_moyenne = df["temperature_c"].mean()

    c3.metric(
        "Température moyenne",
        f"{temperature_moyenne:.1f} °C"
    )

    # ------------------------------------------------------
    # 2. SÉLECTION D'UNE VARIABLE
    # ------------------------------------------------------

    # Création d'une liste déroulante contenant les variables FEATURES
    # L'utilisateur peut choisir la variable qu'il souhaite analyser
    variable = st.selectbox(
        "Choisir une variable à analyser",
        FEATURES
    )

    # ------------------------------------------------------
    # 3. TAUX DE PANNE PAR TRANCHE DE LA VARIABLE
    # ------------------------------------------------------

    # Division des valeurs de la variable sélectionnée en 10 intervalles
    # pd.cut permet de regrouper les valeurs numériques par tranches
    tranches = pd.cut(
        df[variable],
        bins=10
    )

    # Calcul du taux de panne pour chaque tranche
    # La moyenne de failure donne la proportion de pannes
    # observed=True permet de ne conserver que les tranches observées
    taux_par_tranche = df.groupby(
        tranches,
        observed=True
    )["failure"].mean()

    # Récupération du milieu de chaque tranche
    # Les valeurs numériques sont arrondies à deux décimales
    # afin de faciliter la lecture et le classement du graphique
    taux_par_tranche.index = [
        round(interval.mid, 2)
        for interval in taux_par_tranche.index
    ]

    # Affichage du titre du graphique selon la variable choisie
    st.subheader(
        f"Taux de panne selon {variable}"
    )

    # Affichage du taux de panne par tranche sous forme de diagramme en barres
    st.bar_chart(taux_par_tranche)

    # ------------------------------------------------------
    # 4. NUAGE DE POINTS : TEMPÉRATURE ET VIBRATION
    # ------------------------------------------------------

    # Création d'une copie du DataFrame pour ne pas modifier les données originales
    df_graph = df.copy()

    # Transformation des valeurs numériques de panne en catégories lisibles
    # 0 devient Non et 1 devient Oui
    # Cela permet de distinguer visuellement les deux catégories
    df_graph["panne"] = df_graph["failure"].map({
        0: "Non",
        1: "Oui"
    })

    # Affichage du titre du nuage de points
    st.subheader(
        "Relation entre température et vibration"
    )

    # Création du nuage de points
    # Axe X : température en degrés Celsius
    # Axe Y : vibration en mm/s
    # Couleur : présence ou absence d'une panne
    st.scatter_chart(
        df_graph,
        x="temperature_c",
        y="vibration_mm_s",
        color="panne"
    )


# ==========================================================
# SPRINT 2 : DEMANDER UNE PRÉDICTION À L'API
# ==========================================================

with onglet_prediction:

    # Création d'un formulaire pour saisir les caractéristiques du relevé
    with st.form("releve"):

        # Récupération des quatre paramètres nécessaires à la prédiction
        releve = {
            "temperature_c": st.slider(
                "Température (°C)", -40.0, 150.0, 72.0
            ),
            "vibration_mm_s": st.slider(
                "Vibration (mm/s)", 0.0, 50.0, 6.0
            ),
            "load_pct": st.slider(
                "Charge (%)", 0.0, 100.0, 85.0
            ),
            "runtime_hours": st.number_input(
                "Heures de fonctionnement", 0, 100_000, 15000
            ),
        }

        # Bouton permettant d'envoyer le relevé pour obtenir une prédiction
        envoye = st.form_submit_button("Prédire")

    
    if envoye:

        # 1. Création du client pour communiquer avec l'API MaintAI.
        # On utilise l'URL et la clé API saisies dans la barre latérale.
        client = MaintaiClient(url, api_key=cle)

        try:
            # 2. Envoi des quatre paramètres du formulaire à l'API.
            # L'API retourne un dictionnaire contenant la prédiction.
            resultat = client.predict(releve)

        except APIError as e:
            # 3. Cas où l'API répond, mais retourne une erreur.
            # Exemple : clé API incorrecte (401) ou données invalides (422).
            st.warning(
                f"Erreur API {e.status_code} : {e.detail}"
            )

        except httpx.HTTPError as e:
            # 4. Cas où l'API est inaccessible.
            # Exemple : serveur arrêté ou problème de connexion.
            st.error(f"API injoignable : {e}")

        else:
            # 5. Si la prédiction réussit, récupérer la probabilité de panne.
            proba = resultat["failure_probability"]

            # Conversion de la probabilité en pourcentage entier.
            pct = round(proba * 100)

            # Affichage de la probabilité sous forme d'indicateur.
            st.metric(
                "Probabilité de panne",
                f"{pct} %"
            )

            # 6. Affichage du résultat selon la présence d'une alerte.
            if resultat["alert"]:
                st.error("ALERTE : risque de panne détecté !")
            else:
                st.success("État normal : aucun risque de panne détecté.")
