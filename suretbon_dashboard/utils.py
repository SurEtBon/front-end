import pandas as pd
import streamlit as st
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError


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

def write_clicked_restaurant_data(st_data):
    st_data = dict(st_data)
    display_data = st_data["last_active_drawing"]["properties"]
    name = display_data["osm_name"]
    stars = display_data["stars"]
    name = display_data["osm_name"]
    eval = display_data["app_code_synthese_eval_sanit"]
    synthese = display_data["synthese_eval_sanit"]

    return dict(name=name,
                stars=stars,
                eval=eval,
                synthese=synthese)
