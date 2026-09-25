-- Stats SA's standard QLFS province coding (used consistently across its
-- QLFS releases and metadata). Values are fixed and never change, so this
-- table is truncated and reloaded on every pipeline run rather than
-- merged.
CREATE TABLE IF NOT EXISTS reference.dim_province (
    province_code INTEGER PRIMARY KEY,
    province_name VARCHAR(50) NOT NULL
);

DELETE FROM reference.dim_province;

INSERT INTO reference.dim_province (province_code, province_name) VALUES
    (1, 'Western Cape'),
    (2, 'Eastern Cape'),
    (3, 'Northern Cape'),
    (4, 'Free State'),
    (5, 'KwaZulu-Natal'),
    (6, 'North West'),
    (7, 'Gauteng'),
    (8, 'Mpumalanga'),
    (9, 'Limpopo');