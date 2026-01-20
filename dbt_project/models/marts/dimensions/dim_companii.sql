SELECT
    company_id,
    nume_companie AS denumire
FROM {{ ref('int_companii_clean') }}
WHERE company_id IS NOT NULL