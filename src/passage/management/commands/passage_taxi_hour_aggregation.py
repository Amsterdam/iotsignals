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
        DELETE FROM passage_taxihouraggregation
        WHERE passage_at_date = '{run_date}';
        """

    def _get_aggregation_query(self, run_date):
        return f"""
        INSERT INTO passage_taxihouraggregation (
                passage_at_date,
                hh, 
                gebiedstype, 
                gebied, 
                electric,
                unieke_passages, 
                check_on_camera_count           
            )
        select 
            p.passage_at::date as passage_date, 
            extract(hour from p.passage_at) as hh,
            gebiedstype,
            gebied,
            electric, 
            count(distinct kenteken_hash) as unieke_passages, 
            count(distinct camera_naam) as check_on_camera_count
        from 
            passage_hulptabelcameragebiedentaxidashboard h
        left join 
            public.passage_passage p
            on p.camera_naam LIKE '%' || h.camera_id || '%'
        where
            p.taxi_indicator = true
            and electric is not null
            and h.camera_id != ''
            and passage_at >= '{run_date}'
            and passage_at < '{run_date + timedelta(days=1)}'
        group by 
            passage_date, hh, electric, gebiedstype , gebied
        order by 
            gebiedstype , gebied, passage_date, hh, electric ;
        """

    def _run_query_from_date(self, run_date):
        log.info(f"Delete previously made aggregations for date {run_date}")
        delete_query = self._get_delete_query(run_date)
        log.info(f"Run the following query: {delete_query}")
        with connection.cursor() as cursor:
            cursor.execute(delete_query)
            log.info(f"Deleted {cursor.rowcount} records")

        log.info(f"Run aggregation for date {run_date}")
        aggregation_query = self._get_aggregation_query(run_date)
        log.info(f"Run the following query: {aggregation_query}")
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
            for i in range(3, 0, -1):
                # by default update the aggregations for the last three days
                run_date = date.today() - timedelta(days=i)
                self._run_query_from_date(run_date)
