import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
import os

from streamlit_folium import st_folium
from shapely import wkb

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

# source data
data = pd.read_parquet("data/restaurant_matching_sample.parquet")
col1, col2 = st.columns(2)

with col1:
    st.write("sourced data: data types")
    st.write(data.dtypes.tolist())

with col2:
    st.dataframe(data)


# convert 'osm_geo' into valid geo data
data["osm_geo"] = data["osm_geo"].apply(wkb.loads)

# convert to GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry="osm_geo", crs="EPSG:4326")

col1, col2 = st.columns(2)

with col1:
    st.write("converted geodataframe : data types")
    st.write(gdf.dtypes.tolist())

with col2:
    st.dataframe(gdf)

columns_to_keep = [
    "osm_name",
    "osm_type",
    "osm_clean_name",
    "osm_geo",
    "cs_app_libelle_activite_etablissement",
    "levenshtein_distance",
]
st.write(f"keep only these columns: {columns_to_keep}")
gdf = gdf[columns_to_keep]

mask = gdf["levenshtein_distance"] <= 3
st.write(f"keep only these rows with levenshtein_distance <= 3")
gdf = gdf[mask]

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="cartodb positron")

folium.GeoJson(
    gdf, tooltip=folium.features.GeoJsonTooltip(fields=["osm_clean_name"])
).add_to(m)

st_data = st_folium(m, width=725)


"""
tile design options : https://leaflet-extras.github.io/leaflet-providers/preview/

var Stadia_AlidadeSmooth = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'png'
});

var Stadia_AlidadeSmoothDark = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'png'
});


Provider names for leaflet-providers.js
Stadia.OSMBright
Plain JavaScript:
var Stadia_OSMBright = L.tileLayer('https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'png'
});


"""
