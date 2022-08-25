# std
import datetime
import random
import string

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
            fuzzy.FuzzyFloat(*AMSTERDAM_LATITUDE).fuzz(),
        ],
    }


def kenteken_karakter_betrouwbaarheid():
    return [dict(betrouwbaarheid=random.randint(1, 1000), positie=n) for n in range(6)]


FUELS = ('Diesel', 'Elektriciteit', 'Benzine', 'LPG', 'CNG')


def get_brandstoffen_v1():
    return [
        dict(brandstof=random.choice(FUELS), volgnr=n)
        for n in range(random.randint(1, 5))
    ]


def get_brandstoffen_v2():
    return [
        dict(
            naam=random.choice(FUELS),
            volgnummer=n,
            emissieklasse=random.choice(string.digits),
            co2UitstootGecombineerd=random.randint(0, 100),
            co2UitstootGewogen=random.randint(0, 100),
            milieuklasseEgGoedkeuringZwaar=random.choice(string.ascii_letters),
        )
        for n in range(random.randint(1, 5))
    ]


VOERTUIG_SOORTEN = 'Personenauto', 'Bromfiets', 'Bedrijfsauto', 'Bus'


class PassageFactory(DjangoModelFactory):
    class Meta:
        model = Passage

    passage_id = factory.Faker('uuid4')
    version = "passage-v1"
    passage_at = factory.LazyFunction(timezone.now)
    straat = factory.Faker('name')
    rijstrook = fuzzy.FuzzyInteger(1, 10)
    rijrichting = fuzzy.FuzzyChoice((-1, 1))
    camera_id = fuzzy.FuzzyChoice(["3a6b0a00-7e93-48b9-bc06-9e0871a20d18","a8f116f1-4538-433f-9f18-c8eee204b171","0b3925e9-7fb6-43ed-8989-492773e1cedf","b28eae12-4ef3-4623-be0c-8916f453889d","bcb0f06f-d7a1-48d5-a67d-e333a7e32cf5","bcb0f06f-d7a1-48d5-a67d-e333a7e32cf5","06080159-c30d-4eba-b2f8-f20c1dc9d2d0","06080159-c30d-4eba-b2f8-f20c1dc9d2d0","0fbb922e-74b2-43df-9d0f-647e50d27dd0","0fbb922e-74b2-43df-9d0f-647e50d27dd0","b3b97554-fa72-474d-b1a0-052ea678ca0d","b3b97554-fa72-474d-b1a0-052ea678ca0d","c0dd2b1d-0d7d-49b1-8975-27452e8a9407","6699ed92-2fc6-41fa-b131-413f7f9e1bae","a64de2d1-cb57-4217-8aa6-3e121937a0fd","a64de2d1-cb57-4217-8aa6-3e121937a0fd","530f984b-15a6-4fe6-bf5b-afcf9f9bd2cb","530f984b-15a6-4fe6-bf5b-afcf9f9bd2cb","3747d4e9-ce7e-4dca-be20-853f80d9fd29","3747d4e9-ce7e-4dca-be20-853f80d9fd29","3e451ab3-f90a-4a3b-bf81-f3bd1f6c6c78","3e451ab3-f90a-4a3b-bf81-f3bd1f6c6c78","20e5b23c-010f-431c-8ed6-997dfe5884b8","20e5b23c-010f-431c-8ed6-997dfe5884b8","6175c60d-94fc-4f8f-9feb-0da00a4e9aac","6175c60d-94fc-4f8f-9feb-0da00a4e9aac","b225361e-4d07-4461-954b-003f143ef5d1","1706b46c-fed2-4fce-8e00-182cddf05071","4b6465f3-d8d0-411c-8c54-b7b5e8db2eb9","4b6465f3-d8d0-411c-8c54-b7b5e8db2eb9","3fa4095f-afd7-4ab2-9328-a302c8c5f125","3fa4095f-afd7-4ab2-9328-a302c8c5f125","0cee6810-f40e-4ada-b2a5-b962a74d7172","0cee6810-f40e-4ada-b2a5-b962a74d7172","e744c349-822f-472b-9789-32fe5476836b","031daf18-2d8d-43f3-aa9f-c49a9606653a","e744c349-822f-472b-9789-32fe5476836b","4a47252f-abde-4a91-a759-1de60a6e648b","842e11c7-231d-4578-80ca-71fc0aaf6695","e6775b00-ec8f-4300-ac63-1d210edba3b9","e6775b00-ec8f-4300-ac63-1d210edba3b9","0f40719d-2d99-4ffa-bbd5-1d9239dfa5d2","0f40719d-2d99-4ffa-bbd5-1d9239dfa5d2","f7f10912-f184-4860-a13d-e3bd5ecd899e","f7f10912-f184-4860-a13d-e3bd5ecd899e","64772b0d-c7ce-4a35-96f1-2d4710e8b0c3","64772b0d-c7ce-4a35-96f1-2d4710e8b0c3","e6341cf4-f076-4d05-8821-13acf8a2030f","e6341cf4-f076-4d05-8821-13acf8a2030f","c9173178-30ee-4ee2-b3dc-daf838787d2d","c9173178-30ee-4ee2-b3dc-daf838787d2d","23f688a6-f3ee-46ea-9e9d-aa92e2efbce8","36e06b7d-202e-45dd-be57-26e346646c08","c20148e6-4ba1-46e8-a746-c1f96df4ced0","0236d4da-d982-487c-b6a6-bef004753015","1ebd8bb1-3282-4391-b47b-76d17a6a7080","110b165f-eb62-4e7d-9511-60498b536836","bd17e269-993f-4747-b5c0-a2a236d9a1f4","cc4c5e29-c618-44d5-8f90-5438157c21e4","0aa442fc-e86a-4c8e-9605-f91f632af4fb","2be29bd3-8082-4a86-9ea8-f736c3f63087","f7150a8e-d8ac-45e4-8543-d7d4553b5d01","2b6b1ad6-8b81-4cc7-96fa-0d8eb59e7481","69e5d5ff-7f08-4d21-8503-eb2e610b7915","69e5d5ff-7f08-4d21-8503-eb2e610b7915","ca4cc6c7-27e2-41c7-95fc-b3cce9964fa0","ca4cc6c7-27e2-41c7-95fc-b3cce9964fa0","2aafe747-2467-47c9-a8bf-18067d80bb3a","ea47aca6-a1e4-458c-94ca-fb4b96025e29","322aac3d-62c2-495b-afee-7deded30f0e7","9f78bc50-9b51-4602-a4ed-40c6a8248b52","a3437d23-926d-4fa9-97a2-5395e0ca3df1","44cbb3a2-e239-4306-87f2-8ea05277a6dd","bd068a46-b1b5-4c2b-9386-b8fdcb21b56d","abbccbb8-2ffc-4c22-b3cf-20acbe663b42","f92759ff-6258-4023-8baa-99c1332625c2","05a5d458-f2cd-4221-b1c8-c575ff4fbbeb","0204d364-7483-45be-8ab6-f909a61bf280","e680a640-252a-4ebf-a666-860be5781726","b9ab6227-718b-499f-a359-338d1edf5a8e","2f14de31-699e-4c0f-af77-1b3edf72c1e0","319477d0-a3fe-4a80-a4b1-ae588782d700","319477d0-a3fe-4a80-a4b1-ae588782d700","e75665ff-93af-41ac-b124-e601d8e2c502","e75665ff-93af-41ac-b124-e601d8e2c502","918228a7-810a-494d-a567-bc821b2b5788","918228a7-810a-494d-a567-bc821b2b5788","d1291369-1699-44b8-aadb-0cb8e68387ad","d1291369-1699-44b8-aadb-0cb8e68387ad","48316d09-7a88-43cf-90d9-f08a49dc02e9","af55bacc-7a3d-4e4e-b694-a85caa760547","03b05c47-7966-4330-b066-8ffdbea876cd","03b05c47-7966-4330-b066-8ffdbea876cd","83a20e37-5738-42c4-b1b8-69c4178821db","83a20e37-5738-42c4-b1b8-69c4178821db","fb86a172-b183-4a57-97d7-815104234352","fb86a172-b183-4a57-97d7-815104234352","0783b43b-bad4-4c24-b456-4bac1043be1a","76ace8c0-6310-476e-9b44-4a3b1314fdfe","29a732f6-e49d-46de-a013-400883b5c34f","29a732f6-e49d-46de-a013-400883b5c34f","c2359382-2341-4eb3-8d15-691f7da5427d","c2359382-2341-4eb3-8d15-691f7da5427d","1c7622fd-57ae-4394-bd8e-411d5640dabb","1c7622fd-57ae-4394-bd8e-411d5640dabb","c503bd56-30df-4df6-b5f6-3fd63a1b5fb3","c503bd56-30df-4df6-b5f6-3fd63a1b5fb3","59808ef9-9ab2-4398-8e04-cc74b5f9c4f7","59808ef9-9ab2-4398-8e04-cc74b5f9c4f7","cbc446fe-e1ad-49de-9087-8da935aaff03","5ab2bf71-eb8a-4286-9c19-878d7dc7cf01","8ed59c08-5425-48b6-905a-2dfc82018b3c","849ed44e-6c53-47e3-99ee-9fca75f7d8a0","3c180f2a-b175-4dc5-8053-e7c2b9078fbd","28ddc3d5-d6de-47e7-b313-cd4ec86d63b4","28ddc3d5-d6de-47e7-b313-cd4ec86d63b4","faff71b9-a8b5-45c7-afb1-ce8025bd8b7d","faff71b9-a8b5-45c7-afb1-ce8025bd8b7d","f7be41dc-f19e-4cf6-affa-7e3576008609","f7be41dc-f19e-4cf6-affa-7e3576008609","031daf18-2d8d-43f3-aa9f-c49a9606653a","cbc11a20-4c5e-475b-a1d4-2662d5526d20","cbc11a20-4c5e-475b-a1d4-2662d5526d20","1896fdba-4041-44db-897b-deb84b71d270","f9da447a-3b86-47ca-b92b-1f9c054e91be","ac78c914-0d5f-4e93-9b63-810cc3f94e10","755ac34b-4478-4814-b0c0-1b3beb8daf12","755ac34b-4478-4814-b0c0-1b3beb8daf12","12dfdb52-f3fe-4a3e-9d73-343a1d3b04dc","12dfdb52-f3fe-4a3e-9d73-343a1d3b04dc","c0d0638a-8084-49b0-8b99-b317086f488c","c0d0638a-8084-49b0-8b99-b317086f488c","b852f8bc-1a43-47ff-bd61-c31e79c1bf2b","40fa7815-e469-42ec-80ca-4271b59978b5","40fa7815-e469-42ec-80ca-4271b59978b5","5afaa224-9e08-48d0-bb11-8df903125a71","5afaa224-9e08-48d0-bb11-8df903125a71","b27bb60c-41a9-42b4-bea0-6616c4950183","b27bb60c-41a9-42b4-bea0-6616c4950183","93602b65-a751-46d8-afbe-318ecf7c0873","b916e29e-4713-4c44-ae94-5e9df9ef3695","b916e29e-4713-4c44-ae94-5e9df9ef3695","24e8603c-2210-433e-be0b-7dd218640907","24e8603c-2210-433e-be0b-7dd218640907","c17f7656-092c-451c-9f37-889016bb7470","c17f7656-092c-451c-9f37-889016bb7470","c1971cf7-7bb1-435a-9acf-1d70305d10e1","c1971cf7-7bb1-435a-9acf-1d70305d10e1","b5b94a27-e5e4-44bf-9cb8-3c5ae52bdca6","b5b94a27-e5e4-44bf-9cb8-3c5ae52bdca6","28729ee5-35f2-4095-9cfe-a19cd037d1a3","28729ee5-35f2-4095-9cfe-a19cd037d1a3","0893b31e-eb71-4b2e-814a-ae2e1d8d5b64","0893b31e-eb71-4b2e-814a-ae2e1d8d5b64","8b2bef41-44b9-4728-af08-10aae7bf49aa","8b2bef41-44b9-4728-af08-10aae7bf49aa","3f77f1ca-54e8-424e-8915-91e9f0fed43e","75cc79ed-6fa2-475c-852f-1c72c53c4fa7","6456b6e7-8e69-4904-ad26-cec019d9d911","6456b6e7-8e69-4904-ad26-cec019d9d911","a7f6ab31-c835-488c-be76-1aa837a3c20b","a7f6ab31-c835-488c-be76-1aa837a3c20b","e9952c5e-564f-440f-ac71-1422b3a780ee","e9952c5e-564f-440f-ac71-1422b3a780ee","f2fa174b-e018-42af-aae5-dad79be71f95","f2fa174b-e018-42af-aae5-dad79be71f95","66e2cb13-78cc-4836-aea5-e16b7cd19053","0334a4f0-bb22-464f-a91e-15a1bed39d1b","88db3abd-6507-45e0-85a4-efb2f8a47b84","97bf2b9f-0844-45ff-b1dc-f92eca255ba6","e2b106c3-205e-4afa-a6cf-d16953d84f77","647ecf0f-ec93-4e10-b5ff-47f465cd82cf","bb460ce8-a208-4875-bd8e-84240d4d3e8f","e177b0bf-ff30-4752-8e9e-f5fd089ee821","2a3da8a7-e51d-4a6b-bfdf-393cea0d05d5","5ade1aef-fc3a-4c7d-95f8-64ca01ff665f","97c9941e-4b69-45ed-b31b-70d8efd3adee","a7678f4c-c78e-41e3-8db4-1230e0e507df","cd1d2522-5bd7-48b6-b13b-cee5cf46c12f","51c1d3e5-ce11-494c-ba79-f0a039245062","f9ae0922-cd61-4057-a279-ae2f9f425ffd","75c83a4c-8a44-4505-8c91-e85ad4b027e4","75c83a4c-8a44-4505-8c91-e85ad4b027e4","aa330dea-35a5-458c-ae61-6ba62a646fbf","aa330dea-35a5-458c-ae61-6ba62a646fbf","e49c384f-3dc1-4630-b2ab-5a4b3eb5b482","e49c384f-3dc1-4630-b2ab-5a4b3eb5b482","08af3e31-2e2e-443b-b0b5-817cc8350cf4","08af3e31-2e2e-443b-b0b5-817cc8350cf4","4e8f6800-c8af-4eae-99a0-360d6dce2136","8c7bde56-10ee-4eda-b529-19916eec56fc","b4e7d006-a449-4ad2-83b8-78bbd3cf0ad0","bedc3646-6fda-494a-8294-09d90a34c0a4","bef225b3-9af0-4ca9-b360-5e2256b32a0e","bef225b3-9af0-4ca9-b360-5e2256b32a0e","6ece2b50-dbb6-419a-b8f9-f2f3e2490227","6ece2b50-dbb6-419a-b8f9-f2f3e2490227","e284e291-3106-48e6-9ca6-7fad0495ac1c","e284e291-3106-48e6-9ca6-7fad0495ac1c","dfc7ac53-f10a-4084-a084-9b4f579b7066"])
    camera_naam = factory.Faker('name')
    camera_kijkrichting = fuzzy.FuzzyInteger(0, 400)
    camera_locatie = factory.LazyFunction(get_point_in_amsterdam)
    kenteken_land = fuzzy.FuzzyText(length=2)
    kenteken_nummer_betrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kenteken_land_betrouwbaarheid = fuzzy.FuzzyInteger(1.0, 1000.0, 1)
    kenteken_karakters_betrouwbaarheid = factory.LazyFunction(
        kenteken_karakter_betrouwbaarheid
    )
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
    kentekenKaraktersBetrouwbaarheid = factory.LazyFunction(
        kenteken_karakter_betrouwbaarheid
    )
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
    diesel = factory.LazyAttribute(
        lambda self: int('Diesel' in {x['brandstof'] for x in self.brandstoffen})
    )
    gasoline = factory.LazyAttribute(
        lambda self: int('Benzine' in {x['brandstof'] for x in self.brandstoffen})
    )
    electric = factory.LazyAttribute(
        lambda self: int('Elektriciteit' in {x['brandstof'] for x in self.brandstoffen})
    )
    versitKlasse = fuzzy.FuzzyText()


class Betrouwbaarheid(factory.DictFactory):
    landcodeBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    kentekenBetrouwbaarheid = fuzzy.FuzzyInteger(1, 1000)
    karaktersBetrouwbaarheid = factory.LazyFunction(kenteken_karakter_betrouwbaarheid)


class Kenteken(factory.DictFactory):
    kentekenHash = fuzzy.FuzzyText(chars=string.hexdigits, length=40)
    landcode = fuzzy.FuzzyText(chars=string.ascii_uppercase, length=2)
    betrouwbaarheid = factory.SubFactory(Betrouwbaarheid)


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
    brandstoffen = factory.LazyFunction(get_brandstoffen_v2)
    indicatieSnelheid = fuzzy.FuzzyFloat(0, 150)


class Locatie(factory.DictFactory):
    longitude = fuzzy.FuzzyFloat(*AMSTERDAM_LONGITUDE)
    latitude = fuzzy.FuzzyFloat(*AMSTERDAM_LATITUDE)


class Camera(factory.DictFactory):
    id = factory.Faker('uuid4')
    kijkrichting = fuzzy.FuzzyFloat(0, 360)
    locatie = factory.SubFactory(Locatie)
    naam = factory.Faker('name')
    straat = factory.Faker('name')


class PayloadVersion2(factory.DictFactory):
    id = factory.Faker('uuid4')
    version = "passage-v2"
    volgnummer = fuzzy.FuzzyInteger(0, 10)
    timestamp = factory.LazyFunction(timezone.now)
    automatischVerwerkbaar = factory.Faker('boolean', chance_of_getting_true=50)
    camera = factory.SubFactory(Camera)
    voertuig = factory.SubFactory(Voertuig)
    rijstrook = fuzzy.FuzzyInteger(1, 10)
    rijrichting = fuzzy.FuzzyChoice(("VAN", "NAAR"))
