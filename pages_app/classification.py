import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

from core.constants import COLS_TO_REMOVE, RANDOM_STATE, TEXTURE_COLS
from core.data_loader import load_fusion_all, load_genus_all, load_metadata_all


PARAM_GRID = {
    'max_depth': [3, 4, 5, 6, 7, 8, 10, 12],
    'min_samples_split': [2, 4, 6, 8, 10],
    'min_samples_leaf': [1, 2, 3, 4, 5],
    'criterion': ['gini', 'entropy']
}

MAX_DEPTH_AFFICHAGE = 6


def _prepare_X_Y(meta_all, genus_all, fusion_all, source, typologie, inclure_texture):
    """Trois sources, trois origines de données distinctes :
      - Environnement : meta_all seul
      - Microbiologie : genus_all (tous les ~3076 genres, volontairement non
        filtrés sur GENRES_CIBLES car cette page sert d'exemple de classification
        naïve, pas de sélection de variables), fusionné uniquement avec
        Site/Typology depuis meta_all pour pouvoir définir Y (le site) et filtrer.
      - Fusion : fusion_all tel quel (environnement + tous les genres).
    """
    if source == "Environnement":
        df = meta_all
    elif source == "Microbiologie":
        df = meta_all[["Sample_ID", "Site", "Typology"]].merge(
            genus_all, on="Sample_ID", how="inner"
        )
    else:  # Fusion
        df = fusion_all

    df = df if typologie == "Tous les sites" else df[df["Typology"] == typologie]
    Y = df["Site"].reset_index(drop=True)

    cols_env_exclues = COLS_TO_REMOVE if inclure_texture else COLS_TO_REMOVE + TEXTURE_COLS

    if source == "Environnement":
        X = df.drop(columns=cols_env_exclues, errors="ignore")
    elif source == "Microbiologie":
        genus_cols = [c for c in genus_all.columns if c != "Sample_ID"]
        X = df[genus_cols].copy()
    else:  # Fusion
        X = df.drop(columns=cols_env_exclues, errors="ignore")

    X = X.apply(pd.to_numeric, errors="coerce").fillna(0).reset_index(drop=True)

    return X, Y


def _rechercher_hyperparametres(X, Y, seed):
    """GridSearchCV : recherche automatique des hyperparamètres.
       Train_test_split : 80% app et 20% test et
       stratify = Y pour garder la répartion des poids des classes?
    """
    n_splits = min(8, Y.value_counts().min())
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, stratify=Y, random_state=seed
    )
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=3, random_state=seed)
    grid = GridSearchCV(
        DecisionTreeClassifier(random_state=seed, max_features="sqrt"),
        PARAM_GRID, cv=cv, scoring="accuracy", n_jobs=1,
    )
    grid.fit(X_train, y_train)
    best_dt = grid.best_estimator_
    y_pred = best_dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return best_dt, acc, y_test, y_pred, grid.best_params_


def _entrainer_manuel(X, Y, params, seed):
    """Un seul arbre avec des hyperparamètres choisis à la main : pas de
    GridSearchCV, entraînement immédiat."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.2, stratify=Y, random_state=seed
    )
    dt = DecisionTreeClassifier(**params, random_state=seed, max_features="sqrt")
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return dt, acc, y_test, y_pred, params


def show():
    st.subheader("Classification (arbres de décision)")
    st.subheader("Objectif")
    st.caption(
        "L'objectif de cette page est de voir les variables qui discrimine le plus les différents sites."
        )
    st.subheader("Classification des sites par arbre de décision")
    st.caption(
        "Y = Site, X = Environnement / Microbiologie / Fusion, "
        "avec split optionnel par typologie d'eau."
    )

    meta_all = load_metadata_all()
    genus_all = load_genus_all()
    fusion_all = load_fusion_all()

    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Source des données", ["Environnement", "Microbiologie", "Fusion"])
    with col2:
        typologies = ["Tous les sites"] + sorted(meta_all["Typology"].dropna().unique().tolist())
        typologie = st.selectbox("Typologie", typologies)

    if source in ("Environnement", "Fusion"):
        inclure_texture = st.checkbox("Inclure la texture du sol (Clay / Silt / Sand)", value=False)
    else:
        inclure_texture = False  # sans objet pour Microbiologie pure

    X, Y = _prepare_X_Y(meta_all, genus_all, fusion_all, source, typologie, inclure_texture)
    st.caption(f"{len(X)} échantillons · {X.shape[1]} variables · {Y.nunique()} sites")

    if Y.nunique() < 2 or len(X) < 10:
        st.warning("Pas assez d'échantillons/classes pour entraîner un arbre sur cette sélection.")
        return

    if X.shape[1] > 500:
        st.caption(
            "Beaucoup de variables (tous les genres microbiens sont inclus, sans filtre) : "
            "la recherche automatique peut prendre 30-60 secondes, voire plus."
        )

    # ── Seed ─────────────────────────────────────────────────────────────────
    if "classif_seed_input" not in st.session_state:
        st.session_state["classif_seed_input"] = RANDOM_STATE

    col_seed, col_btn = st.columns([3, 1])

    with col_btn:
        st.write("")  # alignement vertical avec le number_input
        if st.button("Graine aléatoire"):
            st.session_state["classif_seed_input"] = random.randint(0, 999_999)

    with col_seed:
        seed = st.number_input(
            "Seed (graine aléatoire)", min_value=0, max_value=999_999,
            step=1, key="classif_seed_input",
        )

    # ── Hyperparamètres ──────────────────────────────────────────────────────
    mode_hp = st.radio(
        "Hyperparamètres",
        ["Recherche automatique (GridSearchCV)", "Choix manuel"],
        horizontal=True,
    )

    params_manuels = None
    if mode_hp == "Choix manuel":
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            profondeur_options = ["Aucune limite", 3, 4, 5, 6, 7, 8, 10, 12]
            max_depth_choice = st.selectbox("max_depth", profondeur_options)
            max_depth = None if max_depth_choice == "Aucune limite" else max_depth_choice
            if max_depth_choice == "Aucune limite" and source in ("Microbiologie", "Fusion"):
                st.caption(
                    "⚠️ Avec autant de variables, un arbre sans limite de profondeur "
                    "risque d'être très lent à afficher (voire de faire planter la page)."
                )
        with c2:
            min_samples_split = st.slider("min_samples_split", 2, 20, 2)
        with c3:
            min_samples_leaf = st.slider("min_samples_leaf", 1, 10, 1)
        with c4:
            criterion = st.selectbox("criterion", ["gini", "entropy"])
        params_manuels = {
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "criterion": criterion,
        }

    signature = (source, typologie, inclure_texture, mode_hp, str(params_manuels), seed)

    if st.button("▶️ Entraîner l'arbre"):
        if mode_hp == "Choix manuel":
            with st.spinner("Entraînement de l'arbre..."):
                best_dt, acc, y_test, y_pred, best_params = _entrainer_manuel(X, Y, params_manuels, seed)
        else:
            with st.spinner("Entraînement de l'arbre (GridSearchCV)..."):
                best_dt, acc, y_test, y_pred, best_params = _rechercher_hyperparametres(X, Y, seed)
        st.session_state["classif_signature"] = signature
        st.session_state["classif_resultats"] = (best_dt, acc, y_test, y_pred, best_params)

    if st.session_state.get("classif_signature") != signature:
        st.info("Clique sur ▶️ Entraîner l'arbre pour lancer le calcul sur cette sélection.")
        return

    best_dt, acc, y_test, y_pred, best_params = st.session_state["classif_resultats"]

    st.markdown(f"**Accuracy (test) : {acc:.3f}** — seed utilisé : `{seed}`")

    # Signale explicitement les sites jamais prédits sur le test set : sans
    # ça, l'UndefinedMetricWarning de sklearn (précision = 0.0 forcée) reste
    # invisible côté utilisateur et l'accuracy globale peut paraître
    # trompeusement bonne malgré un site totalement raté.
    classes_absentes_pred = set(y_test.unique()) - set(y_pred)
    if classes_absentes_pred:
        st.warning(
            f"⚠️ Le modèle n'a jamais prédit : {', '.join(sorted(classes_absentes_pred))} "
            f"sur cette sélection ({len(X)} échantillons, {Y.nunique()} sites) — "
            "l'accuracy globale peut être trompeuse."
        )

    with st.expander("Hyperparamètres utilisés"):
        st.json(best_params)

    with st.expander("Rapport de classification"):
        st.text(classification_report(y_test, y_pred, zero_division=0))

    importances = pd.Series(best_dt.feature_importances_, index=X.columns)
    importances = importances[importances > 0].sort_values(ascending=False)

    profondeur_reelle = best_dt.get_depth()
    profondeur_affichee = min(profondeur_reelle, MAX_DEPTH_AFFICHAGE)
    if profondeur_reelle > MAX_DEPTH_AFFICHAGE:
        st.caption(
            f"ℹ️ L'arbre entraîné a une profondeur de {profondeur_reelle} niveaux ; "
            f"seuls les {MAX_DEPTH_AFFICHAGE} premiers sont affichés ci-dessous "
            "(les prédictions/l'accuracy, elles, utilisent bien l'arbre complet)."
        )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7), gridspec_kw={"width_ratios": [3, 1]})
    plot_tree(
        best_dt, feature_names=list(X.columns), class_names=sorted(Y.unique()),
        filled=True, rounded=True, precision=2, fontsize=7, ax=ax1,
        max_depth=profondeur_affichee,
    )
    ax1.set_title(f"Arbre — {source} / {typologie} (profondeur réelle={profondeur_reelle})", fontsize=11)

    importances.head(20).plot(kind="barh", ax=ax2, color="steelblue")
    ax2.invert_yaxis()
    ax2.set_title(f"Feature importances (top {min(20, len(importances))})", fontsize=11)
    st.pyplot(fig)