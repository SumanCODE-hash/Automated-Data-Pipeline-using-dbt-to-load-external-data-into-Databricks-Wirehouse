-- analytics/trends-dbt/models/staging/stg_daily_trends.sql

WITH raw_source AS (
    SELECT * 
    FROM {{ ref('raw_trends') }}
)

SELECT
    country_name,
    term AS search_keyword,
    CAST(rank AS INT) AS search_rank,
    CAST(percent_gain AS INT) AS traffic_percent_gain,
    CAST(snapshot_date AS DATE) AS extraction_date
FROM raw_source
WHERE term IS NOT NULL
