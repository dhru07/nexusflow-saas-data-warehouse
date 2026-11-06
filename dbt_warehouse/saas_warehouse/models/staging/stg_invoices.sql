{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('invoices', 'invoice_id') }}

)

SELECT
    CAST(invoice_id AS STRING) AS invoice_id,
    CAST(subscription_id AS STRING) AS subscription_id,
    CAST(invoice_number AS STRING) AS invoice_number,

    CAST(invoice_date AS DATE) AS invoice_date,
    CAST(due_date AS DATE) AS due_date,
    CAST(billing_period_start AS DATE) AS billing_period_start,
    CAST(billing_period_end AS DATE) AS billing_period_end,

    CAST(subtotal AS NUMERIC) AS subtotal,
    CAST(tax AS NUMERIC) AS tax,
    CAST(total_amount AS NUMERIC) AS total_amount,

    CAST(currency AS STRING) AS currency,
    CAST(status AS STRING) AS status,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated