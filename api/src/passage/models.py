import uuid

from datetimeutc.fields import DateTimeUTCField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.gis.db import models


class Passage(models.Model):
    """Passage measurement.

    Each passing of a vehicle with a license plate passes into
    an environment zone which passes an environment camera
    should result in a record here.
    """

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    passage_id = models.UUIDField(null=False, blank=False)
    passage_at = DateTimeUTCField(db_index=True, null=False)
    created_at = DateTimeUTCField(db_index=True, auto_now_add=True, editable=False)
    volgnummer = models.PositiveIntegerField(default=1, null=False, blank=False)

    version = models.CharField(max_length=20)

    # camera properties
    straat = models.CharField(max_length=255, null=True, blank=True)
    rijrichting = models.SmallIntegerField(null=True, blank=True)
    rijstrook = models.SmallIntegerField(null=True, blank=True)
    camera_id = models.CharField(max_length=255, null=True, blank=True)
    camera_naam = models.CharField(max_length=255, null=True, blank=True)
    camera_kijkrichting = models.FloatField(null=True, blank=True)
    camera_locatie = models.PointField(srid=4326, null=True, blank=True)

    # car properties
    kenteken_land = models.CharField(max_length=2, null=True, blank=True)
    kenteken_nummer_betrouwbaarheid = models.SmallIntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)], null=True, blank=True
    )
    kenteken_land_betrouwbaarheid = models.SmallIntegerField(
        validators=[MaxValueValidator(1000), MinValueValidator(0)], null=True, blank=True
    )
    kenteken_karakters_betrouwbaarheid = models.JSONField(null=True, blank=True)
    indicatie_snelheid = models.FloatField(null=True, blank=True)
    automatisch_verwerkbaar = models.BooleanField(null=True, blank=True)
    voertuig_soort = models.CharField(max_length=64, null=True, blank=True)
    merk = models.CharField(max_length=255, null=True, blank=True)
    inrichting = models.CharField(max_length=255, null=True, blank=True)
    datum_eerste_toelating = models.DateField(null=True, blank=True)
    datum_tenaamstelling = models.DateField(null=True, blank=True)
    toegestane_maximum_massa_voertuig = models.IntegerField(null=True, blank=True)
    europese_voertuigcategorie = models.CharField(max_length=2, null=True, blank=True)
    europese_voertuigcategorie_toevoeging = models.CharField(max_length=1, null=True, blank=True)
    taxi_indicator = models.BooleanField(null=True, blank=True)
    maximale_constructie_snelheid_bromsnorfiets = models.SmallIntegerField(null=True, blank=True)

    # fuel properties
    brandstoffen = models.JSONField(null=True, blank=True)
    extra_data = models.JSONField(null=True, blank=True)
    diesel = models.SmallIntegerField(null=True, blank=True)
    gasoline = models.SmallIntegerField(null=True, blank=True)
    electric = models.SmallIntegerField(null=True, blank=True)

    # TNO Versit klasse.
    # Zie ook: https://www.tno.nl/media/2451/lowres_tno_versit.pdf
    versit_klasse = models.CharField(null=True, blank=True, max_length=255)

    kenteken_hash = models.CharField(max_length=255, null=True, blank=True)
    massa_ledig_voertuig = models.IntegerField(null=True, blank=True)
    aantal_assen = models.SmallIntegerField(null=True, blank=True)
    aantal_staanplaatsen = models.SmallIntegerField(null=True, blank=True)
    aantal_wielen = models.SmallIntegerField(null=True, blank=True)
    aantal_zitplaatsen = models.SmallIntegerField(null=True, blank=True)
    handelsbenaming = models.CharField(max_length=255, null=True, blank=True)
    lengte = models.SmallIntegerField(null=True, blank=True)
    breedte = models.SmallIntegerField(null=True, blank=True)
    maximum_massa_trekken_ongeremd = models.IntegerField(null=True, blank=True)
    maximum_massa_trekken_geremd = models.IntegerField(null=True, blank=True)
    co2_uitstoot_gecombineerd = models.FloatField(null=True, blank=True)
    co2_uitstoot_gewogen = models.FloatField(null=True, blank=True)
    milieuklasse_eg_goedkeuring_zwaar = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        # create a unique index for (passage_id, volgnummer).
        # passage_at is included as it is required; it is used to partition
        unique_together = ('passage_id', 'volgnummer', 'passage_at')


class PassageHourAggregation(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    week = models.IntegerField()
    dow = models.IntegerField()  # day of week
    hour = models.IntegerField()
    camera_id = models.CharField(max_length=255)
    camera_naam = models.CharField(max_length=255)
    rijrichting = models.IntegerField()
    camera_kijkrichting = models.FloatField()
    kenteken_land = models.TextField()
    voertuig_soort = models.CharField(max_length=64, null=True, blank=True)
    europese_voertuigcategorie = models.CharField(max_length=2, null=True, blank=True)
    taxi_indicator = models.BooleanField(null=True, blank=True)
    diesel = models.IntegerField(null=True, blank=True)
    gasoline = models.IntegerField(null=True, blank=True)
    electric = models.IntegerField(null=True, blank=True)
    toegestane_maximum_massa_voertuig = models.TextField()
    count = models.IntegerField()


class Camera(models.Model):
    id = models.AutoField(primary_key=True)
    camera_id = models.CharField(max_length=255, null=True, blank=True)
    vma_linknr = models.CharField(max_length=255, null=True, blank=True)
    camera_naam = models.CharField(max_length=255, db_index=True)
    rijrichting = models.IntegerField(null=True, blank=True, db_index=True)
    rijrichting_correct = models.CharField(max_length=10, null=True, blank=True)
    camera_kijkrichting = models.FloatField(null=True, blank=True, db_index=True)

    order_kaart = models.IntegerField(null=True, blank=True)     # in sheet: volgorde
    order_naam = models.CharField(max_length=255, null=True, blank=True)      # in sheet: straatnaam
    cordon = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    richting = models.CharField(max_length=10, null=True, blank=True)
    location = models.PointField(srid=4326, null=True, blank=True)
    geom = models.CharField(max_length=255, null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)


class HourAggregationBase(models.Model):
    id = models.AutoField(primary_key=True)
    passage_at_timestamp = DateTimeUTCField()
    passage_at_date = models.DateField()
    passage_at_year = models.IntegerField()
    passage_at_month = models.IntegerField()
    passage_at_day = models.IntegerField()
    passage_at_week = models.IntegerField()
    passage_at_day_of_week = models.CharField(max_length=20)
    passage_at_hour = models.IntegerField(db_index=True)

    order_kaart = models.IntegerField(null=True, blank=True)  # in sheet: volgorde
    order_naam = models.CharField(max_length=255, null=True,
                                  blank=True)  # in sheet: straatnaam
    cordon = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    richting = models.CharField(max_length=3, null=True, blank=True)
    location = models.PointField(srid=4326, null=True, blank=True)
    geom = models.CharField(max_length=255, null=True, blank=True)
    azimuth = models.FloatField(null=True, blank=True)

    kenteken_land = models.TextField()
    intensiteit = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class HeavyTrafficHourAggregation(HourAggregationBase):
    voertuig_soort = models.CharField(max_length=64, null=True)
    inrichting = models.CharField(max_length=255, null=True)
    voertuig_klasse_toegestaan_gewicht = models.CharField(max_length=255, null=True, blank=True)


class IGORHourAggregation(HourAggregationBase):
    camera_id = models.CharField(max_length=255, null=True, blank=True)
    vma_linknr = models.CharField(max_length=255, null=True, blank=True)
    camera_naam = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    taxi_indicator = models.BooleanField(null=True)
    europese_voertuigcategorie = models.CharField(max_length=2, null=True)


class HeavyTrafficHourAggregationV2(models.Model):
    id = models.AutoField(primary_key=True)
    passage_at_date = models.DateField()
    passage_at_year = models.SmallIntegerField()
    passage_at_month = models.SmallIntegerField()
    passage_at_day = models.SmallIntegerField()
    passage_at_week = models.SmallIntegerField()
    passage_at_day_of_week = models.CharField(max_length=20)
    passage_at_hour = models.SmallIntegerField(db_index=True)

    camera_id = models.CharField(max_length=255, null=True, blank=True)
    camera_naam = models.CharField(max_length=255, null=True, blank=True)
    camera_kijkrichting = models.FloatField(null=True, blank=True)
    camera_locatie = models.PointField(srid=4326, null=True, blank=True)

    rijrichting = models.SmallIntegerField(null=True, blank=True)
    rijrichting_correct = models.CharField(max_length=10, null=True, blank=True)
    straat = models.CharField(max_length=255, null=True, blank=True)

    cordon = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    cordon_order_kaart = models.IntegerField(null=True, blank=True)
    cordon_order_naam = models.CharField(max_length=255, null=True, blank=True)

    massa_ledig_voertuig = models.CharField(max_length=255, null=True, blank=True)
    toegestane_maximum_massa_voertuig = models.CharField(max_length=255, null=True, blank=True)
    voertuig_soort = models.CharField(max_length=64, null=True, blank=True)
    inrichting = models.CharField(max_length=255, null=True, blank=True)
    europese_voertuigcategorie = models.CharField(max_length=2, null=True, blank=True)
    europese_voertuigcategorie_toevoeging = models.CharField(max_length=1, null=True,
                                                             blank=True)
    versit_klasse = models.CharField(null=True, blank=True, max_length=255)
    brandstoffen = models.JSONField(null=True, blank=True)
    co2_uitstoot_gecombineerd = models.FloatField(null=True, blank=True)
    co2_uitstoot_gewogen = models.FloatField(null=True, blank=True)
    milieuklasse_eg_goedkeuring_zwaar = models.CharField(max_length=255, null=True,
                                                         blank=True)
    count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'passage_heavytraffichouraggregation_v2'