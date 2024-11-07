import geopandas as gpd
import pandas as pd
import streamlit as st
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

from geopy.geocoders import Nominatim
from shapely.geometry import Point


CODE_DESCRIPTION = {
    1: "**Niveau d'hygiène très satisfaisant** : établissements ne présentant pas de non-conformité, ou présentant uniquement des non-conformités mineures.",
    2: "**Niveau d'hygiène satisfaisant** : établissements présentant des non-conformités qui ne justifient pas l’adoption de mesures de police administrative mais auxquels l’autorité administrative adresse un courrier de rappel de la réglementation en vue d’une amélioration des pratiques.",
    3: "**Niveau d'hygiène à améliorer** : établissements dont l'exploitant a été mis en demeure de procéder à des mesures correctives dans un délai fixé par l'autorité administrative et qui conduit à un nouveau contrôle des services de l’État pour vérifier la mise en place de ces mesures correctives.",
    4: "**Niveau d'hygiène à corriger de manière urgente** : établissements présentant des non-conformités susceptibles de mettre en danger la santé du consommateur et pour lesquels l'autorité administrative ordonne la fermeture administrative, le retrait, ou la suspension de l'agrément sanitaire.",
}

def load_data(query):
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


        results = run_query(query)

        df = pd.DataFrame(results)

    except DefaultCredentialsError as e:
        logging.error(
            f"Error: {e}. Check environment variables and service account credentials."
        )
        logging.info("Loading data from local `parquet` file..")
        df = pd.read_parquet("data/restaurant_matching_sample.parquet")

    return df

def get_feature_style(feature):
    eval_code = feature["properties"]["app_code_synthese_eval_sanit"]  # Access the app_code_synthese_eval_sanit value
    color_map = {
        1: "green",
        2: "blue",
        3: "orange",
        4: "red"
    }
    return {
        "color": color_map.get(eval_code, "gray"),  # Border color
        "fill": True,
        "fillColor": color_map.get(eval_code, "gray"),  # Fill color
        "weight": 3,
        "fillOpacity": 0.8,
        "radius": 6
    }


@st.cache_data(ttl=1800)
def geocode_address(address):
    geolocator = Nominatim(user_agent="SûrEtBon", timeout=10)
    location = geolocator.geocode(address)
    if location:
        return (location.longitude, location.latitude)
    else:
        return None

def center_map_to_searched_term(search_term, gdf):
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
        return gdf


def write_clicked_restaurant_data(st_data):
    #TO DO : check if side pannel refreshes properly
    st_data = dict(st_data)
    display_data = st_data["last_active_drawing"]["properties"]
    name = display_data["osm_name"]
    google_rating = display_data["google_rating"]
    tripadvisor_rating = display_data["tripadvisor_rating"]
    name = display_data["osm_name"]
    eval = display_data["app_code_synthese_eval_sanit"]
    synthese = display_data["synthese_eval_sanit"]

    return dict(name=name,
                eval=eval,
                synthese=synthese,
                google_rating=google_rating,
                tripadvisor_rating=tripadvisor_rating
                )
