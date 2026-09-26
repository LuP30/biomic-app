# BIOMIC-APP

Application Streamlit de visualisation et d'analyse du suivi saisonnier des milieux humides, développée dans le cadre d'un stage de Master à l'UPPA, à partir des données du projet [BIOMIC](https://www.biomic-project.eu/wp-content/uploads/2023/05/index2.html).

L'application explore les liens entre paramètres physico-chimiques, texture des sédiments et composition microbienne sur 8 sites suivis sur 4 saisons.

## Objectif

Produire un graphe de corrélation entre groupes microbiens (réseau trophique), en s'appuyant sur une chaîne d'analyses :

1. **Arbre de décision (Environnement)** — `Y = Site`, `X = paramètres environnementaux`, pour identifier les variables qui discriminent le plus les sites.
2. **Séparation par typologie d'eau** — eau douce / saumâtre / salée.
3. **Arbre de décision (Microbiologie / Fusion)** — même logique que l'étape 1, avec les abondances microbiennes comme variables.
4. **Régression (Random Forest multi-sortie)** — prédiction de l'abondance des genres microbiens à partir des paramètres environnementaux.
5. **Réseau trophique** — graphe de corrélation entre genres microbiens (visualisation avec un seuil de corrélation ajustable).

## Structure du projet

```
biomic_app/
├── app.py                          # Point d'entrée Streamlit
├── core/
│   ├── constants.py                 # Constantes partagées (sites, typologies, saisons, genres cibles...)
│   └── data_loader.py               # Chargement, nettoyage et fusion des données (mis en cache)
├── pages_app/
│   ├── accueil.py                   # Page d'accueil avec découverte des données
│   ├── exploration.py               # Exploration des données avec différents graphiques
│   ├── classification.py            # Exemple de la méthode utilisé pour récupérer les variables pour faire le réseau trophique
│   ├── regression.py                # Simulation via prédiction avec des forêts aléatoires sur le réseau trophique
│   └── reseau_trophique.py          # Visualisation du réseau de corrélation (réseau trophique)
├── graphs/
│   ├── carte.py                     # Carte interactive des sites (Folium)
│   ├── graph_evol.py                # Évolution temporelle par site
│   ├── graph_radar.py               # Comparaison multi-sites (graphique radar)
│   └── diag_ternaire.py             # Texture des sédiments (diagramme ternaire)
├── scripts/
│   └── train_regression_model.py    # Entraînement du modèle de forêt aléatoires
├── models/                          # Modèles entraînés (.pkl)
├── data/                            # Fichiers sources .xlsx 
├── environment.yml                  # Environnement conda (installation locale)
├── requirements.txt                 # Dépendances pip (déploiement Streamlit Cloud)
├── AUTHORS
├── README
└── LICENSE

```

## Données

Deux fichiers sources :

- `Metadata_suivi_saisonnier_18-12-2024.xlsx` — paramètres physico-chimiques, métaux, nutriments, texture des sédiments (feuilles `ALL_DATA` et `MOYENNES`).
- `Genus_table_occ5_ab-rel_all-org_16SA-B_18SE.xlsx` — abondances relatives de genres microbiens (feuilles `All_samples` et `Moyennes`).


## Installation

```bash
conda env create -f environment.yml
conda activate biomic_app
```

## Lancement

```bash
streamlit run app.py
```

## Licence

Distribué sous licence Apache 2.0 — voir [`LICENSE`](LICENSE).

## Auteur

Lucas PREVOT - Master 2 MIBD, Université de Pau et des Pays de l'Adour (UPPA).
