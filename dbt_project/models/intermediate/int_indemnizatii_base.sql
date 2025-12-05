WITH src AS (
    SELECT
        pk,
        nr_crt,
        autoritate_tutelara,
        intreprindere,
        cui,
        nume,
        functie,
        suma_clean,
        variabila_clean,
        created_at
    FROM {{ ref('stg_indemnizatii_clean') }}
)

SELECT
    pk,
    nr_crt,
    autoritate_tutelara,
    intreprindere,
    cui,
    nume,
    functie,
    COALESCE(suma_clean, 0) AS suma_clean,
    COALESCE(variabila_clean, 0) AS variabila_clean,
    COALESCE(suma_clean, 0) + COALESCE(variabila_clean, 0) AS total_plata,
    created_at
FROM src