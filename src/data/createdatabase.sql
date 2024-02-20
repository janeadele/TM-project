
CREATE DATABASE timemanagement;


CREATE TABLE hours (
    id SERIAL PRIMARY KEY,
    startTime TIMESTAMP,
    endTime TIMESTAMP,
    lunchBreakStart TIMESTAMP,
    lunchBreakEnd TIMESTAMP,
    consultantName VARCHAR(255),
    customerName VARCHAR(255)  
);

psql -h timemanagement.postgres.database.azure.com -p 5432 --dbname=timemanagement -U timeuser

pg_restore -U timeuser -h timemanagement.postgres.database.azure.com -d timemanagement -W -v "C:\Skillio\Week 3\TM project\dumpfile.dump"
