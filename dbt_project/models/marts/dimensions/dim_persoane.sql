SELECT
    person_id,
    nume_normalizat
FROM {{ ref('int_persoane_clean') }}
WHERE person_id IS NOT NULL