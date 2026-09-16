# Cadrage — Dashboard Airbnb Paris

**Groupe** : Melissa, Sonia, Kennedy — Data et IA MD4

## Message clé

> Les arrondissements périphériques (Ménilmontant, Buttes-Chaumont, Gobelins) offrent un
> meilleur point d'entrée sur le marché Airbnb parisien que le centre, déjà cher et saturé.

## Audience cible

Un particulier qui envisage de mettre un bien en location sur Airbnb à Paris et hésite sur
le quartier et le type de logement à privilégier.

## KPIs retenus

| KPI | Vanity ou actionable ? | Justification |
|---|---|---|
| **Prix médian par quartier** | Actionable | Indique le revenu potentiel par nuit dans chaque arrondissement. La médiane est utilisée plutôt que la moyenne car les prix contiennent des valeurs aberrantes (jusqu'à 97 000 €/nuit) qui fausseraient une moyenne. |
| **Disponibilité moyenne sur 365 jours** | Actionable | Proxy de saturation du marché : un quartier où les annonces affichent 0 jour disponible est déjà occupé par des locations tournant en continu, donc plus difficile à pénétrer pour un nouvel entrant. |
| **Nombre de concurrents actifs par quartier** | Actionable | Mesure l'intensité concurrentielle locale. Volontairement calculé par quartier (et non comme un total Paris, qui serait une vanity metric sans valeur décisionnelle). |

## Nettoyage des données appliqué

- **Prix manquant (~38 % des lignes)** : exclu des calculs de KPIs liés au prix plutôt
  qu'imputé, pour ne pas inventer de donnée (principe d'honnêteté).
- **Prix aberrants** : conservés dans le jeu de données mais exclus des visualisations de
  prix via un filtre 10 € – 2000 €, pour éviter qu'un point extrême (97 000 €) n'écrase
  l'échelle des graphiques.
- **`neighbourhood_group`** : colonne vide à 100 %, ignorée. `neighbourhood` (= arrondissement)
  est utilisé comme seule granularité géographique.

## Structure du dashboard

- **Sidebar** : filtres sur `room_type` et `neighbourhood`, + un curseur de fourchette de prix.
- **Page 1 — Vue synthèse** : zone KPIs (3 indicateurs contextualisés centre vs périphérie)
  + carte des arrondissements colorée par prix médian.
- **Page 2 — Comparateur de quartiers** : graphique en barres du prix médian par quartier et
  tableau détaillé, réactifs aux filtres de la sidebar.
