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


