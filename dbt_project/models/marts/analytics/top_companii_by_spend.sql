SELECT
    f.an_raportare,
    c.denumire as companie,
    SUM(f.total_plata) AS total_spend
FROM {{ ref('fact_indemnizatii') }} f
JOIN {{ ref('dim_companii') }} c
    ON f.company_id = c.company_id
GROUP BY 1, 2
ORDER BY total_spend DESC