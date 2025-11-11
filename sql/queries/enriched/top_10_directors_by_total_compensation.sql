SELECT
    personal,
    intreprindere,
    suma_total_num AS total_compensation
FROM indemnizatii
WHERE calitate_membru ILIKE '%director%'
ORDER BY total_compensation DESC
LIMIT 10;