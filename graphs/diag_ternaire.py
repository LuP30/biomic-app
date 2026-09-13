import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ZONES = [
    {"nom": "Argile",               "color": "#F0E442",
     "pts": [(100,0,0), (60,40,0), (40,40,20), (40,15,45), (55,0,45)]},
    {"nom": "Argile sableuse",      "color": "#CC0000",
     "pts": [(55,0,45), (40,15,45), (35,20,45), (35,0,65)]},
    {"nom": "Argile limoneuse",     "color": "#009E73",
     "pts": [(60,40,0), (40,60,0), (40,40,20)]},
    {"nom": "Limon argileux",       "color": "#56B4E9",
     "pts": [(40,15,45), (40,40,20), (25,55,20), (25,30,45)]},
    {"nom": "Limon argileux fin",   "color": "#0072B2",
     "pts": [(40,40,20), (40,60,0), (25,75,0), (25,55,20)]},
    {"nom": "Limon argilo-sableux", "color": "#E69F00",
     "pts": [(35,0,65), (35,20,45), (25,30,45), (20,30,50), (20,0,80)]},
    {"nom": "Limon sableux",        "color": "#CC79A7",
     "pts": [(20,0,80), (15,0,85), (0,30,70), (0,50,50), (10,50,40), (10,40,50), (20,30,50)]},
    {"nom": "Limon",                "color": "#8B6914",
     "pts": [(25,30,45), (20,30,50), (10,40,50), (10,50,40), (0,50,50), (25,50,25)]},
    {"nom": "Limon fin",            "color": "#7CB36A",
     "pts": [(25,50,25), (0,50,50), (0,80,20), (10,80,10), (10,90,0), (25,75,0)]},
    {"nom": "Limon très fin",       "color": "#00CC44",
     "pts": [(0,80,20), (0,100,0), (10,90,0), (10,80,10)]},
    {"nom": "Sable limoneux",       "color": "#F5A623",
     "pts": [(0,15,85), (0,30,70), (15,0,85), (10,0,90)]},
    {"nom": "Sable",                "color": "#FFFACD",
     "pts": [(10,0,90), (0,0,100), (0,15,85)]},
]

LABELS = [
    {"nom": "Argile",               "a": 65, "l": 18, "s": 17},
    {"nom": "Argile\nsableuse",     "a": 44, "l":  5, "s": 51},
    {"nom": "Argile\nlimoneuse",    "a": 47, "l": 47, "s":  6},
    {"nom": "Limon\nargileux",      "a": 32, "l": 35, "s": 33},
    {"nom": "Limon\nargileux fin",  "a": 32, "l": 60, "s":  8},
    {"nom": "Limon\nargilo-sabl.",  "a": 27, "l": 14, "s": 59},
    {"nom": "Limon\nsableux",       "a": 10, "l": 28, "s": 62},
    {"nom": "Limon",                "a": 16, "l": 43, "s": 41},
    {"nom": "Limon\nfin",           "a": 12, "l": 65, "s": 23},
    {"nom": "Limon\ntrès fin",      "a":  4, "l": 87, "s":  9},
    {"nom": "Sable\nlimoneux",      "a":  5, "l": 18, "s": 77},
    {"nom": "Sable",                "a":  2, "l":  5, "s": 93},
]


def show(data):
    texture_cols = ["Clay", "Silt", "Sand"]

    df = data[texture_cols].copy()
    df_norm = df.div(df.sum(axis=1), axis=0) * 100

    fig = go.Figure()

    # ── Zones colorées ─────────────────────────────────────────────────────
    for z in ZONES:
        pts = z["pts"]
        a_arg = [p[0] for p in pts] + [pts[0][0]]
        b_sab = [p[2] for p in pts] + [pts[0][2]]
        c_lim = [p[1] for p in pts] + [pts[0][1]]
        fig.add_trace(go.Scatterternary(
            a=a_arg, b=b_sab, c=c_lim,
            mode='lines',
            fill='toself',
            fillcolor=z["color"],
            opacity=0.75,
            line=dict(color='#222', width=1.5),
            name=z["nom"],
            showlegend=True,
            hoverinfo='name',
        ))

    # ── Labels dans les zones ──────────────────────────────────────────────
    for lbl in LABELS:
        fig.add_trace(go.Scatterternary(
            a=[lbl["a"]], b=[lbl["s"]], c=[lbl["l"]],
            mode='text',
            text=[lbl["nom"]],
            textfont=dict(size=9, color='#111'),
            showlegend=False,
            hoverinfo='skip',
        ))

    # ── Points de données ──────────────────────────────────────────────────
    fig.add_trace(go.Scatterternary(
        a=df_norm["Clay"],
        b=df_norm["Sand"],
        c=df_norm["Silt"],
        mode='markers+text',
        text=data["Site"],
        textposition='top center',
        textfont=dict(size=9, color='black'),
        marker=dict(size=10, color='black', symbol='circle',
                    line=dict(color='white', width=1.5)),
        name='Échantillons',
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Argile : %{a:.1f}%<br>"
            "Limon  : %{c:.1f}%<br>"
            "Sable  : %{b:.1f}%<br>"
            "<extra></extra>"
        ),
    ))

    # ── Mise en page ───────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(
            text='Diagramme de texture des sols',
            x=0.5,
            font=dict(size=17)
        ),
        ternary=dict(
            sum=100,
            aaxis=dict(
                title=dict(text='Argile (%)', font=dict(size=13)),
                tickfont=dict(size=10), tickformat='.0f',
                showgrid=True, gridcolor='rgba(0,0,0,0.12)',
            ),
            baxis=dict(
                title=dict(text='Sable (%)', font=dict(size=13)),
                tickfont=dict(size=10), tickformat='.0f',
                showgrid=True, gridcolor='rgba(0,0,0,0.12)',
            ),
            caxis=dict(
                title=dict(text='Limon (%)', font=dict(size=13)),
                tickfont=dict(size=10), tickformat='.0f',
                showgrid=True, gridcolor='rgba(0,0,0,0.12)',
            ),
            bgcolor='white',
        ),
        legend=dict(
            orientation='v', x=1.02, y=0.98,
            font=dict(size=10), bgcolor='rgba(255,255,255,0.8)'
        ),
        height=750,
        paper_bgcolor='white',
        margin=dict(l=60, r=200, t=70, b=60),
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Voir les données brutes"):
        df_display = data[["Site"] + texture_cols].copy()
        df_display["Clay_%"] = df_norm["Clay"].round(1)
        df_display["Silt_%"] = df_norm["Silt"].round(1)
        df_display["Sand_%"] = df_norm["Sand"].round(1)
        st.dataframe(df_display, use_container_width=True)