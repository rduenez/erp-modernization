

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    balance DECIMAL(10, 2)
);
INSERT INTO customers (name, balance) VALUES 
('Acme Corp', 5000.00),
('Tech Solutions', 12000.00);


-- Insert a new customer after the backup
INSERT INTO customers (name, balance) VALUES ('Late Night LLC', 300.00);

-- Delete the customers table to simulate a disaster
DROP TABLE customers;

-- Verify that the customers table has been dropped
SELECT * FROM customers;