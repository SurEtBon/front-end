import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely import wkb
import folium

data =  pd.read_parquet("/home/donatien.konan.pro/code/donat-konan33/de-project-2024/front-end/data/restaurant_matching.parquet")

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

class suretbonDashboard:
    def __init__(self) -> None:
        pass

    def icone(self):
        """
        the Logo of SûrEtBon
        """
        with open()


    def introduction_page(self):
        """Layout the views of the dashboard"""
        st.title("SûrEtBon Dashboard")
        st.write(
            """
       ---

        Restaurant Cleanliness and Customer Rating Evaluation
        Application Overview
        This Streamlit application is designed to help users evaluate restaurants based on two essential criteria:
        sanitary cleanliness and customer satisfaction. Providing a user-friendly interface, the app allows users to search for,
        review, and rate various dining establishments.

        ---
        Key Features
        ---

        Cleanliness Evaluation: Users can review information on the sanitary cleanliness of restaurants, based on established standards and inspections.
        Customer Ratings: The app gathers and displays ratings from customers, providing an overview of customer satisfaction for each restaurant.
        Search Filters: Users can filter results by cuisine type, location, or cleanliness score, making it easy to find a restaurant that meets their expectations.
        Intuitive Interface: With Streamlit’s simple and interactive design, users can easily navigate through the information,
        access analysis graphs, and submit their own ratings.

        ---

        Application Objective
        ---
        The primary objective of this application is to promote healthy and
        transparent dining practices by providing customers with reliable information to make informed restaurant choices.
        By combining cleanliness evaluations with customer ratings, the app encourages restaurant owners to uphold high
        standards of cleanliness and service.
        """
        )




if __name__ == "__main__":
    dashboard = suretbonDashboard()
    dashboard.introduction_page()
