# std
import string
from functools import partial
from typing import Literal
# 3rd party
import pytz
from django.contrib.gis.geos import Point
from hypothesis import strategies as st

st_optional = partial(st.one_of, st.none())
st_uuids = st.uuids().map(str)
st_small_integers = st.integers(min_value=1, max_value=32767)
st_ams_longitudes = st.floats(4.58565, 5.31360, allow_nan=False, allow_infinity=False)
st_ams_latitudes = st.floats(52.03560, 52.48769, allow_nan=False, allow_infinity=False)
st_floats = st.floats(allow_nan=False, allow_infinity=False, min_value=0)
st_timezones = st.just(pytz.timezone('Europe/Amsterdam'))
st_timestamps = st.datetimes(timezones=st_timezones).map(lambda dt: dt.isoformat())
st_dates = st.dates().map(str)
st_years = st.dates().map(lambda date: date.year)
st_text = partial(st.text, alphabet=string.ascii_letters, min_size=1, max_size=255)
st_landcodes = st.text(string.ascii_uppercase, min_size=2, max_size=2)
st_hashes = st.text(string.hexdigits, min_size=40, max_size=40)
st_fuels = st.sampled_from(('Diesel', 'Elektriciteit', 'Benzine', 'LPG', 'CNG'))
st_accuracy_integers = st.integers(min_value=0, max_value=1000)
st_number_plate_accuracy_lists = st.lists(
    st.fixed_dictionaries({
        'betrouwbaarheid': st_accuracy_integers,
        'posities': st_small_integers,
    }),
    min_size=1,
)
st_nullable_booleans = st_optional(st.booleans())


@st.composite
def st_passages_v1(draw):
    """
    Strategy for generating passage payload (version 2).

    :param draw: Callable for drawing examples from other strategies.

    :return: Dictionary containing passage payload.
    """
    fuels = draw(st.lists(st.fixed_dictionaries({
        "volgnr": st_small_integers,
        "brandstof": st_fuels,
        "euroklasse": st_text(),
    }), unique_by=lambda x: x["brandstof"]))

    fuel_names = {fuel["brandstof"] for fuel in fuels}

    return draw(st.fixed_dictionaries({
        "id": st_uuids,
        "passageAt": st_timestamps,
        "version": st.just("passage-v1"),
        "straat": st_text(),
        "rijrichting": st.sampled_from((-1, 1)),
        "rijstrook": st.sampled_from(range(10)),
        "cameraId": st_uuids,
        "cameraNaam": st_text(),
        "cameraKijkrichting": st_floats,
        "cameraLocatie": st.builds(Point, st_ams_latitudes, st_ams_longitudes).map(lambda p: p.hex),
        "kentekenLand": st_landcodes,
        "kentekenNummerBetrouwbaarheid": st_accuracy_integers,
        "kentekenLandBetrouwbaarheid": st_accuracy_integers,
        "kentekenKaraktersBetrouwbaarheid": st_number_plate_accuracy_lists,
        "indicatieSnelheid": st_floats,
        "automatischVerwerkbaar": st.booleans(),
        "voertuigSoort": st_text(max_size=25),
        "merk": st_text(),
        "inrichting": st_text(),
        "datumEersteToelating": st_dates,
        "datumTenaamstelling": st_dates,
        "toegestaneMaximumMassaVoertuig": st_small_integers,
        "europeseVoertuigcategorie": st_text(max_size=2),
        "europeseVoertuigcategorieToevoeging": st.sampled_from(string.ascii_uppercase),
        "taxiIndicator": st.booleans(),
        "maximaleConstructieSnelheidBromsnorfiets": st_floats,
        "brandstoffen": st.just(fuels),
        "extraData": st.none(),
        "diesel": st.just(int('Diesel' in fuel_names)),
        "gasoline": st.just(int('Benzine' in fuel_names)),
        "electric": st.just(int('Elektriciteit' in fuel_names)),
        "versitKlasse": st_text(),
    }))


@st.composite
def st_passages_v2(draw):
    """
    Strategy for generating passage payload (version 2).

    :param draw: Callable for drawing examples from other strategies.

    :return: Dictionary containing passage payload.
    """
    return draw(st.fixed_dictionaries({
        "id": st_uuids,
        "version": st.just("passage-v2"),
        "timestamp": st_timestamps,
        "camera": st.fixed_dictionaries({
            "id": st_uuids,
            "kijkrichting": st_floats,
            "locatie": st.fixed_dictionaries({
                "longitude": st_ams_longitudes,
                "latitude": st_ams_latitudes,
            }),
            "naam": st_text(),
            "rijrichting": st.sampled_from(("VAN", "NAAR")),
            "rijstrook": st.sampled_from(range(10)),
            "straat": st_text(),
        }),
        "voertuig": st.fixed_dictionaries({
            "kenteken": st.fixed_dictionaries({
                "kentekenHash": st_hashes,
                "landcode": st_landcodes,
            }),
            "jaarEersteToelating": st_years,
            "toegestaneMaximumMassaVoertuig": st_small_integers,
            "europeseVoertuigcategorie": st_text(max_size=2),
            "europeseVoertuigcategorieToevoeging": st.sampled_from(string.ascii_uppercase),
            "taxiIndicator": st.booleans(),
            "maximaleConstructiesnelheidBromSnorfiets": st_small_integers,
            "versitKlasse": st_text(),
            "vervaldatumApk": st_dates,
            "wamVerzekerd": st.booleans(),
            "massaLedigVoertuig": st_small_integers,
            "aantalAssen": st_small_integers,
            "aantalStaanplaatsen": st_small_integers,
            "aantalWielen": st_small_integers,
            "aantalZitplaatsen": st_small_integers,
            "handelsbenaming": st_text(),
            "lengte": st_small_integers,
            "breedte": st_small_integers,
            "maximumMassaTrekkenOngeremd": st_small_integers,
            "maximumMassaTrekkenGeremd": st_small_integers,
            "voertuigSoort": st_text(max_size=25),
            "inrichting": st_text(),
            "merk": st_text(),
            "brandstoffen": st.lists(st.fixed_dictionaries({
                "naam": st_fuels,
                "volgnummer": st_small_integers,
                "emissieklasse": st.sampled_from(string.digits),
            }), min_size=1),
            "co2UitstootGecombineerd": st_floats,
            "co2UitstootGewogen": st_floats,
            "milieuklasseEgGoedkeuringZwaar": st_text(),
        }),
        "indicatieSnelheid": st_floats,
        "automatischVerwerkbaar": st.booleans(),
        "betrouwbaarheid": st.fixed_dictionaries({
            "landcodeBetrouwbaarheid": st_accuracy_integers,
            "kentekenBetrouwbaarheid": st_accuracy_integers,
            "karaktersBetrouwbaarheid": st_number_plate_accuracy_lists,
        }),
    }))


@st.composite
def st_passages(draw, version: Literal[1, 2] = 1):
    """
    Strategy for generating passage payload.

    :param draw: Callable for drawing examples from other strategies.
    :param version: The version of the vehicle data to generate.

    :return: Dictionary containing passage payload.
    """
    return draw(st_passages_v1() if version == 1 else st_passages_v2())
