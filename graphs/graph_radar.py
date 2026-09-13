import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.constants import SEASON_COLORS, SEASON_LABELS, VARIABLES_CHIMIQUES as VARIABLES

SEASON_ORDER = list(SEASON_LABELS.values())


def show(data):
    variable_selectionnee = st.selectbox("📊 Variable", options=list(VARIABLES.keys()))
    cfg = VARIABLES[variable_selectionnee]
    col_var = cfg["col"]
    titre = cfg["titre"]

    df_var = data[["Site", "Season", col_var]].copy()

    sites = sorted(df_var["Site"].dropna().unique().tolist())
    sites_closed = sites + [sites[0]]

    fig = go.Figure()

    for season in SEASON_ORDER:
        df_season = df_var[df_var["Season"] == season]

        r_values = []
        for site in sites_closed:
            val = df_season.loc[df_season["Site"] == site, col_var]
            r_values.append(val.values[0] if not val.empty else None)

        fig.add_trace(go.Scatterpolar(
            r=r_values,
            theta=sites_closed,
            mode="lines+markers",
            fill="toself",
            opacity=0.45,
            name=season,
            line=dict(color=SEASON_COLORS[season], width=2),
            marker=dict(size=7, color=SEASON_COLORS[season]),
            hovertemplate="<b>%{theta}</b><br>" + titre + " : %{r:.2f}<extra>" + season + "</extra>",
        ))

    valeur_max = df_var[col_var].max()
    plafond = valeur_max * 1.15 if pd.notna(valeur_max) else 1

    fig.update_layout(
        title=dict(text=f"{titre} par site et par saison", x=0.5, font=dict(size=17)),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, plafond],
                tickfont=dict(size=10),
                gridcolor="rgba(0,0,0,0.15)",
            ),
            angularaxis=dict(tickfont=dict(size=12)),
            bgcolor="white",
        ),
        legend=dict(title="Saison", font=dict(size=12)),
        paper_bgcolor="white",
        height=650,
        margin=dict(l=60, r=60, t=70, b=60),
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Voir les données brutes"):
        st.dataframe(df_var, use_container_width=True)

