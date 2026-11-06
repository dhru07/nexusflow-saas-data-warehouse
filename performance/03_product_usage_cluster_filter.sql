-- Optimized access pattern: filter by partition and clustered dimensions.
-- Replace customer_id with a real customer_id from the table.
SELECT
    customer_id,
    user_id,
    event_type,
    event_timestamp,
    feature_name
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
  AND customer_id = 'CUST_004944'
LIMIT 1000
