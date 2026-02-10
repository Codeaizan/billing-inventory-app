import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple
from contextlib import contextmanager
from utils.logger import logger
from config import DATABASE_PATH


class DatabaseManager:
    """Manages all database operations with connection pooling and error handling"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.ensure_database_exists()
        # Run migration for batch/expiry columns
        self.add_batch_expiry_columns()
        self.migrate_dual_banking()
        self.migrate_add_igst_column()
    
    def ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Read schema file
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_batch_expiry_columns(self):
        """Add batch_number and expiry_date columns to products table if they don't exist"""
        try:
            with self.get_connection() as conn:
                # Check if columns already exist
                cursor = conn.execute("PRAGMA table_info(products)")
                columns = [row['name'] for row in cursor.fetchall()]
                
                if 'batch_number' not in columns:
                    conn.execute("ALTER TABLE products ADD COLUMN batch_number TEXT")
                    logger.info("Added batch_number column to products table")
                
                if 'expiry_date' not in columns:
                    conn.execute("ALTER TABLE products ADD COLUMN expiry_date TEXT")
                    logger.info("Added expiry_date column to products table")
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding batch/expiry columns: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with WAL mode"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA foreign_keys=ON")  # Enable foreign keys
        
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    # ==================== USER OPERATIONS ====================
    
    def verify_user(self, username: str, password_hash: str) -> Optional[dict]:
        """Verify user credentials"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username=? AND password_hash=?",
                    (username, password_hash)
                )
                user = cursor.fetchone()
                
                if user:
                    # Update last login
                    user_id = user['id']
                    conn.execute(
                        "UPDATE users SET last_login=? WHERE id=?",
                        (datetime.now(), user_id)
                    )
                    conn.commit()
                    return dict(user)
                
                return None
        except Exception as e:
            logger.error(f"Error verifying user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM users WHERE id=?", (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def add_product(self, product_data: dict) -> Optional[int]:
        """Add a new product"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO products (name, category, hsn_code, unit, mrp, discount_percent,
                                         selling_price, purchase_price, gst_rate, current_stock,
                                         min_stock_level, barcode, description, package_size,
                                         batch_number, expiry_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_data['name'],
                    product_data['category'],
                    product_data['hsn_code'],
                    product_data['unit'],
                    product_data['mrp'],
                    product_data['discount_percent'],
                    product_data['selling_price'],
                    product_data.get('purchase_price', 0),
                    product_data.get('gst_rate', 12.0),
                    product_data.get('current_stock', 0),
                    product_data.get('min_stock_level', 10),
                    product_data.get('barcode', ''),
                    product_data.get('description', ''),
                    product_data.get('package_size', ''),
                    product_data.get('batch_number', ''),
                    product_data.get('expiry_date', '')
                ))
                conn.commit()
                logger.info(f"Product added: {product_data['name']}")
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.error(f"Product already exists or invalid data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return None
    
    def update_product(self, product_id: int, product_data: dict) -> bool:
        """Update product details"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE products 
                    SET name=?, category=?, hsn_code=?, unit=?, mrp=?,
                        discount_percent=?, selling_price=?, purchase_price=?, gst_rate=?,
                        min_stock_level=?, barcode=?, description=?, package_size=?,
                        batch_number=?, expiry_date=?, updated_at=?
                    WHERE id=?
                """, (
                    product_data['name'],
                    product_data['category'],
                    product_data['hsn_code'],
                    product_data['unit'],
                    product_data['mrp'],
                    product_data['discount_percent'],
                    product_data['selling_price'],
                    product_data.get('purchase_price', 0),
                    product_data.get('gst_rate', 12.0),
                    product_data.get('min_stock_level', 10),
                    product_data.get('barcode', ''),
                    product_data.get('description', ''),
                    product_data.get('package_size', ''),
                    product_data.get('batch_number', ''),
                    product_data.get('expiry_date', ''),
                    datetime.now(),
                    product_id
                ))
                conn.commit()
                logger.info(f"Product updated: ID {product_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return False
    
    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """Get product by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM products WHERE id=?", (product_id,))
                product = cursor.fetchone()
                return dict(product) if product else None
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None
    
    def search_products(self, search_term: str) -> List[dict]:
        """Search products by name or barcode"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM products 
                    WHERE name LIKE ? OR barcode LIKE ?
                    ORDER BY name
                    LIMIT 50
                """, (f'%{search_term}%', f'%{search_term}%'))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def get_all_products(self, category: Optional[str] = None) -> List[dict]:
        """Get all products, optionally filtered by category"""
        try:
            with self.get_connection() as conn:
                if category:
                    cursor = conn.execute(
                        "SELECT * FROM products WHERE category=? ORDER BY name",
                        (category,)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM products ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM products WHERE id=?", (product_id,))
                conn.commit()
                logger.info(f"Product deleted: ID {product_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False
    
    def update_product_stock(self, product_id: int, new_stock: int, 
                           change_type: str = 'ADJUSTMENT',
                           reference_id: Optional[int] = None,
                           notes: Optional[str] = None) -> bool:
        """Update product stock and log history"""
        try:
            with self.get_connection() as conn:
                # Get current stock
                cursor = conn.execute("SELECT current_stock FROM products WHERE id=?", (product_id,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                old_stock = result['current_stock']
                quantity_change = new_stock - old_stock
                
                # Update stock
                conn.execute("""
                    UPDATE products 
                    SET current_stock=?, updated_at=?
                    WHERE id=?
                """, (new_stock, datetime.now(), product_id))
                
                # Log history
                conn.execute("""
                    INSERT INTO stock_history 
                    (product_id, change_type, quantity_change, old_stock, new_stock, 
                     reference_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (product_id, change_type, quantity_change, old_stock, new_stock,
                      reference_id, notes))
                
                conn.commit()
                logger.info(f"Stock updated for product {product_id}: {old_stock} -> {new_stock}")
                return True
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return False
    
    def get_low_stock_products(self) -> List[dict]:
        """Get products with stock below minimum level"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM products 
                    WHERE current_stock <= min_stock_level
                    ORDER BY current_stock ASC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
            return []
    
    # ==================== CUSTOMER OPERATIONS ====================
    
    def search_customers(self, search_text: str) -> List[dict]:
        """Search customers by name or phone"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM customers 
                    WHERE name LIKE ? OR phone LIKE ?
                    ORDER BY name
                    LIMIT 20
                """, (f'%{search_text}%', f'%{search_text}%'))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return []
    
    def get_customer_by_phone(self, phone: str) -> Optional[dict]:
        """Get customer by phone number"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM customers WHERE phone=?", (phone,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting customer by phone: {e}")
            return None
    
    def add_or_update_customer(self, customer_data: dict) -> Tuple[bool, str, Optional[int]]:
        """Add new customer or update existing one. Returns (success, message, customer_id)"""
        try:
            phone = customer_data.get('phone', '').strip()
            
            # Check if customer exists by phone
            existing_customer = None
            if phone:
                existing_customer = self.get_customer_by_phone(phone)
            
            with self.get_connection() as conn:
                if existing_customer:
                    # Update existing customer
                    conn.execute("""
                        UPDATE customers 
                        SET name=?, email=?, address=?, city=?, state=?, 
                            pin_code=?, gstin=?, updated_at=?
                        WHERE id=?
                    """, (
                        customer_data['name'],
                        customer_data.get('email', ''),
                        customer_data.get('address', ''),
                        customer_data.get('city', ''),
                        customer_data.get('state', ''),
                        customer_data.get('pin_code', ''),
                        customer_data.get('gstin', ''),
                        datetime.now(),
                        existing_customer['id']
                    ))
                    conn.commit()
                    logger.info(f"Customer updated: {customer_data['name']}")
                    return True, "Customer updated", existing_customer['id']
                else:
                    # Add new customer
                    cursor = conn.execute("""
                        INSERT INTO customers (name, phone, email, address, city, state, pin_code, gstin)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        customer_data['name'],
                        customer_data.get('phone', ''),
                        customer_data.get('email', ''),
                        customer_data.get('address', ''),
                        customer_data.get('city', ''),
                        customer_data.get('state', ''),
                        customer_data.get('pin_code', ''),
                        customer_data.get('gstin', '')
                    ))
                    conn.commit()
                    logger.info(f"Customer added: {customer_data['name']}")
                    return True, "Customer added", cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding/updating customer: {e}")
            return False, str(e), None
    
    def get_customer_bills(self, customer_id: int) -> List[dict]:
        """Get all bills for a customer"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM bills 
                    WHERE customer_id=?
                    ORDER BY created_at DESC
                """, (customer_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting customer bills: {e}")
            return []
    
    def add_customer(self, customer_data: dict) -> Optional[int]:
        """Add a new customer"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO customers (name, phone, email, address, city, state, pin_code, gstin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_data['name'],
                    customer_data.get('phone', ''),
                    customer_data.get('email', ''),
                    customer_data.get('address', ''),
                    customer_data.get('city', ''),
                    customer_data.get('state', ''),
                    customer_data.get('pin_code', ''),
                    customer_data.get('gstin', '')
                ))
                conn.commit()
                logger.info(f"Customer added: {customer_data['name']}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding customer: {e}")
            return None
    
    def search_customers(self, search_term: str) -> List[dict]:
        """Search customers by name or phone"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM customers 
                    WHERE name LIKE ? OR phone LIKE ?
                    ORDER BY name
                    LIMIT 50
                """, (f'%{search_term}%', f'%{search_term}%'))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return []
    
    def get_customer_by_id(self, customer_id: int) -> Optional[dict]:
        """Get customer by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
                customer = cursor.fetchone()
                return dict(customer) if customer else None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None
    
    # ==================== BILL OPERATIONS ====================
    
    def generate_invoice_number(self) -> str:
        """Generate next invoice number in format NH/5/25-26"""
        try:
            with self.get_connection() as conn:
                # Get current financial year
                now = datetime.now()
                if now.month >= 4:  # April to March
                    fy_start = now.year
                    fy_end = now.year + 1
                else:
                    fy_start = now.year - 1
                    fy_end = now.year
                
                fy_suffix = f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"
                
                # Get last invoice number for this FY
                cursor = conn.execute("""
                    SELECT invoice_number FROM bills 
                    WHERE invoice_number LIKE ?
                    ORDER BY id DESC LIMIT 1
                """, (f'NH/%/{fy_suffix}',))
                
                last_invoice = cursor.fetchone()
                
                if last_invoice:
                    # Extract number from NH/5/25-26
                    parts = last_invoice['invoice_number'].split('/')
                    last_num = int(parts[1])
                    next_num = last_num + 1
                else:
                    next_num = 1
                
                invoice_number = f"NH/{next_num}/{fy_suffix}"
                logger.info(f"Generated invoice number: {invoice_number}")
                return invoice_number
        except Exception as e:
            logger.error(f"Error generating invoice number: {e}")
            # Fallback to timestamp-based number
            return f"NH/{int(datetime.now().timestamp())}/00-00"
    
    def create_bill(self, bill_data: dict, items: List[dict]) -> Tuple[bool, str, Optional[int]]:
        """Create a new bill with items. Returns (success, message, bill_id)"""
        try:
            with self.get_connection() as conn:
                # Insert bill
                cursor = conn.execute("""
                    INSERT INTO bills (
                        invoice_number,
                        customer_id,
                        customer_name,
                        customer_phone,
                        customer_address,
                        customer_city,
                        customer_pin_code,
                        customer_gstin,
                        sales_person_id,
                        is_gst_bill,
                        subtotal,
                        discount_amount,
                        taxable_amount,
                        cgst_amount,
                        sgst_amount,
                        igst_amount,
                        total_tax,
                        round_off,
                        grand_total,
                        created_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_data['invoice_number'],
                    bill_data.get('customer_id'),
                    bill_data['customer_name'],
                    bill_data.get('customer_phone', ''),
                    bill_data.get('customer_address', ''),
                    bill_data.get('customer_city', ''),
                    bill_data.get('customer_pin_code', ''),
                    bill_data.get('customer_gstin', ''),
                    bill_data['sales_person_id'],
                    bill_data.get('is_gst_bill', 0),
                    bill_data['subtotal'],
                    bill_data.get('discount_amount', 0.0),
                    bill_data.get('taxable_amount', 0.0),
                    bill_data.get('cgst_amount', 0.0),
                    bill_data.get('sgst_amount', 0.0),
                    bill_data.get('igst_amount', 0.0),
                    bill_data.get('total_tax', 0.0),
                    bill_data.get('round_off', 0.0),
                    bill_data['grand_total'],
                    bill_data['created_by']
                ))
                
                bill_id = cursor.lastrowid
                
                # Insert bill items
                for item in items:
                    conn.execute("""
                        INSERT INTO bill_items (
                            bill_id,
                            product_id,
                            product_name,
                            hsn_code,
                            batch_number,
                            expiry_date,
                            quantity,
                            unit,
                            mrp,
                            discount_percent,
                            rate,
                            amount
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        bill_id,
                        item['product_id'],
                        item['product_name'],
                        item.get('hsn_code', ''),
                        item.get('batch_number', ''),
                        item.get('expiry_date', ''),
                        item['quantity'],
                        item.get('unit', 'Nos'),
                        item['mrp'],
                        item.get('discount_percent', 0.0),
                        item['rate'],
                        item['amount']
                    ))
                    
                    # Update product stock
                    conn.execute("""
                        UPDATE products 
                        SET current_stock = current_stock - ?, updated_at=?
                        WHERE id=?
                    """, (item['quantity'], datetime.now(), item['product_id']))
                    
                    # Record stock history
                    conn.execute("""
                        INSERT INTO stock_history (
                            product_id,
                            change_type,
                            quantity_before,
                            quantity_after,
                            quantity_changed,
                            bill_id,
                            notes,
                            created_by
                        )
                        SELECT
                            ?,
                            'SALE',
                            current_stock + ?,
                            current_stock,
                            ?,
                            ?,
                            'Stock reduced due to sale',
                            ?
                        FROM products
                        WHERE id=?
                    """, (
                        item['product_id'],
                        item['quantity'],
                        -item['quantity'],
                        bill_id,
                        bill_data['created_by'],
                        item['product_id']
                    ))
                
                conn.commit()
                logger.info(f"Bill created: {bill_data['invoice_number']}")
                return True, "Bill created successfully", bill_id
        except Exception as e:
            logger.error(f"Error creating bill: {e}")
            return False, str(e), None

    
    def get_last_invoice_number(self, pattern: str) -> Optional[str]:
        """Get last invoice number matching pattern. Pattern example: 'NH/%/25-26'"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT invoice_number FROM bills 
                    WHERE invoice_number LIKE ?
                    ORDER BY id DESC LIMIT 1
                """, (pattern,))
                row = cursor.fetchone()
                return row['invoice_number'] if row else None
        except Exception as e:
            logger.error(f"Error getting last invoice number: {e}")
            return None
    
    def get_bill_by_id(self, bill_id: int) -> Optional[dict]:
        """Get bill by ID with items"""
        try:
            with self.get_connection() as conn:
                # Get bill
                cursor = conn.execute("SELECT * FROM bills WHERE id=?", (bill_id,))
                bill = cursor.fetchone()
                if not bill:
                    return None
                
                bill_dict = dict(bill)
                
                # Get bill items
                cursor = conn.execute("""
                    SELECT * FROM bill_items 
                    WHERE bill_id=?
                    ORDER BY id
                """, (bill_id,))
                bill_dict['items'] = [dict(row) for row in cursor.fetchall()]
                
                return bill_dict
        except Exception as e:
            logger.error(f"Error getting bill: {e}")
            return None
    
    def get_bill_by_invoice_number(self, invoice_number: str) -> Optional[dict]:
        """Get bill by invoice number with items"""
        try:
            with self.get_connection() as conn:
                # Get bill
                cursor = conn.execute(
                    "SELECT * FROM bills WHERE invoice_number=?",
                    (invoice_number,)
                )
                bill = cursor.fetchone()
                if not bill:
                    return None
                
                bill_dict = dict(bill)
                
                # Get bill items
                cursor = conn.execute("""
                    SELECT * FROM bill_items 
                    WHERE bill_id=?
                    ORDER BY id
                """, (bill_dict['id'],))
                bill_dict['items'] = [dict(row) for row in cursor.fetchall()]
                
                return bill_dict
        except Exception as e:
            logger.error(f"Error getting bill by invoice: {e}")
            return None
    
    def search_bills(self, search_term: str = '', start_date: Optional[str] = None,
                    end_date: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Search bills by invoice number or customer name"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM bills WHERE 1=1"
                params = []
                
                if search_term:
                    query += " AND (invoice_number LIKE ? OR customer_name LIKE ?)"
                    params.extend([f'%{search_term}%', f'%{search_term}%'])
                
                if start_date:
                    query += " AND DATE(created_at) >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(created_at) <= ?"
                    params.append(end_date)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching bills: {e}")
            return []
    
    def get_recent_bills(self, limit: int = 50) -> List[dict]:
        """Get recent bills"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM bills 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting recent bills: {e}")
            return []
    
    # ==================== PRODUCT BATCH OPERATIONS ====================
    
    def add_product_batch(self, batch_data: dict) -> Optional[int]:
        """Add a new product batch"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO product_batches (product_id, batch_number, expiry_date, quantity, mrp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    batch_data['product_id'],
                    batch_data['batch_number'],
                    batch_data.get('expiry_date'),
                    batch_data.get('quantity', 0),
                    batch_data.get('mrp')
                ))
                conn.commit()
                logger.info(f"Batch added: {batch_data['batch_number']}")
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.error(f"Batch already exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Error adding batch: {e}")
            return None
    
    def get_product_batches(self, product_id: int) -> List[dict]:
        """Get all batches for a product"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM product_batches 
                    WHERE product_id=? AND quantity > 0
                    ORDER BY expiry_date ASC
                """, (product_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting batches: {e}")
            return []
    
    def get_expiring_batches(self, days: int = 90) -> List[dict]:
        """Get batches expiring within specified days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT pb.*, p.name as product_name
                    FROM product_batches pb
                    JOIN products p ON pb.product_id = p.id
                    WHERE pb.quantity > 0 
                    AND pb.expiry_date <= DATE('now', ? || ' days')
                    ORDER BY pb.expiry_date ASC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting expiring batches: {e}")
            return []
    
    # ==================== REPORTING & ANALYTICS ====================
    
    def get_sales_summary(self, start_date: str, end_date: str) -> dict:
        """Get sales summary for date range"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_bills,
                        COALESCE(SUM(subtotal), 0) as total_sales,
                        COALESCE(SUM(discount_amount), 0) as total_discount,
                        COALESCE(SUM(total_tax), 0) as total_tax,
                        COALESCE(SUM(grand_total), 0) as total_revenue,
                        COALESCE(AVG(grand_total), 0) as avg_bill_value
                    FROM bills
                    WHERE DATE(created_at) BETWEEN ? AND ?
                """, (start_date, end_date))
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return {}
    
    def get_top_selling_products(self, limit: int = 10, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[dict]:
        """Get top selling products"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT 
                        bi.product_id,
                        bi.product_name,
                        SUM(bi.quantity) as total_quantity,
                        SUM(bi.amount) as total_revenue,
                        COUNT(DISTINCT bi.bill_id) as num_bills
                    FROM bill_items bi
                    JOIN bills b ON bi.bill_id = b.id
                    WHERE 1=1
                """
                params = []
                
                if start_date:
                    query += " AND DATE(b.created_at) >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(b.created_at) <= ?"
                    params.append(end_date)
                
                query += """
                    GROUP BY bi.product_id, bi.product_name
                    ORDER BY total_quantity DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    def get_payment_mode_summary(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[dict]:
        """Get payment mode wise summary"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT 
                        payment_mode,
                        COUNT(*) as count,
                        SUM(grand_total) as total_amount
                    FROM bills
                    WHERE 1=1
                """
                params = []
                
                if start_date:
                    query += " AND DATE(created_at) >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(created_at) <= ?"
                    params.append(end_date)
                
                query += " GROUP BY payment_mode ORDER BY total_amount DESC"
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting payment summary: {e}")
            return []
    
    def get_daily_sales(self, days: int = 30) -> List[dict]:
        """Get daily sales for last N days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        DATE(created_at) as sale_date,
                        COUNT(*) as num_bills,
                        SUM(grand_total) as total_sales
                    FROM bills
                    WHERE DATE(created_at) >= DATE('now', '-' || ? || ' days')
                    GROUP BY DATE(created_at)
                    ORDER BY sale_date DESC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting daily sales: {e}")
            return []
    
    def get_inventory_value(self) -> dict:
        """Calculate total inventory value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_products,
                        SUM(current_stock) as total_stock,
                        SUM(current_stock * purchase_price) as purchase_value,
                        SUM(current_stock * selling_price) as selling_value
                    FROM products
                """)
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error getting inventory value: {e}")
            return {}
    
    # ==================== BACKUP OPERATIONS ====================
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            import shutil
            
            # Create backup of current database first
            current_backup = f"{self.db_path}.before_restore"
            shutil.copy2(self.db_path, current_backup)
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Database file size
            db_path = self.db_path
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                stats['db_size_mb'] = round(size_bytes / (1024 * 1024), 2)
            else:
                stats['db_size_mb'] = 0
            
            # Table counts
            with self.get_connection() as conn:
                tables = ['products', 'customers', 'bills', 'bill_items', 'stock_history', 
                         'users', 'salespersons']
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[table] = cursor.fetchone()['count']
            
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    # ==================== SALES PERSON OPERATIONS ====================
    
    def get_all_sales_persons(self, active_only: bool = True) -> List[dict]:
        """Get all sales persons"""
        try:
            with self.get_connection() as conn:
                if active_only:
                    cursor = conn.execute(
                        "SELECT * FROM salespersons WHERE is_active=1 ORDER BY name"
                    )
                else:
                    cursor = conn.execute("SELECT * FROM salespersons ORDER BY name")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting sales persons: {e}")
            return []
    
    def get_sales_person_by_id(self, sales_person_id: int) -> Optional[dict]:
        """Get sales person by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM salespersons WHERE id=?",
                    (sales_person_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting sales person: {e}")
            return None
    
    def add_sales_person(self, name: str, phone: str = '', email: str = '') -> Tuple[bool, str, Optional[int]]:
        """Add new sales person"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO salespersons (name, phone, email)
                    VALUES (?, ?, ?)
                """, (name.strip(), phone.strip(), email.strip()))
                conn.commit()
                logger.info(f"Sales person added: {name}")
                return True, "Sales person added successfully", cursor.lastrowid
        except sqlite3.IntegrityError:
            return False, "Sales person with this name already exists", None
        except Exception as e:
            logger.error(f"Error adding sales person: {e}")
            return False, str(e), None
    
    def update_sales_person(self, sales_person_id: int, name: str, 
                          phone: str = '', email: str = '') -> Tuple[bool, str]:
        """Update sales person"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE salespersons 
                    SET name=?, phone=?, email=?
                    WHERE id=?
                """, (name.strip(), phone.strip(), email.strip(), sales_person_id))
                conn.commit()
                logger.info(f"Sales person updated: {name}")
                return True, "Sales person updated successfully"
        except sqlite3.IntegrityError:
            return False, "Sales person with this name already exists"
        except Exception as e:
            logger.error(f"Error updating sales person: {e}")
            return False, str(e)
    
    def delete_sales_person(self, sales_person_id: int) -> Tuple[bool, str]:
        """Delete/deactivate sales person"""
        try:
            with self.get_connection() as conn:
                # Check if sales person has bills
                cursor = conn.execute(
                    "SELECT COUNT(*) as count FROM bills WHERE sales_person_id=?",
                    (sales_person_id,)
                )
                count = cursor.fetchone()['count']
                
                if count > 0:
                    # Deactivate instead of delete
                    conn.execute(
                        "UPDATE salespersons SET is_active=0 WHERE id=?",
                        (sales_person_id,)
                    )
                    conn.commit()
                    logger.info(f"Sales person deactivated: ID {sales_person_id}")
                    return True, "Sales person deactivated (has existing bills)"
                else:
                    # Safe to delete
                    conn.execute("DELETE FROM salespersons WHERE id=?", (sales_person_id,))
                    conn.commit()
                    logger.info(f"Sales person deleted: ID {sales_person_id}")
                    return True, "Sales person deleted successfully"
        except Exception as e:
            logger.error(f"Error deleting sales person: {e}")
            return False, str(e)
    
    def get_sales_person_performance(self, sales_person_id: int, start_date: str, 
                                    end_date: str) -> dict:
        """Get sales performance for a sales person"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_bills,
                        COALESCE(SUM(grand_total), 0) as total_revenue,
                        COALESCE(AVG(grand_total), 0) as avg_bill_value
                    FROM bills
                    WHERE sales_person_id=? 
                    AND DATE(created_at) BETWEEN ? AND ?
                """, (sales_person_id, start_date, end_date))
                result = cursor.fetchone()
                return dict(result) if result else {
                    'total_bills': 0, 'total_revenue': 0.0, 'avg_bill_value': 0.0
                }
        except Exception as e:
            logger.error(f"Error getting sales person performance: {e}")
            return {'total_bills': 0, 'total_revenue': 0.0, 'avg_bill_value': 0.0}
    
    # ==================== COMPANY SETTINGS OPERATIONS ====================
    
    def get_company_settings(self) -> dict:
        """Get company settings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM company_settings WHERE id=1")
                settings = cursor.fetchone()
                return dict(settings) if settings else {}
        except Exception as e:
            logger.error(f"Error getting company settings: {e}")
            return {}
    
    def update_company_settings(self, settings: dict) -> bool:
        """Update company settings"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE company_settings 
                    SET company_name=?, company_tagline=?, company_subtitle=?,
                        company_certifications=?, office_address=?, factory_address=?,
                        phone=?, email=?, instagram=?, bank_name=?, bank_account_no=?,
                        bank_ifsc=?, gstin=?, state_name=?, state_code=?,
                        invoice_prefix=?, invoice_note=?, updated_at=?
                    WHERE id=1
                """, (
                    settings['company_name'], settings['company_tagline'],
                    settings['company_subtitle'], settings['company_certifications'],
                    settings['office_address'], settings['factory_address'],
                    settings['phone'], settings['email'], settings['instagram'],
                    settings['bank_name'], settings['bank_account_no'],
                    settings['bank_ifsc'], settings['gstin'],
                    settings['state_name'], settings['state_code'],
                    settings['invoice_prefix'], settings['invoice_note'],
                    datetime.now()
                ))
                conn.commit()
                logger.info("Company settings updated successfully")
                return True
        except Exception as e:
            logger.error(f"Error updating company settings: {e}")
            return False
        
    def migrate_dual_banking(self):
        """Migrate to support dual banking (GST and Non-GST)"""
        try:
            with self.get_connection() as conn:
                # Check if columns exist
                cursor = conn.execute("PRAGMA table_info(company_settings)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Add GST banking columns if they don't exist
                if 'gst_bank_name' not in columns:
                    conn.execute("ALTER TABLE company_settings ADD COLUMN gst_bank_name TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN gst_bank_account_no TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN gst_bank_ifsc TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN gst_bank_branch TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN gst_upi_id TEXT DEFAULT ''")
                    
                    # Migrate existing data to GST banking
                    conn.execute("""
                        UPDATE company_settings 
                        SET gst_bank_name = bank_name,
                            gst_bank_account_no = bank_account_no,
                            gst_bank_ifsc = bank_ifsc
                        WHERE gst_bank_name = '' OR gst_bank_name IS NULL
                    """)
                    
                    logger.info("Migrated existing banking data to GST banking")
                
                # Add Non-GST banking columns if they don't exist
                if 'non_gst_bank_name' not in columns:
                    conn.execute("ALTER TABLE company_settings ADD COLUMN non_gst_bank_name TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN non_gst_bank_account_no TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN non_gst_bank_ifsc TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN non_gst_bank_branch TEXT DEFAULT ''")
                    conn.execute("ALTER TABLE company_settings ADD COLUMN non_gst_upi_id TEXT DEFAULT ''")
                    
                    logger.info("Added Non-GST banking columns")
                
                conn.commit()
                logger.info("Dual banking migration completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error in dual banking migration: {e}")
            return False

    def migrate_add_igst_column(self) -> bool:
        """Ensure igst_amount column exists in bills table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("PRAGMA table_info(bills)")
                columns = [row["name"] for row in cursor.fetchall()]

                if "igst_amount" not in columns:
                    conn.execute("ALTER TABLE bills ADD COLUMN igst_amount REAL DEFAULT 0.0")
                    conn.commit()
                    logger.info("Added igst_amount column to bills table")

            return True
        except Exception as e:
            logger.error(f"Error adding igst_amount column: {e}")
            return False



# Create global instance
db = DatabaseManager()
