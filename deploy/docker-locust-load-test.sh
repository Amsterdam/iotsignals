#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

# Remove docker containers from previous runs
docker-compose down
docker-compose rm -f

# Run migrations
docker-compose run api /deploy/docker-wait.sh
docker-compose run api /deploy/docker-migrate.sh
docker-compose run api python manage.py make_partitions

# Run the load test
docker-compose up locust

# Remove remaining docker containers
docker-compose down
docker-compose rm -f
