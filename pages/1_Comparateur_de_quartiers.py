import plotly.express as px
import streamlit as st

from data_utils import COLOR_SCALE, color_domains, filter_data, load_data, neighbourhood_summary, sidebar_filters

st.set_page_config(page_title="Comparateur de quartiers", page_icon="📊", layout="wide")

st.title("📊 Quel arrondissement offre le meilleur compromis prix / occupation / concurrence ?")
st.markdown(
    "Le prix seul ne suffit pas : détail par arrondissement pour arbitrer entre prix, "
    "occupation estimée et intensité concurrentielle, réactif aux filtres de la sidebar."
)

df = load_data()
domains = color_domains(df)
room_types, neighbourhoods, price_range = sidebar_filters(df)
filtered = filter_data(df, room_types, neighbourhoods, price_range)

if filtered.empty:
    st.warning("Aucune annonce ne correspond à cette sélection de filtres.")
    st.stop()

summary = neighbourhood_summary(filtered).sort_values("prix_median")

# --- Zone KPIs -------------------------------------------------------------
cheapest = summary.loc[summary["prix_median"].idxmin()]
busiest = summary.loc[summary["jours_occupes_proxy"].idxmax()]
price_spread = summary["prix_median"].max() - summary["prix_median"].min()

k1, k2, k3 = st.columns(3)
k1.metric(
    "Écart de prix entre quartiers affichés",
    f"{price_spread:.0f} €",
    f"{summary['prix_median'].min():.0f} € – {summary['prix_median'].max():.0f} €",
    delta_color="off",
)
k2.metric(
    "Quartier le + abordable",
    cheapest["neighbourhood"],
    f"{cheapest['prix_median']:.0f} €/nuit",
    delta_color="off",
)
k3.metric(
    "Quartier le + occupé",
    busiest["neighbourhood"],
    f"{busiest['jours_occupes_proxy']:.0f} j/an",
    delta_color="off",
)
st.caption(
    "KPIs calculés sur les arrondissements actuellement affichés (dépend des filtres "
    "sidebar), pour situer rapidement les extrêmes avant de lire le détail ci-dessous."
)

st.divider()

summary = summary.rename(columns={"neighbourhood": "Arrondissement"})
col1, col2 = st.columns(2)

with col1:
    st.subheader("Prix médian par arrondissement")
    fig_price = px.bar(
        summary,
        x="prix_median",
        y="Arrondissement",
        orientation="h",
        color="prix_median",
        color_continuous_scale=COLOR_SCALE,
        range_color=domains["prix_median"],
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
        color_continuous_scale=COLOR_SCALE,
        range_color=domains["nb_concurrents"],
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
