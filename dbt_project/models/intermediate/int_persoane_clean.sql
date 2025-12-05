WITH src AS (
    SELECT DISTINCT
        nume
    FROM {{ ref('stg_indemnizatii_clean') }}
)

SELECT
    md5(trim(upper(nume))) AS person_id,
    trim(upper(nume)) AS nume_normalizat
FROM src