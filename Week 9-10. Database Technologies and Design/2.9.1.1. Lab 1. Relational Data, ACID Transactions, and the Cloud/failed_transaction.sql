BEGIN;
INSERT INTO sales (product_id, quantity) VALUES (1, 100);
-- This will fail because our schema has a CHECK (stock_level >= 0) constraint
UPDATE inventory 
SET stock_level = stock_level - 100 
WHERE product_id = 1; 
-- Because the step above fails, the database is in an error state. 
-- We must undo the entire process.
ROLLBACK;
