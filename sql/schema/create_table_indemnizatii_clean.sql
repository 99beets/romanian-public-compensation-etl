CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.indemnizatii_clean (
    id SERIAL PRIMARY KEY,
    nr_crt INT,
    autoritate_tutelara TEXT,
    intreprindere TEXT,
    cui VARCHAR(20),
    personal TEXT,
    calitate_membru TEXT,
    suma TEXT,
    indemnizatie_variabila TEXT,
    suma_num INT,
    indemnizatie_variabila_num INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);