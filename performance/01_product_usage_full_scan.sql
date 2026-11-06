-- Baseline: broad scan over the Gold product usage fact.
-- Use this as the comparison query for partition pruning.
SELECT
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS distinct_users
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
GROUP BY event_type
ORDER BY event_count DESC
