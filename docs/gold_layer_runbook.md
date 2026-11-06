# NexusFlow Gold Layer Runbook

The Gold layer contains analytics-ready dimensions and facts in `saas_marts`.

## Models and grain

- `dim_customers`: one row per SCD Type 2 customer version; use `customer_version_id` as the version key.
- `dim_users`: one row per user.
- `dim_plans`: one row per plan.
- `dim_date`: one row per calendar date.
- `fact_subscriptions`: one row per subscription.
- `fact_invoices`: one row per invoice.
- `fact_payments`: one row per payment attempt; multiple attempts per invoice are expected.
- `fact_product_usage`: one row per valid product event.

## Build

From `dbt_warehouse/saas_warehouse/`:

```bash
DBT_ENGINE_MANAGE_STATE=0 dbt parse
DBT_ENGINE_MANAGE_STATE=0 dbt build --select path:models/marts
```

## Verify SCD2 dimension

```sql
SELECT COUNT(*) AS customer_versions,
       COUNT(DISTINCT customer_id) AS distinct_customers,
       COUNTIF(is_current) AS current_customer_versions
FROM `data-engineering-course-511511.saas_marts.dim_customers`;
```

Expected: 5,100 versions, 5,000 distinct customers, 5,000 current versions.

## Verify fact grains

```sql
SELECT 'subscriptions' AS model, COUNT(*) AS rows, COUNT(DISTINCT subscription_id) AS keys
FROM `data-engineering-course-511511.saas_marts.fact_subscriptions`
UNION ALL
SELECT 'invoices', COUNT(*), COUNT(DISTINCT invoice_id)
FROM `data-engineering-course-511511.saas_marts.fact_invoices`
UNION ALL
SELECT 'payments', COUNT(*), COUNT(DISTINCT payment_id)
FROM `data-engineering-course-511511.saas_marts.fact_payments`
UNION ALL
SELECT 'product_usage', COUNT(*), COUNT(DISTINCT event_id)
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`;
```

Expected current counts: subscriptions 7,000; invoices 30,000; payments 33,103;
product usage 200,460.

## MRR definition

`fact_subscriptions.current_mrr` uses the validated convention that
`monthly_price` is already the monthly-equivalent subscription charge.
It is zero for non-active subscriptions. This is current-state MRR, not
historical month-end MRR.

Do not join invoice and payment facts directly for financial totals: payments
are at payment-attempt grain and multiple attempts can exist per invoice.

For point-in-time customer attributes, join facts to customer versions using
the valid_from/valid_to interval, not customer_id alone.
