from django_filters.rest_framework import FilterSet

from django_filters.rest_framework import DjangoFilterBackend
from datapunt_api.pagination import HALCursorPagination
from datapunt_api.rest import DatapuntViewSetWritable

from .models import PeopleMeasurement
from . import serializers


class PeopleMeasurementFilter(FilterSet):
    class Meta(object):
        model = PeopleMeasurement
        fields = {
            'version': ['exact'],
            'timestamp': ['exact', 'lt', 'gt'],
            'sensor': ['exact'],
            'sensortype': ['exact'],
            'latitude': ['exact', 'lt', 'gt'],
            'longitude': ['exact', 'lt', 'gt'],
            'count': ['exact', 'lt', 'gt']
        }


class PeopleMeasurementPager(HALCursorPagination):
    count_table = False
    page_size = 100
    max_page_size = 10000
    ordering = '-timestamp'


class PeopleMeasurementViewSet(DatapuntViewSetWritable):
    serializer_class = serializers.PeopleMeasurementSerializer
    serializer_detail_class = serializers.PeopleMeasurementDetailSerializer

    queryset = PeopleMeasurement.objects.all().order_by('timestamp')

    http_method_names = ['post', 'list', 'get']

    filter_backends = [DjangoFilterBackend]
    filter_class = PeopleMeasurementFilter

    pagination_class = PeopleMeasurementPager
