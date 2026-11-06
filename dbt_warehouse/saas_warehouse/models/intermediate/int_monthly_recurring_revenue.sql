{{ config(materialized='view') }}

-- Current MRR by customer and currency.
-- This is a current-state snapshot, not a historical month-end MRR series.
SELECT
    customer_id,
    currency,
    SUM(monthly_recurring_revenue) AS current_mrr,
    COUNT(DISTINCT subscription_id) AS active_subscription_count
FROM {{ ref('int_subscription_mrr') }}
GROUP BY
    customer_id,
    currency
