{{ config(materialized='view') }}

-- Current subscription-level MRR.
-- monthly_price is treated as the monthly-equivalent
-- subscription charge, not a per-seat price.

SELECT
    s.subscription_id,
    s.customer_id,
    s.plan_id,
    s.status,
    s.start_date,
    s.current_period_start,
    s.current_period_end,
    s.quantity,
    s.currency,
    s.monthly_price,

    s.monthly_price AS monthly_recurring_revenue

FROM {{ ref('stg_subscriptions') }} AS s

WHERE LOWER(s.status) = 'active'
  AND COALESCE(s.is_deleted, FALSE) = FALSE