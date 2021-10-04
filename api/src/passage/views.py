# std
from copy import deepcopy
from datetime import date, timedelta
# 3rd party
from django.contrib.gis.geos import Point, GEOSGeometry
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

    @action(methods=['get'], detail=False, url_path='export-taxi')
    def export_taxi(self, request, *args, **kwargs):
        # 1. Get the iterator of the QuerySet
        qs = (
            models.PassageHourAggregation.objects.annotate(datum=F('date'))
            .values('datum')
            .annotate(aantal_taxi_passages=Sum('count'))
            .filter(taxi_indicator=True)
        )

        # 2. Create the instance of our CSVExport class
        csv_export = CSVExport()

        # 3. Export (download) the file
        #  return csv_export.export(
        #  "export",
        #  iterator,
        #  lambda x: [x['datum'], x['aantal_taxi_passages']],
        #  header=['datum', 'aantal_taxi_passages'],
        #  )

        return csv_export.export("export", qs.iterator(), streaming=True)

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


NEW_FIELDS = [
    'kenteken_hash',
    'vervaldatum_apk',
    'wam_verzekerd',
    'massa_ledig_voertuig',
    'aantal_assen',
    'aantal_staanplaatsen',
    'aantal_wielen',
    'aantal_zitplaatsen',
    'handelsbenaming',
    'lengte',
    'breedte',
    'maximum_massa_trekken_ongeremd',
    'maximum_massa_trekken_geremd',
    'co2_uitstoot_gecombineerd',
    'co2_uitstoot_gewogen',
    'milieuklasse_eg_goedkeuring_zwaar',
]


RIJRICHTING_MAPPING = {'VAN': -1, 'NAAR': 1}
RIJRICHTING_MAPPING_INVERSE = {value: key for key, value in RIJRICHTING_MAPPING.items()}


def upgrade(passage):
    """
    Upgrade the given payload from v1 to v2.
    """
    passage = deepcopy(passage)

    camera_locatie = GEOSGeometry(passage.pop('camera_locatie'))

    result = dict(
        # passage properties
        id=passage.pop('id'),
        version='passage-v2',
        timestamp=passage.pop('passage_at'),
        automatisch_verwerkbaar=passage.pop('automatisch_verwerkbaar'),
        indicatie_snelheid=passage.pop('indicatie_snelheid'),
        # camera properties
        camera=dict(
            id=passage.pop('camera_id'),
            naam=passage.pop('camera_naam'),
            kijkrichting=passage.pop('camera_kijkrichting'),
            rijstrook=passage.pop('rijstrook'),
            locatie={
                "latitude": camera_locatie.x,
                "longitude": camera_locatie.y,
            },
            straat=passage.pop('straat'),
            rijrichting=RIJRICHTING_MAPPING_INVERSE[passage.pop('rijrichting')]
        ),
        # anpr measurement accuracy properties
        betrouwbaarheid=dict(
            landcode_betrouwbaarheid=passage.pop('kenteken_land_betrouwbaarheid'),
            kenteken_betrouwbaarheid=passage.pop('kenteken_nummer_betrouwbaarheid'),
            karakters_betrouwbaarheid=passage.pop('kenteken_karakters_betrouwbaarheid'),
        ),
        # vehicle properties
        voertuig=dict(
            kenteken=dict(
                landcode=passage.pop('kenteken_land'),
                kenteken_hash=passage.pop('kenteken_hash', None),
            ),
            voertuig_soort=passage.pop('voertuig_soort'),
            merk=passage.pop('merk'),
            inrichting=passage.pop('inrichting'),
            jaar_eerste_toelating=int(passage.pop('datum_eerste_toelating')[:4]),
            toegestane_maximum_massa_voertuig=passage.pop('toegestane_maximum_massa_voertuig'),
            europese_voertuigcategorie=passage.pop('europese_voertuigcategorie'),
            europese_voertuigcategorie_toevoeging=passage.pop('europese_voertuigcategorie_toevoeging'),
            taxi_indicator=passage.pop('taxi_indicator'),
            maximale_constructiesnelheid_brom_snorfiets=passage.pop('maximale_constructie_snelheid_bromsnorfiets'),
            brandstoffen=[
                dict(naam=fuel.pop('brandstof'), **fuel)
                for fuel in passage.pop('brandstoffen')
            ],
            # New fields...
            versit_klasse=passage.pop('versit_klasse', None),
            vervaldatum_apk=passage.pop('vervaldatum_apk', None),
            wam_verzekerd=passage.pop('wam_verzekerd', None),
            massa_ledig_voertuig=passage.pop('massa_ledig_voertuig', None),
            aantal_assen=passage.pop('aantal_assen', None),
            aantal_staanplaatsen=passage.pop('aantal_staanplaatsen', None),
            aantal_wielen=passage.pop('aantal_wielen', None),
            aantal_zitplaatsen=passage.pop('aantal_zitplaatsen', None),
            handelsbenaming=passage.pop('handelsbenaming', None),
            lengte=passage.pop('lengte', None),
            breedte=passage.pop('breedte', None),
            maximum_massa_trekken_ongeremd=passage.pop('maximum_massa_trekken_ongeremd', None),
            maximum_massa_trekken_geremd=passage.pop('maximum_massa_trekken_geremd', None),
            co2_uitstoot_gecombineerd=passage.pop('co2_uitstoot_gecombineerd', None),
            co2_uitstoot_gewogen=passage.pop('co2_uitstoot_gewogen', None),
            milieuklasse_eg_goedkeuring_zwaar=passage.pop('milieuklasse_eg_goedkeuring_zwaar', None),
        )
    )

    # we explicitly set the version
    del passage['version']

    # these fields do not exist in v2
    del passage['extra_data']
    del passage['diesel']
    del passage['gasoline']
    del passage['electric']
    del passage['datum_tenaamstelling']

    assert not passage, f"Unprocessed keys: {list(passage)}"

    return result


def downgrade(passage, *, drop_new_fields=True):
    """
    Downgrade the given payload from v2 to v1.

    Note that a downgraded message is never exactly the same as a version 1
    message, some fields from version 1 do not exist in version 2, and when
    keeping new fields there will be a number of additional fields present that
    you wouldn't normally expect in a version 1 message.

    :param passage: The passage payload to downgrade (keys in snakecase)
    :param drop_new_fields: True to remove new fields, False to keep them.

    :return: Dictionary with the payload converted to 'version 1' format.
    """
    clone = deepcopy(passage)

    camera = clone.pop('camera')
    camera_location = camera.pop('locatie')
    vehicle = clone.pop('voertuig')
    betrouwbaarheid = clone.pop('betrouwbaarheid')
    number_plate = vehicle.pop('kenteken')
    fuels = {fuel['naam'] for fuel in vehicle.get('brandstoffen') or []}

    if drop_new_fields:
        for field in NEW_FIELDS:
            if field in vehicle:
                del vehicle[field]

        del number_plate['kenteken_hash']

    result = dict(
        # passage properties
        id=clone.pop('id'),
        automatisch_verwerkbaar=clone.pop('automatisch_verwerkbaar'),
        indicatie_snelheid=clone.pop('indicatie_snelheid'),
        passage_at=clone.pop('timestamp'),
        version='passage-v1',
        kenteken_land_betrouwbaarheid=betrouwbaarheid.pop('landcode_betrouwbaarheid'),
        kenteken_nummer_betrouwbaarheid=betrouwbaarheid.pop('kenteken_betrouwbaarheid'),
        kenteken_karakters_betrouwbaarheid=betrouwbaarheid.pop('karakters_betrouwbaarheid'),
        # vehicle properties
        kenteken_land=number_plate.pop('landcode'),
        diesel=int('Diesel' in fuels),
        gasoline=int('Benzine' in fuels),
        electric=int('Elektriciteit' in fuels),
        datum_eerste_toelating=str(date(int(vehicle.pop('jaar_eerste_toelating')), 1, 1)),
        extra_data=None,
        maximale_constructie_snelheid_bromsnorfiets=vehicle.pop('maximale_constructiesnelheid_brom_snorfiets'),
        brandstoffen=[
            dict(brandstof=fuel.pop('naam'), **fuel)
            for fuel in vehicle.pop('brandstoffen')
        ],
        datum_tenaamstelling=None,
        **vehicle,
        **number_plate,
        # camera properties
        camera_id=camera.pop('id'),
        camera_naam=camera.pop('naam'),
        camera_kijkrichting=camera.pop('kijkrichting'),
        camera_locatie=Point(camera_location['latitude'], camera_location['longitude']).hex,
        rijrichting={'VAN': -1, 'NAAR': 1}[camera.pop('rijrichting')],
        **camera,
    )

    # we explicitly set the version
    del clone['version']

    assert not clone, f"Unprocessed keys: {list(clone)}"

    return result


class PassageViewSetVersion1(PassageViewSet):

    def create(self, request, *args, **kwargs):
        # convert to snakecase, and downgrade to a flattened structure.
        passage = keymap(to_snakecase, request.data)
        downgraded = downgrade(passage, drop_new_fields=False)
        request.data.update(downgraded)
        return super().create(request, *args, **kwargs)