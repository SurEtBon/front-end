#!/bin/bash
echo -n $SECRETS | base64 --decode > /app/.streamlit/secrets.toml
echo -n $CONFIG | base64 --decode > /app/.streamlit/config.toml
poetry run streamlit run /app/dashboard_code.py