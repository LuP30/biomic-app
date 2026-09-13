"""
core/data_loader.py

Chargement et fusion des deux sources de données du suivi saisonnier des
milieux humides :
  - Metadata_suivi_saisonnier_18-12-2024.xlsx  (environnement)
  - Genus_table_occ5_ab-rel_all-org_16SA-B_18SE.xlsx  (abondances microbiennes)

6 fonctions publiques, chacune mise en cache indépendamment par Streamlit :
  - load_metadata_moyennes() / load_metadata_all()
  - load_genus_moyennes()    / load_genus_all()
  - load_fusion_moyennes()   / load_fusion_all()

"_moyennes" = 32 lignes Site x Saison (feuilles MOYENNES / Moyennes)
"_all"      = 96 échantillons individuels (feuilles ALL_DATA / All_samples)
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
META_FILE = DATA_DIR / "Metadata_suivi_saisonnier_18-12-2024.xlsx"
GENUS_FILE = DATA_DIR / "Genus_table_occ5_ab-rel_all-org_16SA-B_18SE.xlsx"

# Colonnes de contaminants avec valeurs censurées par un seuil de détection
# (ex: "< 0.4") donc on les supprime 
CENSORED_COLS = [
    "Se", "1,3,5-TriCB", "2,4'-Dicofol", "4,4'-Dicofol",
    "o,p-DDE", "p,p-DDE", "o,p-DDD", "o,p-DDT", "p,p-DDT", "cypermethrine",
]


# ── Helpers privés ──────────────────────────────────────────────────────────

def _to_numeric_censored(series):
    """Convertit '< X' en X/2 (demi seuil de détection). Convention à valider
    avec ton encadrant, comme pour l'IQS (ERL/ERM)."""
    def parse(v):
        if isinstance(v, str) and v.strip().startswith("<"):
            try:
                return float(v.strip("< ").strip()) / 2
            except ValueError:
                return None
        return v
    return pd.to_numeric(series.map(parse), errors="coerce")


def _clean_metadata(df):
    for col in CENSORED_COLS:
        if col in df.columns:
            df[col] = _to_numeric_censored(df[col])
    df["Site"] = df["Site"].str.upper()
    df["Season"] = df["Season"].str.upper()
    return df


def _transpose_genus(sheet):
    """Transpose la table de genres : lignes = échantillons, colonnes = genres."""
    df = pd.read_excel(GENUS_FILE, sheet_name=sheet)
    df = df.set_index("Genus").T
    df.index.name = "SampleCol"
    return df.reset_index()


# ── Metadata ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_metadata_moyennes():
    df = pd.read_excel(META_FILE, sheet_name="MOYENNES")
    return _clean_metadata(df)


@st.cache_data
def load_metadata_all():
    df = pd.read_excel(META_FILE, sheet_name="ALL_DATA")
    df = _clean_metadata(df)
    df["Sample_ID"] = df["Sample_ID"].str.upper()
    return df


# ── Genus ────────────────────────────────────────────────────────────────────

@st.cache_data
def load_genus_moyennes():
    genus = _transpose_genus("Moyennes")
    parsed = genus["SampleCol"].str.split("_", n=1, expand=True)
    genus["Site"] = parsed[0].str.upper()
    genus["Season"] = parsed[1].str.upper()
    return genus.drop(columns=["SampleCol"])


@st.cache_data
def load_genus_all():
    genus = _transpose_genus("All_samples")
    genus["Sample_ID"] = (
        genus["SampleCol"].str.replace(r"\.\d+$", "", regex=True).str.upper()
    )
    return genus.drop(columns=["SampleCol"])


# ── Fusion ───────────────────────────────────────────────────────────────────

@st.cache_data
def load_fusion_moyennes():
    """Jointure sur (Site, Season) : les identifiants texte diffèrent entre
    les deux fichiers à ce niveau (ST6_A20 vs St6_Autumn_2020)."""
    meta = load_metadata_moyennes()
    genus = load_genus_moyennes()
    return meta.merge(genus, on=["Site", "Season"], how="inner")


@st.cache_data
def load_fusion_all():
    """Jointure exacte sur Sample_ID (identique des deux côtés une fois
    nettoyé)."""
    meta = load_metadata_all()
    genus = load_genus_all()
    return meta.merge(genus, on="Sample_ID", how="inner")


def genus_columns(genus_df):
    """Liste des colonnes de genres (tout sauf les clés d'identification)."""
    id_cols = {"Sample_ID", "Site", "Season"}
    return [c for c in genus_df.columns if c not in id_cols]