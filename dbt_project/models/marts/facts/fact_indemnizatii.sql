WITH b AS (
    SELECT *
    FROM {{ ref('int_indemnizatii_base') }}
),

p AS (
    SELECT *
    FROM {{ ref('int_persoane_clean') }}
),

c AS (
    SELECT *
    FROM {{ ref('int_companii_clean') }}
)

SELECT
    b.pk,
    p.person_id,
    c.company_id,
    b.total_plata,
    b.suma_clean,
    b.variabila_clean,

    {{ var('indemnizatii_year') }} AS an_raportare
FROM b
LEFT JOIN p
    ON trim(upper(p.nume_normalizat)) = trim(upper(b.nume))
LEFT JOIN c
    ON c.company_id = b.cui