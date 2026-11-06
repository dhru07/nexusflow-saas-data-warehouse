-- Table-level storage and row metadata.
-- Run in BigQuery with region qualifier matching the dataset location.
SELECT
    table_schema,
    table_name,
    row_count,
    size_bytes,
    ROUND(size_bytes / POW(1024, 2), 2) AS size_mb,
    creation_time
FROM `data-engineering-course-511511.region-asia-south2.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_schema IN ('saas_raw', 'saas_staging', 'saas_intermediate', 'saas_marts')
ORDER BY size_bytes DESC
