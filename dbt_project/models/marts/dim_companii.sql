SELECT
    company_id,
    nume_companie AS denumire
FROM {{ ref('int_companii_clean') }}