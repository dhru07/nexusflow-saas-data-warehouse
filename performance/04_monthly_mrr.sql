-- Representative BI workload: monthly recurring revenue by currency.
SELECT
    currency,
    SUM(current_mrr) AS current_mrr,
    COUNT(DISTINCT customer_id) AS customers
FROM `data-engineering-course-511511.saas_intermediate.int_monthly_recurring_revenue`
GROUP BY currency
ORDER BY currency
