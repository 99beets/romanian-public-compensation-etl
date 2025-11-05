SELECT
    intreprindere
    AVG(suma_num) AS avg_monthly_compensation
FROM indemnizatii
WHERE calitate ILIKE '%membru%'
GROUP BY intreprindere
ORDER BY avg_monthly_compensation DESC;