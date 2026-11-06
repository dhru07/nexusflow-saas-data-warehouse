-- Period end must not precede period start.
SELECT
    subscription_id,
    start_date,
    current_period_start,
    current_period_end
FROM {{ ref('fact_subscriptions') }}
WHERE current_period_start < start_date
   OR current_period_end < current_period_start
