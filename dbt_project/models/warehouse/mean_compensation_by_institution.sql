WITH

source_indemnizatii AS (
    SELECT * FROM {{ ref('stg_indemnizatii') }}
),

mean_compensation_by_institution AS (
    SELECT
        intreprindere,
        autoritate_tutelara,
        ROUND(AVG(suma_total_num), 2) AS mean_total_compensation,
        COUNT(*) AS employee_count
    FROM
        source_indemnizatii
    WHERE
        suma_total_num IS NOT NULL AND suma_total_num > 0
    GROUP BY
        intreprindere, autoritate_tutelara
)

SELECT *
FROM mean_compensation_by_institution
ORDER BY mean_total_compensation DESC