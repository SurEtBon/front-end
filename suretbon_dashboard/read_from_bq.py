import streamlit as st
import pandas as pd
import logging

from google.oauth2 import service_account
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

from shapely import wkb
from shapely import Geometry
from shapely import to_wkt


logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


# Check for invalid geometries in osm_geo
def check_for_invalid_geometries(df: pd.DataFrame) -> None:
    invalid_geometries = df[
        df["osm_geo"].apply(lambda x: not isinstance(x, Geometry) or x.is_empty)
    ]
    print(f"Number of invalid geometries: {len(invalid_geometries)}")


def convert_geometry_to_WKT_format_for_arrow_compatibility(
    df: pd.DataFrame,
) -> pd.DataFrame:
    # Convert geometry to WKT format for Arrow compatibility
    df["osm_geo"] = df["osm_geo"].apply(
        lambda geom: to_wkt(geom) if isinstance(geom, Geometry) else None
    )
    return df


def main():
    try:
        # Create API client.
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        logging.info("Big Suery client successfully created")

        # Perform query.
        # Uses st.cache_data to only rerun when the query changes or after 10 min.
        @st.cache_data(ttl=600)
        def run_query(query):
            query_job = client.query(query)
            rows_raw = query_job.result()
            # Convert to list of dicts. Required for st.cache_data to hash the return value.
            rows = [dict(row) for row in rows_raw]
            return rows

        query = """SELECT * FROM `algebraic-link-440513-f9.mart.restaurant_matching` LIMIT 200"""
        df = pd.DataFrame(run_query(query))
        print(f"{df.shape=}")

        check_for_invalid_geometries(df)

        converted_df = convert_geometry_to_WKT_format_for_arrow_compatibility(df)
        print(f"{converted_df.shape=}")

        converted_df["osm_geo"] = converted_df["osm_geo"].apply(wkb.loads)
        # still fails on dashboard_code.py:
        # pyarrow.lib.ArrowTypeError: ('Did not pass numpy.dtype object',
        # 'Conversion failed for column osm_geo with type geometry')

    except DefaultCredentialsError as e:
        logging.error(
            f"Error: {e}. Check environment variables and service account credentials."
        )
        logging.info("Loading data from local `parquet` file..")
        df = pd.read_parquet("data/restaurant_matching_sample.parquet")


if __name__ == "__main__":
    main()
