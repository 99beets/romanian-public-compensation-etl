SELECT
    personal,
    intreprindere,
    suma_num,
    indemnizatie_variabila_num,
    suma_num + indemnizatie_variabila_num AS total_compensation
FROM indemnizatii
WHERE calitate_membru ILIKE '%director%'
ORDER BY total_compensation DESC
LIMIT 10;