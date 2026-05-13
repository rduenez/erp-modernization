
-- 1. Create the Master Table (Partitioned by Year)
CREATE TABLE transactions (
    id SERIAL,
    amount DECIMAL(10, 2),
    transaction_date DATE NOT NULL
) PARTITION BY RANGE (transaction_date);


-- 2. Create the Physical Partitions
CREATE TABLE transactions_2025 PARTITION OF transactions
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE transactions_2026 PARTITION OF transactions
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- 3. Insert Test Data
INSERT INTO transactions (amount, transaction_date) VALUES 
(500.00, '2025-06-15'),
(1200.00, '2026-04-19');
