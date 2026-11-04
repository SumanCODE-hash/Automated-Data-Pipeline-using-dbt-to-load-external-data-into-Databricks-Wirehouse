{{
    config(
        materialized='incremental',
        unique_key=['country_name', 'search_keyword', 'extraction_date']
    )
}}  

WITH raw_source AS (
    SELECT
        country_name,
        term AS search_keyword,
        CAST(rank AS INT) AS search_rank,
        CAST(percent_gain AS INT) AS traffic_percent_gain,
        CAST(snapshot_date AS DATE) AS extraction_date
    FROM {{ ref('raw_trends') }}
    WHERE term IS NOT NULL
)

SELECT * FROM raw_source

{% if is_incremental() %}
  -- This macro tells dbt to look at what is already in Databricks 
  -- and only grab rows with dates newer than the max date currently stored.
  WHERE extraction_date > (SELECT MAX(extraction_date) FROM {{ this }})
{% endif %}
