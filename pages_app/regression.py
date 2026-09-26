from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.constants import GENRES_CIBLES, SEASON_ORDER, VARIABLES_CHIMIQUES
from core.data_loader import load_fusion_all
from pages_app import reseau_trophique

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "rf_multioutput.pkl"

LABELS_CHIMIQUES = {cfg["col"]: cfg["titre"] for cfg in VARIABLES_CHIMIQUES.values()}


# ── Chargement du modèle et des données ─────────────────────────────────────

@st.cache_resource
def _load_model():
    payload = joblib.load(MODEL_PATH)
    return payload["model"], payload["feature_names"], payload["target_names"]


@st.cache_data
def _build_X_reel(feature_names):
    """Reconstruit X exactement comme lors de l'entraînement (mêmes colonnes,
    même ordre), à partir des données ALL_DATA actuelles. Renvoie aussi Site
    et Season pour permettre le filtrage par échantillon dans show()."""
    fusion_all = load_fusion_all()
    X = fusion_all.reindex(columns=feature_names, fill_value=0)
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0)
    Y_reel = fusion_all[GENRES_CIBLES].apply(pd.to_numeric, errors="coerce").fillna(0)
    meta = fusion_all[["Site", "Season"]]
    return X, Y_reel, meta


def show():
    st.subheader("Simulation : impact de paramètres chimiques modifiés")
    st.caption(
        "Choisis un sous-ensemble d'échantillons (site, saison, ou la totalité), "
        "modifie un ou plusieurs paramètres environnementaux, compare la prédiction "
        "du modèle à la réalité observée, puis observe l'impact sur le réseau trophique."
    )

    if not MODEL_PATH.exists():
        st.error(
            "Modèle introuvable. Lance d'abord `python scripts/train_regression_model.py` "
            "depuis la racine du repo pour générer le fichier "
            f"`{MODEL_PATH.relative_to(MODEL_PATH.parent.parent)}`."
        )
        return

    model, feature_names, target_names = _load_model()
    X_reel_total, Y_reel_total, meta = _build_X_reel(feature_names)

    # ── Sélection des échantillons concernés ────────────────────────────────
    st.markdown("### 1. Échantillons concernés")
    col_site, col_saison = st.columns(2)
    with col_site:
        sites_dispo = sorted(meta["Site"].dropna().unique().tolist())
        site_choisi = st.selectbox("Site", ["Tous les sites"] + sites_dispo)
    with col_saison:
        saisons_dispo = sorted(
            meta["Season"].dropna().unique().tolist(),
            key=lambda s: SEASON_ORDER.get(s, 99),
        )
        saison_choisie = st.selectbox("Saison", ["Toutes les saisons"] + saisons_dispo)

    masque = pd.Series(True, index=meta.index)
    if site_choisi != "Tous les sites":
        masque &= meta["Site"] == site_choisi
    if saison_choisie != "Toutes les saisons":
        masque &= meta["Season"] == saison_choisie

    X_reel = X_reel_total[masque]
    Y_reel = Y_reel_total[masque]

    st.caption(f"{len(X_reel)} échantillon(s) sélectionné(s).")
    if len(X_reel) == 0:
        st.warning("Aucun échantillon ne correspond à cette sélection.")
        return
    if len(X_reel) < 10:
        st.warning(
            "Peu d'échantillons pour cette sélection : la corrélation utilisée "
            "pour le réseau trophique (étape 3) sera instable, voire peu "
            "interprétable en dessous de 3-4 échantillons."
        )

    # ── Sélection des paramètres à modifier ─────────────────────────────────
    st.markdown("### 2. Paramètres à modifier")
    parametres_choisis = st.multiselect(
        "Paramètres environnementaux",
        options=sorted(feature_names),
        format_func=lambda code: LABELS_CHIMIQUES.get(code, code),
    )

    deltas = {}
    if parametres_choisis:
        cols = st.columns(min(3, len(parametres_choisis)))
        for i, param in enumerate(parametres_choisis):
            valeur_moyenne = X_reel[param].mean()
            with cols[i % len(cols)]:
                deltas[param] = st.number_input(
                    f"Δ {LABELS_CHIMIQUES.get(param, param)} (moyenne actuelle : {valeur_moyenne:.3g})",
                    value=0.0,
                    step=round(max(abs(valeur_moyenne) * 0.1, 0.01), 3),
                    key=f"delta_{param}",
                )

    signature = (site_choisi, saison_choisie, tuple(sorted(deltas.items())))

    # ── Lancement de la simulation ──────────────────────────────────────────
    if st.button("▶️ Lancer la simulation", disabled=not parametres_choisis):
        X_modifie = X_reel.copy()
        for param, delta in deltas.items():
            X_modifie[param] = X_modifie[param] + delta

        with st.spinner("Prédiction en cours..."):
            Y_pred_reference = pd.DataFrame(
                model.predict(X_reel), columns=target_names, index=X_reel.index
            )
            Y_pred_modifie = pd.DataFrame(
                model.predict(X_modifie), columns=target_names, index=X_reel.index
            )

        st.session_state["regression_resultats"] = {
            "signature": signature,
            "Y_reel": Y_reel,
            "Y_pred_reference": Y_pred_reference,
            "Y_pred_modifie": Y_pred_modifie,
            "deltas": dict(deltas),
        }

    if "regression_resultats" not in st.session_state:
        st.info("Choisis au moins un paramètre, règle un delta, puis lance la simulation.")
        return

    resultats = st.session_state["regression_resultats"]
    if resultats["signature"] != signature:
        st.info(
            "Le site, la saison ou les paramètres modifiés ont changé depuis le "
            "dernier calcul. Clique sur ▶️ Lancer la simulation pour mettre à jour."
        )
        return

    Y_reel = resultats["Y_reel"]
    Y_pred_reference = resultats["Y_pred_reference"]
    Y_pred_modifie = resultats["Y_pred_modifie"]

    st.caption("Dernière simulation : " + ", ".join(
        f"{LABELS_CHIMIQUES.get(p, p)} {'+' if d >= 0 else ''}{d:g}" for p, d in resultats["deltas"].items()
    ))

    # ── Comparaison des abondances ──────────────────────────────────────────
    st.markdown("### 3. Impact sur les abondances prédites")

    df_compare = pd.DataFrame({
        "Réel (moyenne)": Y_reel.mean(),
        "Prédit référence (moyenne)": Y_pred_reference.mean(),
        "Prédit modifié (moyenne)": Y_pred_modifie.mean(),
    })
    df_compare["Écart (modifié - référence)"] = (
        df_compare["Prédit modifié (moyenne)"] - df_compare["Prédit référence (moyenne)"]
    )
    df_compare = df_compare.sort_values("Écart (modifié - référence)", key=abs, ascending=False)

    fig = go.Figure()
    for col, color in [
        ("Réel (moyenne)", "#888888"),
        ("Prédit référence (moyenne)", "#2c7bb6"),
        ("Prédit modifié (moyenne)", "#d7191c"),
    ]:
        fig.add_trace(go.Bar(x=df_compare.index, y=df_compare[col], name=col, marker_color=color))
    fig.update_layout(
        barmode="group",
        height=500,
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=40, r=40, t=40, b=140),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Tableau détaillé"):
        st.dataframe(df_compare, use_container_width=True)

    # ── Impact sur le réseau trophique ──────────────────────────────────────
    st.markdown("### 4. Impact sur le réseau trophique")
    seuil = st.slider("Seuil de corrélation |ρ|", min_value=0.5, max_value=0.95, value=0.7, step=0.05)

    G_reel, _ = reseau_trophique.build_correlation_graph(Y_reel, seuil)
    G_simule, _ = reseau_trophique.build_correlation_graph(Y_pred_modifie, seuil)

    aretes_reel = {frozenset(e) for e in G_reel.edges()}
    aretes_simule = {frozenset(e) for e in G_simule.edges()}
    gagnees = aretes_simule - aretes_reel
    perdues = aretes_reel - aretes_simule
    communes = aretes_reel & aretes_simule

    c1, c2, c3 = st.columns(3)
    c1.metric("Liaisons communes", len(communes))
    c2.metric("Liaisons apparues", len(gagnees))
    c3.metric("Liaisons disparues", len(perdues))

    col_reel, col_simule = st.columns(2)
    with col_reel:
        st.caption("Réseau réel (données observées)")
        st.download_button(
                f"📥 Télécharger le graphe réel",
                data= reseau_trophique.afficher_pyvis(G_reel, seed=0),
                file_name=f"reseau_trophique_reel.html",
                mime="text/html",
                key=f"dl_groupe_reel",
            )
    with col_simule:
        st.caption("Réseau simulé (après modification)")
        st.download_button(
                f"📥 Télécharger le graphe simulé",
                data= reseau_trophique.afficher_pyvis(G_simule, seed=0),
                file_name=f"reseau_trophique_simule.html",
                mime="text/html",
                key=f"dl_groupe_simule",
            )

    if gagnees:
        with st.expander(f"Liaisons apparues ({len(gagnees)})"):
            for a in gagnees:
                st.markdown(f"- {' — '.join(sorted(a))}")
    if perdues:
        with st.expander(f"Liaisons disparues ({len(perdues)})"):
            for a in perdues:
                st.markdown(f"- {' — '.join(sorted(a))}")