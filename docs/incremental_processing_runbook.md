# Incremental Product Events Runbook

This milestone demonstrates a dbt incremental model on BigQuery using MERGE,
a stable event ID, event-date partitioning, customer/user clustering, and an
ingestion-time lookback for late-arriving events.

## 1. Add the files

- Copy `scripts/generate_incremental_events.py` to the repository's `scripts/`.
- Copy `int_product_events_incremental.sql` and `_incremental_models.yml` to
  `dbt_warehouse/saas_warehouse/models/intermediate/`.

## 2. Build the initial incremental table

From `dbt_warehouse/saas_warehouse/`:

```bash
DBT_ENGINE_MANAGE_STATE=0 dbt parse
DBT_ENGINE_MANAGE_STATE=0 dbt build --select int_product_events_incremental
```

The first run creates the table from all valid staged events. Expected baseline:
199,960 rows.

Verify:

```sql
SELECT
    COUNT(*) AS rows,
    COUNT(DISTINCT event_id) AS distinct_events,
    MIN(event_timestamp) AS earliest_event,
    MAX(event_timestamp) AS latest_event,
    MAX(ingested_at) AS latest_ingestion
FROM `data-engineering-course-511511.saas_intermediate.int_product_events_incremental`;
```

## 3. Generate a late-arriving batch

From the repository root:

```bash
python scripts/generate_incremental_events.py --count 500 --late-days 14
```

This creates:
`data/incremental/batch_003/product_events.jsonl`

These are 500 new valid event IDs. Their event timestamps are up to 14 days old,
but their ingestion timestamps are current. This deliberately tests why
incremental processing should use ingestion time for arrival detection rather
than only filtering on event_timestamp.

## 4. Append the batch to BigQuery

From the repository root:

```bash
python src/nexusflow/load_to_bigquery.py \
  --tables product_events \
  --data-dir data/incremental/batch_003 \
  --write-disposition WRITE_APPEND
```

## 5. Rebuild the incremental model

From `dbt_warehouse/saas_warehouse/`:

```bash
DBT_ENGINE_MANAGE_STATE=0 dbt build --select int_product_events_incremental
```

Expected after the incremental run:
- 200,460 rows
- 200,460 distinct event IDs
- 500 new records have event timestamps older than their ingestion timestamps
- original events remain present

## 6. Verify the late-arriving records

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT event_id) AS distinct_event_ids,
    COUNTIF(batch_id = 'batch_003') AS batch_003_rows,
    COUNTIF(
        batch_id = 'batch_003'
        AND event_timestamp < TIMESTAMP_SUB(ingested_at, INTERVAL 1 DAY)
    ) AS late_arriving_rows
FROM `data-engineering-course-511511.saas_intermediate.int_product_events_incremental`;
```

Expected:
- total_rows = 200,460
- distinct_event_ids = 200,460
- batch_003_rows = 500
- late_arriving_rows = 500

## Design notes

- `unique_key='event_id'` lets dbt MERGE update existing IDs instead of blindly
  inserting duplicate copies.
- `ingested_at` detects when data arrived in the warehouse. `event_timestamp`
  describes when the business event actually happened. These are different.
- The three-day lookback provides a small overlap window for ingestion-time
  watermark safety. It does not mean the event itself must be recent.
- This is a controlled demo, not a complete production CDC solution. A
  production design should persist an explicit ingestion watermark/checkpoint,
  handle deletes, and consider source replay and backfill policies.
- The `int_product_events_valid` upstream view filters invalid user/customer
  references and soft-deleted rows.
