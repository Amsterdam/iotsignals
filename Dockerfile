FROM python:3.11.4-slim-bullseye as api
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN groupadd -r datapunt && useradd -r -g datapunt datapunt
RUN mkdir -p /static && chown datapunt /static

RUN apt update -y \
    && apt upgrade -y \
    && apt install -y --no-install-recommends gdal-bin build-essential  libpcre3-dev netcat postgresql-13 \
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

USER datapunt
COPY src /app/src/
COPY deploy /deploy/

RUN export DJANGO_SETTINGS_MODULE=main.settings

ARG SECRET_KEY=dev
ARG AUTHORIZATION_TOKEN=dev
RUN python src/manage.py collectstatic --no-input

CMD ["/deploy/docker-run.sh"]
WORKDIR /app/src

FROM api as dev
WORKDIR /app
USER root
ADD requirements_dev.txt requirements_dev.txt
RUN pip install -r requirements_dev.txt
USER datapunt
WORKDIR /app/src


FROM dev as test
WORKDIR /app
COPY tests /app/tests/
ENV PYTHONPATH=/app/src
WORKDIR /app/src
CMD ["/deploy/docker-run.sh"]