{{ config(materialized='table') }}
WITH source_dates AS (
    SELECT DATE(created_at) AS d FROM {{ ref('stg_customers') }}
    UNION ALL SELECT DATE(event_timestamp) FROM {{ ref('int_product_events_incremental') }}
    UNION ALL SELECT invoice_date FROM {{ ref('stg_invoices') }}
    UNION ALL SELECT start_date FROM {{ ref('stg_subscriptions') }}
),
bounds AS (
    SELECT LEAST(MIN(d), DATE '2024-01-01') AS min_date,
           GREATEST(MAX(d), CURRENT_DATE()) AS max_date
    FROM source_dates
),
calendar AS (
    SELECT date_day
    FROM bounds, UNNEST(GENERATE_DATE_ARRAY(min_date, max_date)) AS date_day
)
SELECT
    date_day,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    EXTRACT(MONTH FROM date_day) AS month,
    FORMAT_DATE('%B', date_day) AS month_name,
    EXTRACT(DAY FROM date_day) AS day_of_month,
    EXTRACT(DAYOFWEEK FROM date_day) AS day_of_week,
    FORMAT_DATE('%A', date_day) AS day_name,
    EXTRACT(ISOWEEK FROM date_day) AS iso_week,
    EXTRACT(YEAR FROM date_day) * 100 + EXTRACT(MONTH FROM date_day) AS year_month,
    DATE_TRUNC(date_day, MONTH) AS month_start,
    DATE_TRUNC(date_day, QUARTER) AS quarter_start,
    DATE_TRUNC(date_day, YEAR) AS year_start,
    EXTRACT(DAYOFWEEK FROM date_day) IN (1, 7) AS is_weekend
FROM calendar
