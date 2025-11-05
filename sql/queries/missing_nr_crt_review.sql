SELECT *
FROM indemnizatii
WHERE nr_crt IS NULL OR nr_crt = '' OR nr_crt = '0';