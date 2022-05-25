import datetime
import logging
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Case, Value, When

from iotsignals import settings
from passage.models import Passage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--sleep', nargs='?', default=1, type=float)

    def handle(self, **options):
        logger.info("message")

        sleep = options['sleep']

        date_min = datetime.datetime(2022, 5, 6, 13, 0)
        date_max = datetime.datetime.today()

        for date in (
            date_min + timedelta(n) for n in range((date_max - date_min).days + 1)
        ):
            if date != date_min:
                # for the first date we want a specific timestamp (13:00). For all
                # following days we want the full day (starting at 00:00)
                date = date.date()

            self.stdout.write(f"Selecting data in: {self.style.SQL_KEYWORD(date)}")
            num_updated_rows = Passage.objects.filter(
                passage_at__gte=date,
                passage_at__lt=date + timedelta(days=1),
            ).update(rijrichting=Case(
                When(rijrichting=-1, then=Value(1)),
                When(rijrichting=1, then=Value(-1)),
            ))
            self.stdout.write(f'Processed: {self.style.SUCCESS(num_updated_rows)}')

            if num_updated_rows > 0:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(sleep)}')
                time.sleep(sleep)
            else:
                self.stdout.write(f'sleeping for: {self.style.SUCCESS(0.1)}')
                time.sleep(0.1)

            partition_name = f'passage_passage_{date:%Y%m%d}'
            vacuum_query = f'VACUUM FULL ANALYZE {partition_name}'
            size_query = (
                "SELECT pg_size_pretty(pg_database_size("
                f"'{settings.DATABASES['default']['NAME']}'));"
            )

            self.stdout.write(f'Starting vacuum: {vacuum_query}')
            try:
                with connection.cursor() as cursor:
                    cursor.execute(size_query)
                    size = cursor.fetchone()[0]
                    self.stdout.write(f'Total DB size before vacuum: {self.style.SUCCESS(size)}')
                    cursor.execute(vacuum_query)
            except Exception as e:
                self.stderr.write(f'Error vacuuming: {e}')
            self.stdout.write(f'sleeping for: {self.style.SUCCESS(sleep)}')
            time.sleep(sleep)

        self.stdout.write(self.style.SUCCESS('Finished'))
