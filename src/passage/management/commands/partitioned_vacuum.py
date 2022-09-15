import logging
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Max, Min
from django.db.models.functions import TruncDay
from django.template.defaultfilters import filesizeformat

from main import settings
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
        initial_size = initial_size_pretty = None
        for date in (
            date_min + timedelta(n) for n in range((date_max - date_min).days)
        ):
            i += 1
            partition_name = f'passage_passage_{date:%Y%m%d}'
            vacuum_query = f'VACUUM FULL ANALYZE {partition_name}'
            size_query = (
                "SELECT pg_database_size("
                f"'{settings.DATABASES['default']['NAME']}');"
            )

            self.stdout.write(f'Starting vacuum: {vacuum_query}')
            try:
                with connection.cursor() as cursor:
                    cursor.execute(size_query)
                    size = cursor.fetchone()[0]

                    if not initial_size:
                        initial_size = size
                        initial_size_pretty = filesizeformat(size)

                    size_pretty = filesizeformat(size)
                    change = size - initial_size
                    change_pretty = filesizeformat(change)
                    procentual_change = change / initial_size * 100

                    self.stdout.write(f'Total DB size: {self.style.SUCCESS(size_pretty)} '
                                      f'(initial: {initial_size_pretty}, '
                                      f'change: {change_pretty}, '
                                      f'{procentual_change:.1f}%)')
                    cursor.execute(vacuum_query)
            except Exception as e:
                self.stderr.write(f'Error vacuuming: {e}')

            if i % 10 == 0:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(sleep)}')
                time.sleep(sleep)
            else:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(0.1)}')
                time.sleep(0.1)

        self.stdout.write(self.style.SUCCESS('Finished'))