{{ config(materialized='table',
    partition_by={"field": "invoice_date", "data_type": "date", "granularity": "month"},
    cluster_by=['subscription_id', 'status']) }}
SELECT
    invoice_id, subscription_id, invoice_number, invoice_date, due_date,
    billing_period_start, billing_period_end, subtotal, tax, total_amount,
    currency, status, created_at, updated_at
FROM {{ ref('stg_invoices') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE
