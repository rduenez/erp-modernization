-- 1. Customers Table (Entity)
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL, 
    customer_name VARCHAR(150) NOT NULL,
    tax_id VARCHAR(20), -- e.g., RFC in Mexico
    credit_limit DECIMAL(12, 2) DEFAULT 0.00,
    payment_terms VARCHAR(50),
    price_tier VARCHAR(20) DEFAULT 'Standard',
    
    -- Audit & Control Fields
    is_active BOOLEAN DEFAULT TRUE, -- Soft Delete flag
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT 'system',
    modified_date TIMESTAMP,
    modified_by VARCHAR(50)
);

-- 2. Products Table (Entity)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50),
    unit_of_measure VARCHAR(20) DEFAULT 'EA',
    cost_price DECIMAL(10, 2) NOT NULL,
    standard_retail_price DECIMAL(10, 2) NOT NULL,
    minimum_stock_level INT DEFAULT 0,
    
    -- Audit & Control Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    modified_date TIMESTAMP,
    modified_by VARCHAR(50)
);


-- 3. Orders Table (One-to-Many from Customers)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL REFERENCES customers(customer_id), -- Foreign Key
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    required_date TIMESTAMP,
    
    -- State Machine Pattern
    status VARCHAR(20) DEFAULT 'Draft' 
        CHECK (status IN ('Draft', 'Confirmed', 'Shipped', 'Invoiced', 'Cancelled')),
    
    sub_total DECIMAL(12, 2) DEFAULT 0.00,
    tax_amount DECIMAL(12, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) DEFAULT 0.00,
    ship_to_address TEXT,
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);


-- 4. Order Lines Table (Resolves Many-to-Many between Orders and Products)
CREATE TABLE order_lines (
    order_line_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL, -- CRITICAL: Locked at time of order
    discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    line_total DECIMAL(12, 2) GENERATED ALWAYS AS 
	(quantity * unit_price * (1 - (discount_percent / 100))) STORED,
    
    status VARCHAR(20) DEFAULT 'Pending'
);


