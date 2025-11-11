SELECT
    intreprindere,
    SUM(suma_total_num) AS total_spend
FROM indemnizatii
GROUP BY intreprindere
ORDER BY total_spend DESC;