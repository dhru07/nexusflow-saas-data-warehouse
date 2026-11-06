{{ config(materialized='view') }}

WITH deduplicated AS (

    {{ deduplicate_source('support_tickets', 'ticket_id') }}

)

SELECT
    CAST(ticket_id AS STRING) AS ticket_id,
    CAST(customer_id AS STRING) AS customer_id,
    CAST(user_id AS STRING) AS user_id,

    CAST(subject AS STRING) AS subject,
    CAST(category AS STRING) AS category,
    CAST(priority AS STRING) AS priority,
    CAST(status AS STRING) AS status,

    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(first_response_at AS TIMESTAMP) AS first_response_at,
    CAST(resolved_at AS TIMESTAMP) AS resolved_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at,

    CAST(batch_id AS STRING) AS batch_id,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    CAST(source_updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(record_hash AS STRING) AS record_hash,
    CAST(is_deleted AS BOOL) AS is_deleted

FROM deduplicated