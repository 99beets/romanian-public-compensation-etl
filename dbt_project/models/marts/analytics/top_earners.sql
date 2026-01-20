SELECT
    f.an_raportare,
    f.person_id,
    p.nume_normalizat as persoana,
    SUM(f.total_plata) AS total_salary
FROM {{ ref('fact_indemnizatii') }} f
JOIN {{ ref('dim_persoane') }} p
    ON f.person_id = p.person_id
GROUP BY 1, 2, 3
ORDER BY total_salary DESC
LIMIT 50
