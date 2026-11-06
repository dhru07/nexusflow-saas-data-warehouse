{{ config(materialized='view') }}

-- One row per customer and calendar date with basic product engagement.
-- Keep event-type analysis generic until the source event taxonomy is finalized.
SELECT
    customer_id,
    DATE(event_timestamp) AS activity_date,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS active_users,
    COUNT(DISTINCT feature_name) AS distinct_features_used,
    COUNT(DISTINCT event_type) AS distinct_event_types
FROM {{ ref('int_product_events_valid') }}
GROUP BY
    customer_id,
    activity_date
