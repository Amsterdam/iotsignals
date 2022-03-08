# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
#
# VERSION = 2020.01.29

PYTHON = python3

dc = docker-compose
run = $(dc) run --rm
manage = $(run) dev python manage.py

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pip-tools:
	pip install pip-tools

install: pip-tools                  ## Install requirements and sync venv with expected state as defined in requirements.txt
	pip-sync requirements.txt requirements_dev.txt

requirements: pip-tools             ## Upgrade requirements (in requirements.in) to latest versions and compile requirements.txt
	pip-compile --upgrade --output-file requirements.txt requirements.in
	pip-compile --upgrade --output-file requirements_dev.txt requirements_dev.in

upgrade: requirements install       ## Run 'requirements' and 'install' targets

build:                              ## Build docker image
	$(dc) build
	cd deploy/test; $(dc) build

push: build                         ## Push docker image to registry
	$(dc) push

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

test:
	$(run) dev pytest $(ARGS)

loadtest:
	$(run) api python /app/manage.py migrate
	$(run) api python /app/make_paritions.py
	$(run) locust $(ARGS)

pdb:
	$(run) dev pytest --pdb $(ARGS)

bash:
	$(run) dev bash

shell:
	$(manage) shell_plus

migrate:
	$(manage) migrate

migrations:
	$(manage) makemigrations $(ARGS)
