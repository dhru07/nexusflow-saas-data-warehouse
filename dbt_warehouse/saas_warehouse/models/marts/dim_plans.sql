{{ config(materialized='table') }}
SELECT plan_id, plan_name, monthly_price, billing_interval, max_users,
       currency, is_active, created_at, updated_at
FROM {{ ref('stg_plans') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE
