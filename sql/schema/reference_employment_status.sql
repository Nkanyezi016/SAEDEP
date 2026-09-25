-- Labels for the "Status" (employment_status_code) variable, per Stats
-- SA's published QLFS variable definitions. If a future QLFS release ships
-- with its own codebook, cross-check these labels against it before
-- trusting them for publication-grade analysis.
CREATE TABLE IF NOT EXISTS reference.dim_employment_status (
    employment_status_code INTEGER PRIMARY KEY,
    employment_status_label VARCHAR(50) NOT NULL
);

DELETE FROM reference.dim_employment_status;

INSERT INTO reference.dim_employment_status (employment_status_code, employment_status_label) VALUES
    (1, 'Employed'),
    (2, 'Unemployed (official/strict definition)'),
    (3, 'Discouraged work-seeker'),
    (4, 'Other not economically active');
