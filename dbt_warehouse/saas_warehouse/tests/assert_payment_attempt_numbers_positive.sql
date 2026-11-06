SELECT
    payment_id,
    invoice_id,
    attempt_number
FROM {{ ref('fact_payments') }}
WHERE attempt_number IS NULL
   OR attempt_number < 1
