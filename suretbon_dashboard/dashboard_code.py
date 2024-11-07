import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from streamlit_folium import st_folium
from shapely import wkb

from utils import CODE_DESCRIPTION
from utils import load_data
from utils import center_map_to_searched_term
from utils import get_feature_style
from utils import write_clicked_restaurant_data
from utils import load_logo

######### CONFIG LAYOUT, DEFINE QUERY, LOAD DATA #########
st.set_page_config(layout="wide")


###### HEADER ######
col1, col2 = st.columns(2)
with col1:
    with st.container():
        with st.header(""):
            st.markdown("""
                        ## Bienvenue sur notre Application **SûrEtBon**
                        Saisir son adresse pour voir les restaurants les plus proches

                        ----
                        """)

        with col2:
            img = load_logo()
            st.components.v1.html(img, width= 200, height=150)


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
    "type",
    "geopandas_osm",
    "synthese_eval_sanit",
    "app_code_synthese_eval_sanit",
    "full_address",
    "nb_inspections",
    "date_inspection",
    "google_rating",
    "google_nb_rating",
    "tripadvisor_rating",
    "tripadvisor_nb_rating"
]
gdf = gdf[columns_to_keep]

#

######### HANDLE ADDRESS SEARCH BAR #########
# search bar for an address
search_term = st.text_input("Adresse")

# default map to Paris
center_lat = 48.8566
center_lon = 2.3522

if search_term:
    gdf = center_map_to_searched_term(search_term, gdf)

######### SHOW MAP #########
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodb positron")

field = ["osm_name", "type"]
aliases = ["Etablissement | ", "Type d'établissement | "]
folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=field, aliases=aliases),
    marker=folium.CircleMarker(),
    style_function=get_feature_style
).add_to(m)

st_data = st_folium(m, width=900)

######### DISPLAY SIDE BAR #########
with st.sidebar:
    img = load_logo()
    st.components.v1.html(img, width= 200, height=150)
    st.divider()
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
        st.write("**Note sur Google**")
        st.write(f"{display_data['google_rating']}/5 *({display_data['google_nb_rating']} reviews)*")
        st.write("**Note sur Tripadvisor**")
        st.write(f"{display_data['tripadvisor_rating']}/5 *({display_data['tripadvisor_nb_rating']} reviews)*")
        st.divider()

        st.write(CODE_DESCRIPTION[eval])
        st.write(f"Date de la dernière inspection : {display_data['date_inspection']}")
        st.write(f"Nombre d'inspection(s) : {display_data['nb_inspections']}")
    else:
        st.write("**Cliquez sur un établissement pour voir les détails**")

st.markdown(
    """
    ----
    Important :
    Les données sanitaires proviennent de relevés issus de la DGAL. Cliquez [ici](https://agriculture.gouv.fr/mots-cles/dgal) pour plus d'informations
    """
)
