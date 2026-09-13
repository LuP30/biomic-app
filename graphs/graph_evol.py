import plotly.graph_objects as go
import streamlit as st
from core.constants import SEASON_ORDER, SEASON_LABELS

# ── Chargement des données ──────────────────────────────────────────────────
def show(data):
    
    # ── Définition des variables et zones de couleur ───────────────────────────
    VARIABLES = {
        "pH": {
            "col": "pH",
            "titre_y": "pH",
            "zones": [
                {"y0": 0,   "y1": 6.5, "color": "red",   "label": "Acide"},
                {"y0": 6.5, "y1": 8,   "color": "green",  "label": "Neutre"},
                {"y0": 8,   "y1": 14,  "color": "blue",   "label": "Basique"},
            ],
        },
        "Salinité": {
            "col": "Salinity",
            "titre_y": "Salinité",
            "zones": [
                {"y0": 0,  "y1": 1,  "color": "blue",   "label": "Eau douce"},
                {"y0": 1,  "y1": 10, "color": "orange", "label": "Eau saumâtre"},
                {"y0": 10, "y1": 35, "color": "red",    "label": "Eau salée"},
            ],
        },
    }

    # ── Sélecteurs ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        sites_disponibles = sorted(data["Site"].dropna().unique().tolist())
        site_selectionne = st.selectbox("🗺️ Site", options=sites_disponibles)

    with col2:
        variable_selectionnee = st.selectbox("📊 Variable", options=list(VARIABLES.keys()))

    # ── Filtrage des données ───────────────────────────────────────────────────
    cfg = VARIABLES[variable_selectionnee]
    col_var = cfg["col"]

    df_site = data.loc[
        data["Site"] == site_selectionne,
        ["Season", col_var]
    ].copy()

    df_site["Season_num"] = df_site["Season"].map(SEASON_ORDER)
    df_site = df_site.dropna(subset=["Season_num", col_var])
    df_site = df_site.sort_values("Season_num")

    # ── Construction du graphique ──────────────────────────────────────────────
    fig = go.Figure()

    # Zones de couleur (bandes horizontales)
    for zone in cfg["zones"]:
        fig.add_hrect(
            y0=zone["y0"],
            y1=zone["y1"],
            fillcolor=zone["color"],
            opacity=0.12,
            line_width=0,
            annotation_text=zone["label"],
            annotation_position="right",
            annotation_font=dict(size=11, color=zone["color"]),
        )

    # Ligne d'évolution
    if not df_site.empty:
        fig.add_trace(go.Scatter(
            x=df_site["Season_num"],
            y=df_site[col_var],
            mode="lines+markers",
            line=dict(color="#2c3e50", width=3),
            marker=dict(size=9, color="#2c3e50", symbol="circle",
                        line=dict(color="white", width=2)),
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                f"{variable_selectionnee} : %{{y:.2f}}<br>"
                "<extra></extra>"
            ),
            customdata=df_site["Season"].values,
            name=variable_selectionnee,
        ))
    else:
        st.warning(f"Aucune donnée disponible pour le site **{site_selectionne}** "
                f"et la variable **{variable_selectionnee}**.")

    # Mise en page
    fig.update_layout(
        title=dict(
            text=f"Évolution de la variable : {variable_selectionnee.lower()} — Site {site_selectionne}",
            x=0.5,
            font=dict(size=17, color="black")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(SEASON_LABELS.keys()),
            ticktext=list(SEASON_LABELS.values()),
            title=dict(text="Saison", font=dict(color="black")),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.5)",
            tickfont=dict(color="black")
        ),
        yaxis=dict(
            title=dict(text=cfg["titre_y"], font=dict(color="black")),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.5)",
            tickfont=dict(color="black")
        ),
        height=520,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=60, r=120, t=70, b=60),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Tableau des valeurs ────────────────────────────────────────────────────
    with st.expander("📋 Voir les données brutes"):
        df_display = df_site[["Season", col_var]].rename(
            columns={"Season": "Saison", col_var: variable_selectionnee}
        ).reset_index(drop=True)
        st.dataframe(df_display, use_container_width=True)