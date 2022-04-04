
# IOTsignals migrations

## Abstract

Iotsignals (also called passage archive) is a project that stores all 
passages that are registered by ANPR (automatic number plate regocnition) 
camera's placed on several (access)roads in Amsterdam. 

Each passage is stored as a single row in one large postgres database 
using a python/Django/DRF layer as API. Django migrations are used to 
manage the database schema. Those are very nice and work great, 
until your database is very large. 

Meet IOTsignals: 800million rows, 1TB of data. Plain Django, plain postgres. 
This write-up is not intended to describe future improvements (there are many, 
we know), but serves to document the current situation and prevent major issues
that can occur when altering the database schema.

Django migrations are run inside a transaction, and because there are scenarios
where postgres tables double in size during an ALTER TABLE, this database
has the potential to grow to 2TB during a migration. That is problematic
because it runs on a postgres cluster (secure PROD) with a shared storage 
of 2TB total.

Doubling the database will cause all workloads on secure PROD to come 
to a grinding halt.

The solution: prevent table rewrites on table level and instead do table rewrites
on partition level.

## Intro

The IOTsignals project has been around since 2018 and was setup without proper
planning. Nowadays the table grows with about 1GB per day, ~xxx passages.

The passage table has been split up into partitions by the passage timestamp. Each
partition holds the rows for a single day. This works ok-ish for now. There are 
many improvements to be done in the architecture but for now we need to maintain 
the current setup. 

## Doubling table sizes

Django migrations are 



---------------------

WIP NOTES

---------------------


Migration steps:
    1) Migrate up to 0021
    2) Run command `passage_set_passage_id`
    3) Migrate the rest

-----

Initial local test:
- generate 3GB data
- measure initial state
    - measure dead_tuple_count
    - measure total db size
- run migration
    - in same transaction measure state (dead_tuple_count, total_db_size)
- analyze:
    - did the database grow?
    - How much?
    - Why?

Second local test:
- same test as initial local test, but now purposely write new data (volgnummer, default=1).
- analyze:
    - how does growth compare to initial test?

------

# Get database size
SELECT pg_size_pretty(pg_database_size('iotsignals'));

# Get indices size
SELECT pg_size_pretty(SUM(pg_indexes_size(relid))) as index_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname LIKE 'passage_passage%';



---------------------------

Test one, no optimizations

1) Migration up to 21 & generate test data:
database size: 3922
index size: 784

2) Set passage_id
database size: 4149 (+5%)
index size: 731

4) Migrate
Slow migrations:
- 22
- 25 (very slow)

database size: 3840
index size: 691

---------------------------

Test 2, vacuum after data generation

1) Migration up to 21 & generate test data:
database size: 4275
index size: 784

2) Vacuum
database size: 4180
index size: 691

3) Set passage_id
database size: 4845 (+15%)
index size: 787

4) Migrates

- passage 22
database size: 4845
index size: 787

- passage 23
database size: 4846
index size: 787

- passage 24
database size: 4846
index size: 787

- passage 25
database size:
index size:

tijdens 25:

7410
7677
7895
8088
8126
8339
8529
4190

============

De migration:

BEGIN;
--
-- Alter field massa_ledig_voertuig on passage
--
ALTER TABLE "passage_passage" ALTER COLUMN "massa_ledig_voertuig" TYPE integer USING "massa_ledig_voertuig"::integer;
COMMIT;

Aanname: db is te groot voor memory, rewrite moet op disk.

----

Wat zien we hier?

- Begin/commit: transaction
-

https://www.postgresql.org/docs/11/routine-vacuuming.html#VACUUM-FOR-SPACE-RECOVERY

---------

Relevante postgres docs:

In PostgreSQL, an UPDATE or DELETE of a row does not immediately remove the
old version of the row. This approach is necessary to gain the benefits of
multiversion concurrency control (MVCC, see Chapter 13): the row version must
not be deleted while it is still potentially visible to other transactions.
But eventually, an outdated or deleted row version is no longer of interest to
any transaction. The space it occupies must then be reclaimed for reuse by
new rows, to avoid unbounded growth of disk space requirements.
This is done by running VACUUM.

Plain VACUUM may not be satisfactory when a table contains large numbers of dead
row versions as a result of massive update or delete activity. If you have such
a table and you need to reclaim the excess disk space it occupies, you will need
to use VACUUM FULL, or alternatively CLUSTER or one of the table-rewriting
variants of ALTER TABLE. These commands rewrite an entire new copy of the table
and build new indexes for it. All these options require an ACCESS EXCLUSIVE lock.
Note that they also temporarily use extra disk space approximately equal to the
size of the table, since the old copies of the table and indexes can't be released
until the new ones are complete.


zijn relevant hierin.. en verder, over de ALTER TABLE waarin een table-rewrite nodig is:
-> https://www.postgresql.org/docs/11/routine-vacuuming.html#VACUUM-FOR-SPACE-RECOVERY


Adding a column with a volatile DEFAULT or changing the type of an existing column
will require the entire table and its indexes to be rewritten. As an exception,
when changing the type of an existing column, if the USING clause does not change
the column contents and the old type is either binary coercible to the new type
or an unconstrained domain over the new type, a table rewrite is not needed; but
any indexes on the affected columns must still be rebuilt. Adding or removing a
system oid column also requires rewriting the entire table. Table and/or index
rebuilds may take a significant amount of time for a large table; and will temporarily
require as much as double the disk space.
-> https://www.postgresql.org/docs/11/sql-createcast.html

Over table rewrites:
https://www.postgresql.org/docs/11/sql-altertable.html#SQL-ALTERTABLE-NOTES

Kunnen we de partities niet een voor een migreren?
Nee (https://www.postgresql.org/docs/10/ddl-partitioning.html#DDL-PARTITIONING-DECLARATIVE):

Partitions cannot have columns that are not present in the parent.
It is neither possible to specify columns when creating partitions with
CREATE TABLE nor is it possible to add columns to partitions after-the-fact
using ALTER TABLE. Tables may be added as a partition with
ALTER TABLE ... ATTACH PARTITION only if their columns exactly match the
parent, including any oid column.

==================================

Nieuwe test, nieuwe migrations

1) Migrate to 20, generate testdata
dbsize: 3969
indices: 560

2) Partitioned vacuum
dbsize: 3646
indices: 511

3) Run command
dbsize: 4542 (+25%, 250GB!)
indices: 619

4) Finish migrations

21:
dbsize: 4724 (+30%, 300GB!)
indices: 799

22:
dbsize: 4725
indices: 799

5) Vacuum
dbsize: 3839
indices: 691

=======================================

Nieuwe test, set massa_ledig_voertuig=None na copy

1) Migrate to passage 20
dbsize: 3695mb
indices: 559mb

2) Partitioned vacuum
dbsize: 3646
indices: 510

3) Run command
dbsize: 4162mb (+13% = 130GB)
indices: 568mb

4) Finish migrations

21:
dbsize: 4344 (+18%, 180GB)
indices: 748mb

22:
no change

5) Vacuum
dbsize: 3834mb (+4%, 40GB)
indices: 690mb


------------------------

# Get database size
SELECT pg_size_pretty(pg_database_size('iotsignals'));

# Get indices size
SELECT pg_size_pretty(SUM(pg_indexes_size(relid))) as index_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname LIKE 'passage_passage%';