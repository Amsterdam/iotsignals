import logging
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Case, F, Max, Min, Value, When
from django.db.models.functions import TruncDay, TruncYear
from django.db.utils import ProgrammingError
from passage.models import Passage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--sleep', nargs='?', default=1, type=int)

    def handle(self, **options):
        logger.info("message")

        sleep = options['sleep']

        dates = Passage.objects.aggregate(
            min=TruncDay(Min('passage_at')), max=TruncDay(Max('passage_at'))
        )

        print(dates)
        if not dates['min']:
            self.stdout.write('No data to be processed')
            return

        date_min = dates['min'] + timedelta(days=1)
        date_max = dates['max'] + timedelta(days=2)

        i = 0
        for date in (
            date_min + timedelta(n) for n in range((date_max - date_min).days)
        ):
            i += 1
            partition_name = f'passage_passage_{date:%Y%m%d}'
            vacuum_query = f'VACUUM FULL ANALYZE {partition_name}'
            self.stdout.write(f'Starting vacuum: {vacuum_query}')
            try:
                with connection.cursor() as cursor:
                    cursor.execute(vacuum_query)
            except ProgrammingError as e:
                self.stderr.write(f'Error vacuuming: {e}')

            if i % 10 == 0:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(sleep)}')
                time.sleep(sleep)
            else:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(0.1)}')
                time.sleep(0.1)

        self.stdout.write(self.style.SUCCESS('Finished'))
