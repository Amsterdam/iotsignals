import logging
import csv
import os

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.db import transaction
from django.apps import apps

log = logging.getLogger(__name__)

class Command(BaseCommand):

    def _insert_camera_hulptabel(self):
        hulptabelModel = apps.get_model('passage', 'HulptabelCameragebiedenTaxidashboard')
        hulptabel_csv_path = os.path.join(
            settings.BASE_DIR, 'passage', 'camerahulptabel.csv'
        )

        with transaction.atomic():
            hulptabelModel.objects.all().delete()

            with open(hulptabel_csv_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile, dialect='excel', delimiter=',')

                inserts = []
                for row in reader:
                    for key in row.keys():
                        row[key] = None if row[key] == '' else row[key]
                    inserts.append(hulptabelModel(**row))

            hulptabelModel.objects.bulk_create(inserts)
            return hulptabelModel.objects.count()

    def handle(self, *args, **options):
       log.info(f"replacing Camera Hulp tabel")
       inserted = self._insert_camera_hulptabel()
       log.info(f"Inserted {inserted} row")

