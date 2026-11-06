-- Partition + clustering filter: restrict the date partition and customer.
-- Replace the example customer ID with one that exists in your dimension.
SELECT
    customer_id,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS distinct_users
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
  AND customer_id = (
      SELECT customer_id
      FROM `data-engineering-course-511511.saas_marts.dim_customers`
      WHERE is_current = TRUE
      ORDER BY customer_id
      LIMIT 1
  )
GROUP BY customer_id, event_type
ORDER BY event_count DESC
