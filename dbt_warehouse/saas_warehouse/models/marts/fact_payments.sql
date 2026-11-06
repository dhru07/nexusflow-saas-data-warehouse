{{ config(materialized='table',
    partition_by={"field": "payment_date", "data_type": "timestamp", "granularity": "month"},
    cluster_by=['invoice_id', 'status']) }}
SELECT
    payment_id, invoice_id, attempt_number, payment_date,
    DATE(payment_date) AS payment_date_day, amount, currency,
    payment_method, status, failure_code, created_at, updated_at
FROM {{ ref('stg_payments') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE
