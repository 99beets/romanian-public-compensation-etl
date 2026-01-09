SELECT
    person_id,
    nume_normalizat as nume
FROM {{ ref('int_persoane_clean') }}