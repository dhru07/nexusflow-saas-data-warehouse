{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('product_events', 'event_id') }}

)

SELECT
    CAST(event_id AS STRING) AS event_id,
    CAST(user_id AS STRING) AS user_id,
    CAST(customer_id AS STRING) AS customer_id,

    CAST(event_type AS STRING) AS event_type,
    CAST(feature_name AS STRING) AS feature_name,

    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,

    event_properties,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated