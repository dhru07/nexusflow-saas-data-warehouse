{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='event_id',
        partition_by={
            "field": "event_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by=['customer_id', 'user_id']
    )
}}

SELECT
    event_id,
    user_id,
    customer_id,
    event_type,
    feature_name,
    event_timestamp,
    DATE(event_timestamp) AS event_date,
    event_properties,
    batch_id,
    ingested_at,
    source_updated_at,
    record_hash
FROM {{ ref('int_product_events_valid') }}

{% if is_incremental() %}
WHERE ingested_at >= TIMESTAMP_SUB(
    (SELECT COALESCE(MAX(ingested_at), TIMESTAMP('1970-01-01')) FROM {{ this }}),
    INTERVAL 3 DAY
)
{% endif %}
