{{ config(materialized='view') }}

-- Preserve invalid event rows rather than silently dropping them.
-- Reasons distinguish missing users from mismatched user/customer ownership.
SELECT
    e.event_id,
    e.user_id,
    e.customer_id,
    e.event_type,
    e.feature_name,
    e.event_timestamp,
    e.event_properties,
    CASE
        WHEN u.user_id IS NULL THEN 'unknown_user_id'
        WHEN u.customer_id != e.customer_id THEN 'user_customer_mismatch'
        ELSE 'other_validation_failure'
    END AS quarantine_reason,
    e.batch_id,
    e.ingested_at,
    e.source_updated_at,
    e.record_hash
FROM {{ ref('stg_product_events') }} AS e
LEFT JOIN {{ ref('stg_users') }} AS u
    ON e.user_id = u.user_id
WHERE COALESCE(e.is_deleted, FALSE) = FALSE
  AND (
      u.user_id IS NULL
      OR u.customer_id != e.customer_id
  )
