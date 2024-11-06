import pandas as pd
import streamlit as st
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

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
