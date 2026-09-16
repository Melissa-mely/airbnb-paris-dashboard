"""Chargement et nettoyage partagés entre les pages du dashboard.

Centralisé ici pour que app.py et pages/*.py utilisent exactement le même
nettoyage et les mêmes filtres (cohérence des chiffres affichés).
"""

import pandas as pd
import streamlit as st

# Fourchette de prix jugée réaliste pour une location courte durée à Paris.
# Sert à écarter les valeurs aberrantes (ex: 97 000 €/nuit) des graphiques,
# sans les supprimer du fichier source.
PRICE_MIN, PRICE_MAX = 10, 2000

# Échelle de couleur unique utilisée sur tous les graphiques du dashboard :
# vert = favorable à l'investisseur, rouge = défavorable. Appliquée à des
# métriques "plus c'est bas mieux c'est" (prix, concurrence, score) pour que
# la lecture couleur reste cohérente d'une page à l'autre.
COLOR_SCALE = "RdYlGn_r"


@st.cache_data
def load_data(path: str = "listings.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # neighbourhood_group est vide à 100 % sur ce dataset Paris : on l'ignore
    # et on utilise neighbourhood (= arrondissement) comme granularité géo.
    df = df.drop(columns=["neighbourhood_group"])

    # price est parfois vide (~38% des lignes) : on force le type numérique,
    # les valeurs manquantes deviennent NaN et sont donc exclues des calculs
    # de médiane/moyenne (pandas ignore les NaN par défaut) plutôt qu'imputées.
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    return df


def sidebar_filters(df: pd.DataFrame):
    """Filtres communs affichés dans la sidebar de chaque page.

    Utilise des clés de widget fixes (key=...) pour que la sélection reste
    la même quand on navigue entre les pages du dossier pages/.
    """
    st.sidebar.header("Filtres")

    room_types = st.sidebar.multiselect(
        "Type de logement",
        options=sorted(df["room_type"].unique()),
        default=sorted(df["room_type"].unique()),
        key="room_types",
    )

    neighbourhoods = st.sidebar.multiselect(
        "Arrondissement",
        options=sorted(df["neighbourhood"].unique()),
        default=sorted(df["neighbourhood"].unique()),
        key="neighbourhoods",
    )

    price_range = st.sidebar.slider(
        "Fourchette de prix (€/nuit)",
        min_value=PRICE_MIN,
        max_value=PRICE_MAX,
        value=(PRICE_MIN, PRICE_MAX),
        step=10,
        key="price_range",
    )

    return room_types, neighbourhoods, price_range


def filter_data(df: pd.DataFrame, room_types, neighbourhoods, price_range) -> pd.DataFrame:
    mask = (
        df["room_type"].isin(room_types)
        & df["neighbourhood"].isin(neighbourhoods)
        & df["price"].between(price_range[0], price_range[1])
    )
    return df[mask]


def paris_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Référence Paris entière (prix nettoyé uniquement), pour les comparaisons
    des KPIs face à la sélection filtrée par l'utilisateur."""
    return df[df["price"].between(PRICE_MIN, PRICE_MAX)]


# Nombre minimal d'annonces pour qu'un arrondissement soit inclus dans un
# classement : en dessous, le prix médian/l'occupation deviennent trop
# instables (quelques annonces atypiques suffisent à faire basculer le rang).
MIN_LISTINGS_FOR_RANKING = 30


def neighbourhood_summary(df: pd.DataFrame, min_listings: int = 0) -> pd.DataFrame:
    """Agrège les 3 KPIs par arrondissement.

    `jours_occupes_proxy` = 365 - disponibilité moyenne affichée. On l'utilise
    plutôt que la disponibilité brute car, dans ce dataset, les quartiers
    centraux et chers affichent PLUS de jours disponibles (moins occupés) que
    les quartiers périphériques bon marché : la disponibilité brute mesurait
    donc l'inverse de ce qu'on veut montrer (occupation/demande, pas de la
    place libre pour un nouvel entrant). C'est un proxy, pas un taux de
    réservation réel (un jour bloqué au calendrier n'est pas forcément loué).
    """
    summary = (
        df.groupby("neighbourhood")
        .agg(
            prix_median=("price", "median"),
            jours_occupes_proxy=("availability_365", lambda s: 365 - s.mean()),
            nb_concurrents=("id", "count"),
        )
        .round(0)
        .reset_index()
    )
    if min_listings:
        summary = summary[summary["nb_concurrents"] >= min_listings]
    return summary
