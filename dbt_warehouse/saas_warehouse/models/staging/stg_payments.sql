{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('payments', 'payment_id') }}

)

SELECT
    CAST(payment_id AS STRING) AS payment_id,
    CAST(invoice_id AS STRING) AS invoice_id,
    CAST(attempt_number AS INT64) AS attempt_number,

    CAST(payment_date AS TIMESTAMP) AS payment_date,
    CAST(amount AS NUMERIC) AS amount,

    CAST(currency AS STRING) AS currency,
    CAST(payment_method AS STRING) AS payment_method,
    CAST(status AS STRING) AS status,
    CAST(failure_code AS STRING) AS failure_code,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated