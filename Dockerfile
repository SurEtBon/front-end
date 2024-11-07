FROM python:3.12.7

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml

RUN apt-get update \
    && apt-get -y upgrade \
    && pip3 install --no-cache-dir poetry \
    && poetry install --only main \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /app/.streamlit

RUN echo -n $SECRETS | base64 --decode > /app/.streamlit/secrets.toml && \
    echo -n $CONFIG| base64 --decode > /app/.streamlit/config.toml

COPY ./suretbon_dashboard/utils.py /app/utils.py
COPY ./suretbon_dashboard/dashboard_code.py /app/dashboard_code.py

EXPOSE 8501

ENTRYPOINT ["poetry", "run", "streamlit", "run", "/app/dashboard_code.py"]