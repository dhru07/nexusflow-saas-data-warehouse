# NexusFlow — B2B SaaS Analytics Data Warehouse

An end-to-end data engineering project that builds an analytics warehouse for a fictional B2B SaaS platform using Python, Google BigQuery, dbt Core, and GitHub Actions.

## Project Overview

NexusFlow simulates a subscription-based SaaS business and transforms raw operational data into analytics-ready dimensional models. The platform supports reporting on recurring revenue, customer growth, subscriptions, payments, and product usage.

## Architecture

```text
Python Synthetic Data Generator
              |
              v
       BigQuery Raw Layer
              |
              v
       dbt Staging Layer
              |
              v
     dbt Intermediate Layer
              |
              v
         dbt Gold Marts
              |
              v
        Looker Studio
```

Additional engineering capabilities include incremental processing, customer history tracking with SCD Type 2, data-quality validation, and query-performance analysis.

## Technology Stack

| Area | Tools |
|---|---|
| Programming | Python, SQL |
| Data Warehouse | Google BigQuery |
| Transformation | dbt Core, dbt-bigquery |
| Data Generation | Python, Faker |
| Data Modeling | Dimensional modeling, facts and dimensions |
| Orchestration / CI | GitHub Actions |
| Visualization | Looker Studio (planned) |

## Data Pipeline

1. Generate synthetic SaaS operational data.
2. Load source records into BigQuery raw tables.
3. Deduplicate and standardize records in dbt staging models.
4. Apply business logic and data-quality handling in intermediate models.
5. Build analytics-ready dimensions and fact tables in the marts layer.
6. Analyze subscription revenue and product usage.
7. Validate data integrity and query performance.

## Engineering Features

- **Layered warehouse:** Raw, staging, intermediate, and marts datasets.
- **Incremental processing:** BigQuery MERGE strategy with a three-day ingestion lookback.
- **Historical tracking:** dbt timestamp-based SCD Type 2 customer snapshot.
- **Data quality:** Uniqueness, null, relationship, financial reconciliation, and custom business-rule tests.
- **Invalid-event handling:** Quarantine models for product events with invalid user references.
- **Performance analysis:** Date partitioning and customer/user clustering analysis.
- **Reproducible synthetic data:** Deterministic generation using a fixed seed.

## Repository Structure

```text
.
├── dbt_warehouse/
│   └── saas_warehouse/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── snapshots/
│       ├── tests/
│       └── macros/
├── docs/
├── images/
├── performance/
├── scripts/
├── src/
│   └── nexusflow/
├── requirements.txt
└── README.md
```

## Validation and Performance

The generated baseline contains 305,108 distinct source records across eight operational entities, after deduplication.

The product-usage mart contains 200,460 records. In the measured BigQuery query comparison, adding a date partition filter reduced bytes processed from 6,146,974 to 237,530 — a 96.13% reduction.

See:
- `docs/data_quality_validation_runbook.md`
- `docs/performance_analysis.md`
- `docs/scd2_customer_snapshot_runbook.md`
- `docs/incremental_processing_runbook.md`

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Authenticate with Google Cloud and configure Application Default Credentials.
5. Configure the dbt profile in `~/.dbt/profiles.yml`.
6. Run dbt commands from `dbt_warehouse/saas_warehouse`.

```bash
dbt debug
dbt parse
```

BigQuery resources and credentials must be configured separately. Do not commit credentials or generated source datasets.

## Project Status

Core ingestion, dbt transformations, SCD Type 2 snapshots, incremental processing, gold marts, custom data-quality tests, and initial performance analysis have been implemented and validated.

GitHub Actions CI/CD and Looker Studio reporting are planned and will be pushed soon.

## Author

Dhruv Singh
