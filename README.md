# SAEDEP — South African Employment Data Engineering Pipeline
 
SAEDEP (South African Employment Data Engineering Pipeline) is an end-to-end data engineering project focused on processing and analysing South African labour-market data.
 
The project uses the **Quarterly Labour Force Survey (QLFS)** published by Statistics South Africa to build a reproducible pipeline that transforms raw survey data into clean, validated and structured analytical data.
 
The pipeline covers the complete journey from raw source data to analytical tables that can be used to investigate employment, unemployment, demographics, education, provinces, industries and labour-market trends in South Africa.
 
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
                    │     dbt      │
                    │  SQL Models  │
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
 
The raw source data is kept separate from the processed data so that the original dataset remains unchanged.
 
### 2. Orchestration
 
Apache Airflow manages and orchestrates the pipeline.
 
Instead of manually running each stage, Airflow controls the order in which the different pipeline tasks execute and manages their dependencies.
 
The pipeline follows:
 
```
Extract → Transform → Validate → Load → dbt
```
 
### 3. Extract
 
The Extract stage uses Python to read and prepare the raw QLFS source data for processing.
 
The extraction process makes the source data available to the transformation stage without modifying the original source.
 
### 4. Transform
 
The Transform stage uses Python and Pandas to clean and restructure the raw QLFS data.
 
The transformation process includes:
 
- Selecting relevant columns
- Removing unnecessary fields
- Cleaning values
- Handling missing data
- Standardising data types
- Preparing the dataset for storage
- Creating derived fields where required
The goal is to convert the raw survey data into a consistent structure suitable for downstream processing.
