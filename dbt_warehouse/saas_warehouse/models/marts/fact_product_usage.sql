{{ config(materialized='table',
    partition_by={"field": "event_date", "data_type": "date", "granularity": "day"},
    cluster_by=['customer_id', 'user_id']) }}
SELECT
    event_id, user_id, customer_id, event_type, feature_name,
    event_timestamp, DATE(event_timestamp) AS event_date, event_properties,
    batch_id, ingested_at
FROM {{ ref('int_product_events_incremental') }}
