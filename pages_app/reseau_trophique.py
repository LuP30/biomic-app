import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from core.constants import SEASON_ORDER, GENRES_CIBLES

def build_correlation_graph(df_genres, seuil):
    """Construit le graphe de corrélation (|ρ| >= seuil) à partir d'un tableau
    d'abondances (colonnes = genres). Retourne (G, corr). Réutilisable en
    dehors de cette page (ex: réseau simulé dans regression.py)."""
    corr = df_genres.corr(method="pearson")
    G = nx.Graph()
    G.add_nodes_from(corr.columns)
    for i, genre_a in enumerate(corr.columns):
        for j, genre_b in enumerate(corr.columns):
            if i >= j:
                continue
            rho = corr.loc[genre_a, genre_b]
            if abs(rho) >= seuil:
                G.add_edge(genre_a, genre_b, weight=round(rho, 3))
    return G, corr

def show(genus_moyennes):
    st.subheader("Réseau de corrélation entre genres microbiens")
    st.caption(
        "Un groupe = une composante connexe du graphe une fois seuillé : "
        "tout genre relié à au moins un autre par |ρ| ≥ seuil. "
        "Les genres sans aucune connexion au-delà du seuil sont exclus."
    )

    saisons_disponibles = sorted(
        genus_moyennes["Season"].dropna().unique().tolist(),
        key=lambda s: SEASON_ORDER.get(s, 99),
    )
    saison_selectionnee = st.selectbox(
        "🗓️ Saison", options=["Toutes les saisons"] + saisons_disponibles
    )

    if saison_selectionnee == "Toutes les saisons":
        genus_scope = genus_moyennes
    else:
        genus_scope = genus_moyennes[genus_moyennes["Season"] == saison_selectionnee]

    seuil = st.slider("Seuil de corrélation |ρ|", min_value=0.5, max_value=0.95, value=0.7, step=0.05)

    df_filt = genus_scope[GENRES_CIBLES].copy()
    st.caption(f"Corrélations calculées sur {len(df_filt)} échantillon(s).")
    if len(df_filt) < 10:
        st.warning(
            "Peu d'échantillons pour cette sélection : les corrélations peuvent être instables."
        )

    G, corr = build_correlation_graph(df_filt, seuil)

    # ── Heatmap de corrélation (vue d'ensemble) ─────────────────────────────
    st.subheader("Matrice de corrélation entre genres")
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        zmin=-1,
        zmax=1,
        colorbar=dict(title="ρ Pearson"),
        hovertemplate="<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>ρ:</b> %{z:.2f}<extra></extra>",
    ))
    fig_heatmap.update_layout(
        xaxis=dict(tickfont=dict(size=9), tickangle=-45),
        yaxis=dict(tickfont=dict(size=9)),
        height=750,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=180, r=60, t=30, b=180),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.download_button(
        "📥 Télécharger la heatmap (HTML interactif)",
        data=fig_heatmap.to_html(include_plotlyjs="cdn"),
        file_name=f"heatmap_correlation_{saison_selectionnee}.html",
        mime="text/html",
        key=f"dl_heatmap_{saison_selectionnee}",
    )

    # ── Réseau par groupe (composantes connexes) ────────────────────────────
    st.subheader("Réseau par groupe")

    groupes = [c for c in nx.connected_components(G) if len(c) >= 2]
    isoles = [n for n in G.nodes() if G.degree(n) == 0]

    if not groupes:
        st.warning(
            f"Aucun groupe trouvé pour un seuil de {seuil} : "
            "aucune paire de genres n'atteint cette corrélation."
        )
        return

    st.markdown(
        f"**{len(groupes)} groupe(s)** trouvé(s) sur {len(GENRES_CIBLES)} genres testés — "
        f"{sum(len(g) for g in groupes)} genres connectés, {len(isoles)} isolés (exclus)."
    )

    groupes_tries = sorted(groupes, key=len, reverse=True)

    for idx, groupe in enumerate(groupes_tries, start=1):
        with st.expander(f"Groupe {idx} — {len(groupe)} genres", expanded=(idx == 1)):
            seed_key = f"seed_groupe_{idx}"
            if seed_key not in st.session_state:
                st.session_state[seed_key] = 0

            if st.button("🔄 Régénérer la disposition", key=f"regen_{idx}_{seuil}_{saison_selectionnee}"):
                st.session_state[seed_key] += 1

            sous_graphe = G.subgraph(groupe)
            html_reseau = afficher_pyvis(sous_graphe, seed=st.session_state[seed_key])
            st.download_button(
                f"📥 Télécharger le graphe (Groupe {idx})",
                data=html_reseau,
                file_name=f"reseau_groupe_{idx}_{saison_selectionnee}.html",
                mime="text/html",
                key=f"dl_groupe_{idx}_{seuil}_{saison_selectionnee}",
            )

    if isoles:
        with st.expander(f"Genres isolés exclus ({len(isoles)})"):
            for n in sorted(isoles):
                st.markdown(f"- {n}")


def afficher_pyvis(G, seed=0):
    net = Network(
        height="550px", width="100%", bgcolor="#ffffff", font_color="#222222",
        notebook=False, cdn_resources="in_line",
    )
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=150, spring_strength=0.05, damping=0.9)

    # Disposition initiale dépendante du seed : change à chaque clic sur
    # "Régénérer la disposition" (le seed est incrémenté côté show()).
    positions = nx.spring_layout(G, seed=seed, scale=400)

    for node in G.nodes():
        degree = G.degree(node)
        x, y = positions[node]
        net.add_node(
            node,
            label=node,
            title=f"{node}\nDegré : {degree}",
            size=10 + degree * 4,
            color="#2c7bb6",
            font={"size": 10},
            x=float(x),
            y=float(y),
        )

    for u, v, data in G.edges(data=True):
        rho = data["weight"]
        color = "#4575b4" if rho > 0 else "#d73027"
        width = abs(rho) * 6
        net.add_edge(u, v, title=f"ρ = {rho:.3f}", color=color, width=width, value=abs(rho))

    html = net.generate_html(notebook=False)
    components.html(html, height=570, scrolling=True)
    return html