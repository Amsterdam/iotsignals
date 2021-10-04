#!/usr/bin/python

import psycopg2
from os import environ
from sys import exit
from datetime import datetime, timedelta

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


def make_partitions(*timestamps):
    """
    Make the partitions for the given timestamps, defaulting to 6 partitions.

    :param timestamps: Iterable of timestamps to generated partitions for.
    """
    if not timestamps:
        start_date = datetime.today()
        timestamps = (start_date + timedelta(i) for i in range(PARTITIONS_TO_ADD))

    conn = psycopg2.connect(
        host=environ['DATABASE_HOST'],
        dbname=environ['DATABASE_NAME'],
        user=environ['DATABASE_USER'],
        password=environ['DATABASE_PASSWORD']
    )

    with conn.cursor() as cur:
        # check pg version?, we need 10+ for partitions and 11+ for
        # indexes within the partitions
        cur.execute("""
            SELECT Substr(setting, 1, strpos(setting, '.')-1)::smallint as version
            FROM pg_settings
            WHERE name = 'server_version';
        """)
        rows = cur.fetchall()

        if len(rows) == 1 and int(rows[0][0]) < 11:
            raise Exception("Need postgres v11 or higher")

        for timestamp in timestamps:
            cur.execute(make_partition_sql(timestamp))


if __name__ == '__main__':
    make_partitions()
