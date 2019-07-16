import logging
from rest_framework.test import APITestCase
from django.db import connection

log = logging.getLogger(__name__)

TEST_POST = {
    "data": {
        "id": "902d9a26-6b6e-49d5-8598-0de774e23da1",
        "sensor": "Kalverstraat",
        "sensortype": "countingcamera",
        "version": "1",
        "latitude":"52.379189",
        "longitude":"4.899431",
        "timestamp": "2019-06-21T10:35:46+02:00",
        "density": 0.0,
        "count": 0.0,
        "speed": 0.6614829134196043
    },
    "details": [
        {
            "timestamp": "2019-06-21T10:35:46+02:00",
            "count": "1.486830472946167",
            "id": "f6c08c28-a800-4e03-b23c-44a6b2d9f53d",
            "direction": "speed"
        },{
            "timestamp": "2019-06-21T10:35:46+02:00",
            "count": "0",
            "id": "b8018928-ff83-4b6a-8934-24f27612e841",
            "direction": "density"
        },{
            "timestamp": "2019-06-21T10:35:46+02:00",
            "count": "6",
            "id": "b8018928-ff83-4b6a-8934-24f27612e841",
            "direction": "up"
        },{
            "timestamp": "2019-06-21T10:35:46+02:00",
            "count": "2",
            "id": "b8018928-ff83-4b6a-8934-24f27612e841",
            "direction": "down"
        },{
            "timestamp": "2019-06-21T10:35:46+02:00",
            "count": "1.3242228031158447",
            "id": "043bb61d-f396-436e-989b-88ce3fb4ded3",
            "direction": "speed"
        }
    ]
}


def get_record_count():
    with connection.cursor() as cursor:
        cursor.execute("select count(id) from peoplemeasurement_peoplemeasurement;")
        row = cursor.fetchone()
        if len(row):
            return row[0]
        return 0


class PeopleMeasurementTestV0(APITestCase):
    """ Test the people measurement endpoint """

    def setUp(self):
        self.URL = '/v0/people/measurement/'

    def test_post_new_people_measurement(self):
        """ Test posting a new vanilla message """
        record_count_before = get_record_count()
        response = self.client.post(self.URL, TEST_POST, format='json')

        self.assertEqual(record_count_before+1, get_record_count())
        self.assertEqual(response.status_code, 201, response.data)

        for k, v in TEST_POST['data'].items():
            self.assertEqual(response.data[k], v)

    def test_post_new_people_measurement_with_missing_density_count_speed_details(self):
        """ Test posting a new vanilla message """
        record_count_before = get_record_count()
        test_post = TEST_POST.copy()
        del test_post['data']['density']
        del test_post['data']['count']
        del test_post['data']['speed']
        del test_post['details']
        response = self.client.post(self.URL, test_post, format='json')

        self.assertEqual(record_count_before+1, get_record_count())
        self.assertEqual(response.status_code, 201, response.data)

        for k, v in test_post['data'].items():
            self.assertEqual(response.data[k], v)

        for i in ('density', 'count', 'speed', 'details'):
            self.assertEqual(response.data[i], None)
