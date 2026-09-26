"""
scripts/train_regression_model.py

Entraîne le modèle de régression Environnement -> Abondance microbienne
et le sauvegarde au format joblib pour être chargé
par l'application Streamlit sans ré-entraînement à chaque lancement.

Modèle retenu : MultiOutputRegressor(RandomForestRegressor).

Usage (depuis la racine du repo) :
    python scripts/train_regression_model.py
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.multioutput import MultiOutputRegressor

# Permet de lancer le script depuis n'importe quel dossier (ajoute la racine
# du repo au sys.path pour que "core.xxx" soit importable).
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.constants import FEATURES_CHIMIQUES, GENRES_CIBLES, RANDOM_STATE
from core.data_loader import load_fusion_all

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "rf_multioutput.pkl"


def build_X_Y():
    """X = 11 paramètres chimiques ciblés (mêmes variables que le graphique
    radar), Y = abondances des 21 genres cibles."""
    fusion_all = load_fusion_all()

    Y = fusion_all[GENRES_CIBLES].apply(pd.to_numeric, errors="coerce").fillna(0)

    X = fusion_all[FEATURES_CHIMIQUES].apply(pd.to_numeric, errors="coerce")
    X = X.fillna(X.median())  # médiane plutôt que 0 pour les valeurs manquantes afin de mieux simuler les prédictions

    return X, Y


def main():
    X, Y = build_X_Y()
    print(f"X : {X.shape[0]} échantillons x {X.shape[1]} variables")
    print(f"Y : {Y.shape[1]} genres cibles")

    model = MultiOutputRegressor(
        RandomForestRegressor(
            n_estimators=300,
            max_features="sqrt",
            random_state=RANDOM_STATE,
        )
    )

    # ── Validation croisée (KFold, adapté au petit échantillon n≈96) ────────
    cv = KFold(n_splits=7, shuffle=True, random_state=RANDOM_STATE)
    y_pred_cv = cross_val_predict(model, X, Y, cv=cv)

    mae_par_genre = pd.Series(
        mean_absolute_error(Y, y_pred_cv, multioutput="raw_values"),
        index=Y.columns,
    ).sort_values(ascending=False)

    print("\nMAE par genre (validation croisée, KFold=7) :")
    print(mae_par_genre)

    # ── Entraînement final sur l'ensemble des données disponibles ───────────
    model.fit(X, Y)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_names": list(X.columns),
            "target_names": list(Y.columns),
            "mae_cv": mae_par_genre.to_dict(),
        },
        MODEL_PATH,
    )
    print(f"\nModèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    main()