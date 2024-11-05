import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import folium


data =  pd.read_parquet("../data/restaurant_matching.parquet")

# Convertir la colonne WKB en géométries
data['osm_geo'] = data['osm_geo'].apply(wkb.loads)
# Convertir ensuite en GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry='osm_geo', crs="EPSG:4326")
gdf = gdf[['osm_name', 'osm_type',
       'osm_clean_name', 'osm_geo',
       'cs_app_libelle_activite_etablissement',
       'levenshtein_distance']]

gdf = gdf[gdf['levenshtein_distance'] <= 3]

m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()])
folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=['osm_clean_name'])
).add_to(m)

m
