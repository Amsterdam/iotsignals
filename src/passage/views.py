# std
from datetime import timedelta
# 3rd party
from contrib.rest_framework.authentication import SimpleTokenAuthentication
from datapunt_api.pagination import HALCursorPagination
from django.db.models import DateTimeField, ExpressionWrapper, F, Sum
from django.utils import timezone
from django_filters.filterset import filterset_factory
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
# iotsignals
from passage.conversion import convert_to_v1
from passage.case_converters import to_snakecase
from passage.expressions import HoursInterval
from writers import CSVExport

from . import models, serializers
from .util import keymap


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

    @action(
        methods=['get'],
        detail=False,
        url_path='export',
        authentication_classes=[SimpleTokenAuthentication],
        permission_classes=[IsAuthenticated],
    )
    def export(self, request, *args, **kwargs):
        # 1. Get the iterator of the QuerySet
        previous_week = timezone.now() - timedelta(days=timezone.now().weekday(), weeks=1)
        year = previous_week.year
        week = previous_week.isocalendar()[1]

        Filter = filterset_factory(
            models.PassageHourAggregation, fields=['year', 'week']
        )
        qs = Filter(request.GET).qs

        # If no date has been given, we return the data of last week
        # Since the last week of the year can contain days of both years
        # we will search in both years.
        if not request.GET.get('year') and not request.GET.get('week'):
            monday = previous_week
            sunday = monday + timedelta(days=6)
            qs = qs.filter(date__gte=monday, date__lte=sunday)

        qs = (
            qs.annotate(
                bucket=ExpressionWrapper(
                    F("date") + HoursInterval(F("hour")), output_field=DateTimeField()
                ),
            )
            .values("camera_id", "camera_naam", "bucket")
            .annotate(sum=Sum("count"))
            .order_by("bucket")
        )

        # 2. Create the instance of our CSVExport class
        csv_export = CSVExport()

        # 3. Export (download) the file
        return csv_export.export("export", qs.iterator(), streaming=True)


class PassageViewSetVersion2(PassageViewSet):

    def create(self, request, *args, **kwargs):
        # convert to snakecase, and downgrade to a flattened structure.
        passage_v1 = keymap(to_snakecase, request.data)
        passage_v2 = convert_to_v1(passage_v1)
        request.data.update(passage_v2)
        return super().create(request, *args, **kwargs)
