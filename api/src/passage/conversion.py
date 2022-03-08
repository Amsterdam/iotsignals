# std
from copy import deepcopy
from datetime import date

from django.contrib.gis.geos import GEOSGeometry

NEW_FIELDS = [
    'kenteken_hash',
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


def downgrade(passage):
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
    number_plate = vehicle.pop('kenteken')
    betrouwbaarheid = number_plate.pop('betrouwbaarheid')
    fuels = {fuel['naam'] for fuel in vehicle.get('brandstoffen') or []}

    passage_v1 = dict(
        # passage properties
        id=passage_v2.pop('id'),
        volgnummer=passage_v2.pop('volgnummer'),
        automatisch_verwerkbaar=passage_v2.pop('automatisch_verwerkbaar'),
        indicatie_snelheid=vehicle.pop('indicatie_snelheid'),
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
        rijstrook=passage_v2.pop('rijstrook'),
        rijrichting=RIJRICHTING_MAPPING[passage_v2.pop('rijrichting')],
        **camera,
    )

    return passage_v1