SELECT te.person_id
FROM {{ ref('top_earners') }} te
LEFT JOIN {{ ref('dim_persoane') }} dp
    ON te.person_id = dp.person_id
WHERE dp.person_id IS NULL