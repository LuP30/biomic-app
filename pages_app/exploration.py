import streamlit as st

import graphs.graph_evol as graph_evol
import graphs.graph_radar as graph_radar
import graphs.diag_ternaire as diag_ternaire


def show(meta):
    st.subheader("Exploration")
    sous_page = st.selectbox("Visualisation", [
        "Évolution des paramètres sédimentaires",
        "Graphique radar (paramètres physico-chimiques)",
        "Diagramme ternaire (texture)",
    ])

    if sous_page == "Évolution des paramètres sédimentaires":
        graph_evol.show(meta)
    elif sous_page == "Graphique radar (paramètres physico-chimiques)":
        graph_radar.show(meta)
    else:
        diag_ternaire.show(meta)
  
        