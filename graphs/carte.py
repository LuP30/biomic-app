import streamlit as st
import folium
from streamlit_folium import st_folium

from core.constants import TYPOLOGIES_LABELS


def show(data):
    st.subheader("🗺️ Carte interactive des sites")

    # ── Extraction des sites uniques avec coordonnées ──────────────────────
    sites = (
        data[["Site", "Localisation_X", "Localisation_Y"]]
        .drop_duplicates()
        .dropna(subset=["Localisation_X", "Localisation_Y"])
        .reset_index(drop=True)
    )

    if sites.empty:
        st.warning("Aucune coordonnée géographique disponible dans les données.")
        return

    # ── Sélecteur de fond de carte ─────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        fond_carte = st.selectbox(
            "🖼️ Fond de carte",
            options=["OpenStreetMap", "CartoDB positron"],
        )

    # ── Centre de la carte ─────────────────────────────────────────────────
    center_lat = sites["Localisation_X"].mean()
    center_lon = sites["Localisation_Y"].mean()

    # ── Construction de la carte Folium ────────────────────────────────────
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles=fond_carte,
    )

    destination = m  # les marqueurs s'ajoutent directement à la carte

    # ── Ajout des marqueurs ────────────────────────────────────────────────
    for _, row in sites.iterrows():
        extra = _build_popup_extra(data, row["Site"])
        popup_html = (
            f"<div style='font-family:sans-serif; min-width:160px'>"
            f"<b style='font-size:14px'>{row['Site']}</b><hr style='margin:4px 0'>"
            f"<span style='color:#555'>Lat :</span> {row['Localisation_X']:.5f}<br>"
            f"<span style='color:#555'>Lon :</span> {row['Localisation_Y']:.5f}"
            f"{extra}"
            f"</div>"
        )
        folium.Marker(
            location=[row["Localisation_X"], row["Localisation_Y"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["Site"],
            icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
        ).add_to(destination)

    # ── Affichage Streamlit ────────────────────────────────────────────────
    st_folium(m, use_container_width=True, height=550)


def _build_popup_extra(data, site_name):
    """Construit une mini-fiche HTML avec pH, Salinité, Typologie"""
    import math
    import pandas as pd

    df = data[data["Site"] == site_name]
    if df.empty:
        return ""

    # Texte HTML à afficher dans le popup
    lines = []

    # Typologie (salée / saumâtre / douce)
    if "Typology" in df.columns:
        typologie = df["Typology"].dropna().unique()
        if len(typologie) > 0:
            lines.append(f"<span style='color:#555'>Typologie :</span> {TYPOLOGIES_LABELS.get(typologie[0], typologie[0])}")

    # Colonnes numériques : moyenne des valeurs pour pH et Salinité par site et saison
    mapping = {
        "pH": "pH",
        "Salinity": "Salinité",
    }
    for col, label in mapping.items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            val = df[col].mean()
            if not math.isnan(val):
                lines.append(f"<span style='color:#555'>{label} :</span> {val:.2f}")

    if not lines:
        return ""

    return "<hr style='margin:4px 0'>" + "<br>".join(lines)