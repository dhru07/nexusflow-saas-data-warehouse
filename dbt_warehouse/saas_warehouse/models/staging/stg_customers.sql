{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('customers', 'customer_id') }}

)

SELECT
    CAST(customer_id AS STRING) AS customer_id,
    CAST(company_name AS STRING) AS company_name,
    CAST(industry AS STRING) AS industry,
    CAST(country AS STRING) AS country,
    CAST(employee_count AS INT64) AS employee_count,
    CAST(customer_segment AS STRING) AS customer_segment,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated