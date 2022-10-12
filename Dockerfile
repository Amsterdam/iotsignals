FROM amsterdam/python:3.8-buster as api
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN mkdir -p /static && chown datapunt /static

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY src /app/src/
COPY deploy /deploy/

WORKDIR /app

USER datapunt

RUN export DJANGO_SETTINGS_MODULE=main.settings

ARG SECRET_KEY=dev
ARG AUTHORIZATION_TOKEN=dev
RUN python src/manage.py collectstatic --no-input

CMD uwsgi
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