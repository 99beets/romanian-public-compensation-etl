SELECT
    personal,
    autoritate_tutelara,
    intreprindere,
    suma_total_num AS total_compensation
FROM indemnizatii
ORDER BY total_compensation DESC;