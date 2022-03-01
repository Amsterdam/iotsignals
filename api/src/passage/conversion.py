# std
from copy import deepcopy
from datetime import date

from django.contrib.gis.geos import GEOSGeometry

NEW_FIELDS = [
    'kenteken_hash',
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
    passage_v2 = deepcopy(passage)

    camera = passage_v2.pop('camera')
    camera_location = camera.pop('locatie')
    vehicle = passage_v2.pop('voertuig')
    betrouwbaarheid = passage_v2.pop('betrouwbaarheid')
    number_plate = vehicle.pop('kenteken')
    fuels = {fuel['naam'] for fuel in vehicle.get('brandstoffen') or []}

    if drop_new_fields:
        for field in NEW_FIELDS:
            if field in vehicle:
                del vehicle[field]

        del number_plate['kenteken_hash']

    passage_v1 = dict(
        # passage properties
        id=passage_v2.pop('id'),
        automatisch_verwerkbaar=passage_v2.pop('automatisch_verwerkbaar'),
        indicatie_snelheid=passage_v2.pop('indicatie_snelheid'),
        passage_at=passage_v2.pop('timestamp'),
        version='passage-v1',
        kenteken_land_betrouwbaarheid=betrouwbaarheid.pop('landcode_betrouwbaarheid'),
        kenteken_nummer_betrouwbaarheid=betrouwbaarheid.pop('kenteken_betrouwbaarheid'),
        kenteken_karakters_betrouwbaarheid=betrouwbaarheid.pop('karakters_betrouwbaarheid'),
        # vehicle properties
        kenteken_land=number_plate.pop('landcode'),
        diesel=int('Diesel' in fuels),
        gasoline=int('Benzine' in fuels),
        electric=int('Elektriciteit' in fuels),
        datum_eerste_toelating=date(vehicle.pop('jaar_eerste_toelating'), 1, 1),
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
        camera_locatie={
            "type": "Point",
            "coordinates": [camera_location['latitude'], camera_location['longitude']]
        },
        rijrichting=RIJRICHTING_MAPPING[camera.pop('rijrichting')],
        **camera,
    )

    return passage_v1