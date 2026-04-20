-- 1. Create the Accounts Table (Financials)
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);

-- 2. Create the Inventory Table (Products)
CREATE TABLE inventory (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    stock_level INT NOT NULL CHECK (stock_level >= 0),
    price DECIMAL(10, 2) NOT NULL
);

-- 3. Create the Sales Table (Orders - Relies on Inventory)
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES inventory(product_id),
    quantity INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO accounts (account_name, balance) VALUES ('Main Revenue Account', 10000.00);
INSERT INTO inventory (sku, name, stock_level, price) VALUES ('WIDGET-01', 'Industrial Widget', 50, 200.00);

CREATE INDEX idx_inventory_sku ON inventory(sku);

