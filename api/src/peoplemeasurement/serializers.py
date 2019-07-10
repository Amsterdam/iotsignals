from django.contrib.gis.geos import Point

from rest_framework import serializers
from datapunt_api.rest import HALSerializer
from datapunt_api.rest import DisplayField

from .models import PeopleMeasurement

import logging
log = logging.getLogger(__name__)


class PeopleMeasurementSerializer(HALSerializer):

    _display = DisplayField()

    class Meta:
        model = PeopleMeasurement
        fields = [
            '_display',
            '_links',
            'id',
            'version',
            'timestamp',
            'sensor',
            'sensortype',
            'latitude',
            'longitude',
            'count',
        ]


class PeopleMeasurementDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PeopleMeasurement
        fields = '__all__'
