import logging
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.db import connection

log = logging.getLogger(__name__)


def make_partition_sql(timestamp):
    """
    Get the SQL for making a partition for the passage table for a particular day

    :param timestamp: datetime of the date to get the sql for.

    :return: SQL query for generating the the passage partition.
    """
    return f"""
        CREATE table IF NOT EXISTS passage_passage_{timestamp.strftime("%Y%m%d")}
        PARTITION OF passage_passage
        FOR VALUES
        FROM ('{timestamp.date()}') TO ('{timestamp.date() + timedelta(1)}');
    """


def check_postgres_major_version(cursor, required):
    """
    Check postgres version, assert that the required major version is met. We
    need 10+ for partitions and 11+ for indexes within the partitions.

    :param cursor: The cursor to execute version retrieval query.
    :param required: The minimum required major version.
    """
    cursor.execute("""
        SELECT substr(setting, 1, strpos(setting, '.')-1)::smallint as version
        FROM pg_settings
        WHERE name = 'server_version';
    """)
    if cursor.fetchone()[0] < required:
        raise Exception("Need postgres v11 or higher")


def make_partitions(timestamps):
    """
    Make the partitions for the given timestamps, defaulting to 6 partitions.

    :param timestamps: Iterable of timestamps to generated partitions for.
    """
    log.info("Creating partitions")

    with connection.cursor() as cursor:
        check_postgres_major_version(cursor, 11)

        for timestamp in timestamps:
            query = make_partition_sql(timestamp)
            log.info(query)
            cursor.execute(query)

    with connection.cursor() as cursor:
        for timestamp in timestamps:
            test_query = f"""
            SELECT EXISTS (
                SELECT FROM 
                    pg_tables
                WHERE 
                    schemaname = 'public' AND 
                    tablename  = 'passage_passage_{timestamp.strftime("%Y%m%d")}'
                );
            """
            cursor.execute(test_query)
            result = cursor.fetchone()
            assert result[0] is True


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--days', nargs='?', default=6, type=int)

    def handle(self, **options):
        num_days = options.get('days')
        start_date = datetime.today()
        timestamps = [start_date + timedelta(i) for i in range(num_days)]
        make_partitions(timestamps)
