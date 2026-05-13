
-- 1. Enable encryption extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Create the HR table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    encrypted_curp BYTEA -- Stored as encrypted binary data, not text
);

-- 3. Create the Audit Log table
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    action VARCHAR(50),
    changed_by VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create an Audit Trigger Function
CREATE OR REPLACE FUNCTION log_employee_changes() RETURNS TRIGGER AS '
BEGIN
    INSERT INTO audit_log (action, changed_by) 
    VALUES (TG_OP, current_user);
    RETURN NEW;
END;
' LANGUAGE plpgsql;

CREATE TRIGGER employee_audit
AFTER INSERT OR UPDATE OR DELETE ON employees
FOR EACH ROW EXECUTE FUNCTION log_employee_changes();

-- 5. ACCESS CONTROL: Create a restricted user for the Python application
CREATE USER erp_app_user WITH PASSWORD 'app_password123';
GRANT SELECT, INSERT, UPDATE ON employees TO erp_app_user;
GRANT USAGE, SELECT ON SEQUENCE employees_id_seq TO erp_app_user;
-- Notice we DO NOT grant DELETE or DROP permissions to the app user!


-- 6. Insert an employee with encrypted CURP
INSERT INTO employees (name, encrypted_curp) 
VALUES ('Juan Perez', pgp_sym_encrypt('PERJ850101HDFRXX01', 'my_encryption_key'));

-- 7. Query to retrieve and decrypt the CURP for Juan Perez
SELECT name, 
       pgp_sym_decrypt(encrypted_curp::bytea, 'my_encryption_key') AS decrypted_curp
FROM employees 
WHERE name = 'Juan Perez';
