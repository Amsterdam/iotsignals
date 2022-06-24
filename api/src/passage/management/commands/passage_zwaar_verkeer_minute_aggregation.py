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
        WHERE year = {run_date.year}
        AND month = {run_date.month}
        AND day = {run_date.day}
        ;
        """

    def _get_aggreagation_query(self, run_date):
       return f"""
        INSERT INTO passage_heavytrafficminuteaggregation (
            date, 
            year, 
            month, 
            day, 
            week, 
            dow, 
            hour,
			minute,
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
			kenteken_hash,
			kenteken_land,
			datum_eerste_toelating,
			massa_ledig_voertuig,
			toegestane_maximum_massa_voertuig,
			aantal_assen,
			aantal_wielen,
			lengte,
			maximum_massa_trekken_ongeremd,
			maximum_massa_trekken_geremd,
			breedte,
			voertuig_soort, 
			inrichting,
            europese_voertuigcategorie,
			europese_voertuigcategorie_toevoeging,
			versit_klasse,
-- 			brandstof_alcohol,
-- 			brandstof_benzine,
-- 			brandstof_cng,
-- 			brandstof_diesel,
-- 			brandstof_electriciteit,
-- 			brandstof_lng,
-- 			brandstof_lpg,
-- 			brandstof_niet_geregistreerd,
-- 			brandstof_waterstof,
-- 			meerdere_brandstoffen,
            brandstoffen,
			co2_uitstoot_gecombineerd,
			co2_uitstoot_gewogen,
			milieuklasse_eg_goedkeuring_zwaar,
            count
        )
        SELECT DATE(p.passage_at),
               EXTRACT(YEAR FROM p.passage_at)::int AS YEAR,
               EXTRACT(MONTH FROM p.passage_at)::int AS MONTH,
               EXTRACT(DAY FROM p.passage_at)::int AS DAY,
               EXTRACT(week FROM p.passage_at)::int AS week,
               EXTRACT(dow FROM p.passage_at)::int AS dow,
               EXTRACT(HOUR FROM p.passage_at)::int AS HOUR,
			   EXTRACT(MINUTE FROM p.passage_at)::int AS MINUTE,
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
				p.kenteken_hash,
				p.kenteken_land,
				p.datum_eerste_toelating,
			   CASE
				WHEN massa_ledig_voertuig <= 3500 THEN 'klasse01_0-3500'
				WHEN massa_ledig_voertuig <= 7500 THEN 'klasse02_3501-7500'
				WHEN massa_ledig_voertuig <= 11250 THEN 'klasse03_7501-11250'
				WHEN massa_ledig_voertuig <= 15000 THEN 'klasse04_11251-15000'
				WHEN massa_ledig_voertuig <= 20000 THEN 'klasse05_15001-20000'
				WHEN massa_ledig_voertuig <= 30000 THEN 'klasse06_20001-30000'
				WHEN massa_ledig_voertuig <= 45000 THEN 'klasse07_30001-45000'
				ELSE 'klasse08_45001'
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
                 WHEN toegestane_maximum_massa_voertuig <= 80000 THEN 'klasse10_70001-80000'
                 ELSE 'klasse11_80001'
               END                                   AS
               toegestane_maximum_massa_voertuig,
				aantal_assen,
				aantal_wielen,
				lengte,
				maximum_massa_trekken_ongeremd,
				maximum_massa_trekken_geremd,
				breedte,
				voertuig_soort, 
				inrichting,
				europese_voertuigcategorie,
				europese_voertuigcategorie_toevoeging,
				versit_klasse,
-- 				brandstof_alcohol,
-- 				brandstof_benzine,
-- 				brandstof_cng,
-- 				brandstof_diesel,
-- 				brandstof_electriciteit,
-- 				brandstof_lng,
-- 				brandstof_lpg,
-- 				brandstof_niet_geregistreerd,
-- 				brandstof_waterstof,
-- 				meerdere_brandstoffen,
                brandstoffen,
				co2_uitstoot_gecombineerd,
				co2_uitstoot_gewogen,
				milieuklasse_eg_goedkeuring_zwaar,
				COUNT(*)
        FROM passage_passage as p
		left join	passage_camera AS h
        on			p.camera_naam = h.camera_naam AND
                    p.camera_kijkrichting = h.camera_kijkrichting AND
                    p.rijrichting = h.rijrichting
        WHERE p.passage_at >= '{run_date}'
        AND p.passage_at < '{run_date + timedelta(days=1)}'
		AND p.voertuig_soort = 'Bedrijfsauto' OR p.toegestane_maximum_massa_voertuig > 3500
		AND h.rijrichting_correct = 'ja'
		GROUP BY
			   DATE(passage_at),
               EXTRACT(YEAR FROM passage_at)::int,
               EXTRACT(MONTH FROM passage_at)::int,
               EXTRACT(DAY FROM passage_at)::int,
               EXTRACT(week FROM passage_at)::int,
               EXTRACT(dow FROM passage_at)::int,
               EXTRACT(HOUR FROM passage_at)::int,
			   EXTRACT(MINUTE FROM passage_at)::int,
               p.camera_id,
               p.camera_naam,
			   p.camera_locatie,
			   p.camera_kijkrichting,
			   p.rijrichting,
			   h.rijrichting_correct,
			   p.straat,
				h.cordon,
				cordon_order_kaart,
				cordon_order_naam,
				p.kenteken_hash,
				p.kenteken_land,
				p.datum_eerste_toelating,
			   massa_ledig_voertuig,
               toegestane_maximum_massa_voertuig,
				aantal_assen,
				aantal_wielen,
				lengte,
				maximum_massa_trekken_ongeremd,
				maximum_massa_trekken_geremd,
				breedte,
				voertuig_soort, 
				inrichting,
				europese_voertuigcategorie,
				europese_voertuigcategorie_toevoeging,
				versit_klasse,
--                 brandstof_alcohol,
--                 brandstof_benzine,
--                 brandstof_cng,
--                 brandstof_diesel,
--                 brandstof_electriciteit,
--                 brandstof_lng,
--                 brandstof_lpg,
--                 brandstof_niet_geregistreerd,
--                 brandstof_waterstof,
--                 meerdere_brandstoffen,
                brandstoffen,
				co2_uitstoot_gecombineerd,
				co2_uitstoot_gewogen,
				milieuklasse_eg_goedkeuring_zwaar
        ORDER  BY p.camera_id,
				  p.rijrichting,
                  DATE(passage_at),
				  EXTRACT(HOUR FROM passage_at)::int,
				  EXTRACT(MINUTE FROM passage_at)::int;
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
        aggregation_query = self._get_aggreagation_query(run_date)
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
