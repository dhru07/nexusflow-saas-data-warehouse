{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('plans', 'plan_id') }}

)

SELECT
    CAST(plan_id AS STRING) AS plan_id,
    CAST(plan_name AS STRING) AS plan_name,
    CAST(monthly_price AS NUMERIC) AS monthly_price,
    CAST(billing_interval AS STRING) AS billing_interval,
    CAST(max_users AS INT64) AS max_users,
    CAST(is_active AS BOOL) AS is_active,
    CAST(currency AS STRING) AS currency,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated