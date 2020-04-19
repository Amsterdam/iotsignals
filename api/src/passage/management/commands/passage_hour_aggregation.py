import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

from passage.models import Passage, PassageHourAggregation

log = logging.getLogger(__name__)

# Data collection was started sometime in 2018, so to be sure, we start the first run on the first of january 2019
FIRST_DATE = date(2018, 1, 1)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) argument
        parser.add_argument(
            '--first_run',
            action='store_true',
            help='Do the first run of the passages aggregation',
        )

    def _get_query(self, run_date):
        return f"""
        INSERT INTO passage_passagehouraggregation (
            date, 
            year, 
            month, 
            day, 
            week, 
            dow, 
            hour, 
            camera_id, 
            camera_naam, 
            rijrichting, 
            camera_kijkrichting, 
            kenteken_land, 
            voertuig_soort, 
            europese_voertuigcategorie, 
            taxi_indicator, 
            diesel, 
            gasoline, 
            electric, 
            toegestane_maximum_massa_voertuig, 
            count
        )
        SELECT DATE(passage_at),
               EXTRACT(YEAR FROM passage_at) :: int  AS YEAR,
               EXTRACT(MONTH FROM passage_at) :: int AS MONTH,
               EXTRACT(DAY FROM passage_at) :: int   AS DAY,
               EXTRACT(week FROM passage_at) :: int  AS week,
               EXTRACT(dow FROM passage_at) :: int   AS dow,
               EXTRACT(HOUR FROM passage_at) :: int  AS HOUR,
               camera_id,
               camera_naam,
               rijrichting,
               camera_kijkrichting,
               CASE
                 WHEN kenteken_land = 'NL' THEN 'NL'
                 ELSE 'overig'
               END                                   AS kenteken_land,
               voertuig_soort,
               europese_voertuigcategorie,
               taxi_indicator,
               diesel,
               gasoline,
               electric,
               CASE
                 WHEN toegestane_maximum_massa_voertuig <= 3500 THEN 'klasse01_0-3500'
                 WHEN toegestane_maximum_massa_voertuig < 7500 THEN 'klasse02_3501-7500'
                 WHEN toegestane_maximum_massa_voertuig <= 10000 THEN
                 'klasse03_7501-10000'
                 WHEN toegestane_maximum_massa_voertuig <= 20000 THEN
                 'klasse04_10001-20000'
                 WHEN toegestane_maximum_massa_voertuig <= 30000 THEN
                 'klasse05_20001-30000'
                 WHEN toegestane_maximum_massa_voertuig <= 40000 THEN
                 'klasse06_30001-40000'
                 WHEN toegestane_maximum_massa_voertuig <= 50000 THEN
                 'klasse07_40001-50000'
                 WHEN toegestane_maximum_massa_voertuig <= 60000 THEN
                 'klasse08_50001-60000'
                 WHEN toegestane_maximum_massa_voertuig <= 70000 THEN
                 'klasse09_60001-70000'
                 WHEN toegestane_maximum_massa_voertuig <= 80000 THEN
                 'klasse10_70001-80000'
                 ELSE 'klasse11_80001'
               END                                   AS
               toegestane_maximum_massa_voertuig,
               COUNT(*)
        FROM passage_passage
        WHERE EXTRACT(YEAR FROM created_at) :: int = {run_date.year}
        AND EXTRACT(MONTH FROM created_at) :: int = {run_date.month}
        AND EXTRACT(DAY FROM created_at) :: int = {run_date.day}
        GROUP  BY DATE(passage_at),
                  EXTRACT(YEAR FROM passage_at) :: int,
                  EXTRACT(MONTH FROM passage_at) :: int,
                  EXTRACT(DAY FROM passage_at) :: int,
                  EXTRACT(week FROM passage_at) :: int,
                  EXTRACT(dow FROM passage_at) :: int,
                  EXTRACT(HOUR FROM passage_at) :: int,
                  camera_id,
                  camera_naam,
                  rijrichting,
                  camera_kijkrichting,
                  CASE
                    WHEN kenteken_land = 'NL' THEN 'NL'
                    ELSE 'overig'
                  END,
                  voertuig_soort,
                  europese_voertuigcategorie,
                  taxi_indicator,
                  diesel,
                  gasoline,
                  electric,
                  CASE
                    WHEN toegestane_maximum_massa_voertuig <= 3500 THEN
                    'klasse01_0-3500'
                    WHEN toegestane_maximum_massa_voertuig < 7500 THEN
                    'klasse02_3501-7500'
                    WHEN toegestane_maximum_massa_voertuig <= 10000 THEN
                    'klasse03_7501-10000'
                    WHEN toegestane_maximum_massa_voertuig <= 20000 THEN
                    'klasse04_10001-20000'
                    WHEN toegestane_maximum_massa_voertuig <= 30000 THEN
                    'klasse05_20001-30000'
                    WHEN toegestane_maximum_massa_voertuig <= 40000 THEN
                    'klasse06_30001-40000'
                    WHEN toegestane_maximum_massa_voertuig <= 50000 THEN
                    'klasse07_40001-50000'
                    WHEN toegestane_maximum_massa_voertuig <= 60000 THEN
                    'klasse08_50001-60000'
                    WHEN toegestane_maximum_massa_voertuig <= 70000 THEN
                    'klasse09_60001-70000'
                    WHEN toegestane_maximum_massa_voertuig <= 80000 THEN
                    'klasse10_70001-80000'
                    ELSE 'klasse11_80001'
                  END
        ORDER  BY camera_id,
                  DATE(passage_at),
                  EXTRACT(HOUR FROM passage_at) :: int  
        ;
    """

    def _run_query_from_date(self, run_date):
        log.info(f"Running aggregation for date {run_date}")

        query = self._get_query(run_date)
        Passage.objects.raw(query)

    def handle(self, *args, **options):
        if options['first_run']:
            run_date = FIRST_DATE
            while run_date < date.today():
                run_date = run_date + timedelta(days=1)
                self._run_query_from_date(run_date)

        else:
            run_date = date.today() - timedelta(days=1)
            self._run_query_from_date(run_date)
