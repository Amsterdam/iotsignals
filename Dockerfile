FROM python:3.10.12-slim-bullseye as api
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN groupadd -r datapunt && useradd -r -g datapunt datapunt
RUN mkdir -p /static && chown datapunt /static

RUN apt update -y \
    && apt upgrade -y \
    && apt install -y --no-install-recommends gdal-bin build-essential  libpcre3-dev netcat postgresql-13 zlib1g-dev wget ca-certificates file\
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

#Bloody UWSGI from pip doesnt come with all the required plugins. Beter make it form scratch
RUN wget --no-check-certificate https://projects.unbit.it/downloads/uwsgi-2.0.20.tar.gz
RUN file uwsgi-2.0.20.tar.gz
RUN tar zxf uwsgi-2.0.20.tar.gz -C / \
    && cd /uwsgi-2.0.20 \
    && python uwsgiconfig.py --build \
    && ln -s /uwsgi-2.0.20/uwsgi  /usr/local/bin/uwsgi


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