#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

cd /app/

# there are two apps, contenttypes (from Django) and passages
yes yes | python manage.py migrate contenttypes --noinput

# migrate passage up to specific migration during schema migration process
yes yes | python manage.py migrate passage 0022 --noinput

