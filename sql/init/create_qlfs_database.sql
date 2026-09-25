-- Runs once, automatically, the first time the postgres container's data
-- volume is initialized (see docker-entrypoint-initdb.d in the official
-- postgres image). Creates a second database, separate from Airflow's own
-- metadata database, to hold the QLFS staging/reference/analytics schemas
-- so pipeline data and Airflow's internal bookkeeping don't share tables.
CREATE DATABASE qlfs;