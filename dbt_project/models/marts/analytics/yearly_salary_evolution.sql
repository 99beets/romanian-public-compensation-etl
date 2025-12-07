SELECT
    c.denumire AS companie,
    f.an_raportare,
    SUM(total_plata) AS total_spend,
    AVG(total_plata) AS avg_salary,
    COUNT(*) AS num_people
FROM {{ ref('fact_indemnizatii') }} f
JOIN {{ ref('dim_companii')}} c
    ON f.company_id = c.company_id
GROUP BY 1, 2
ORDER BY companie, an_raportare DESC