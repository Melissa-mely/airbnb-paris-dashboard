import pandas as pd
import plotly.express as px
import streamlit as st

from data_utils import filter_data, load_data, paris_baseline, sidebar_filters

st.set_page_config(page_title="Où louer à Paris ?", page_icon="🏠", layout="wide")

st.title("🏠 Où louer sur Airbnb à Paris sans se heurter à un marché déjà saturé ?")
st.markdown(
    "Les arrondissements **périphériques** affichent des prix nettement plus bas et "
    "plus de disponibilité que le centre, déjà cher et occupé en continu."
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

avg_availability = filtered["availability_365"].mean()
avg_availability_paris = baseline["availability_365"].mean()

n_competitors = len(filtered)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Prix médian / nuit",
    f"{median_price:.0f} €",
    delta=f"{median_price - median_price_paris:+.0f} € vs médiane Paris",
    delta_color="inverse",
)
col2.metric(
    "Disponibilité moyenne",
    f"{avg_availability:.0f} j/an",
    delta=f"{avg_availability - avg_availability_paris:+.0f} j vs moyenne Paris",
)
col3.metric("Concurrents actifs (sélection)", f"{n_competitors:,}".replace(",", " "))

st.caption(
    "Comparaisons faites contre la médiane/moyenne Paris entière (prix nettoyé 10-2000€), "
    "indépendamment des filtres, pour situer la sélection actuelle."
)

st.divider()

# --- Zone détail : carte + prix médian par quartier -----------------------
map_col, chart_col = st.columns([1, 1])

with map_col:
    st.subheader("Répartition géographique (échantillon)")
    sample = filtered.sample(min(4000, len(filtered)), random_state=0).copy()

    # Découpage en 3 tranches de prix pour un canal couleur simple à lire
    # (vert = abordable, orange = moyen, rouge = cher), plutôt qu'un dégradé
    # continu difficile à interpréter sur une petite carte.
    tiers = pd.qcut(sample["price"], q=3, labels=["Abordable", "Moyen", "Cher"], duplicates="drop")
    color_map = {"Abordable": "#2ecc71", "Moyen": "#f39c12", "Cher": "#e74c3c"}
    sample["couleur"] = tiers.map(color_map)

    st.map(sample, latitude="latitude", longitude="longitude", color="couleur", size=25)
    st.caption("🟢 Abordable · 🟠 Moyen · 🔴 Cher — tercile de prix sur la sélection filtrée.")

with chart_col:
    st.subheader("Prix médian par arrondissement")
    by_neigh = (
        filtered.groupby("neighbourhood")["price"]
        .median()
        .sort_values()
        .reset_index()
    )
    fig_bar = px.bar(
        by_neigh,
        x="price",
        y="neighbourhood",
        orientation="h",
        color="price",
        color_continuous_scale="RdYlGn_r",
        labels={"price": "Prix médian (€/nuit)", "neighbourhood": ""},
        height=480,
    )
    fig_bar.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.caption(
    "➡️ Voir la page **Comparateur de quartiers** pour le détail chiffré par arrondissement."
)
