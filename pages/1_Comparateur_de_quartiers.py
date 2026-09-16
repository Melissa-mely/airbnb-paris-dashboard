import plotly.express as px
import streamlit as st

from data_utils import filter_data, load_data, neighbourhood_summary, sidebar_filters

st.set_page_config(page_title="Comparateur de quartiers", page_icon="📊", layout="wide")

st.title("📊 Comparateur de quartiers")
st.markdown(
    "Détail par arrondissement pour affiner le choix : prix, occupation estimée et "
    "intensité concurrentielle, réactifs aux filtres de la sidebar."
)

df = load_data()
room_types, neighbourhoods, price_range = sidebar_filters(df)
filtered = filter_data(df, room_types, neighbourhoods, price_range)

if filtered.empty:
    st.warning("Aucune annonce ne correspond à cette sélection de filtres.")
    st.stop()

summary = (
    neighbourhood_summary(filtered)
    .sort_values("prix_median")
    .rename(columns={"neighbourhood": "Arrondissement"})
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Prix médian par arrondissement")
    fig_price = px.bar(
        summary,
        x="prix_median",
        y="Arrondissement",
        orientation="h",
        color="prix_median",
        color_continuous_scale="RdYlGn_r",
        labels={"prix_median": "Prix médian (€/nuit)"},
        height=550,
    )
    fig_price.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_price, use_container_width=True)

with col2:
    st.subheader("Nombre de concurrents actifs")
    fig_comp = px.bar(
        summary.sort_values("nb_concurrents"),
        x="nb_concurrents",
        y="Arrondissement",
        orientation="h",
        color="nb_concurrents",
        color_continuous_scale="Blues",
        labels={"nb_concurrents": "Annonces concurrentes"},
        height=550,
    )
    fig_comp.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_comp, use_container_width=True)

st.subheader("Détail chiffré")
st.dataframe(
    summary.rename(
        columns={
            "prix_median": "Prix médian (€)",
            "jours_occupes_proxy": "Occupation estimée (j/an)",
            "nb_concurrents": "Concurrents actifs",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
st.caption(
    "Occupation estimée = 365 − disponibilité moyenne affichée (proxy de demande, "
    "pas un taux de réservation réel)."
)
