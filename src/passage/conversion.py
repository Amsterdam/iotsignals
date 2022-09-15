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


RIJRICHTING_MAPPING = {'VAN': 1, 'NAAR': -1}
RIJRICHTING_MAPPING_INVERSE = {value: key for key, value in RIJRICHTING_MAPPING.items()}


def convert_to_v1(passage):
    """
    Convert the given payload from v2 to v1.

    Note that a converted message is never exactly the same as a version 1
    message: some fields from version 1 do not exist in version 2,
    and there will be a number of additional fields present that
    you wouldn't normally expect in a version 1 message.

    :param passage: The passage payload to downgrade (keys in snakecase)
    :return: Dictionary with the payload converted to 'version 1' format.
    """
    passage_v2 = deepcopy(passage)

    camera = passage_v2.pop('camera')
    camera_location = camera.pop('locatie', {})
    vehicle = passage_v2.pop('voertuig')
    number_plate = vehicle.pop('kenteken', {})
    betrouwbaarheid = number_plate.pop('betrouwbaarheid', {})
    fuels = {fuel['naam'] for fuel in vehicle.get('brandstoffen') or []}

    datum_eerste_toelating = date(vehicle.pop('jaar_eerste_toelating'), 1, 1) \
        if 'jaar_eerste_toelating' in vehicle else None

    rijrichting = passage_v2.pop('rijrichting', None)
    mapped_rijrichting = RIJRICHTING_MAPPING[rijrichting] if rijrichting else None
    if 'latitude' in camera_location and 'longitude' in camera_location:
        camera_locatie = {
            "type": "Point",
            "coordinates": [camera_location['latitude'], camera_location['longitude']]
        }
    else:
        camera_locatie = None

    passage_v1 = dict(
        # passage properties
        id=passage_v2.pop('id'),
        volgnummer=passage_v2.pop('volgnummer'),
        automatisch_verwerkbaar=passage_v2.pop('automatisch_verwerkbaar', None),
        indicatie_snelheid=vehicle.pop('indicatie_snelheid', None),
        passage_at=passage_v2.pop('timestamp'),
        version='passage-v2',
        kenteken_land_betrouwbaarheid=betrouwbaarheid.pop('landcode_betrouwbaarheid', None),
        kenteken_nummer_betrouwbaarheid=betrouwbaarheid.pop('kenteken_betrouwbaarheid', None),
        kenteken_karakters_betrouwbaarheid=betrouwbaarheid.pop('karakters_betrouwbaarheid', None),
        # vehicle properties
        kenteken_land=number_plate.pop('landcode', None),
        diesel=int('Diesel' in fuels) if fuels else None,
        gasoline=int('Benzine' in fuels) if fuels else None,
        electric=int('Elektriciteit' in fuels) if fuels else None,
        datum_eerste_toelating=datum_eerste_toelating,
        extra_data=None,
        maximale_constructie_snelheid_bromsnorfiets=vehicle.pop('maximale_constructiesnelheid_brom_snorfiets', None),
        brandstoffen=[
            dict(brandstof=fuel.pop('naam'), **fuel)
            for fuel in vehicle.pop('brandstoffen', [])
        ],
        datum_tenaamstelling=None,
        **vehicle,
        **number_plate,
        # camera properties
        camera_id=camera.pop('id'),
        camera_naam=camera.pop('naam', None),
        camera_kijkrichting=camera.pop('kijkrichting', None),
        camera_locatie=camera_locatie,
        rijstrook=passage_v2.pop('rijstrook', None),
        rijrichting=mapped_rijrichting,
        **camera,
    )

    return passage_v1
