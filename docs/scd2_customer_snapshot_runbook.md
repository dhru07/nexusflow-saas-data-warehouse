# Customer SCD Type 2 Snapshot Runbook

This exercise demonstrates how dbt snapshots preserve historical versions of
customer attributes when the source changes.

## Important: run in two phases

Do not append the update batch before the baseline snapshot. The first snapshot
must capture the original customer state.

## Phase A — baseline snapshot

1. Copy `snap_customers.sql` into:
   `dbt_warehouse/saas_warehouse/snapshots/`
2. From `dbt_warehouse/saas_warehouse/`, run:

   ```bash
   DBT_ENGINE_MANAGE_STATE=0 dbt parse
   DBT_ENGINE_MANAGE_STATE=0 dbt snapshot --select snap_customers
   ```

3. Verify the baseline:

   ```sql
   SELECT
       COUNT(*) AS snapshot_rows,
       COUNT(DISTINCT customer_id) AS distinct_customers,
       COUNTIF(dbt_valid_to IS NULL) AS current_versions
   FROM `data-engineering-course-511511.saas_intermediate.snap_customers`;
   ```

   Expected for the initial baseline: 5,000 rows, 5,000 distinct customers,
   and 5,000 current versions.

## Phase B — create and load updates

Run from the repository root:

```bash
python scripts/generate_customer_updates.py --count 100
```

The script creates:
`data/incremental/batch_002/customers.jsonl`

It updates 100 existing customer IDs and changes industry, customer segment,
employee count, and updated_at. It does not create new customer IDs.

Append those records to the existing raw table:

```bash
python src/nexusflow/load_to_bigquery.py \
  --tables customers \
  --data-dir data/incremental/batch_002 \
  --write-disposition WRITE_APPEND
```

The raw customer table should now contain 5,125 rows (5,025 original rows,
including 25 original duplicates, plus 100 update records). The staging view
should still expose 5,000 distinct customer IDs.

## Phase C — capture changed versions

From `dbt_warehouse/saas_warehouse/`, run:

```bash
DBT_ENGINE_MANAGE_STATE=0 dbt build --select stg_customers
DBT_ENGINE_MANAGE_STATE=0 dbt snapshot --select snap_customers
```

Expected snapshot result after the second snapshot:
- 5,100 snapshot rows
- 5,000 distinct customer IDs
- 5,000 current versions
- 100 historical versions with dbt_valid_to populated
- 100 current versions with a later dbt_valid_from for the changed customers

## Phase D — validate SCD2 history

```sql
SELECT
    COUNT(*) AS snapshot_rows,
    COUNT(DISTINCT customer_id) AS distinct_customers,
    COUNTIF(dbt_valid_to IS NULL) AS current_versions,
    COUNTIF(dbt_valid_to IS NOT NULL) AS historical_versions
FROM `data-engineering-course-511511.saas_intermediate.snap_customers`;
```

Expected after the second snapshot:
- snapshot_rows = 5,100
- distinct_customers = 5,000
- current_versions = 5,000
- historical_versions = 100

Inspect changed customers:

```sql
SELECT
    customer_id,
    company_name,
    industry,
    customer_segment,
    employee_count,
    dbt_valid_from,
    dbt_valid_to
FROM `data-engineering-course-511511.saas_intermediate.snap_customers`
WHERE dbt_valid_to IS NOT NULL
ORDER BY customer_id
LIMIT 20;
```

## Notes and safety

- This is a deterministic simulated source update dated 2026-11-07.
- The script always selects the first N sorted customer IDs. It is designed
  for this controlled demo and should not be treated as a production source
  change generator.
- The generated batch is separate from `data/generated/`; it does not alter
  the original baseline files.
- Do not run Phase B before Phase A. If updates are appended first, the initial
  snapshot will only see the updated values and cannot reconstruct the prior
  state.
- Keep the generated batch local; `data/` is ignored by Git.
- The snapshot uses the timestamp strategy. `updated_at` must advance whenever
  tracked customer attributes change.
- `DBT_ENGINE_MANAGE_STATE=0` is a temporary workaround because dbt-state's
  automatic SSO login interrupted prior commands. It produces a deprecation
  warning in dbt 1.12.6. Do not replace it with `--no-manage-state` unless
  your installed CLI confirms that option exists.
