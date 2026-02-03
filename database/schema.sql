-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Products/Inventory table (Updated for medicines with batch tracking)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    hsn_code TEXT DEFAULT '30049012',
    unit TEXT DEFAULT 'Nos',
    mrp REAL NOT NULL,
    discount_percent REAL DEFAULT 55.0,
    selling_price REAL NOT NULL,
    purchase_price REAL DEFAULT 0.0,
    gst_rate REAL DEFAULT 12.0,
    current_stock INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    barcode TEXT UNIQUE,
    description TEXT,
    package_size TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Batches table (For tracking batch numbers and expiry dates)
CREATE TABLE IF NOT EXISTS product_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    batch_number TEXT NOT NULL,
    expiry_date TEXT,
    quantity INTEGER DEFAULT 0,
    mrp REAL,
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(product_id, batch_number)
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    pin_code TEXT,
    gstin TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills/Invoices table (Simplified - no separate GST breakdown)
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    customer_address TEXT,
    customer_city TEXT,
    customer_state TEXT,
    customer_pin_code TEXT,
    customer_gstin TEXT,
    subtotal REAL NOT NULL,
    total_discount REAL DEFAULT 0.0,
    round_off REAL DEFAULT 0.0,
    grand_total REAL NOT NULL,
    payment_mode TEXT DEFAULT 'Cash',
    notes TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Bill Items table (Updated with batch, expiry, MRP, discount)
CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    hsn_code TEXT,
    batch_number TEXT,
    expiry_date TEXT,
    quantity INTEGER NOT NULL,
    mrp REAL NOT NULL,
    discount_percent REAL NOT NULL,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Stock History table
CREATE TABLE IF NOT EXISTS stock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    batch_number TEXT,
    change_type TEXT NOT NULL, -- 'SALE', 'PURCHASE', 'ADJUSTMENT', 'RETURN'
    quantity_change INTEGER NOT NULL,
    old_stock INTEGER NOT NULL,
    new_stock INTEGER NOT NULL,
    reference_id INTEGER, -- Bill ID or Purchase ID
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_batches_expiry ON product_batches(expiry_date);
CREATE INDEX IF NOT EXISTS idx_bills_invoice ON bills(invoice_number);
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);

-- Company Settings table
CREATE TABLE IF NOT EXISTS company_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Only one row allowed
    company_name TEXT NOT NULL DEFAULT 'Natural Health World',
    company_tagline TEXT DEFAULT 'The Herbal Healing',
    company_subtitle TEXT DEFAULT 'Manufacturer & Supplier of Ayurvedic Medicine',
    company_certifications TEXT DEFAULT '(An ISO 9001 : 2015) Vegan, Halal & GMP Certified Company',
    office_address TEXT DEFAULT '4, Circus Range, Kolkata - 700 019',
    factory_address TEXT DEFAULT '260A, Rajdanga Nabapally, Kasba, Kolkata - 700107',
    phone TEXT DEFAULT '9143746966, 9836623186',
    email TEXT DEFAULT 'skr.nhw@gmail.com',
    instagram TEXT DEFAULT '@naturalhealthworld_',
    bank_name TEXT DEFAULT 'STATE BANK OF INDIA',
    bank_account_no TEXT DEFAULT '42567178838',
    bank_ifsc TEXT DEFAULT 'SBIN0011534',
    gstin TEXT DEFAULT '',
    state_name TEXT DEFAULT 'West Bengal',
    state_code TEXT DEFAULT '19',
    invoice_prefix TEXT DEFAULT 'NH',
    invoice_note TEXT DEFAULT 'Note - Please make cheques in favor of "NATURAL HEALTH WORLD"',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default company settings
INSERT OR IGNORE INTO company_settings (id, company_name) VALUES (1, 'Natural Health World');


-- Insert default admin user (password: admin123)
-- Password hash generated using bcrypt
INSERT OR IGNORE INTO users (id, username, password_hash, full_name) 
VALUES (1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLhJ632.', 'Administrator');
