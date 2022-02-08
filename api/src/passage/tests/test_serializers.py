from datetime import date
from unittest import mock

import pytest
from django.utils import timezone

from passage.serializers import PassageDetailSerializer


class TestPassageDetailSerializer:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (date(2021, 1, 1), date(2021, 1, 1)),
            (date(2020, 12, 31), date(2020, 1, 1)),
            (date(2019, 8, 17), date(2019, 1, 1)),
        ],
    )
    def test_validate_datum_eerste_toelating(self, value, expected):
        serializer = PassageDetailSerializer()
        assert serializer.validate_datum_eerste_toelating(value) == expected

    @pytest.mark.parametrize("value", [None, 0, 1, "01-01-2021", timezone.now()])
    def test_validate_datum_tenaamstelling(self, value):
        serializer = PassageDetailSerializer()
        assert serializer.validate_datum_tenaamstelling(value) is None

    @pytest.mark.parametrize(
        "value,expected",
        [
            (None, None),
            (0, 1500),
            (1500, 1500),
            (3500, 1500),
            (3501, 3501),
            (9999, 9999),
        ],
    )
    def validate_toegestane_maximum_massa_voertuig(self, value, expected):
        serializer = PassageDetailSerializer()
        assert serializer.validate_toegestane_maximum_massa_voertuig(value) == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (None, None),
            (0, 0),
            (9, 0),
            (10, 10),
            (19, 10),
            (20, 20),
            (9999, 9990),
        ],
    )
    def test_validate_co2_uitstoot_gecombineerd(self, value, expected):
        serializer = PassageDetailSerializer()
        assert serializer.validate_co2_uitstoot_gecombineerd(value) == expected

    @mock.patch("passage.serializers.PassageDetailSerializer._validate_inrichting")
    @mock.patch(
        "passage.serializers.PassageDetailSerializer._validate_voertuigcategorie"
    )
    def test_validate(
        self, mocked_validate_inrichting, mocked_validate_voertuigcategorie
    ):
        data = {"foo": "bar"}
        serializer = PassageDetailSerializer()
        serializer.validate(data)

        mocked_validate_inrichting.assert_any_call(data)
        mocked_validate_voertuigcategorie.assert_any_call(data)

    @pytest.mark.parametrize(
        "voertuig_soort,inrichting,expected",
        [
            (None, "foobar", "foobar"),
            ("personenauto", "foobar", "Personenauto"),
            ("PERSONENAUTO", "foobar", "Personenauto"),
            ("foo", "foobar", "foobar"),
        ],
    )
    def test_validate_inrichting(self, voertuig_soort, inrichting, expected):
        data = {'inrichting': inrichting}
        if voertuig_soort is not None:
            data['voertuig_soort'] = voertuig_soort

        serializer = PassageDetailSerializer()
        serializer._validate_inrichting(data)

        assert data['inrichting'] == expected

    @pytest.mark.parametrize(
        "max_massa,categorie_toevoeging,merk,expected_toevoeging,expected_merk",
        [
            (None, 'foo', 'bar', 'foo', 'bar'),
            (9999, 'foo', 'bar', 'foo', 'bar'),
            (3501, 'foo', 'bar', 'foo', 'bar'),
            (3500, 'foo', 'bar', None, None),
            (0, 'foo', 'bar', None, None),
        ],
    )
    def test_validate_voertuigcategorie(
        self, max_massa, categorie_toevoeging, merk, expected_toevoeging, expected_merk
    ):
        data = {
            'europese_voertuigcategorie_toevoeging': categorie_toevoeging,
            'merk': merk,
        }
        if max_massa is not None:
            data['toegestane_maximum_massa_voertuig'] = max_massa

        serializer = PassageDetailSerializer()
        serializer._validate_voertuigcategorie(data)

        assert data['europese_voertuigcategorie_toevoeging'] == expected_toevoeging
        assert data['merk'] == expected_merk


