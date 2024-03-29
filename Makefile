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

push_semver:
	VERSION=$${VERSION} $(MAKE) push
	VERSION=$${VERSION%\.*} $(MAKE) push
	VERSION=$${VERSION%%\.*} $(MAKE) push

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

test:                               ## Execute tests
	$(dc) run --rm test pytest /app/tests $(ARGS)

dev: migrate						## Run the development app (and run extra migrations first)
	$(run) --service-ports dev

api:
	$(run) --service-ports api

loadtest: migrate
	$(manage) make_partitions $(ARGS)
	$(run) locust $(ARGS)

test_data:
	$(manage) generate_test_data --num_days 25 --num_rows_per_day 2000

pdb:
	$(run) dev pytest --pdb $(ARGS)

bash:
	$(run) dev bash

shell:
	$(manage) shell_plus

dbshell:
	$(manage) dbshell

migrate:
	$(manage) migrate

migrations:
	$(manage) makemigrations $(ARGS)