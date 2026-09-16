# Cadrage — Dashboard Airbnb Paris

**Groupe** : Melissa, Sonia, Kennedy — Data et IA MD4

## Message clé

> Les arrondissements périphériques (Gobelins, Ménilmontant, Buttes-Chaumont) offrent un
> meilleur rapport prix/occupation que le centre parisien, plus cher sans être plus demandé.

## Audience cible

Un particulier qui envisage de mettre un bien en location sur Airbnb à Paris et hésite sur
le quartier et le type de logement à privilégier.

## KPIs retenus

| KPI | Vanity ou actionable ? | Justification |
|---|---|---|
| **Prix médian par quartier** | Actionable | Indique le revenu potentiel par nuit dans chaque arrondissement. La médiane est utilisée plutôt que la moyenne car les prix contiennent des valeurs aberrantes (jusqu'à 97 000 €/nuit) qui fausseraient une moyenne. |
| **Occupation estimée (365 − disponibilité)** | Actionable | Proxy de demande locative par quartier. Attention : la disponibilité brute (`availability_365`) est en réalité **plus élevée** dans les quartiers centraux et chers que dans les quartiers périphériques bon marché — on l'inverse donc (365 − disponibilité) pour obtenir un indicateur qui va dans le sens du message (plus de jours occupés = plus de demande), au lieu d'un indicateur qui contredirait le prix. |
| **Nombre de concurrents actifs par quartier** | Actionable | Mesure l'intensité concurrentielle locale. Volontairement calculé par quartier (et non comme un total Paris, qui serait une vanity metric sans valeur décisionnelle). |

## Nettoyage des données appliqué

- **Prix manquant (~38 % des lignes)** : exclu des calculs de KPIs liés au prix plutôt
  qu'imputé, pour ne pas inventer de donnée (principe d'honnêteté).
- **Prix aberrants** : conservés dans le jeu de données mais exclus des visualisations de
  prix via un filtre 10 € – 2000 €, pour éviter qu'un point extrême (97 000 €) n'écrase
  l'échelle des graphiques.
- **`neighbourhood_group`** : colonne vide à 100 %, ignorée. `neighbourhood` (= arrondissement)
  est utilisé comme seule granularité géographique.
- **Arrondissements sous-échantillonnés** : exclus des classements (pages Comparateur et
  Top opportunités) en dessous de 30 annonces actives, pour éviter qu'un petit échantillon
  ne fausse le prix médian ou le score.

## Structure du dashboard

- **Sidebar** : filtres sur `room_type` et `neighbourhood`, + un curseur de fourchette de prix.
- **Page 1 — Vue synthèse** : zone KPIs (3 indicateurs contextualisés centre vs périphérie)
  + carte des arrondissements colorée par prix, + prix médian par quartier.
- **Page 2 — Comparateur de quartiers** : détail par arrondissement (prix, occupation estimée,
  concurrence), réactif aux filtres de la sidebar.
- **Page 3 — Top opportunités** : classement des arrondissements par score combiné
  (prix + occupation + concurrence), conclusion directement actionnable pour l'audience cible.
