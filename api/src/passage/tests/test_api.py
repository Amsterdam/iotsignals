import logging

from django.db import connection
from django.http import StreamingHttpResponse
from django.urls import reverse
from passage.case_converters import to_camelcase
from model_bakery import baker
from rest_framework.test import APITestCase

from .factories import PassageFactory

log = logging.getLogger(__name__)


TEST_POST = {
    "version": "passage-v1",
    "id": "cbbd2efc-78f4-4d41-bf5b-4cbdf1e87269",
    "passage_at": "2018-10-16T12:13:44+02:00",
    "straat": "Spaarndammerdijk",
    "rijstrook": 1,
    "rijrichting": 1,
    "camera_id": "ddddffff-4444-aaaa-7777-aaaaeeee1111",
    "camera_naam": "Spaarndammerdijk [Z]",
    "camera_kijkrichting": 0,
    "camera_locatie": {"type": "Point", "coordinates": [4.845423, 52.386831]},
    "kenteken_land": "NL",
    "kenteken_nummer_betrouwbaarheid": 640,
    "kenteken_land_betrouwbaarheid": 690,
    "kenteken_karakters_betrouwbaarheid": [
        {"betrouwbaarheid": 650, "positie": 1},
        {"betrouwbaarheid": 630, "positie": 2},
        {"betrouwbaarheid": 640, "positie": 3},
        {"betrouwbaarheid": 660, "positie": 4},
        {"betrouwbaarheid": 620, "positie": 5},
        {"betrouwbaarheid": 640, "positie": 6},
    ],
    "indicatie_snelheid": 23,
    "automatisch_verwerkbaar": True,
    "voertuig_soort": "Bromfiets",
    "merk": "SYM",
    "inrichting": "N.V.t.",
    "datum_eerste_toelating": "2015-03-06",
    "datum_tenaamstelling": "2015-03-06",
    "toegestane_maximum_massa_voertuig": 249,
    "europese_voertuigcategorie": "L1",
    "europese_voertuigcategorie_toevoeging": "e",
    "taxi_indicator": True,
    "maximale_constructie_snelheid_bromsnorfiets": 25,
    "brandstoffen": [{"brandstof": "Benzine", "volgnr": 1}],
    "versit_klasse": "test klasse",
}


def get_records_in_partition():
    with connection.cursor() as cursor:
        cursor.execute('select count(*) from passage_passage_20181016')
        row = cursor.fetchone()
        if len(row) > 0:
            return row[0]
        return 0


class PassageAPITestV0(APITestCase):
    """Test the passage endpoint."""

    def setUp(self):
        self.URL = '/v0/milieuzone/passage/'
        self.p = PassageFactory()

    def valid_response(self, url, response, content_type):
        """Check common status/json."""
        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

        self.assertEqual(
            f"{content_type}",
            response["Content-Type"],
            "Wrong Content-Type for {}".format(url),
        )

    def test_post_new_passage_camelcase(self):
        """ Test posting a new camelcase passage """
        before = get_records_in_partition()

        # convert keys to camelcase for test
        camel_case = {to_camelcase(k): v for k, v in TEST_POST.items()}
        res = self.client.post(self.URL, camel_case, format='json')

        # check if the record was stored in the correct partition
        self.assertEqual(before + 1, get_records_in_partition())

        self.assertEqual(res.status_code, 201, res.data)
        for k, v in TEST_POST.items():
            self.assertEqual(res.data[k], v)

    def test_post_new_passage(self):
        """ Test posting a new passage """
        before = get_records_in_partition()

        res = self.client.post(self.URL, TEST_POST, format='json')

        # check if the record was stored in the correct partition
        self.assertEqual(before + 1, get_records_in_partition())

        self.assertEqual(res.status_code, 201, res.data)
        for k, v in TEST_POST.items():
            self.assertEqual(res.data[k], v)

    def test_post_new_passage_missing_attr(self):
        """Test posting a new passage with missing fields"""
        before = get_records_in_partition()
        NEW_TEST = dict(TEST_POST)
        NEW_TEST.pop('voertuig_soort')
        NEW_TEST.pop('europese_voertuigcategorie_toevoeging')
        res = self.client.post(self.URL, NEW_TEST, format='json')

        # check if the record was stored in the correct partition
        self.assertEqual(before + 1, get_records_in_partition())

        self.assertEqual(res.status_code, 201, res.data)
        for k, v in NEW_TEST.items():
            self.assertEqual(res.data[k], v)

    def test_post_range_betrouwbaarheid(self):
        """Test posting a invalid range betrouwbaarheid"""
        before = get_records_in_partition()
        NEW_TEST = dict(TEST_POST)
        NEW_TEST["kenteken_nummer_betrouwbaarheid"] = -1
        res = self.client.post(self.URL, NEW_TEST, format='json')

        # check if the record was NOT stored in the correct partition
        self.assertEqual(before, get_records_in_partition())
        self.assertEqual(res.status_code, 400, res.data)

    def test_post_duplicate_key(self):
        """ Test posting a new passage with a duplicate key """
        before = get_records_in_partition()

        res = self.client.post(self.URL, TEST_POST, format='json')
        self.assertEqual(res.status_code, 201, res.data)

        # # Post the same message again
        res = self.client.post(self.URL, TEST_POST, format='json')
        self.assertEqual(res.status_code, 409, res.data)

    def test_get_passages_not_allowed(self):
        PassageFactory.create()
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 405)

    def test_update_passages_not_allowed(self):
        # first post a record
        self.client.post(self.URL, TEST_POST, format='json')

        # Then check if I cannot update it
        response = self.client.put(
            f'{self.URL}{TEST_POST["id"]}/', TEST_POST, format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_passages_not_allowed(self):
        # first post a record
        self.client.post(self.URL, TEST_POST, format='json')

        # Then check if I cannot update it
        response = self.client.delete(f'{self.URL}{TEST_POST["id"]}/')
        self.assertEqual(response.status_code, 404)

    def test_passage_taxi_export(self):

        baker.make('passage.PassageHourAggregation', count=2, taxi_indicator=True, _quantity=500)

        # first post a record
        url = reverse('v0:passage-export-taxi')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        assert isinstance(response, StreamingHttpResponse)

        content = b''.join(response.streaming_content)
        assert content == b'datum,aantal_taxi_passages\r\n2020-07-29,1000\r\n'
