# std
import csv
import logging
from datetime import datetime, timedelta
from itertools import cycle
# 3rd party
from typing import Literal
import pytest
from django.contrib.gis.geos import Point
from django.db import connection
from django.test import override_settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from hypothesis import given, settings, seed, Verbosity, Phase, HealthCheck
from model_bakery import baker
from rest_framework_gis.fields import GeoJsonDict
# iotsignals
from make_paritions import make_partition_sql
from passage.case_converters import to_snakecase
from passage.models import Passage
from rest_framework import status
from .factories import PassageFactory
from .strategies import st_passages
from passage.views import downgrade, upgrade, NEW_FIELDS
from ..util import keymap, keyfilter

log = logging.getLogger(__name__)


class TestRoundTrip:

    @given(st_passages(version=1))
    @settings(max_examples=10)
    def test_roundtrip_1_2_1(self, passage):
        """
        Attempt to verify the upgrade and downgrade functions by checking the
        roundtrip property, i.e. converting 1 -> 2 -> should give us what we
        started with.
        """
        passage = keymap(to_snakecase, passage)
        v2 = upgrade(passage)
        v1 = downgrade(v2)

        # these fields are irretrievably cleared during upgrade
        expected = dict(
            passage,
            datum_tenaamstelling=None,
            datum_eerste_toelating=f"{passage['datum_eerste_toelating'][:4]}-01-01",
        )

        assert expected == v1

    @given(st_passages(version=2))
    @settings(max_examples=10)
    def test_roundtrip_2_1_2(self, passage):
        """
        Attempt to verify the upgrade and downgrade functions by checking the
        roundtrip property, i.e. converting 2 -> 1 -> 2 should give us what we
        started with.
        """
        passage = keymap(to_snakecase, passage)
        v1 = downgrade(passage, drop_new_fields=False)
        v2 = upgrade(v1)
        assert passage == v2


def get_passage_payload(version: Literal[1, 2]) -> dict:
    """
    Get a passage payload for the requested version

    :param version: The version of the payload to get.

    :return: Dict containing the passage information (payload for POST request)
    """
    result = None

    # This is abusing hypothesis a little bit to just draw one deterministic
    # example.
    @settings(
        max_examples=1,
        database=None,
        deadline=None,
        verbosity=Verbosity.quiet,
        phases=(Phase.generate,),
        suppress_health_check=HealthCheck.all(),
    )
    @seed(12345)
    @given(st_passages(version=version))
    def draw_example(passage):
       nonlocal result
       result = passage

    draw_example()

    assert isinstance(result, dict)  # silence mypy
    return result


def get_records_in_partition():
    with connection.cursor() as cursor:
        cursor.execute('select count(*) from passage_passage_20181016')
        row = cursor.fetchone()
        if len(row) > 0:
            return row[0]
        return 0


def assert_response(response, payload):
    data = response.data
    is_version_1 = payload['version'] == 'passage-v1'

    # The response from the POST is always in version-1 (flat) format, but the
    # payload that was sent could be version-1 (flat) or version-2 (nested)
    # so to correctly assert we need to do some conversion.
    snake_case_payload = keymap(to_snakecase, payload)
    expected = snake_case_payload if is_version_1 else downgrade(snake_case_payload, drop_new_fields=False)

    # Check for privacy changes
    if expected['toegestane_maximum_massa_voertuig'] <= 3500:
        expected['toegestane_maximum_massa_voertuig'] = 1500
        expected['europese_voertuigcategorie_toevoeging'] = None
        expected['merk'] = None

    if expected['voertuig_soort'].lower() == 'personenauto':
        expected['inrichting'] = 'Personenauto'

    expected[
        'datum_eerste_toelating'
    ] = f"{expected['datum_eerste_toelating'][:4]}-01-01"

    expected['datum_tenaamstelling'] = None

    for k, v in expected.items():
        k = to_snakecase(k)
        if isinstance(data[k], GeoJsonDict):
            coordinates = data[k]['coordinates']
            assert Point(*coordinates).hex == v, (k, data[k])
        else:
            assert data[k] == v, (k, data[k])


class TestPassageAPI:

    @pytest.fixture(autouse=True)
    def inject_api_client(self, api_client):
        self.client = api_client

    def valid_response(self, url, response, content_type):
        """Check common status/json."""
        assert 200 == response.status_code, "Wrong response code for {}".format(url)

        assert (
            f"{content_type}" == response["Content-Type"]
        ), "Wrong Content-Type for {}".format(url)

    def url(self, version):
        return f'/v{version - 1}/milieuzone/passage/'

    def post(self, body):
        """
        POST the given body to the passage endpoint.
        """
        version = int(body['version'][len('passage-v'):])
        timestamp = parse_datetime(body['passageAt' if version == 1 else 'timestamp'])

        with connection.cursor() as cursor:
            for timestamp in (timestamp + timedelta(days=i) for i in range(-1, 2)):
                cursor.execute(make_partition_sql(timestamp))

        return self.client.post(self.url(version), body, format='json')


@pytest.mark.django_db
@pytest.mark.parametrize('version', [1, 2])
class TestPassageAPI_Versions_1_2(TestPassageAPI):
    """Test the passage endpoint (both versions 1 and 2)."""

    def test_post_new_passage(self, version):
        """ Test posting a new passage """
        passage_payload = get_passage_payload(version)
        assert Passage.objects.count() == 0
        res = self.post(passage_payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(id=passage_payload['id'])
        assert_response(res, passage_payload)

    def test_post_new_passage_missing_attr(self, version):
        """Test posting a new passage with missing fields"""
        passage_payload = get_passage_payload(version)
        assert Passage.objects.count() == 0
        if version == 1:
            passage_payload.pop('merk')
            passage_payload.pop('europeseVoertuigcategorieToevoeging')
        else:
            passage_payload['voertuig'].pop('merk')
            passage_payload['voertuig'].pop('europeseVoertuigcategorieToevoeging')
        res = self.post(passage_payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(id=passage_payload['id'])
        assert_response(res, passage_payload)

    def test_post_range_betrouwbaarheid(self, version):
        """Test posting a invalid range betrouwbaarheid"""
        passage_payload = get_passage_payload(version)
        before = get_records_in_partition()
        if version == 1:
            passage_payload["kentekenNummerBetrouwbaarheid"] = -1
        else:
            passage_payload["betrouwbaarheid"]["kentekenBetrouwbaarheid"] = -1
        res = self.post(passage_payload)

        # check if the record was NOT stored in the correct partition
        assert before == get_records_in_partition()
        assert res.status_code == 400, res.data

    def test_post_duplicate_key(self, version):
        """ Test posting a new passage with a duplicate key """
        passage_payload = get_passage_payload(version)
        res = self.post(passage_payload)
        assert res.status_code == 201, res.data

        # Post the same message again
        res = self.post(passage_payload)
        assert res.status_code == 409, res.data

    def test_get_passages_not_allowed(self, version):
        PassageFactory.create()
        response = self.client.get(self.url(version))
        assert response.status_code == 405

    def test_update_passages_not_allowed(self, version):
        # first post a record
        passage_payload = get_passage_payload(version)
        self.post(passage_payload)

        # Then check if I cannot update it
        response = self.client.put(
            f'{self.url(version)}{passage_payload["id"]}/', passage_payload, format='json'
        )
        assert response.status_code == 404

    def test_delete_passages_not_allowed(self, version):
        # first post a record
        passage_payload = get_passage_payload(version)
        self.post(passage_payload)

        # Then check if I cannot update it
        response = self.client.delete(f'{self.url(version)}{passage_payload["id"]}/')
        assert response.status_code == 404

    def test_passage_taxi_export(self, version):

        baker.make(
            'passage.PassageHourAggregation',
            count=2,
            taxi_indicator=True,
            _quantity=500,
        )

        # first post a record
        url = reverse(f'v{version - 1}:passage-export-taxi')
        response = self.client.get(url)
        assert response.status_code == 200

        date = datetime.now().strftime("%Y-%m-%d")
        lines = [line for line in response.streaming_content]
        assert lines == [b'datum,aantal_taxi_passages\r\n', f'{date},1000\r\n'.encode()]

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_no_auth(self, version):
        url = reverse(f'v{version - 1}:passage-export')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_wrong_auth(self, version):
        url = reverse(f'v{version - 1}:passage-export')
        response = self.client.get(url, HTTP_AUTHORIZATION='Token bar')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(AUTHORIZATION_TOKEN='foo')
    def test_passage_export_no_filters(self, version):

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
        url = reverse(f'v{version - 1}:passage-export')
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
    def test_passage_export_filters(self, version):
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
        url = reverse(f'v{version - 1}:passage-export')
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

    def test_privacy_maximum_massa(self, version):
        passage_payload = get_passage_payload(version)
        if version == 1:
            passage_payload['toegestaneMaximumMassaVoertuig'] = 3000
        else:
            passage_payload['voertuig']['toegestaneMaximumMassaVoertuig'] = 3000

        res = self.post(passage_payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(id=passage_payload['id'])
        assert_response(res, passage_payload)

    def test_privacy_voertuig_soort(self, version):
        passage_payload = get_passage_payload(version)
        if version == 1:
            passage_payload['voertuigSoort'] = 'PeRsonEnaUto'
        else:
            passage_payload['voertuig']['voertuigSoort'] = 'PeRsonEnaUto'

        res = self.post(passage_payload)
        assert res.status_code == 201, res.data
        assert Passage.objects.get(id=passage_payload['id'])
        assert_response(res, passage_payload)

    def test_privacy_tenaamstelling(self, version):
        # version 2 only sends datum tenaamstelling
        if version == 1:
            passage_payload = get_passage_payload(version)
            passage_payload['datumTenaamstelling'] = '2020-02-02'
    
            res = self.post(passage_payload)
            assert res.status_code == 201, res.data
            assert Passage.objects.get(id=passage_payload['id'])
            assert_response(res, passage_payload)

    def test_privacy_datum_eerste_toelating(self, version):
        # version 2 only sends jaar eerste toelating
        if version == 1:
            passage_payload = get_passage_payload(version)
            passage_payload['datumEersteToelating'] = '2020-02-02'

            res = self.post(passage_payload)
            assert res.status_code == 201, res.data
            assert Passage.objects.get(id=passage_payload['id'])
            assert_response(res, passage_payload)


@pytest.mark.django_db
class TestPassageAPI_Version_2(TestPassageAPI):
    """Test the passage version 2 endpoint."""

    @pytest.fixture(autouse=True)
    def inject_api_client(self, api_client):
        self.client = api_client

    def test_downgraded_version_2_message_should_save_new_fields(self):
        """
        Verify that when a version 2 message is flattened that the new fields
        are correctly saved to the database.
        """
        passage_payload = get_passage_payload(2)
        res = self.post(passage_payload)
        assert res.status_code == 201, res.data

        actual = Passage.objects.values('kenteken_hash', *NEW_FIELDS).get(id=passage_payload['id'])
        actual['vervaldatum_apk'] = str(actual['vervaldatum_apk'])
        actual['maximum_massa_trekken_geremd'] = int(actual['maximum_massa_trekken_geremd'])
        actual['maximum_massa_trekken_ongeremd'] = int(actual['maximum_massa_trekken_ongeremd'])

        vehicle_number_plate = {
            **passage_payload['voertuig']['kenteken'],
            **passage_payload['voertuig'],
        }
        expected = keyfilter(
            lambda key: key in NEW_FIELDS,
            keymap(to_snakecase, vehicle_number_plate),
        )
        assert actual == expected
