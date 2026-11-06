{{ config(materialized='table', cluster_by=['customer_id', 'plan_id']) }}
SELECT
    subscription_id, customer_id, plan_id, status, start_date, trial_end_date,
    current_period_start, current_period_end, cancel_at_period_end, canceled_at,
    quantity, currency, monthly_price,
    CASE WHEN LOWER(status) = 'active' THEN monthly_price ELSE NUMERIC '0' END AS current_mrr,
    created_at, updated_at
FROM {{ ref('stg_subscriptions') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE
