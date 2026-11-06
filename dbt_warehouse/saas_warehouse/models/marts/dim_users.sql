{{ config(materialized='table', cluster_by=['customer_id']) }}
SELECT user_id, customer_id, email, full_name, role, is_active,
       created_at, updated_at
FROM {{ ref('stg_users') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE
