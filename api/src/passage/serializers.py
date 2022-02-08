import logging
from datetime import date

from datapunt_api.rest import DisplayField, HALSerializer
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .errors import DuplicateIdError
from .models import Passage

log = logging.getLogger(__name__)


class PassageSerializer(HALSerializer):

    _display = DisplayField()

    class Meta:
        model = Passage
        fields = [
            '_display',
            '_links',
            'id',
            'versie',
            'merk',
            'created_at',
            'passage_at',
        ]


class PassageDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        validators=[]
    )  # Disable the validators for the id, which improves performance (rps) by over 200%

    class Meta:
        model = Passage
        fields = '__all__'

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            # this is pretty nasty to check the string like this, however when
            # a partition does not exist an IntegrityError is raised - in this
            # case we don't want to return a 409 duplicate error. Unfortunately
            # the string argument is the only way to distinguish between
            # different types of IntegrityError.
            if 'duplicate key' in e.args[0]:
                log.info(f"DuplicateIdError for id {validated_data['id']}")
                raise DuplicateIdError(str(e))
            else:
                raise

    def validate_datum_eerste_toelating(self, value):
        if value is None:
            raise ValidationError()
        return date(year=value.year, month=1, day=1)

    def validate_datum_tenaamstelling(self, value):
        return None

    def validate_toegestane_maximum_massa_voertuig(self, value):
        if value is not None and value <= 3500:
            return 1500
        return value

    def validate(self, data):
        self._validate_voertuigcategorie(data)
        self._validate_inrichting(data)
        self._validate_breedte(data)

        return data

    def _validate_inrichting(self, data):
        if 'voertuig_soort' in data:
            if data['voertuig_soort'].lower() == 'personenauto':
                data['inrichting'] = 'Personenauto'

    def _validate_voertuigcategorie(self, data):
        if 'toegestane_maximum_massa_voertuig' in data:
            if data['toegestane_maximum_massa_voertuig'] <= 3500:
                data['europese_voertuigcategorie_toevoeging'] = None
                data['merk'] = None

    def _validate_breedte(self, data):
        if data.get('voertuig_soort', '').lower() == 'personenauto':
            data['breedte'] = -1
