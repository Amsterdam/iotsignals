#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p iotsignalstest -f ${DIR}/docker-compose.yml $*
}


dc down -v
dc pull
dc build

dc up -d database

dc run --rm tests

dc stop
dc rm --force
dc down
