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

COPY ./suretbon_dashboard/utils.py /app/utils.py
COPY ./suretbon_dashboard/dashboard_code.py /app/dashboard_code.py

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["entrypoint.sh"]