import logging
from datetime import datetime, timedelta

import pytz
from django.core.management.base import BaseCommand
from factory.django import DjangoModelFactory

from passage.management.commands.make_partitions import make_partitions
from passage.models import Passage
from tests.passage.factories import PassageFactory

log = logging.getLogger(__name__)


class NewPassageFactory(DjangoModelFactory):
    class Meta:
        model = Passage


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) argument
        parser.add_argument(
            '--num_days',
            type=int,
            help='The number of days to fill with data',
        )
        parser.add_argument(
            '--num_rows_per_day',
            type=int,
            help='The number rows per day to generate',
        )

    def handle(self, *args, **options):
        num_days = options.get('num_days', 7)
        num_rows_per_day = options.get('num_rows_per_day', 1000)
        self.create_data_range(num_days, num_rows_per_day)

    def create_data_range(self, num_days=7, num_rows_per_day=1000):
        timestamp_range = [datetime.today() - timedelta(days=i) for i in range(num_days)]
        timestamp_range = sorted(timestamp_range)
        make_partitions(timestamp_range)

        today = datetime.now(tz=pytz.utc)
        for i in range(num_days):
            dt = today - timedelta(days=i)
            self.create_data(dt, num_rows=num_rows_per_day)

    def create_data(self, dt, num_rows=10000):
        log.info(f"========================== {dt} ==========================")

        start_dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = dt.replace(hour=23, minute=59, second=59, microsecond=999)
        log.info(f"Creating {num_rows} rows for range {start_dt} - {end_dt}")

        passages = PassageFactory.build_batch(
            size=num_rows,
            passage_at=dt,
            created_at=dt
        )

        Passage.objects.bulk_create(passages)

        log.info(f"Created {len(passages)} passages")
