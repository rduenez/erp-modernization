BEGIN; -- Starts the transaction

-- Step 1: Record the sale
INSERT INTO sales (product_id, quantity) VALUES (1, 5);

-- Step 2: Deduct from inventory
UPDATE inventory 
SET stock_level = stock_level - 5 
WHERE product_id = 1;

-- Step 3: Credit the accounting ledger
UPDATE accounts 
SET balance = balance + 1000.00 
WHERE account_id = 1;

COMMIT; -- Saves all changes permanently
