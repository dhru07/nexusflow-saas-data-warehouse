-- Baseline: broad scan across the product-usage fact table.
-- Use this as a comparison point, not as a recommended production query.
SELECT
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS distinct_users
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
GROUP BY event_type
ORDER BY event_count DESC
