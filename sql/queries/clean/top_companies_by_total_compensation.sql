SELECT
    intreprindere,
    SUM(suma_num) + SUM(indemnizatie_variabila_num) AS total_spend
FROM indemnizatii
GROUP BY intreprindere
ORDER BY total_spend DESC;