# NexusFlow Performance Analysis Runbook

## Objective

Measure the effect of partition pruning and clustering on representative
product-usage analytics. Do not claim a speedup unless BigQuery's measured
bytes processed and execution details support it.

## Table design under test

`saas_marts.fact_product_usage` is configured as:
- Partitioned by `event_date` (daily).
- Clustered by `customer_id` and `user_id`.

Confirm the actual table configuration in BigQuery before interpreting results.

## Step 1 — Confirm table configuration

In BigQuery, open `saas_marts.fact_product_usage` → Details and confirm:
- Partitioning field: `event_date`
- Partition granularity: Day
- Clustering fields: `customer_id`, `user_id`

If the details differ, stop and share a screenshot or the table DDL.

## Step 2 — Dry-run the queries

From the repository root, run each query with the `bq` CLI. Example:

```bash
bq query --project_id=data-engineering-course-511511 \
  --location=asia-south2 --use_legacy_sql=false --dry_run \
  < performance/01_product_usage_full_scan.sql
```

Repeat for:
- `02_product_usage_partition_pruned.sql`
- `03_product_usage_cluster_filter.sql`
- `04_monthly_mrr.sql`

Record the bytes processed shown by each dry run. Dry runs estimate bytes; they do not measure elapsed execution time.

## Step 3 — Execute representative queries

Run the same queries without `--dry_run` and record:
- Bytes processed
- Bytes billed (if shown)
- Slot milliseconds (if shown in job details)
- Elapsed time (informational only; cache and shared capacity can affect it)

For a fair comparison, use the same query text and data snapshot. Run each query more than once if you want to compare elapsed time, and note whether results were served from cache.

## Step 4 — Inspect table storage

Run `05_table_storage_metadata.sql`. This provides row counts and storage size by dataset/table. If the region-qualified `INFORMATION_SCHEMA` view is unavailable in your project, use the BigQuery table Details panel instead and record the limitation.

## Step 5 — Record results

Create a table in `docs/performance_analysis.md` with columns:

| Query | Design | Bytes processed | Bytes billed | Slot ms | Elapsed ms | Cache hit |
|---|---|---:|---:|---:|---:|---|
| Full scan | No date filter | | | | | |
| Partition filter | Date predicate | | | | | |
| Partition + cluster filter | Date and customer filter | | | | | |
| MRR aggregation | Intermediate view | | | | | |

Use actual job details only. Do not invent timings or percentages.

## Interpretation

- Partition pruning should reduce scanned data when the date predicate restricts
  partitions. If the date range covers most of the table, the reduction may be small.
- Clustering can improve block pruning for filters on clustered columns, but
  the effect depends on table size, data distribution, and query selectivity.
- A dry run is not proof of elapsed-time improvement.
- The MRR query reads an intermediate view; inspect its underlying query plan
  and bytes processed before describing its cost.

## Cost safety

BigQuery on-demand query charges are based primarily on bytes processed, subject
to pricing and free-tier details. Check the estimate before executing broad scans.
Avoid repeatedly running full-table scans if the dry-run estimate is unexpectedly high.
