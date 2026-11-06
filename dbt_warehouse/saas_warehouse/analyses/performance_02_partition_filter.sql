-- Partition-pruned query: filter the event_date partition column directly.
SELECT
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS distinct_users
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
GROUP BY event_type
ORDER BY event_count DESC
