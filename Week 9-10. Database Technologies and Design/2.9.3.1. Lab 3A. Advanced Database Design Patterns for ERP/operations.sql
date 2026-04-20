INSERT INTO customers (customer_code, customer_name, tax_id, created_by) 
VALUES ('CUST-001', 'Acme Corp', 'XAXX010101000', 'admin');

INSERT INTO products (sku, description, cost_price, standard_retail_price) 
VALUES ('WIDGET-X', 'Premium Widget', 50.00, 150.00);

-- We DO NOT use: DELETE FROM customers WHERE customer_id = 1;
-- We use:
UPDATE customers 
SET is_active = FALSE, modified_date = CURRENT_TIMESTAMP, modified_by = 'compliance_officer' 
WHERE customer_code = 'CUST-001';

-- Create Draft
INSERT INTO orders (order_number, customer_id, status) VALUES ('ORD-10045', 1, 'Draft');

-- Add Line Item (locking in the $150 price)
INSERT INTO order_lines (order_id, product_id, quantity, unit_price) VALUES (1, 1, 10, 150.00);

-- Confirm Order
UPDATE orders SET status = 'Confirmed' WHERE order_number = 'ORD-10045';

