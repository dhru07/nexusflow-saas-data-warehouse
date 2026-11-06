{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('users', 'user_id') }}

)

SELECT
    CAST(user_id AS STRING) AS user_id,
    CAST(customer_id AS STRING) AS customer_id,
    CAST(email AS STRING) AS email,
    CAST(full_name AS STRING) AS full_name,
    CAST(role AS STRING) AS role,
    CAST(is_active AS BOOL) AS is_active,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated