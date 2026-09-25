-- Weighted labour force participation rate by province and gender:
--   (employed + unemployed) / working-age population.
DROP TABLE IF EXISTS analytics.labour_force_participation;

CREATE TABLE analytics.labour_force_participation AS
SELECT
    p.province_name,
    s.gender_code,
    SUM(CASE WHEN s.employment_status_code IN (1, 2) THEN s.survey_weight ELSE 0 END) AS labour_force_weighted,
    SUM(s.survey_weight) AS working_age_population_weighted,
    ROUND(
        100.0 * SUM(CASE WHEN s.employment_status_code IN (1, 2) THEN s.survey_weight ELSE 0 END)
        / NULLIF(SUM(s.survey_weight), 0),
        2
    ) AS labour_force_participation_rate_pct
FROM staging.qlfs_responses s
JOIN reference.dim_province p ON p.province_code = s.province_code
GROUP BY p.province_name, s.gender_code
ORDER BY p.province_name, s.gender_code;
