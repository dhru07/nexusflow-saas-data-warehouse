# NexusFlow Data Quality Validation Runbook

These are singular dbt tests. A passing test returns zero failing rows.

## Included business checks

1. Invoice reconciliation: `total_amount` should equal `subtotal + tax`
   within one cent.
2. Nonnegative financial values: invoice totals, payment amounts, and current
   subscription MRR must not be negative.
3. Subscription periods: current period must not precede subscription start,
   and period end must not precede period start.
4. Payment attempts: attempt_number must be a positive integer.
5. SCD Type 2 validity: version intervals must not be reversed or overlap.

## Run

From `dbt_warehouse/saas_warehouse/`:

```bash
DBT_ENGINE_MANAGE_STATE=0 dbt parse
DBT_ENGINE_MANAGE_STATE=0 dbt test --select assert_invoice_amounts_reconcile assert_nonnegative_financial_amounts assert_subscription_periods_valid assert_payment_attempt_numbers_positive assert_customer_scd2_intervals_valid
```

Do not disable a test if it fails. Inspect the returned rows and decide whether
the source data, transformation, or business assumption needs correction.

## Important interpretation

- Invoice reconciliation assumes the generator defines total_amount as
  subtotal + tax. If discounts or credits exist in the model, extend the
  expression to include them rather than weakening the test.
- Payment attempts may be multiple per invoice. Do not compare the sum of all
  payment attempts to invoice totals: failed/retried attempts can inflate that
  sum.
- This test pack does not claim payment success rate, churn, or revenue
  recognition is fully reconciled. Those require explicit business definitions.
- SCD2 interval validation permits adjacent validity boundaries and checks
  that a historical version does not overlap its next version.
