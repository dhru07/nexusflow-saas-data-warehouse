-- A customer version must have a valid interval.
-- Adjacent versions may share a boundary; overlapping intervals are invalid.
WITH versions AS (
    SELECT
        customer_id,
        customer_version_id,
        valid_from,
        valid_to,
        LEAD(valid_from) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_version_id
        ) AS next_valid_from
    FROM {{ ref('dim_customers') }}
)
SELECT *
FROM versions
WHERE valid_to IS NOT NULL
  AND valid_to < valid_from

UNION ALL

SELECT *
FROM versions
WHERE valid_to IS NOT NULL
  AND next_valid_from IS NOT NULL
  AND valid_to > next_valid_from
