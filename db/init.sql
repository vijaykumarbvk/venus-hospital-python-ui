-- ---------------------------------------------------------------------
-- Venus Hospital — database bootstrap
--
-- Run ONCE against RDS from the bastion, before deploying the services:
--   mysql -h <rds-endpoint> -u admin -p < db/init.sql
--
-- This only creates the empty schemas. Each Flask service calls
-- SQLAlchemy's create_all() at startup and builds its own tables, so
-- there is no DDL here to drift out of sync with the models.
-- ---------------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS venus_user_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS venus_doctor_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS venus_patient_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS venus_appointment_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SHOW DATABASES LIKE 'venus%';
