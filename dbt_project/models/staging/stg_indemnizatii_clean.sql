with source as (

    select *
    from {{ source('indemnizatii_source', 'indemnizatii_clean') }}

),

cleaned as (

    select
        -- Use actual physical primary key
        id as pk,

        nr_crt,
        autoritate_tutelara,
        intreprindere,
        cui,

        -- Rename ambiguous columns
        personal as nume,
        calitate_membru as functie,

        -- Keep raw text values
        suma as suma_raw,
        indemnizatie_variabila as variabila_raw,

        -- Clean numeric values provided by ETL
        suma_num as suma_clean,
        indemnizatie_variabila_num as variabila_clean,

        created_at

    from source

)

select *
from cleaned
