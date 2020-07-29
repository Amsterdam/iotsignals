from datapunt_api.pagination import HALCursorPagination
from datapunt_api.rest import DatapuntViewSetWritable
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import exceptions, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from writers import CSVStream

from passage.case_converters import to_snakecase

from . import models, serializers


class PassageFilter(FilterSet):
    class Meta(object):
        model = models.Passage
        fields = {
            'merk': ['exact'],
            'voertuig_soort': ['exact'],
            'indicatie_snelheid': ['exact'],
            'kenteken_nummer_betrouwbaarheid': ['exact'],
            'version': ['exact'],
            'kenteken_land': ['exact'],
            'toegestane_maximum_massa_voertuig': ['exact'],
            'europese_voertuigcategorie': ['exact'],
            'europese_voertuigcategorie_toevoeging': ['exact'],
            'taxi_indicator': ['exact'],
            'maximale_constructie_snelheid_bromsnorfiets': ['exact'],
            'created_at': ['exact', 'lt', 'gt'],
            'passage_at': ['exact', 'lt', 'gt'],
            'diesel': ['isnull', 'exact', 'lt', 'gt'],
            'gasoline': ['isnull', 'exact', 'lt', 'gt'],
            'electric': ['isnull', 'exact', 'lt', 'gt'],
        }


"""
from dateutil import tz

utcnow = datetime.datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
"""


class PassagePager(HALCursorPagination):
    """Sidcon pagination configuration.

    Fill-levels will be many. So we use cursor based pagination.
    """

    count_table = False
    page_size = 50
    max_page_size = 10000
    ordering = "-passage_at"


class PassageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PassageDetailSerializer
    serializer_detail_class = serializers.PassageDetailSerializer

    queryset = models.Passage.objects.all().order_by('passage_at')

    filter_backends = (DjangoFilterBackend,)
    filter_class = PassageFilter

    pagination_class = PassagePager

    # override create to convert request.data from camelcase to snakecase.
    def create(self, request, *args, **kwargs):
        tmp = {to_snakecase(k): v for k, v in request.data.items()}
        request.data.clear()
        request.data.update(tmp)
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='export-taxi')
    def export_taxi(self, request, *args, **kwargs):
        # 1. Get the iterator of the QuerySet
        iterator = (
            models.PassageHourAggregation.objects.annotate(datum=F('date'))
            .values('datum')
            .annotate(aantal_taxi_passages=Sum('count'))
            .filter(taxi_indicator=True)
        )

        # 2. Create the instance of our CSVStream class
        csv_stream = CSVStream()

        # 3. Stream (download) the file
        return csv_stream.export(
            "export",
            iterator,
            lambda x: [x['datum'], x['aantal_taxi_passages']],
            header=['datum', 'aantal_taxi_passages'],
        )
