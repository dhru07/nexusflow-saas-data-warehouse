{{ config(materialized='view') }}

-- Keep only events whose user and customer references resolve and agree.
-- Invalid events remain available in the quarantine model for investigation.
SELECT
    e.event_id,
    e.user_id,
    e.customer_id,
    e.event_type,
    e.feature_name,
    e.event_timestamp,
    e.event_properties,
    e.batch_id,
    e.ingested_at,
    e.source_updated_at,
    e.record_hash
FROM {{ ref('stg_product_events') }} AS e
INNER JOIN {{ ref('stg_users') }} AS u
    ON e.user_id = u.user_id
   AND e.customer_id = u.customer_id
WHERE COALESCE(e.is_deleted, FALSE) = FALSE
