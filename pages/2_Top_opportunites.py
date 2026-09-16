import plotly.express as px
import streamlit as st

from data_utils import (
    COLOR_SCALE,
    MIN_LISTINGS_FOR_RANKING,
    active_filters_caption,
    color_domains,
    filter_data,
    load_data,
    neighbourhood_summary,
    sidebar_filters,
    style_minimal,
)

st.set_page_config(page_title="Top opportunités", page_icon="🏆", layout="wide")

st.title("🏆 Top opportunités : où se lancer en priorité ?")
st.markdown(
    "Classement des arrondissements combinant **prix**, **occupation estimée** et "
    "**concurrence** en un score unique, pour répondre directement à la question "
    "posée par ce dashboard."
)

st.info(
    "**Sur quelle base ce classement est-il fait ?** Chaque arrondissement est classé "
    "séparément sur 3 critères — prix médian (le plus bas gagne), occupation estimée "
    "(la plus haute gagne), nombre de concurrents actifs (le plus bas gagne) — puis on "
    "fait la **moyenne des 3 rangs** obtenus. Un score de 1 signifierait 1er sur les "
    "3 critères à la fois ; plus le score est bas, meilleure est l'opportunité. Les "
    f"3 critères comptent à poids égal, et les arrondissements avec moins de "
    f"{MIN_LISTINGS_FOR_RANKING} annonces actives sont exclus (échantillon trop petit "
    "pour un prix médian fiable)."
)

df = load_data()
domains = color_domains(df)
room_types, neighbourhoods, price_range = sidebar_filters(df)
filtered = filter_data(df, room_types, neighbourhoods, price_range)

if filtered.empty:
    st.warning("Aucune annonce ne correspond à cette sélection de filtres.")
    st.stop()

st.caption(active_filters_caption(df, room_types, neighbourhoods, price_range))

summary = neighbourhood_summary(filtered, min_listings=MIN_LISTINGS_FOR_RANKING)

if summary.empty:
    st.warning(
        f"Aucun arrondissement n'atteint le seuil de {MIN_LISTINGS_FOR_RANKING} annonces "
        "avec cette sélection de filtres — élargissez les filtres pour voir un classement."
    )
    st.stop()

# Score = moyenne de 3 rangs (1 = meilleur sur ce critère). On utilise des
# rangs plutôt qu'une moyenne pondérée de valeurs brutes : les 3 KPIs ont des
# unités différentes (€, jours, nombre d'annonces) qu'on ne peut pas sommer
# directement sans choisir arbitrairement des poids.
summary["rang_prix"] = summary["prix_median"].rank(ascending=True)
summary["rang_occupation"] = summary["jours_occupes_proxy"].rank(ascending=False)
summary["rang_concurrence"] = summary["nb_concurrents"].rank(ascending=True)
summary["score"] = (summary["rang_prix"] + summary["rang_occupation"] + summary["rang_concurrence"]) / 3
summary = summary.sort_values("score").reset_index(drop=True)

st.subheader("Top 3 recommandés")
top3 = summary.head(3)
cols = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
for col, (_, row), medal in zip(cols, top3.iterrows(), medals):
    with col:
        st.markdown(f"### {medal} {row['neighbourhood']}")
        st.metric("Prix médian", f"{row['prix_median']:.0f} €")
        st.metric("Occupation estimée", f"{row['jours_occupes_proxy']:.0f} j/an")
        st.metric("Concurrents actifs", f"{row['nb_concurrents']:.0f}")

st.divider()

st.subheader("Classement complet")
fig_score = px.bar(
    summary.sort_values("score", ascending=False),
    x="score",
    y="neighbourhood",
    orientation="h",
    color="score",
    color_continuous_scale=COLOR_SCALE,
    range_color=domains["score"],
    labels={"score": "Score (rang moyen, plus bas = mieux)", "neighbourhood": ""},
    height=550,
)
style_minimal(fig_score)
st.plotly_chart(fig_score, use_container_width=True)

st.dataframe(
    summary[["neighbourhood", "prix_median", "jours_occupes_proxy", "nb_concurrents", "score"]].rename(
        columns={
            "neighbourhood": "Arrondissement",
            "prix_median": "Prix médian (€)",
            "jours_occupes_proxy": "Occupation estimée (j/an)",
            "nb_concurrents": "Concurrents actifs",
            "score": "Score (rang moyen, plus bas = mieux)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    f"Arrondissements avec moins de {MIN_LISTINGS_FOR_RANKING} annonces exclus du classement "
    "(échantillon trop petit pour un prix médian fiable). Score = moyenne des rangs sur les "
    "3 KPIs, à poids égal entre eux ; occupation estimée = 365 − disponibilité affichée (proxy)."
)
