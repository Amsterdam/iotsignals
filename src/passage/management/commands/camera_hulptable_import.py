import datetime
import logging
from datetime import date, timedelta
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.apps import apps
from django.db import connection

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        CameraModel = apps.get_model('passage', 'Camera')
        helper_table_csv_path = os.path.join(
            settings.BASE_DIR, 'passage', 'helpertable.csv'
        )
        with transaction.atomic():
            CameraModel.objects.all().delete()

            with open(helper_table_csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile, dialect='excel', delimiter=',')

                inserts = []
                for row in reader:
                    for key in row.keys():
                        row[key] = None if row[key] == '' else row[key]

                    lat = row.pop('latitude')
                    lon = row.pop('longitude')
                    if lat is not None and lon is not None:
                        row['location'] = Point(
                            float(lat), float(lon), srid=4326
                        )

                    # convert ja/nee to boolean, or None
                    rijrichting_correct = row.get('rijrichting_correct')
                    if rijrichting_correct is not None:
                        rijrichting_correct = rijrichting_correct.lower() == 'ja'
                    row['rijrichting_correct'] = rijrichting_correct

                    # the following fields have been added to the initial table
                    # during migrations. Depending on the migration, fields may
                    # not exist.
                    existing_field_names = [f.name for f in CameraModel._meta.fields]
                    later_added_fields = [
                        # migration 0015
                        'camera_id',
                        'vma_linknr',
                        # migration 0029
                        'rijrichting_correct'
                    ]

                    for fieldname in later_added_fields:
                        if fieldname not in existing_field_names:
                            row.pop(fieldname)

                    inserts.append(CameraModel(**row))

            CameraModel.objects.bulk_create(inserts)