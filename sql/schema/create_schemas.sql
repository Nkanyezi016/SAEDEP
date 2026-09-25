-- Three-schema layout: staging holds the raw-but-cleaned QLFS extract as
-- loaded by src/load.py; reference holds small static lookup tables;
-- analytics holds the materialized query results in sql/analytics/.
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS reference;
CREATE SCHEMA IF NOT EXISTS analytics;
