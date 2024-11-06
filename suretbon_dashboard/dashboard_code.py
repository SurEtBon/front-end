import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from streamlit_folium import st_folium
from shapely import wkb

from utils import load_data
from utils import CODE_DESCRIPTION

st.set_page_config(layout="wide")

query = """
    SELECT *
    FROM `algebraic-link-440513-f9.mart.restaurants_final_matching`
    LIMIT 1000
    """

df = load_data(query)

# convert geospatial data into type that works with pandas
df["geopandas_osm"] = df["geopandas_osm"].apply(wkb.loads)
df["date_inspection"] = df["date_inspection"].apply(str)

# convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geopandas_osm", crs="EPSG:4326")

# filter out some columns
columns_to_keep = [
    "osm_name",
    "osm_clean_name",
    "geopandas_osm",
    "distance_name_label",
    "synthese_eval_sanit",
    "app_code_synthese_eval_sanit",
    "full_address",
    "nb_inspections",
    "date_inspection",
]
gdf = gdf[columns_to_keep]

# keep only these rows with levenshtein_distance <= 3
mask = gdf["distance_name_label"] <= 3
gdf = gdf[mask]

address = st.text_input("Adresse")
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="cartodb positron")

def get_feature_style(feature):
    eval_code = feature["properties"]["app_code_synthese_eval_sanit"]  # Access the app_code_synthese_eval_sanit value
    color_map = {
        1: "green",
        2: "blue",
        3: "black",
        4: "red"
    }
    return {
        "color": color_map.get(eval_code, "gray"),  # Default to gray if code not matched
        "weight": 2,
        "fillOpacity": 0.6
    }

folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=["osm_name"]),
    marker=folium.Circle(radius=300), #, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
    style_function=get_feature_style
).add_to(m)

st_data = st_folium(m, width=725)
st.write(dict(st_data))

with st.sidebar:
    st_data = dict(st_data)
    display_data = st_data["last_active_drawing"]["properties"]

    name = display_data["osm_name"]
    full_address = display_data["full_address"]
    st.write("**Nom de l'établissement**")
    st.write(name)
    st.write("**Adresse**")
    st.write(full_address)

    st.divider()

    eval = display_data["app_code_synthese_eval_sanit"]
    synthese = display_data["synthese_eval_sanit"]
    st.write("**Evaluation**")
    st.write(str(eval) + " - " + synthese)
    st.write(CODE_DESCRIPTION[eval])
    st.write(f"Date de la dernière inspection : {display_data['date_inspection']}")
    st.write(f"Nombre d'inspection(s) : {display_data['nb_inspections']}")


    st.write(st_data)



    # adresse_2_ua
# code_postal
# libelle_commune

# dernière date d'inspections

