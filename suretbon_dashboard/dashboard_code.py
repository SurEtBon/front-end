import folium
import geopandas as gpd
import pandas as pd
import streamlit as st
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

from streamlit_folium import st_folium
from shapely import wkb

try:
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    logging.info("Big Query client successfully created")

    # Perform query.
    # Uses st.cache_data to only rerun when the query changes or after 1 hour.
    @st.cache_data(ttl=3600)
    def run_query(query):
        query_job = client.query(query)
        rows_raw = query_job.result()
        # Convert to list of dicts. Required for st.cache_data to hash the return value.
        rows = [dict(row) for row in rows_raw]
        return rows

    query = """
        SELECT *
        FROM `algebraic-link-440513-f9.mart.restaurants_final_matching`
        LIMIT 200
        """
    results = run_query(query)

    df = pd.DataFrame(results)

except DefaultCredentialsError as e:
    logging.error(
        f"Error: {e}. Check environment variables and service account credentials."
    )
    logging.info("Loading data from local `parquet` file..")
    df = pd.read_parquet("data/restaurant_matching_sample.parquet")

# convert geospatial data into type that works with pandas
df["geopandas_osm"] = df["geopandas_osm"].apply(wkb.loads)

# convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geopandas_osm", crs="EPSG:4326")

# filter out some columns
columns_to_keep = [
    "osm_name",
    "type",
    "osm_clean_name",
    "geopandas_osm",
    "osm_siret",
    "alimconfiance_name",
    "alimconfiance_clean_name",
    "alimconfiance_siret",
    "distance_name_label",
    "stars",
    "synthese_eval_sanit",
    "app_code_synthese_eval_sanit",
]
gdf = gdf[columns_to_keep]

# keep only these rows with levenshtein_distance <= 3
mask = gdf["distance_name_label"] <= 3
gdf = gdf[mask]

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="cartodb positron")

folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=["osm_clean_name"])
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
