import streamlit as st
import graphs.carte as carte



def show(meta, genus):
    st.subheader("Accueil")
    st.subheader("Bienvenue sur l'application de visualisation et d'analyse des milieux humides.")
    st.write("-"*80)
    st.subheader("Explorez les différentes sections pour découvrir les fonctionnalités disponibles :")
    st.write("- **Exploration** : Visualisez les données et explorez les tendances saisonnières, globales ou par site.")
    st.write("- **Classification (Arbres de décision)** : Utilisez des arbres de décision pour classer les données.")
    st.write("- **Prédiction (Régression Multisortie avec forêts aléatoires)** : Effectuez des prédictions à l'aide de la régression par forêts aléatoires.")
    st.write("- **Réseau trophique** : Analysez les relations trophiques entre les espèces présentes dans les milieux humides.")
    st.write("-"*80)
    st.subheader("Carte interactive sur les sites d'échantillonnage")
    carte.show(meta)
    st.write("-"*80)
    st.subheader("Prévisualisation des données sur les informations des sites et les paramètres physico-chimiques")
    st.dataframe(meta.head(10))
    st.write("-"*80)
    st.subheader("Prévisualisation des données sur les microorganismes (génres bactériens)")
    st.dataframe(genus.head(10))
    st.write("-"*80)
    st.write("Source des données : [BIOMIC](https://www.biomic-project.eu/wp-content/uploads/2023/05/index2.html)")
    