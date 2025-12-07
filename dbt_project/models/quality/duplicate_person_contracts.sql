SELECT
    company_id,
    person_id,
    COUNT(*) AS num_rows
FROM {{ ref('fact_indemnizatii') }}
GROUP BY 1, 2
HAVING COUNT(*) > 1