# README

Ce dossier contient le mini-portail de visualisation autour des donnees RPG 2023.

**Source des données :** Les données du Registre Parcellaire Graphique (RPG) utilisées dans ce projet ont été téléchargées depuis [https://geoservices.ign.fr/rpg](https://geoservices.ign.fr/rpg).

Le point d'entree principal est [index.html](/c:/Users/natha/PycharmProjects/visu/projet/index.html). Les autres fichiers HTML correspondent soit a des visualisations finales, soit a des prototypes ou vues intermediaires.

## Vue d'ensemble

### Pages principales

| Fichier | Visualisation | Role |
| --- | --- | --- |
| [index.html](/c:/Users/natha/PycharmProjects/visu/projet/index.html) | Portail d'accueil | Menu principal qui renvoie vers les visualisations du projet. |
| [map.html](/c:/Users/natha/PycharmProjects/visu/projet/map.html) | Carte interactive France | Carte des parcelles avec filtres, recherche et heatmap. |
| [overview-france.html](/c:/Users/natha/PycharmProjects/visu/projet/overview-france.html) | Statistiques nationales | Vue nationale avec KPIs, carte choroplethe, classement des regions, top cultures et "Ferme France". |
| [cosmos-bubbles.html](/c:/Users/natha/PycharmProjects/visu/projet/cosmos-bubbles.html) | Modèles d'Exploitation | Compare les cultures par surface totale, taille moyenne des parcelles et nombre de parcelles. |
| [fragmentation-combined.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation-combined.html) | Tailles des parcelles | Combine atlas national, comparaison regionale et courbes de distribution des tailles. |
| [methodology.html](/c:/Users/natha/PycharmProjects/visu/projet/methodology.html) | Methodologie | Documentation du pipeline, des choix de design et des transformations. |

### Pages secondaires ou prototypes

| Fichier | Visualisation | Role |
| --- | --- | --- |
| [dashboard.html](/c:/Users/natha/PycharmProjects/visu/projet/dashboard.html) | Tableau de bord | Ancienne vue de synthese pilotee par [dashboard-script.js](/c:/Users/natha/PycharmProjects/visu/projet/dashboard-script.js). |
| [regions.html](/c:/Users/natha/PycharmProjects/visu/projet/regions.html) | Portraits des regions | Prototype de vue regionale. |
| [sunburst.html](/c:/Users/natha/PycharmProjects/visu/projet/sunburst.html) | Hierarchie des cultures | Prototype de lecture hierarchique des groupes et cultures. |
| [waffle.html](/c:/Users/natha/PycharmProjects/visu/projet/waffle.html) | Ferme France | Prototype specifique du waffle chart national. |
| [fragmentation.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation.html) | Atlas de la fragmentation | Version simple/ancienne autour du morcellement. |
| [fragmentation-regional.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation-regional.html) | Anatomie du morcellement | Vue regionale dediee au sujet fragmentation. |
| [distribution-curves.html](/c:/Users/natha/PycharmProjects/visu/projet/distribution-curves.html) | Distribution des tailles | Prototype des courbes de distribution. |
| [methodology_ref.html](/c:/Users/natha/PycharmProjects/visu/projet/methodology_ref.html) | Reference externe adaptee | Fichier de reference/ancienne base pour la page methodologie. |

## Quel fichier sert a quel visu

### 1. Portail

- [index.html](/c:/Users/natha/PycharmProjects/visu/projet/index.html) : page d'accueil et cartes de navigation.

### 2. Carte interactive

- [map.html](/c:/Users/natha/PycharmProjects/visu/projet/map.html) : interface principale.
- [theme.js](/c:/Users/natha/PycharmProjects/visu/projet/theme.js) et [theme-light.css](/c:/Users/natha/PycharmProjects/visu/projet/theme-light.css) : gestion du theme.
- [turf.min.js](/c:/Users/natha/PycharmProjects/visu/projet/turf.min.js) : utilitaires geo.
- [regions.geojson](/c:/Users/natha/PycharmProjects/visu/projet/regions.geojson) : contours des regions.
- [parcels_sample_france_5000.geojson](/c:/Users/natha/PycharmProjects/visu/projet/parcels_sample_france_5000.geojson) : echantillon de parcelles pour la carte/heatmap.

### 3. Vue nationale

- [overview-france.html](/c:/Users/natha/PycharmProjects/visu/projet/overview-france.html) : page finale.
- [data_summary_france.json](/c:/Users/natha/PycharmProjects/visu/projet/data_summary_france.json) : resume national par culture/groupe.
- [data_regions.json](/c:/Users/natha/PycharmProjects/visu/projet/data_regions.json) : stats regionales utilisees dans la vue nationale.
- [data_rankings.json](/c:/Users/natha/PycharmProjects/visu/projet/data_rankings.json) : classements regionaux par culture.
- [regions.geojson](/c:/Users/natha/PycharmProjects/visu/projet/regions.geojson) : geometries de la carte.

### 4. Modèles d'Exploitation

- [cosmos-bubbles.html](/c:/Users/natha/PycharmProjects/visu/projet/cosmos-bubbles.html) : visualisation finale.
- [data_summary_france.json](/c:/Users/natha/PycharmProjects/visu/projet/data_summary_france.json) : surface et nombre de parcelles par culture.
- [data_hierarchy_france.json](/c:/Users/natha/PycharmProjects/visu/projet/data_hierarchy_france.json) : rattachement culture -> groupe pour les couleurs et regroupements.

### 5. Tailles / fragmentation

- [fragmentation-combined.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation-combined.html) : page finale la plus complete sur les tailles.
- [data_fragmentation_regional.json](/c:/Users/natha/PycharmProjects/visu/projet/data_fragmentation_regional.json) : repartition regionale par classes de taille.
- [data_distribution_curves.json](/c:/Users/natha/PycharmProjects/visu/projet/data_distribution_curves.json) : distributions pour les courbes.
- [fragmentation-regional.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation-regional.html), [distribution-curves.html](/c:/Users/natha/PycharmProjects/visu/projet/distribution-curves.html), [fragmentation.html](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation.html) : versions intermediaires ou dediees a un sous-cas.

### 6. Hierarchie / prototypes

- [sunburst.html](/c:/Users/natha/PycharmProjects/visu/projet/sunburst.html) : vue hierarchique.
- [waffle.html](/c:/Users/natha/PycharmProjects/visu/projet/waffle.html) : prototype du waffle.
- [regions.html](/c:/Users/natha/PycharmProjects/visu/projet/regions.html) : ancienne vue regionale.
- [dashboard.html](/c:/Users/natha/PycharmProjects/visu/projet/dashboard.html) : tableau de bord initial.

## Scripts de generation / preparation

### Donnees generales

- [aggregate_data.py](/c:/Users/natha/PycharmProjects/visu/projet/aggregate_data.py) : agregations de base.
- [aggregate_france.py](/c:/Users/natha/PycharmProjects/visu/projet/aggregate_france.py) : agregations nationales.
- [analyze_data.py](/c:/Users/natha/PycharmProjects/visu/projet/analyze_data.py), [analyze_remaining.py](/c:/Users/natha/PycharmProjects/visu/projet/analyze_remaining.py), [analyze_sizes.py](/c:/Users/natha/PycharmProjects/visu/projet/analyze_sizes.py) : scripts d'analyse.

### Generation des fichiers utilises par les visus

- [generate_map.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_map.py) et [generate_map_france.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_map_france.py) : preparation des donnees cartographiques.
- [generate_regional_data.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_regional_data.py) : stats regionales.
- [generate_culture_rankings.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_culture_rankings.py) et [generate_rankings_gpkg.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_rankings_gpkg.py) : classements par culture.
- [analyze_france_fragmentation.py](/c:/Users/natha/PycharmProjects/visu/projet/analyze_france_fragmentation.py), [generate_fragmentation_regional.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_fragmentation_regional.py) et [generate_distribution_curves.py](/c:/Users/natha/PycharmProjects/visu/projet/generate_distribution_curves.py) : pipeline lie aux tailles des parcelles.
- [transform_regions_to_rankings.py](/c:/Users/natha/PycharmProjects/visu/projet/transform_regions_to_rankings.py) : transformation complementaire pour les classements.

## Fichiers front utiles

- [script.js](/c:/Users/natha/PycharmProjects/visu/projet/script.js), [style.css](/c:/Users/natha/PycharmProjects/visu/projet/style.css), [dashboard-script.js](/c:/Users/natha/PycharmProjects/visu/projet/dashboard-script.js), [ranking-chart.js](/c:/Users/natha/PycharmProjects/visu/projet/ranking-chart.js), [fragmentation.js](/c:/Users/natha/PycharmProjects/visu/projet/fragmentation.js) : scripts/styles associes a des vues plus anciennes ou auxiliaires.

## Donnees brutes ou echantillons

- [parcels_sample.geojson](/c:/Users/natha/PycharmProjects/visu/projet/parcels_sample.geojson)
- [parcels_sample_france.geojson](/c:/Users/natha/PycharmProjects/visu/projet/parcels_sample_france.geojson)
- [parcels_sample_france_5000.geojson](/c:/Users/natha/PycharmProjects/visu/projet/parcels_sample_france_5000.geojson)
- [regions.geojson](/c:/Users/natha/PycharmProjects/visu/projet/regions.geojson)

## Fichiers utilitaires / inspection

- [inspect_gpkg.py](/c:/Users/natha/PycharmProjects/visu/projet/inspect_gpkg.py)
- [inspect_id.py](/c:/Users/natha/PycharmProjects/visu/projet/inspect_id.py)
- [inspect_ids.py](/c:/Users/natha/PycharmProjects/visu/projet/inspect_ids.py)
