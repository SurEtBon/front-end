import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from streamlit_folium import st_folium
from shapely import wkb


# source data
data =  pd.read_parquet("data/restaurant_matching_sample.parquet")
col1, col2 = st.columns(2)

with col1:
    st.write("sourced data: data types")
    st.write(data.dtypes.tolist())

with col2:
    st.dataframe(data)



# convert 'osm_geo' into valid geo data
data['osm_geo'] = data['osm_geo'].apply(wkb.loads)

# convert to GeoDataFrame
gdf = gpd.GeoDataFrame(data, geometry='osm_geo', crs="EPSG:4326")

col1, col2 = st.columns(2)

with col1:
    st.write("converted geodataframe : data types")
    st.write(gdf.dtypes.tolist())

with col2:
    st.dataframe(gdf)

columns_to_keep = ['osm_name', 'osm_type',
       'osm_clean_name', 'osm_geo',
       'cs_app_libelle_activite_etablissement',
       'levenshtein_distance']
st.write(f"keep only these columns: {columns_to_keep}")
gdf = gdf[columns_to_keep]

mask = gdf['levenshtein_distance'] <= 3
st.write(f"keep only these rows with levenshtein_distance <= 3")
gdf = gdf[mask]

m = folium.Map(
    location=[48.8566, 2.3522],
    zoom_start=12
    )

folium.GeoJson(
    gdf,
    tooltip=folium.features.GeoJsonTooltip(fields=['osm_clean_name'])
).add_to(m)

st_data = st_folium(m, width=725)

