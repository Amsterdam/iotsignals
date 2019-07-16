from rest_framework import serializers
from datapunt_api.rest import HALSerializer

from .models import PeopleMeasurement

import logging
log = logging.getLogger(__name__)


class PeopleMeasurementSerializer(HALSerializer):

    class Meta:
        model = PeopleMeasurement
        fields = [
            '_links',
            'id',
            'version',
            'timestamp',
            'sensor',
            'sensortype',
            'latitude',
            'longitude',
            'count',
            'details',
        ]


class PeopleMeasurementDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PeopleMeasurement
        fields = '__all__'
