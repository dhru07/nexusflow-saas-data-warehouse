{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('subscriptions', 'subscription_id') }}

)

SELECT
    CAST(subscription_id AS STRING) AS subscription_id,
    CAST(customer_id AS STRING) AS customer_id,
    CAST(plan_id AS STRING) AS plan_id,
    CAST(status AS STRING) AS status,

    CAST(start_date AS DATE) AS start_date,
    CAST(trial_end_date AS DATE) AS trial_end_date,
    CAST(current_period_start AS DATE) AS current_period_start,
    CAST(current_period_end AS DATE) AS current_period_end,

    CAST(cancel_at_period_end AS BOOL) AS cancel_at_period_end,
    CAST(canceled_at AS TIMESTAMP) AS canceled_at,

    CAST(quantity AS INT64) AS quantity,
    CAST(monthly_price AS NUMERIC) AS monthly_price,
    CAST(currency AS STRING) AS currency,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated