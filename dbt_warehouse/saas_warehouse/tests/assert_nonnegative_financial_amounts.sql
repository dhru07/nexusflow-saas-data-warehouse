-- Financial amounts should not be negative.
SELECT 'invoice' AS record_type, invoice_id AS record_id, total_amount AS amount
FROM {{ ref('fact_invoices') }}
WHERE total_amount < 0

UNION ALL

SELECT 'payment', payment_id, amount
FROM {{ ref('fact_payments') }}
WHERE amount < 0

UNION ALL

SELECT 'subscription_mrr', subscription_id, current_mrr
FROM {{ ref('fact_subscriptions') }}
WHERE current_mrr < 0
