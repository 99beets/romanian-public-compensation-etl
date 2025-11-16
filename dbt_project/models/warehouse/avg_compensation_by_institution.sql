WITH 

source_indemnizatii AS (
    SELECT * FROM {{ ref('stg_indemnizatii') }}
),

avg_compensation_by_institution AS (
    SELECT
        autoritate_tutelara,
        ROUND(AVG(suma_total_num), 2) AS avg_total_compensation
    FROM
        source_indemnizatii
    GROUP BY
        autoritate_tutelara
)

SELECT * FROM avg_compensation_by_institution

ORDER BY
    avg_total_compensation DESC