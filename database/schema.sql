-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);


-- Sales Persons table (FIXED - removed underscore)
CREATE TABLE IF NOT EXISTS salespersons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    phone TEXT,
    email TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Insert default sales person
INSERT OR IGNORE INTO salespersons (id, name) VALUES (1, 'Counter Sale');


-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    hsn_code TEXT DEFAULT '30049012',
    unit TEXT DEFAULT 'Nos',
    package_size TEXT,
    batch_number TEXT,              -- ✅ NEW: Optional batch tracking
    expiry_date TEXT,                -- ✅ NEW: Optional expiry (YYYY-MM-DD)
    mrp REAL NOT NULL,
    discount_percent REAL DEFAULT 55.0,
    selling_price REAL NOT NULL,
    purchase_price REAL DEFAULT 0.0,
    gst_rate REAL DEFAULT 12.0,
    current_stock INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    barcode TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Bills table (UPDATED - Added sales_person_id, is_gst_bill, removed payment_mode)
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    customer_address TEXT,
    customer_city TEXT,
    customer_pin_code TEXT,
    customer_gstin TEXT,
    sales_person_id INTEGER NOT NULL,
    is_gst_bill INTEGER DEFAULT 0,
    subtotal REAL NOT NULL,
    discount_amount REAL DEFAULT 0.0,
    taxable_amount REAL DEFAULT 0.0,
    cgst_amount REAL DEFAULT 0.0,
    sgst_amount REAL DEFAULT 0.0,
    igst_amount REAL DEFAULT 0.0,
    total_tax REAL DEFAULT 0.0,
    round_off REAL DEFAULT 0.0,
    grand_total REAL NOT NULL,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (sales_person_id) REFERENCES salespersons(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);


-- Bill Items table
CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    hsn_code TEXT,
    batch_number TEXT,
    expiry_date TEXT,
    quantity INTEGER NOT NULL,
    unit TEXT,
    mrp REAL NOT NULL,
    discount_percent REAL DEFAULT 0.0,
    rate REAL NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);


-- Stock History table
CREATE TABLE IF NOT EXISTS stock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    change_type TEXT NOT NULL,
    quantity_before INTEGER NOT NULL,
    quantity_after INTEGER NOT NULL,
    quantity_changed INTEGER NOT NULL,
    bill_id INTEGER,
    notes TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);


-- Company Settings table (UPDATED WITH DUAL BANKING + BRANCH + UPI)
CREATE TABLE IF NOT EXISTS company_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    company_name TEXT NOT NULL DEFAULT 'Natural Health World',
    company_tagline TEXT DEFAULT 'The Herbal Healing',
    company_subtitle TEXT DEFAULT 'Manufacturer & Supplier of Ayurvedic Medicine',
    company_certifications TEXT DEFAULT '(An ISO 9001 : 2015) Vegan, Halal & GMP Certified Company',
    office_address TEXT DEFAULT '4, Circus Range, Kolkata - 700 019',
    factory_address TEXT DEFAULT '260A, Rajdanga Nabapally, Kasba, Kolkata - 700107',
    phone TEXT DEFAULT '9143746966, 9836623186',
    email TEXT DEFAULT 'skr.nhw@gmail.com',
    instagram TEXT DEFAULT '@naturalhealthworld_',
    
    -- GST Banking Details
    gst_bank_name TEXT DEFAULT 'STATE BANK OF INDIA',
    gst_bank_account_no TEXT DEFAULT '42567178838',
    gst_bank_ifsc TEXT DEFAULT 'SBIN0011534',
    gst_bank_branch TEXT DEFAULT '',
    gst_upi_id TEXT DEFAULT '',
    
    -- Non-GST Banking Details
    non_gst_bank_name TEXT DEFAULT '',
    non_gst_bank_account_no TEXT DEFAULT '',
    non_gst_bank_ifsc TEXT DEFAULT '',
    non_gst_bank_branch TEXT DEFAULT '',
    non_gst_upi_id TEXT DEFAULT '',
    
    gstin TEXT DEFAULT '',
    state_name TEXT DEFAULT 'West Bengal',
    state_code TEXT DEFAULT '19',
    invoice_prefix TEXT DEFAULT 'NH',
    invoice_note TEXT DEFAULT 'Note - Please make cheques in favor of "NATURAL HEALTH WORLD"',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Insert default company settings
INSERT OR IGNORE INTO company_settings (id, company_name) VALUES (1, 'Natural Health World');


-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_bills_invoice ON bills(invoice_number);
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at);
CREATE INDEX IF NOT EXISTS idx_bills_sales_person ON bills(sales_person_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);
CREATE INDEX IF NOT EXISTS idx_stock_history_product ON stock_history(product_id);


-- Insert default admin user (password: admin123)
INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) 
VALUES (1, 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ufWJ7OyqG.Ry', 'Administrator', 'admin');

