WITH src AS (

    SELECT *
    FROM {{ source('indemnizatii_source', 'indemnizatii_clean') }}

),

cleaned AS (

    SELECT
        id AS pk,
        nr_crt,
        autoritate_tutelara,
        intreprindere,
        cui,
        personal AS nume,
        calitate_membru AS functie,
        suma AS suma_raw,
        indemnizatie_variabila AS variabila_raw,
        suma_num AS suma_clean,
        indemnizatie_variabila_num AS variabila_clean,
        created_at

    FROM src

)

SELECT *
FROM cleaned
