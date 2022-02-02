#!/usr/bin/python

# std
from os import environ
from datetime import datetime, timedelta
# 3rd party
import psycopg2


PARTITIONS_TO_ADD = 6


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


def make_partitions(*timestamps):
    """
    Make the partitions for the given timestamps, defaulting to 6 partitions.

    :param timestamps: Iterable of timestamps to generated partitions for.
    """
    if not timestamps:
        start_date = datetime.today()
        timestamps = (start_date + timedelta(i) for i in range(PARTITIONS_TO_ADD))

    connection = psycopg2.connect(
        host=environ['DATABASE_HOST'],
        dbname=environ['DATABASE_NAME'],
        user=environ['DATABASE_USER'],
        password=environ['DATABASE_PASSWORD']
    )

    with connection.cursor() as cursor:
        check_postgres_major_version(cursor, 11)

        for timestamp in timestamps:
            cursor.execute(make_partition_sql(timestamp))


if __name__ == '__main__':
    make_partitions()
