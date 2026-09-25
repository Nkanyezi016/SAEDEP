-- Weighted employed population by industry and sector (formal/informal/
-- private household), for the employed subset only. Industry/sector codes
-- are left raw (not joined to a label table) since this extract did not
-- ship with the industry/sector code list; join reference.dim_industry
-- here once that lookup is available.
DROP TABLE IF EXISTS analytics.industry_sector_breakdown;

CREATE TABLE analytics.industry_sector_breakdown AS
SELECT
    s.industry_code,
    s.sector_code,
    COUNT(*) AS respondent_count,
    SUM(s.survey_weight) AS employed_weighted
FROM staging.qlfs_responses s
WHERE s.employment_status_code = 1
GROUP BY s.industry_code, s.sector_code
ORDER BY employed_weighted DESC;

