{% snapshot snap_customers %}

{{
    config(
        target_schema='saas_intermediate',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

SELECT
    customer_id,
    company_name,
    industry,
    country,
    employee_count,
    customer_segment,
    created_at,
    updated_at
FROM {{ ref('stg_customers') }}
WHERE COALESCE(is_deleted, FALSE) = FALSE

{% endsnapshot %}
