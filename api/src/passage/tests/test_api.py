# std
import csv
import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone, date
from itertools import cycle
# 3rd party
import pytest
import pytz
from django.db import connection
from django.test import override_settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from model_bakery import baker
# iotsignals
from passage.conversion import convert_to_v1, NEW_FIELDS, RIJRICHTING_MAPPING
from iotsignals import PayloadVersion, to_api_version
from passage.case_converters import to_snakecase
from passage.models import Passage
from rest_framework import status
from .factories import PassageFactory, PayloadVersion2, PayloadVersion1
from ..util import keymap, keyfilter

log = logging.getLogger(__name__)


def get_num_records_in_partition(date_str: str = '20181016') -> int:
    """
    :param date_str: Date of the partition to get in the form YYYYMMDD.

    :return: The number of records in the passage partition of the given date.
    """
    with connection.cursor() as cursor:
        cursor.execute(f'select count(*) from passage_passage_{date_str}')
        return next(iter(cursor.fetchone()), 0)


def assert_response(response_data, payload):
    """
    Check the response from a POST against the payload that was sent, an
    AssertionException is raised when the response does not match what would
    be expected from the payload that was sent.

    :param response_data: The data from the POST response.
    :param payload: The original payload that was POSTed.
    """
    # The response from the POST is always in passage-v1 (flat) format, but the
    # payload that was sent could be passage-v1 (flat) or passage-v2 (nested)
    # so to correctly assert we need to do some conversion. Also the response
    # object will always contain new fields (from the generated instance of the
    # Passage mode), so we need to add those when v1 was POSTed
    post_data = keymap(to_snakecase, payload)
    if payload['version'] == 'passage-v1':
        post_data.update(dict.fromkeys(NEW_FIELDS))
    elif payload['version'] == 'passage-v2':
        post_data = convert_to_v1(post_data)
    else:
        raise ValueError(f"Unsupported version number {payload['version']}")

    # Check for privacy changes
    if post_data['toegestane_maximum_massa_voertuig'] <= 3500:
        post_data['toegestane_maximum_massa_voertuig'] = 1500
        post_data['europese_voertuigcategorie_toevoeging'] = None
        post_data['merk'] = None

    if post_data['voertuig_soort'].lower() == 'personenauto':
        post_data['inrichting'] = 'Personenauto'

    post_data[
        'datum_eerste_toelating'
    ] = f"{post_data['datum_eerste_toelating'].year}-01-01"

    post_data['datum_tenaamstelling'] = None

    # perform some post-processing to deal with small inconsistenties between
    # the request POST data and the response data.
    response_data = deepcopy(response_data)

    # created_at is automatically generated, and won't be present in the POST
    # data
    del response_data['created_at']

    # The model has a DateTimeUTCField for passage_at, but DRF serializer
    # converts the generated UTC timestamp to local time
    response_data['passage_at'] = (
        parse_datetime(response_data['passage_at'])
        .astimezone(timezone.utc)
        .isoformat()
    )
    post_data['passage_at'] = post_data['passage_at'].isoformat()

    # Response has GeoJSON, POST data is a dict
    response_data['camera_locatie'] = {
        'type': 'Point',
        'coordinates': response_data['camera_locatie']['coordinates'],
    }

    for k, v in response_data.items():
        assert response_data[k] == v, (k, response_data[k])


class TestPassageAPI:
    """
    Base class for testing the passage api, provides some basic utilities,
    e.g. injecting the api client fixture, posting a request and asserting the
    expected response.
    """

    @pytest.fixture(autouse=True)
    def inject_api_client(self, api_client):
        self.client = api_client

    def valid_response(self, url, response, content_type):
        """Check common status/json."""
        assert 200 == response.status_code, "Wrong response code for {}".format(url)

        assert (
            f"{content_type}" == response["Content-Type"]
        ), "Wrong Content-Type for {}".format(url)

    def url(self, payload_version: PayloadVersion):
        return f'/{to_api_version(payload_version)}/milieuzone/passage/'

    def post(self, body):
        """
        POST the given body to the passage endpoint.
        """
        return self.client.post(self.url(body['version']), body, format='json')

    @classmethod
    def payload(cls, payload_version: PayloadVersion) -> dict:
        """
        Get a passage payload for the requested version

        :param payload_version: The version of the payload to get.
        """
        factory = {
            "passage-v1": PayloadVersion1,
            "passage-v2": PayloadVersion2,
        }[payload_version]

        result = factory.create()
        assert isinstance(result, dict)
        return result


@pytest.mark.django_db
@pytest.mark.parametrize('payload_version', ["passage-v1", "passage-v2"])
class TestPassageAPI_Versions_1_2(TestPassageAPI):
    """
    Test the passage endpoint (both versions 0 and 2, which translate to the
    payload versions "passage-v1" and "passage-v2").
    """

    def test_post_new_passage(self, payload_version: PayloadVersion):
        """ Test posting a new passage """
        payload = self.payload(payload_version)
        assert Passage.objects.count() == 0
        res = self.post(payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(passage_id=payload['id'])
        assert_response(res.data, payload)

    def test_post_new_passage_missing_attr(self, payload_version: PayloadVersion):
        """Test posting a new passage with missing fields"""
        payload = self.payload(payload_version)
        assert Passage.objects.count() == 0
        if payload_version == 'passage-v1':
            payload.pop('merk')
            payload.pop('europeseVoertuigcategorieToevoeging')
        else:
            payload['voertuig'].pop('merk', None)
            payload['voertuig'].pop('europeseVoertuigcategorieToevoeging', None)
        res = self.post(payload)
        response_data = res.data
        assert res.status_code == 201, res.data
        assert Passage.objects.get(passage_id=payload['id'])

        assert_response(response_data, payload)

    def test_post_range_betrouwbaarheid(self, payload_version: PayloadVersion):
        """Test posting a invalid range betrouwbaarheid"""
        payload = self.payload(payload_version)
        before = get_num_records_in_partition()
        if payload_version == 'passage-v1':
            payload["kentekenNummerBetrouwbaarheid"] = -1
        else:
            payload["voertuig"]["kenteken"]["betrouwbaarheid"]["kentekenBetrouwbaarheid"] = -1
        res = self.post(payload)

        # check if the record was NOT stored in the correct partition
        assert before == get_num_records_in_partition()
        assert res.status_code == 400, res.data

    def test_post_duplicate_key(self, payload_version: PayloadVersion):
        """ Test posting a new passage with a duplicate key """
        payload = self.payload(payload_version)
        res = self.post(payload)
        assert res.status_code == 201, res.data

        # Post the same message again
        res = self.post(payload)
        assert res.status_code == 409, res.data

    def test_get_passages_not_allowed(self, payload_version: PayloadVersion):
        PassageFactory.create()
        response = self.client.get(self.url(payload_version))
        assert response.status_code == 405

    def test_update_passages_not_allowed(self, payload_version: PayloadVersion):
        # first post a record
        payload = self.payload(payload_version)
        self.post(payload)

        # Then check if I cannot update it
        response = self.client.put(
            f'{self.url(payload_version)}{payload["id"]}/', payload, format='json'
        )
        assert response.status_code == 404

    def test_delete_passages_not_allowed(self, payload_version: PayloadVersion):
        # first post a record
        payload = self.payload(payload_version)
        self.post(payload)

        # Then check if I cannot update it
        response = self.client.delete(f'{self.url(payload_version)}{payload["id"]}/')
        assert response.status_code == 404

    def test_passage_taxi_export(self, payload_version: PayloadVersion):

        baker.make(
            'passage.PassageHourAggregation',
            count=2,
            taxi_indicator=True,
            _quantity=500,
        )

        # first post a record
        api_version = to_api_version(payload_version)
        url = reverse(f'{api_version}:passage-export-taxi')
        response = self.client.get(url)
        assert response.status_code == 200

        date = datetime.now().strftime("%Y-%m-%d")
        lines = [line for line in response.streaming_content]
        assert lines == [b'datum,aantal_taxi_passages\r\n', f'{date},1000\r\n'.encode()]

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_no_auth(self, payload_version: PayloadVersion):
        api_version = to_api_version(payload_version)
        url = reverse(f'{api_version}:passage-export')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_wrong_auth(self, payload_version: PayloadVersion):
        api_version = to_api_version(payload_version)
        url = reverse(f'{api_version}:passage-export')
        response = self.client.get(url, HTTP_AUTHORIZATION='Token bar')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_no_filters(self, payload_version: PayloadVersion):

        reading_count = 4
        camera_count = 3
        readings_per_camera = 2

        now = datetime.now()
        today = datetime(now.year, now.month, now.day)

        # Get the first day of the week; 2 weeks ago
        start_date = today - timedelta(days=now.weekday(), weeks=2)

        # Fill 3 weeks of data to ensure our export will only get the
        # previous week
        for day in range(7 * 3):
            # Generate 24 hours of data
            for hour in range(24):
                date = start_date + timedelta(days=day, hours=hour)

                # Generate multiple records per camera
                for i in range(camera_count):
                    num = i % camera_count + 1
                    baker.make(
                        'passage.PassageHourAggregation',
                        camera_id=num,
                        camera_naam=f'Camera: {num}',
                        count=reading_count,
                        date=date,
                        year=date.year,
                        week=date.isocalendar()[1],
                        hour=date.hour,
                        taxi_indicator=True,
                        _quantity=readings_per_camera,
                    )

        # first post a record
        api_version = to_api_version(payload_version)
        url = reverse(f'{api_version}:passage-export')
        response = self.client.get(url, HTTP_AUTHORIZATION='Token foo')
        assert response.status_code == 200

        lines = [line.decode() for line in response.streaming_content]
        content = list(csv.reader(lines))
        header = content.pop(0)
        assert header == ['camera_id', 'camera_naam', 'bucket', 'sum']
        assert len(content) == 7 * 24 * camera_count

        expected_content = []
        previous_week = today - timedelta(days=now.weekday(), weeks=1)
        for day in range(7):
            for hour in range(24):
                expected_datetime = previous_week + timedelta(days=day, hours=hour)
                for camera in range(camera_count):
                    camera += 1
                    expected_row = [
                        str(camera),
                        f'Camera: {camera}',
                        expected_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        str(reading_count * readings_per_camera),
                    ]
                    expected_content.append(tuple(expected_row))

        content = set(map(tuple, content))
        expected_content = set(map(tuple, expected_content))
        assert set(expected_content) == set(content)

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_filters(self, payload_version: PayloadVersion):
        date = datetime.fromisocalendar(2019, 11, 1)
        # create data for 3 cameras
        baker.make(
            'passage.PassageHourAggregation',
            camera_id=cycle(range(1, 4)),
            camera_naam=cycle(f'Camera: {i}' for i in range(1, 4)),
            date=date,
            year=date.year,
            week=date.isocalendar()[1],
            hour=1,
            _quantity=100,
        )
        api_version = to_api_version(payload_version)
        url = reverse(f'{api_version}:passage-export')
        response = self.client.get(
            url, dict(year=2019, week=12), HTTP_AUTHORIZATION='Token foo'
        )
        assert response.status_code == 200
        lines = [x for x in response.streaming_content]
        assert len(lines) == 0

        response = self.client.get(
            url, dict(year=2019, week=11), HTTP_AUTHORIZATION='Token foo'
        )
        assert response.status_code == 200
        lines = [x for x in response.streaming_content]

        # Expect the header and 3 lines
        assert len(lines) == 4

        response = self.client.get(url, dict(year=2019), HTTP_AUTHORIZATION='Token foo')
        assert response.status_code == 200
        lines = [x for x in response.streaming_content]

        # Expect the header and 3 lines
        assert len(lines) == 4

    def test_privacy_maximum_massa(self, payload_version: PayloadVersion):
        payload = self.payload(payload_version)
        if payload_version == 'passage-v1':
            payload['toegestaneMaximumMassaVoertuig'] = 3000
        else:
            payload['voertuig']['toegestaneMaximumMassaVoertuig'] = 3000

        res = self.post(payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(passage_id=payload['id'])
        assert_response(res.data, payload)

    def test_privacy_voertuig_soort(self, payload_version: PayloadVersion):
        payload = self.payload(payload_version)
        if payload_version == 'passage-v1':
            payload['voertuigSoort'] = 'PeRsonEnaUto'
        else:
            payload['voertuig']['voertuigSoort'] = 'PeRsonEnaUto'

        res = self.post(payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(passage_id=payload['id'])
        assert_response(res.data, payload)

    def test_privacy_tenaamstelling(self, payload_version: PayloadVersion):
        # version 2 only sends datum tenaamstelling
        if payload_version == 'passage-v1':
            payload = self.payload(payload_version)
            payload['datumTenaamstelling'] = '2020-02-02'

            res = self.post(payload)
            assert res.status_code == 201, res.data
            assert Passage.objects.get(passage_id=payload['id'])
            assert_response(res.data, payload)

    def test_privacy_datum_eerste_toelating(self, payload_version: PayloadVersion):
        # version 2 only sends jaar eerste toelating
        if payload_version == 'passage-v1':
            payload = self.payload(payload_version)
            payload['datumEersteToelating'] = date(2020, 2, 2)

            res = self.post(payload)
            assert res.status_code == 201, res.data
            assert Passage.objects.get(passage_id=payload['id'])
            assert_response(res.data, payload)


@pytest.mark.django_db
class TestPassageAPI_Version_2(TestPassageAPI):
    """Test the passage version 2 endpoint."""

    def test_downgraded_version_2_message_should_save_new_fields(self):
        """
        Verify that when a version 2 message is flattened that the new fields
        are correctly saved to the database.
        """
        payload = self.payload('passage-v2')
        res = self.post(payload)
        assert res.status_code == 201, res.data

        actual = Passage.objects.get(passage_id=payload['id'])

        vehicle = payload['voertuig']
        number_plate = vehicle['kenteken']
        reliability = number_plate['betrouwbaarheid']

        assert str(actual.passage_id) == payload['id']
        assert actual.kenteken_hash == number_plate['kentekenHash']
        assert actual.massa_ledig_voertuig == vehicle['massaLedigVoertuig']
        assert actual.aantal_assen == vehicle['aantalAssen']
        assert actual.aantal_staanplaatsen == vehicle['aantalStaanplaatsen']
        assert actual.aantal_wielen == vehicle['aantalWielen']
        assert actual.aantal_zitplaatsen == vehicle['aantalZitplaatsen']
        assert actual.handelsbenaming == vehicle['handelsbenaming']
        assert actual.lengte == vehicle['lengte']
        assert actual.breedte == vehicle['breedte']
        assert actual.maximum_massa_trekken_ongeremd == vehicle['maximumMassaTrekkenOngeremd']
        assert actual.maximum_massa_trekken_geremd == vehicle['maximumMassaTrekkenGeremd']
        assert actual.indicatie_snelheid == vehicle['indicatieSnelheid']
        assert actual.kenteken_nummer_betrouwbaarheid == reliability['kentekenBetrouwbaarheid']
        assert actual.kenteken_karakters_betrouwbaarheid == reliability['karaktersBetrouwbaarheid']
        assert actual.kenteken_land_betrouwbaarheid == reliability['landcodeBetrouwbaarheid']
        assert actual.rijstrook == payload['rijstrook']
        assert actual.rijrichting == RIJRICHTING_MAPPING[payload['rijrichting']]

        # these moved into brandstoffen
        assert actual.co2_uitstoot_gecombineerd is None
        assert actual.co2_uitstoot_gewogen is None
        assert actual.milieuklasse_eg_goedkeuring_zwaar is None

    def test_downgraded_version_2_empty_fields(self):
        """
        Verify that when a version 2 message, where all optional fields are missing,
        is flattened and is correctly saved to the database.
        """
        payload = self.payload('passage-v2')

        # remove all fields that are not required (version only used for test)
        required_passage_keys = [
            'id', 'voertuig', 'volgnummer', 'timestamp', 'camera', 'version'
        ]
        for key in list(payload.keys()):
            if key not in required_passage_keys:
                del payload[key]

        # remove all data in voertuig, all keys are optional
        payload['voertuig'] = {}

        # remove all fields from camera that are not required
        required_camera_keys = ['id']
        for key in list(payload['camera'].keys()):
            if key not in required_camera_keys:
                del payload['camera'][key]

        res = self.post(payload)
        assert res.status_code == 201, res.data

        actual = Passage.objects.get(passage_id=payload['id'])

        # assert that the required fields are correct
        assert str(actual.passage_id) == payload['id']
        assert actual.volgnummer == payload['volgnummer']
        assert actual.passage_at == payload['timestamp']
        assert actual.camera_id == payload['camera']['id']

        # assert the rest of the optional fields are empty (id, created_at, version
        # fields are added because they are auto-populated
        required_fields = [
            'id',
            'created_at',
            'version',
            'brandstoffen',
            'passage_id',
            'volgnummer',
            'passage_at',
            'camera_id',
        ]
        assert actual.brandstoffen == []
        for field in Passage._meta.get_fields():
            if field.name not in required_fields:
                assert getattr(actual, field.name) is None
