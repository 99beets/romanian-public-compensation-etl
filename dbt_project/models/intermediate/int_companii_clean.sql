WITH src AS (
    SELECT DISTINCT
        cui,
        intreprindere
    FROM {{ ref('stg_indemnizatii_clean') }}
)

SELECT
    cui AS company_id,
    trim(upper(intreprindere)) AS nume_companie
FROM src