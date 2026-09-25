# SAEDEP — South African Employment Data Engineering Pipeline

SAEDEP (South African Employment Data Engineering Pipeline) is an end-to-end data engineering project focused on processing and analysing South African labour-market data.

The project uses the **Quarterly Labour Force Survey (QLFS)** published by Statistics South Africa to build a reproducible pipeline that transforms raw survey data into clean, validated and structured analytical data.

The pipeline covers the complete journey from raw source data to analytical SQL tables that can be used to investigate employment, unemployment, demographics, education, provinces, industries and labour-market trends in South Africa.

## Pipeline Architecture

```
                  Statistics South Africa
                           │
                           ▼
                    QLFS Source Data
                           │
                           ▼
                  ┌─────────────────┐
                  │     Airflow     │
                  │  Orchestration  │
                  └────────┬────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Extract    │
                    │    Python    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Transform   │
                    │ Pandas/Python│
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Validate   │
                    │     Python   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     Load     │
                    │  PostgreSQL  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  SQL Models  │
                    │ sql/analytics│
                    └──────┬───────┘
                           │
                           ▼
                    Analytical Tables
                           │
                           ▼
                    Dashboard / Analysis
```

## Project Process

### 1. Source Data

The pipeline starts with the **Quarterly Labour Force Survey (QLFS)** from Statistics South Africa.

The QLFS contains detailed information about South Africa's labour market, including employment, unemployment, demographics, education and other labour-related characteristics.

The raw source data is kept separate from the processed data so that the original dataset remains unchanged. Raw data is not committed to the repository; drop the source CSV at `data/source/QLFS202602.csv` before running the pipeline.

### 2. Orchestration

Apache Airflow manages and orchestrates the pipeline (`dags/pipeline.py`).

Instead of manually running each stage, Airflow controls the order in which the different pipeline tasks execute and manages their dependencies:

```
setup_sql_schema → Extract → Transform → Validate → Load → run_sql_analytics
```

### 3. Extract (`src/extract.py`)

Reads the raw QLFS CSV and hands it to the transform stage without modifying the original source file.

### 4. Transform (`src/transform.py`)

Cleans and restructures the raw QLFS data with Pandas:

- Selects the relevant columns and renames them to descriptive names
- Drops records with a missing or non-positive survey weight (a weight ≤ 0 can't contribute to a weighted estimate)
- **Filters to the working-age population (15+)**. QLFS never asks anyone under 15 the labour-market questions, so those rows show up with sentinel values rather than genuine answers; keeping them corrupts every employment/labour-force aggregate.
- **Parses `SURVEYDATE` correctly**. The raw field is an unpadded integer (e.g. `2052026` = day 2, month 05, year 2026) rather than a normal date string or day-count; `parse_survey_date()` decodes it by digit position instead of letting `pd.to_datetime()` misread it as an epoch timestamp.
- **Converts Stats SA's `inf` "not applicable" sentinel to null** wherever it appears (employment/labour-force/industry codes, hours worked, etc.), rather than letting it leak into the output as a literal infinity.
- Converts data types and casts coded fields to `category`

### 5. Validate (`src/validate.py`)

Runs a battery of checks against the transformed data before it's allowed to load: required columns present, no nulls in critical fields, **no infinite values in any numeric field**, plausible age range (15–120, matching the transform stage's working-age filter), non-negative hours/weight, valid survey dates, and no duplicate respondent records. Raises with a descriptive error on failure rather than loading bad data silently.

### 6. Load (`src/load.py`)

Two outputs:

- A flat CSV snapshot of the processed data (`load_data`), useful for quick inspection without a database connection.
- The validated data loaded into a `staging.qlfs_responses` table in PostgreSQL (`load_to_sql`), with pandas column names mapped to clean, quoting-free SQL column names (`SQL_COLUMN_MAP` in `src/load.py`).

### 7. SQL layer (`sql/`)

Plain SQL, run by `src/db.py` rather than a dedicated tool like dbt — simple enough for this project's scope, and testable against any SQLAlchemy-compatible engine.

- `sql/schema/` — idempotent DDL: creates the `staging` / `reference` / `analytics` schemas, and two small reference tables (`reference.dim_province` using Stats SA's standard province coding, `reference.dim_employment_status`). Safe to re-run; reference tables are truncated and reloaded each time.
- `sql/analytics/` — materializes analytical tables from `staging.qlfs_responses`:
  - `unemployment_rate_by_province.sql` — weighted official unemployment rate by province
  - `neet_summary.sql` — weighted NEET (Not in Education, Employment or Training) share by province and age group
  - `industry_sector_breakdown.sql` — weighted employed population by industry and sector
  - `labour_force_participation.sql` — weighted labour force participation rate by province and gender

  All aggregates use the QLFS survey weight (`survey_weight`), so results estimate population-level rates rather than raw sample counts.

### 8. Analysis

The materialized tables in the `analytics` schema are ready to query directly, or point a BI tool / notebook at the same Postgres database.

## Running the pipeline

```bash
docker compose up --build
```

This starts Postgres (used both as Airflow's metadata database and, as a separate `qlfs` database on the same instance, the analytics warehouse), then Airflow's scheduler and API server. The Airflow UI is available at `http://localhost:8080`; trigger the `qlfs_data_pipeline` DAG to run the full extract → transform → validate → load → analytics flow.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite runs entirely without Docker or a live Postgres server: SQL schema/analytics tests run against an in-memory DuckDB database (`tests/test_sql_integration.py`), since DuckDB understands the same plain SQL used in `sql/`.

## Project structure

```
dags/pipeline.py         Airflow DAG wiring the pipeline stages together
src/extract.py            Reads the raw QLFS CSV
src/transform.py          Cleans, filters and restructures the data
src/validate.py           Data-quality checks before loading
src/load.py                CSV snapshot + Postgres load
src/db.py                  SQLAlchemy engine + .sql file runner
sql/schema/                 Schema and reference table DDL
sql/analytics/              Analytical queries materialized as tables
sql/init/                    Postgres container init script (creates the qlfs database)
tests/                        Unit tests for extract/transform/validate/load + SQL integration tests
data/source/                 Raw QLFS CSV (not committed)
data/raw/, data/processed/  Pipeline working directories
```


