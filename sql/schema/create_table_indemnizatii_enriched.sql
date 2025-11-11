CREATE TABLE indemnizatii (
    id SERIAL PRIMARY KEY,
    nr_crt INT,
    autoritate_tutelara TEXT,
    intreprindere TEXT,
    cui VARCHAR(20),
    personal TEXT,
    calitate_membru TEXT,
    suma TEXT,
    indemnizatie_variabila TEXT,
    suma_base_num INT,
    suma_extra_num INT,
    suma_total_num INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);