SELECT
    f.an_raportare,
    c.denumire AS companie,
    AVG(f.total_plata) AS avg_salary,
    MIN(f.total_plata) AS lowest,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.total_plata) AS median_salary,
    MAX(f.total_plata) AS highest,
    SUM(f.total_plata) AS total_spend,
    COUNT(*) AS num_people
FROM {{ ref('fact_indemnizatii') }} f
JOIN {{ ref('dum_companii') }} c
    ON f.company_id = c.company_id
GROUP BY 1, 2
ORDER BY total_spend DESC