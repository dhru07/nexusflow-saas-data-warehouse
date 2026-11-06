{{ config(materialized='table', cluster_by=['customer_id']) }}
SELECT
    dbt_scd_id AS customer_version_id,
    customer_id, company_name, industry, country, employee_count,
    customer_segment, created_at, updated_at,
    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,
    dbt_valid_to IS NULL AS is_current
FROM {{ ref('snap_customers') }}
