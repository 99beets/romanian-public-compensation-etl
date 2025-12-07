SELECT
    c.denumire,
    MAX(f.total_plata) - MIN(f.total_plata) AS spread,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY f.total_plata) AS p90,
    PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY f.total_plata) AS p10
FROM {{ ref('fact_indemnizatii') }} f
JOIN {{ ref('dim_companii') }} c
    ON f.company_id = c.company_id
GROUP BY 1
ORDER BY spread DESC