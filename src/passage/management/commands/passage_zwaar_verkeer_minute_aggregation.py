import datetime
import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) argument
        parser.add_argument(
            '--from-date',
            type=datetime.date.fromisoformat,
            help='Run the aggregations from this date',
        )

    def _get_delete_query(self, run_date):
        return f""" 
        DELETE FROM passage_heavytrafficminuteaggregation
        WHERE passage_at_year = {run_date.year}
        AND passage_at_month = {run_date.month}
        AND passage_at_day = {run_date.day}
        ;
        """

    def _get_aggregation_query(self, run_date):
        return f"""
        INSERT INTO passage_heavytrafficminuteaggregation (
            passage_at_date,
            passage_at_year,
            passage_at_month,
            passage_at_day,
            passage_at_week,
            passage_at_day_of_week,
            passage_at_hour,
			passage_at_minute,
			camera_id, 
            camera_naam,
			camera_locatie,
            camera_kijkrichting,
			rijrichting,
			rijrichting_correct,
			straat,
			cordon,
			cordon_order_kaart,
            cordon_order_naam,
            richting,
			kenteken_hash,
			kenteken_land,
			massa_ledig_voertuig,
			toegestane_maximum_massa_voertuig,
			voertuig_soort, 
			inrichting,
            europese_voertuigcategorie,
			europese_voertuigcategorie_toevoeging,
            brandstoffen,
            diesel,
            gasoline,
            electric,
            lengte,
            breedte,
			aantal_staanplaatsen,
			aantal_zitplaatsen,
			merk,
			handelsbenaming,
            count
        )
        SELECT DATE(p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam'),
               EXTRACT(YEAR FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int  AS YEAR,
               EXTRACT(MONTH FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int AS MONTH,
               EXTRACT(DAY FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int   AS DAY,
               EXTRACT(week FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int  AS week,
               EXTRACT(dow FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int   AS dow,
               EXTRACT(HOUR FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int  AS HOUR,
			   EXTRACT(MINUTE FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int  AS MINUTE,
               p.camera_id,
               p.camera_naam,
			   p.camera_locatie,
			   p.camera_kijkrichting,
			   p.rijrichting,
			   h.rijrichting_correct,
			   p.straat,
				h.cordon,
				h.order_kaart as cordon_order_kaart,
				h.order_naam as cordon_order_naam,
                h.richting,
				p.kenteken_hash,
				kenteken_land,
			   CASE
				WHEN massa_ledig_voertuig <= 3500 THEN 'klasse01_0-3500'
				WHEN massa_ledig_voertuig <= 7500 THEN 'klasse02_3501-7500'
				WHEN massa_ledig_voertuig <= 11250 THEN 'klasse03_7501-11250'
				WHEN massa_ledig_voertuig <= 15000 THEN 'klasse04_11251-15000'
				WHEN massa_ledig_voertuig <= 20000 THEN 'klasse05_15001-20000'
				WHEN massa_ledig_voertuig <= 30000 THEN 'klasse06_20001-30000'
				WHEN massa_ledig_voertuig <= 45000 THEN 'klasse07_30001-45000'
                WHEN massa_ledig_voertuig >  45000 THEN 'klasse08_45001'
				ELSE 'onbekend'
				END
			   AS
			   massa_ledig_voertuig,
               CASE
                 WHEN toegestane_maximum_massa_voertuig <= 3500 THEN 'klasse01_0-3500'
                 WHEN toegestane_maximum_massa_voertuig <= 7500 THEN 'klasse02_3501-7500'
                 WHEN toegestane_maximum_massa_voertuig <= 10000 THEN 'klasse03_7501-10000'
                 WHEN toegestane_maximum_massa_voertuig <= 20000 THEN 'klasse04_10001-20000'
                 WHEN toegestane_maximum_massa_voertuig <= 30000 THEN 'klasse05_20001-30000'
                 WHEN toegestane_maximum_massa_voertuig <= 40000 THEN 'klasse06_30001-40000'
                 WHEN toegestane_maximum_massa_voertuig <= 50000 THEN 'klasse07_40001-50000'
                 WHEN toegestane_maximum_massa_voertuig <= 60000 THEN 'klasse08_50001-60000'
                 WHEN toegestane_maximum_massa_voertuig <= 70000 THEN 'klasse09_60001-70000'
                 WHEN toegestane_maximum_massa_voertuig >  70000 THEN 'klasse10_70001'
                 ELSE 'onbekend'
               END                                   AS
               toegestane_maximum_massa_voertuig,
				voertuig_soort, 
				inrichting,
				europese_voertuigcategorie,
				europese_voertuigcategorie_toevoeging,
                brandstoffen,
                diesel,
                gasoline,
                electric,
               CASE 
                WHEN lengte <= 1000 THEN '01 <=1000'
                WHEN lengte >  1000 THEN '02 >1000'
                ELSE '03 onbekend' 
               END as lengte,
               CASE
			   when breedte < 140 THEN '01 0-140'
			   WHEN breedte > 140 THEN '02 >140'
			   ELSE '03 onbekend'
				END as breedte,
			    CASE
				WHEN voertuig_soort = 'Bus' THEN aantal_staanplaatsen
				ELSE NULL
				END as aantal_staanplaatsen,
				CASE
				WHEN voertuig_soort= 'Bus' THEN aantal_zitplaatsen
				ELSE NULL
				END as aantal_zitplaatsen,
			   CASE
				WHEN voertuig_soort = 'Bus' THEN merk
				ELSE NULL
				END as merk,
				CASE
				WHEN voertuig_soort = 'Bus' THEN handelsbenaming
				ELSE NULL
				END as handelsbenaming,
				COUNT(*)
        FROM passage_passage as p
		left join	passage_camera AS h
        on			p.camera_naam = h.camera_naam AND
                    p.rijrichting = h.rijrichting
        WHERE p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam' >= '{run_date}'
        AND p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam' < '{run_date + timedelta(days=1)}'
        AND p.toegestane_maximum_massa_voertuig > 3500
		AND h.rijrichting_correct = True
		GROUP BY
			   DATE(p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam'),
               EXTRACT(YEAR FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               EXTRACT(MONTH FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               EXTRACT(DAY FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               EXTRACT(week FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               EXTRACT(dow FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               EXTRACT(HOUR FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
			   EXTRACT(MINUTE FROM p.passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
               p.camera_id,
               p.camera_naam,
			   p.camera_locatie,
			   p.camera_kijkrichting,
			   p.rijrichting,
			   h.rijrichting_correct,
			   p.straat,
				h.cordon,
				h.order_kaart,
				h.order_naam,
                h.richting,
				p.kenteken_hash,
				kenteken_land,
			   CASE
				WHEN massa_ledig_voertuig <= 3500 THEN 'klasse01_0-3500'
				WHEN massa_ledig_voertuig <= 7500 THEN 'klasse02_3501-7500'
				WHEN massa_ledig_voertuig <= 11250 THEN 'klasse03_7501-11250'
				WHEN massa_ledig_voertuig <= 15000 THEN 'klasse04_11251-15000'
				WHEN massa_ledig_voertuig <= 20000 THEN 'klasse05_15001-20000'
				WHEN massa_ledig_voertuig <= 30000 THEN 'klasse06_20001-30000'
				WHEN massa_ledig_voertuig <= 45000 THEN 'klasse07_30001-45000'
                WHEN massa_ledig_voertuig >  45000 THEN 'klasse08_45001'
				ELSE 'onbekend'
				END,
               CASE
                 WHEN toegestane_maximum_massa_voertuig <= 3500 THEN 'klasse01_0-3500'
                 WHEN toegestane_maximum_massa_voertuig <= 7500 THEN 'klasse02_3501-7500'
                 WHEN toegestane_maximum_massa_voertuig <= 10000 THEN 'klasse03_7501-10000'
                 WHEN toegestane_maximum_massa_voertuig <= 20000 THEN 'klasse04_10001-20000'
                 WHEN toegestane_maximum_massa_voertuig <= 30000 THEN 'klasse05_20001-30000'
                 WHEN toegestane_maximum_massa_voertuig <= 40000 THEN 'klasse06_30001-40000'
                 WHEN toegestane_maximum_massa_voertuig <= 50000 THEN 'klasse07_40001-50000'
                 WHEN toegestane_maximum_massa_voertuig <= 60000 THEN 'klasse08_50001-60000'
                 WHEN toegestane_maximum_massa_voertuig <= 70000 THEN 'klasse09_60001-70000'
                 WHEN toegestane_maximum_massa_voertuig >  70000 THEN 'klasse10_70001'
                 ELSE 'onbekend'
               END,
				voertuig_soort, 
				inrichting,
				europese_voertuigcategorie,
				europese_voertuigcategorie_toevoeging,
                brandstoffen,
                diesel,
                gasoline,
                electric,
               CASE 
                WHEN lengte <= 1000 THEN '01 <=1000'
                WHEN lengte >  1000 THEN '02 >1000'
                ELSE '03 onbekend' 
               END,
               CASE
			   when breedte < 140 THEN '01 0-140'
			   WHEN breedte > 140 THEN '02 >140'
			   ELSE '03 onbekend'
				END,
			   CASE
				WHEN voertuig_soort = 'Bus' THEN aantal_staanplaatsen
				ELSE NULL
				END,
				CASE
				WHEN voertuig_soort= 'Bus' THEN aantal_zitplaatsen
				ELSE NULL
				END,
			   CASE
				WHEN voertuig_soort = 'Bus' THEN merk
				ELSE NULL
				END,
				CASE
				WHEN voertuig_soort = 'Bus' THEN handelsbenaming
				ELSE NULL
				END
        ORDER  BY p.camera_id,
				  p.rijrichting,
                  DATE(passage_at at time zone 'utc' at time zone 'Europe/Amsterdam'),
                  EXTRACT(HOUR FROM passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
				  EXTRACT(MINUTE FROM passage_at at time zone 'utc' at time zone 'Europe/Amsterdam') :: int,
				  kenteken_hash;
        """

    def _run_query_from_date(self, run_date):

        log.info(f"Delete previously made aggregations for date {run_date}")
        delete_query = self._get_delete_query(run_date)
        log.info(f"Run the following query:")
        log.info(delete_query)
        with connection.cursor() as cursor:
            cursor.execute(delete_query)
            log.info(f"Deleted {cursor.rowcount} records")

        log.info(f"Run aggregation for date {run_date}")
        aggregation_query = self._get_aggregation_query(run_date)
        log.info(f"Run the following query:")
        log.info(aggregation_query)
        with connection.cursor() as cursor:
            cursor.execute(aggregation_query)
            log.info(f"Inserted {cursor.rowcount} records")

    def handle(self, *args, **options):
        if options['from_date']:
            run_date = options['from_date']
            while run_date < date.today():
                self._run_query_from_date(run_date)
                run_date = run_date + timedelta(days=1)

        else:
            run_date = date.today() - timedelta(days=1)
            self._run_query_from_date(run_date)
