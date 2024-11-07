import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from streamlit_folium import st_folium
from shapely import wkb
from shapely.geometry import Point

from utils import load_data
from utils import write_clicked_restaurant_data
from utils import geocode_address
from utils import CODE_DESCRIPTION

######### CONFIG LAYOUT, DEFINE QUERY, LOAD DATA #########
st.set_page_config(layout="wide")

query = """
    SELECT *
    FROM `algebraic-link-440513-f9.mart.restaurants_final_matching`
    """

df = load_data(query)

######### PROCESSING #########
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

#st.write(st.session_state)
######### HANDLE ADDRESS SEARCH BAR #########
# search bar for an address
search_term = st.text_input("Adresse")

# default map to Paris
center_lat = 48.8566
center_lon = 2.3522

if search_term:
    # Définir le point de référence (par exemple, un point à Paris)
    coor_geo = geocode_address(search_term)

    # Convertir le GeoDataFrame dans un CRS projeté pour calculer les distances (par ex., EPSG:3857)
    gdf = gdf.to_crs(epsg=3857)

    center_lat = coor_geo[1]
    center_lon = coor_geo[0]
    reference_point = Point(center_lon, center_lat)  # Coordonnées de Paris
    reference_point_gdf = gpd.GeoSeries([reference_point], crs="EPSG:4326").to_crs(epsg=3857)[0]

    # Spécifier le rayon en mètres (ex. : 10 km)
    radius = 1000  # 10 km

    # Filtrer les points dans le rayon
    gdf['distance'] = gdf.geometry.distance(reference_point_gdf)
    gdf = gdf[gdf['distance'] <= radius]

######### SHOW MAP #########
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodb positron")

def get_feature_style(feature):
    eval_code = feature["properties"]["app_code_synthese_eval_sanit"]  # Access the app_code_synthese_eval_sanit value
    color_map = {
        1: "green",
        2: "blue",
        3: "black",
        4: "purple"
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

######### DISPLAY SIDE BAR #########
with st.sidebar:
    st_data = dict(st_data)
    if st_data.get("last_active_drawing"):
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
    else:
        st.write("**Cliquez sur un établissement pour voir les détails**")
