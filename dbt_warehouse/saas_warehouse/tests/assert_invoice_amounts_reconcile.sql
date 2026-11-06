-- Invoice total should equal subtotal + tax within one cent.
SELECT
    invoice_id,
    subtotal,
    tax,
    total_amount,
    subtotal + tax AS expected_total
FROM {{ ref('fact_invoices') }}
WHERE subtotal IS NULL
   OR tax IS NULL
   OR total_amount IS NULL
   OR ABS(total_amount - (subtotal + tax)) > NUMERIC '0.01'
