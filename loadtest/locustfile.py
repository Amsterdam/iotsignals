"""
This is a (much needed) load test for this repo. These are some example usages:

locust --host=http://127.0.0.1:8001 --headless --users 250 --spawn-rate 25 --run-time 30s
"""

# std
import csv
import datetime
import json
import os
import random
import time
from uuid import uuid4
# 3rd party
from locust import HttpUser, task, between


PASSAGE_ENDPOINT_URL = "/v0/milieuzone/passage/"


def get_dt_with_tz_info():
    # Calculate the offset taking into account daylight saving time
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def load_data(filename):

    def postprocess(row):

        del row['count']

        # '' -> undefined
        for key in [key for key, value in row.items() if not value]:
            del row[key]

        # parse bool
        if 'taxi_indicator' in row:
            row['taxi_indicator'] = {'TRUE': True, 'FALSE': False}.get(row['taxi_indicator'], None)

        # parse json fields
        if 'brandstoffen' in row:
            row['brandstoffen'] = json.loads(row['brandstoffen'].replace("'", '"'))

        return row

    with open(filename) as f:
        # this will be our "pool" of values to choose from, multiply each
        # item by the number of times it occurred to make it more likely that
        # we will choose those.
        return [
            postprocess(dict(row))
            for row in csv.DictReader(f)
            for _ in range(int(row['count']))
        ]


# allow caller to provide camera / vehicle data, or default to unique camera
# and vehicle data selected from 2021-09-01
cameras = load_data(os.environ.get('CAMERA_CSV', '/opt/src/data/camera.csv'))
vehicles = load_data(os.environ.get('VEHICLE_CSV', '/opt/src/data/vehicle.csv'))


# make sure sampling is reproducible
random.seed(0)


def create_message(timestamp):
    message = {
        "id": str(uuid4()),
        "passage_at": timestamp,
        "created_at": timestamp,
        "version": "1",
        "kenteken_nummer_betrouwbaarheid": random.randint(0, 1000),
        "kenteken_land_betrouwbaarheid": random.randint(0, 1000),
        "kenteken_karakters_betrouwbaarheid": [
            {
                "positie": positie,
                "betrouwbaarheid": random.randint(0, 1000),
            }
            for positie in range(6)
        ],
        "indicatie_snelheid": random.randrange(0, 100),
        "automatisch_verwerkbaar": random.sample((None, True, False), 1)[0],
        **random.sample(cameras, 1)[0],
        **random.sample(vehicles, 1)[0],
    }
    return message


class CarsBehaviour(HttpUser):
    weight = 1
    wait_time = between(0, 1)

    @task(1)
    def post_cars(self):
        timestamp = get_dt_with_tz_info()
        self.client.post(PASSAGE_ENDPOINT_URL, json=create_message(timestamp))
