"""
core/constants.py

Constantes partagées entre les pages de l'application : sites, typologies,
ordre des saisons, graine aléatoire, etc.
"""

RANDOM_STATE = 42

TYPOLOGIES_LABELS = {
    "FRESHWATER": "Eau douce",
    "BRACKISH": "Eau saumâtre",
    "SALTED": "Eau salée"
}

SEASON_ORDER = {
    "AUTUMN_2020": 1,
    "SPRING_2021": 2,
    "SUMMER_2021": 3,
    "AUTUMN_2021": 4,
}

SEASON_LABELS = {v: k for k, v in SEASON_ORDER.items()}

SEASON_COLORS = {
    "AUTUMN_2020": "#E69F00",
    "SPRING_2021": "#56B4E9",
    "SUMMER_2021": "#009E73",
    "AUTUMN_2021": "#CC79A7",
}

COLS_TO_REMOVE = [
    "Sample_ID", "Site", "Season", "Typology", "Replicate",
    "Localisation_X", "Localisation_Y", "Conductivity",
    "Date", "Heure", "Se",
    "1,3,5-TriCB", "1,2,4-TriCB", "1,2,3-TriCB",
    "HCBD", "Dichlorvos", "PeCBz",
    "a-HCH", "HCB", "g-HCH", "b-HCH", "d-HCH",
    "Heptachlor ", "2,4'-Dicofol", "oxychlordane", "4,4'-Dicofol",
    "Heptachlor epoxyde cis", "Heptachlor epoxyde trans", "o,p-DDE",
    "g-chlordane", "Trans nanochlor", "a-endosulfan", "a-chlordane",
    "p,p-DDE", "Dieldrin", "o,p-DDD", "o,p-DDT",
    "Endrin", "cis-nanochlor", "b-endosulfan",
    "p,p-DDD", "quinoxyfen ", "p,p-DDT",
    "endosulfan sulfate", " mirex ", "cypermethrine"
]

TEXTURE_COLS = ["Clay", "Silt", "Sand"]

FEATURES_CHIMIQUES = ["As", "Al", "Cd", "Cu", "NO2", "Ni", "PO4", "pH", "Pb", "Salinity", "Total_Hydrocarbon"]

VARIABLES_CHIMIQUES = {
    "Arsenic":           {"col": "As",                "titre": "Arsenic"},
    "Aliminium":         {"col": "Al",                "titre": "Aliminium"},
    "Cadmium":           {"col": "Cd",                "titre": "Cadmium"},
    "Cuivre":            {"col": "Cu",                "titre": "Cuivre"},
    "Dioxyde d'Azote":   {"col": "NO2",               "titre": "Dioxyde d'Azote"},
    "Nickel":            {"col": "Ni",                "titre": "Nickel"},
    "Phosphate":         {"col": "PO4",               "titre": "Phosphate"},
    "pH":                {"col": "pH",                "titre": "pH"},
    "Plomb":             {"col": "Pb",                "titre": "Plomb"},
    "Salinité":          {"col": "Salinity",          "titre": "Salinité"},
    "Total Hydrocarbon": {"col": "Total_Hydrocarbon", "titre": "Total Hydrocarbon"},
}

GENRES_CIBLES = [
    "unknown_Gallionellaceae",
    "g__uncultured_Rhodobacteraceae",
    "g__Haladaptatus",
    "unknown_Methylophilaceae",
    "g__Dinghuibacter",
    "g__Sediminispirochaeta",
    "g__Gallionella",
    "g__OPB41",
    "g__Sulfurimonas",
    "g__Cryptosporidium",
    "g__Ellin6067",
    "g__ML635J-40_aquatic_group",
    "g__Lokiarchaeia",
    "g__Thalassiosira",
    "g__Asgardarchaeota",
    "g__Halochromatium",
    "g__Flavobacteriaceae",
    "g__B1-7BS",
    "unknown_Desulfocapsaceae",
    "g__uncultured_Geminicoccaceae",
    "g__Vermamoeba",
]




