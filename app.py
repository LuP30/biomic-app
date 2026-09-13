import streamlit as st

from core.data_loader import (
    load_metadata_moyennes,
    load_genus_moyennes
)

from pages_app import accueil
from pages_app import exploration
from pages_app import reseau_trophique
from pages_app import classification
from pages_app import regression

st.set_page_config(page_title="BIOMIC-APP", layout="wide")
st.title("Application sur les données de BIOMIC")

with st.sidebar:
    st.header("Navigation")
    section = st.radio("Section", [
        "Accueil",
        "Exploration",
        "Classification (arbres de décision)",
        "Prédiction (Régression Multisortie avec forêts aléatoires)",
        "Réseau trophique",
    ])

# ── Accueil ──────────────────────────────────────────────────────────────────
if section == "Accueil":
    meta = load_metadata_moyennes()
    genus = load_genus_moyennes()
    accueil.show(meta, genus)
    
# ── Exploration  ─────────────────────────────────────────
elif section == "Exploration":
    meta = load_metadata_moyennes()
    exploration.show(meta)

# ── Classification par arbre de décision ──────────────────
elif section == "Classification (arbres de décision)":
    classification.show()

# ── Régression Multisortie avec forêts aléatoires ───────────────────────
elif section == "Prédiction (Régression Multisortie avec forêts aléatoires)":
    regression.show()

# ── Réseau trophique ──────────────────────────────────────────────
elif section == "Réseau trophique":
    genus = load_genus_moyennes()
    reseau_trophique.show(genus)
