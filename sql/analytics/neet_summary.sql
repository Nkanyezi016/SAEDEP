-- Weighted NEET ("Not in Education, Employment or Training") share by
-- province and age group. Assumes Stats SA's usual binary flag convention
-- for this extract (1 = Yes/NEET, 2 = No), consistent with the other
-- Yes/No flags in this dataset (e.g. Infempl, Underempl) -- confirm
-- against the release's own codebook if this table will be published.
DROP TABLE IF EXISTS analytics.neet_summary;

CREATE TABLE analytics.neet_summary AS
SELECT
    p.province_name,
    s.age_group,
    SUM(CASE WHEN s.neet_status_code = 1 THEN s.survey_weight ELSE 0 END) AS neet_weighted,
    SUM(s.survey_weight) AS population_weighted,
    ROUND(
        100.0 * SUM(CASE WHEN s.neet_status_code = 1 THEN s.survey_weight ELSE 0 END)
        / NULLIF(SUM(s.survey_weight), 0),
        2
    ) AS neet_rate_pct
FROM staging.qlfs_responses s
JOIN reference.dim_province p ON p.province_code = s.province_code
WHERE s.neet_status_code IS NOT NULL
GROUP BY p.province_name, s.age_group
ORDER BY p.province_name, s.age_group;
