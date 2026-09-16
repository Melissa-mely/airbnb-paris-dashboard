import plotly.express as px
import streamlit as st

from data_utils import (
    COLOR_SCALE,
    filter_data,
    load_data,
    neighbourhood_summary,
    paris_baseline,
    sidebar_filters,
    value_to_hex,
)

st.set_page_config(page_title="Où louer à Paris ?", page_icon="🏠", layout="wide")

st.title("🏠 Où louer sur Airbnb à Paris pour le meilleur rapport prix/occupation ?")
st.markdown(
    "Les arrondissements **périphériques** combinent des prix nettement plus bas et une "
    "occupation estimée au moins aussi forte que le centre, pourtant bien plus cher."
)

df = load_data()
room_types, neighbourhoods, price_range = sidebar_filters(df)

filtered = filter_data(df, room_types, neighbourhoods, price_range)
baseline = paris_baseline(df)

if filtered.empty:
    st.warning("Aucune annonce ne correspond à cette sélection de filtres.")
    st.stop()

# --- Zone KPIs -----------------------------------------------------------
median_price = filtered["price"].median()
median_price_paris = baseline["price"].median()

occupied_days = 365 - filtered["availability_365"].mean()
occupied_days_paris = 365 - baseline["availability_365"].mean()

n_competitors = len(filtered)
# Concurrents moyens par quartier sélectionné, comparé à la moyenne Paris
# (total Paris / nb d'arrondissements) : une sélection sur 1 seul quartier
# se compare ainsi équitablement à "un quartier parisien typique".
avg_competitors_per_neigh = n_competitors / filtered["neighbourhood"].nunique()
avg_competitors_per_neigh_paris = len(baseline) / baseline["neighbourhood"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric(
    "Prix médian / nuit",
    f"{median_price:.0f} €",
    delta=f"{median_price - median_price_paris:+.0f} € vs médiane Paris",
    delta_color="inverse",
)
col2.metric(
    "Occupation estimée",
    f"{occupied_days:.0f} j/an",
    delta=f"{occupied_days - occupied_days_paris:+.0f} j vs moyenne Paris",
)
col3.metric(
    "Concurrents actifs (sélection)",
    f"{n_competitors:,}".replace(",", " "),
    delta=f"{avg_competitors_per_neigh - avg_competitors_per_neigh_paris:+.0f} / quartier vs moyenne Paris",
    delta_color="inverse",
)

st.caption(
    "Comparaisons faites contre la médiane/moyenne Paris entière (prix nettoyé 10-2000€), "
    "indépendamment des filtres, pour situer la sélection actuelle. Occupation estimée = "
    "365 − disponibilité affichée (proxy : un jour bloqué au calendrier n'est pas "
    "forcément loué, mais reste un bon indicateur de demande relative entre quartiers). "
    "Concurrents actifs comparés en moyenne par quartier, pour rester équitable quel que "
    "soit le nombre d'arrondissements sélectionnés."
)

st.divider()

# --- Zone détail : carte + prix médian par quartier -----------------------
map_col, chart_col = st.columns([1, 1])

with map_col:
    st.subheader("Répartition géographique (échantillon)")
    sample = filtered.sample(min(4000, len(filtered)), random_state=0).copy()

    # Dégradé de bleu clair -> foncé selon le prix (une seule teinte, cohérente
    # avec les autres graphiques). Clippé à 600€ : au-delà, quelques annonces
    # très chères écraseraient le dégradé pour tout le reste des points.
    sample["couleur"] = value_to_hex(sample["price"], price_range[0], min(price_range[1], 600))

    st.map(sample, latitude="latitude", longitude="longitude", color="couleur", size=25)
    st.caption("Plus foncé = plus cher (dégradé de prix, clippé à 600€/nuit pour la lisibilité).")

with chart_col:
    st.subheader("Prix médian par arrondissement")
    by_neigh = neighbourhood_summary(filtered).sort_values("prix_median")
    fig_bar = px.bar(
        by_neigh,
        x="prix_median",
        y="neighbourhood",
        orientation="h",
        color="prix_median",
        color_continuous_scale=COLOR_SCALE,
        labels={"prix_median": "Prix médian (€/nuit)", "neighbourhood": ""},
        height=480,
    )
    fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.caption(
    "➡️ Voir la page **Comparateur de quartiers** pour le détail chiffré par arrondissement."
)
