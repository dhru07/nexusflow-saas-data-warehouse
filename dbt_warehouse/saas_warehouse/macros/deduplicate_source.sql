{% macro deduplicate_source(source_table, primary_key) %}

    SELECT *
    FROM {{ source('saas_raw', source_table) }}

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY {{ primary_key }}
        ORDER BY
            ingested_at DESC,
            source_updated_at DESC,
            batch_id DESC
    ) = 1

{% endmacro %}