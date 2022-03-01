# std
import datetime
import random
import string
# 3rd party
from functools import partial

import factory
from django.contrib.gis.geos import Point
from django.utils import timezone
from factory import fuzzy
from factory.django import DjangoModelFactory
# iotsignals
from passage.models import Passage


AMSTERDAM_LATITUDE = 52.03560, 52.48769
AMSTERDAM_LONGITUDE = 4.58565, 5.31360


def get_point_in_amsterdam():
    lat = fuzzy.FuzzyFloat(*AMSTERDAM_LATITUDE).fuzz()
    lon = fuzzy.FuzzyFloat(*AMSTERDAM_LONGITUDE).fuzz()
    return Point(float(lat), float(lon))


def get_point_in_amsterdam_as_json():
    return {
        "type": "Point",
        "coordinates": [
            fuzzy.FuzzyFloat(*AMSTERDAM_LONGITUDE).fuzz(),
            fuzzy.FuzzyFloat(*AMSTERDAM_LATITUDE).fuzz()
        ],
    }


def kenteken_karakter_betrouwbaarheid():
    return [
        dict(betrouwbaarheid=random.randint(1, 1000), positie=n)
        for n in range(6)
    ]


FUELS = ('Diesel', 'Elektriciteit', 'Benzine', 'LPG', 'CNG')


def get_brandstoffen_v1():
    return [
        dict(brandstof=random.choice(FUELS), volgnr=n)
        for n in range(random.randint(1, 5))
    ]


def get_brandstoffen_v2():
    return [
        dict(naam=random.choice(FUELS), volgnummer=n, emissieklasse=random.choice(string.digits))
        for n in range(random.randint(1, 5))
    ]


VOERTUIG_SOORTEN = 'Personenauto', 'Bromfiets', 'Bedrijfsauto', 'Bus'


class PassageFactory(DjangoModelFactory):
    class Meta:
        model = Passage

    id = factory.Faker('uuid4')
    version = "passage-v1"
    passage_at = factory.LazyFunction(timezone.now)
    straat = factory.Faker('name')
    rijstrook = fuzzy.FuzzyInteger(1, 10)
    rijrichting = fuzzy.FuzzyChoice((-1, 1))
    camera_id = factory.Faker('uuid4')
    camera_naam = factory.Faker('name')
    camera_kijkrichting = fuzzy.FuzzyInteger(0, 400)
    camera_locatie = factory.LazyFunction(get_point_in_amsterdam)
    kenteken_land = fuzzy.FuzzyText(length=2)
    kenteken_nummer_betrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kenteken_land_betrouwbaarheid = fuzzy.FuzzyInteger(1.0, 1000.0, 1)
    kenteken_karakters_betrouwbaarheid = factory.LazyFunction(kenteken_karakter_betrouwbaarheid)
    indicatie_snelheid = fuzzy.FuzzyFloat(0, 500)
    automatisch_verwerkbaar = factory.Faker('boolean', chance_of_getting_true=50)
    voertuig_soort = fuzzy.FuzzyChoice(VOERTUIG_SOORTEN)
    merk = factory.Faker('first_name')
    inrichting = factory.Faker('first_name')
    datum_eerste_toelating = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    datum_tenaamstelling = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    toegestane_maximum_massa_voertuig = fuzzy.FuzzyInteger(1, 32000)
    europese_voertuigcategorie = fuzzy.FuzzyText(length=2)
    europese_voertuigcategorie_toevoeging = fuzzy.FuzzyText(length=1)
    taxi_indicator = factory.Faker('boolean', chance_of_getting_true=50)
    maximale_constructie_snelheid_bromsnorfiets = fuzzy.FuzzyInteger(0, 500)
    brandstoffen = factory.LazyFunction(get_brandstoffen_v1)


class PayloadVersion1(factory.DictFactory):
    id = factory.Faker('uuid4')
    passageAt = factory.LazyFunction(timezone.now)
    version = "passage-v1"
    straat = factory.Faker('name')
    rijstrook = fuzzy.FuzzyInteger(1, 10)
    rijrichting = fuzzy.FuzzyChoice((-1, 1))
    cameraId = factory.Faker('uuid4')
    cameraNaam = factory.Faker('first_name')
    cameraKijkrichting = fuzzy.FuzzyFloat(0, 360)
    cameraLocatie = factory.LazyFunction(get_point_in_amsterdam_as_json)
    kentekenLand = fuzzy.FuzzyText(length=2)
    kentekenNummerBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kentekenLandBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kentekenKaraktersBetrouwbaarheid = factory.LazyFunction(kenteken_karakter_betrouwbaarheid)
    indicatieSnelheid = fuzzy.FuzzyFloat(0, 500)
    automatischVerwerkbaar = factory.Faker('boolean', chance_of_getting_true=50)
    voertuigSoort = fuzzy.FuzzyChoice(VOERTUIG_SOORTEN)
    merk = factory.Faker('first_name')
    inrichting = factory.Faker('first_name')
    datumEersteToelating = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    datumTenaamstelling = fuzzy.FuzzyDate(datetime.date(2008, 1, 1))
    toegestaneMaximumMassaVoertuig = fuzzy.FuzzyInteger(1, 32000)
    europeseVoertuigcategorie = fuzzy.FuzzyText(length=2)
    europeseVoertuigcategorieToevoeging = fuzzy.FuzzyText(length=1)
    taxiIndicator = factory.Faker('boolean', chance_of_getting_true=50)
    maximaleConstructieSnelheidBromsnorfiets = fuzzy.FuzzyInteger(0, 500)
    brandstoffen = factory.LazyFunction(get_brandstoffen_v1)
    extraData = {}
    diesel = factory.LazyAttribute(lambda self: int('Diesel' in {x['brandstof'] for x in self.brandstoffen}))
    gasoline = factory.LazyAttribute(lambda self: int('Benzine' in {x['brandstof'] for x in self.brandstoffen}))
    electric = factory.LazyAttribute(lambda self: int('Elektriciteit' in {x['brandstof'] for x in self.brandstoffen}))
    versitKlasse = fuzzy.FuzzyText()


class Kenteken(factory.DictFactory):
    kentekenHash = fuzzy.FuzzyText(chars=string.hexdigits, length=40)
    landcode = fuzzy.FuzzyText(chars=string.ascii_uppercase, length=2)


class Voertuig(factory.DictFactory):
    kenteken = factory.SubFactory(Kenteken)
    jaarEersteToelating = fuzzy.FuzzyInteger(1990, 2020)
    toegestaneMaximumMassaVoertuig = fuzzy.FuzzyInteger(0, 1000)
    europeseVoertuigcategorie = fuzzy.FuzzyText(length=2)
    europeseVoertuigcategorieToevoeging = fuzzy.FuzzyChoice(string.ascii_uppercase)
    taxiIndicator = factory.Faker('boolean', chance_of_getting_true=50)
    maximaleConstructiesnelheidBromSnorfiets = fuzzy.FuzzyInteger(0, 500)
    versitKlasse = fuzzy.FuzzyText()
    massaLedigVoertuig = fuzzy.FuzzyInteger(0, 500)
    aantalAssen = fuzzy.FuzzyInteger(0, 10)
    aantalStaanplaatsen = fuzzy.FuzzyInteger(0, 100)
    aantalWielen = fuzzy.FuzzyInteger(0, 12)
    aantalZitplaatsen = fuzzy.FuzzyInteger(0, 100)
    handelsbenaming = factory.Faker('first_name')
    lengte = fuzzy.FuzzyInteger(0, 500)
    breedte = fuzzy.FuzzyInteger(0, 500)
    maximumMassaTrekkenOngeremd = fuzzy.FuzzyInteger(0, 5000)
    maximumMassaTrekkenGeremd = fuzzy.FuzzyInteger(0, 5000)
    voertuigSoort = fuzzy.FuzzyChoice(VOERTUIG_SOORTEN)
    merk = factory.Faker('first_name')
    inrichting = factory.Faker('first_name')
    co2UitstootGecombineerd = fuzzy.FuzzyFloat(0, 100)
    co2UitstootGewogen = fuzzy.FuzzyFloat(0, 100)
    milieuklasseEgGoedkeuringZwaar = fuzzy.FuzzyText()
    brandstoffen = factory.LazyFunction(get_brandstoffen_v2)


class Betrouwbaarheid(factory.DictFactory):
    landcodeBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kentekenBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    karaktersBetrouwbaarheid = factory.LazyFunction(kenteken_karakter_betrouwbaarheid)


class Locatie(factory.DictFactory):
    longitude = fuzzy.FuzzyFloat(*AMSTERDAM_LONGITUDE)
    latitude = fuzzy.FuzzyFloat(*AMSTERDAM_LATITUDE)


class Camera(factory.DictFactory):
    id = factory.Faker('uuid4')
    kijkrichting = fuzzy.FuzzyFloat(0, 360)
    locatie = factory.SubFactory(Locatie)
    naam = factory.Faker('name')
    straat = factory.Faker('name')
    rijstrook = fuzzy.FuzzyInteger(1, 10)
    rijrichting = fuzzy.FuzzyChoice(("VAN", "NAAR"))


class PayloadVersion2(factory.DictFactory):
    id = factory.Faker('uuid4')
    version = "passage-v2"
    timestamp = factory.LazyFunction(timezone.now)
    automatischVerwerkbaar = factory.Faker('boolean', chance_of_getting_true=50)
    indicatieSnelheid = fuzzy.FuzzyFloat(0, 150)
    camera = factory.SubFactory(Camera)
    voertuig = factory.SubFactory(Voertuig)
    betrouwbaarheid = factory.SubFactory(Betrouwbaarheid)
