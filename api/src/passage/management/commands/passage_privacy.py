import logging

from django.core.management.base import BaseCommand
from django.db.models import Case, F, Value, When
from django.db.models.functions import Greatest, TruncYear
from django.forms import model_to_dict
from passage.models import Passage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **options):
        verbosity = int(options['verbosity'])
        logger.info("message")

        fields = [
            'datum_eerste_toelating',
            'datum_tenaamstelling',
            'toegestane_maximum_massa_voertuig',
            'europese_voertuigcategorie_toevoeging',
            'inrichting',
            'merk',
        ]
        subset = Passage.objects.filter().values('pk')[0:3]
        qs = Passage.objects.filter(pk__in=subset).update(
            datum_eerste_toelating=TruncYear('datum_eerste_toelating'),
            datum_tenaamstelling=Value(None),
            toegestane_maximum_massa_voertuig=Case(
                When(toegestane_maximum_massa_voertuig__lte=3500, then=Value(1500)),
                default=F('toegestane_maximum_massa_voertuig'),
            ),
            europese_voertuigcategorie_toevoeging=Case(
                When(toegestane_maximum_massa_voertuig__lte=3500, then=Value(None)),
                default=F('europese_voertuigcategorie_toevoeging'),
            ),
            inrichting=Case(
                When(voertuig_soort__iexact='PeRsoNenAutO', then=Value('personenauto')),
                default=F('inrichting'),
            ),
            merk=Case(
                When(toegestane_maximum_massa_voertuig__lte=3500, then=Value(None)),
                default=F('merk'),
            ),
        )
        raise Exception('FAIL')
        #  for o in qs:
            #  print('-' * 80)
            #  for field in fields:
                #  new_field = f'x_{field}'
                #  values = (
                    #  self.style.WARNING(getattr(o, field))
                    #  + '->'
                    #  + self.style.SUCCESS(getattr(o, new_field))
                #  )
                #  self.stdout.write(f"{field}: {values}")
