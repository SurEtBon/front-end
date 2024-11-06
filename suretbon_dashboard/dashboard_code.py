import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from streamlit_folium import st_folium
from shapely import wkb

from utils import load_data
from utils import write_clicked_restaurant_data

st.set_page_config(layout="wide")

query = """
    SELECT *
    FROM `algebraic-link-440513-f9.mart.restaurants_final_matching`
    LIMIT 1000
    """

df = load_data(query)

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

address = st.text_input("Adresse")
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="cartodb positron")


folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=["osm_clean_name"]),
).add_to(m)

st_data = st_folium(m, width=725)
st.write(dict(st_data))

with st.sidebar:
    st_data = dict(st_data)
    display_data = st_data["last_active_drawing"]["properties"]

    name = display_data["osm_name"]
    st.write("**Name**")
    name = display_data["osm_name"]
    st.write(name)
    st.divider()


    stars = display_data["stars"]
    st.write("**Stars**")
    st.write(stars)
    st.divider()


    eval = display_data["app_code_synthese_eval_sanit"]
    st.write("**Evaluation**")
    st.write(eval)
    st.divider()

    synthese = display_data["synthese_eval_sanit"]
    st.write("**Synthese**")
    st.write(synthese)
