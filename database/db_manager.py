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
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
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
    
    # ============= USER OPERATIONS =============
    
    def verify_user(self, username: str, password_hash: str) -> Optional[dict]:
        """Verify user credentials"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                    (username, password_hash)
                )
                user = cursor.fetchone()
                
                if user:
                    # Update last login
                    conn.execute(
                        "UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now(), user['id'])
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
                cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    # ============= PRODUCT OPERATIONS =============
    
    def add_product(self, product_data: dict) -> Optional[int]:
        """Add a new product"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO products (name, category, hsn_code, unit, mrp, 
                                        discount_percent, selling_price, purchase_price, 
                                        gst_rate, current_stock, min_stock_level, 
                                        barcode, description, package_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_data['name'], product_data['category'], product_data['hsn_code'],
                    product_data['unit'], product_data['mrp'], product_data['discount_percent'],
                    product_data['selling_price'], product_data.get('purchase_price', 0),
                    product_data.get('gst_rate', 12.0), product_data.get('current_stock', 0),
                    product_data.get('min_stock_level', 10), product_data.get('barcode'),
                    product_data.get('description'), product_data.get('package_size')
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
                        discount_percent=?, selling_price=?, purchase_price=?,
                        gst_rate=?, min_stock_level=?, barcode=?, 
                        description=?, package_size=?, updated_at=?
                    WHERE id=?
                """, (
                    product_data['name'], product_data['category'], product_data['hsn_code'],
                    product_data['unit'], product_data['mrp'], product_data['discount_percent'],
                    product_data['selling_price'], product_data.get('purchase_price', 0),
                    product_data.get('gst_rate', 12.0), product_data.get('min_stock_level', 10),
                    product_data.get('barcode'), product_data.get('description'),
                    product_data.get('package_size'), datetime.now(), product_id
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
                cursor = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,))
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
                """, (f"%{search_term}%", f"%{search_term}%"))
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
                        "SELECT * FROM products WHERE category = ? ORDER BY name",
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
                conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                logger.info(f"Product deleted: ID {product_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False
    
    def update_product_stock(self, product_id: int, new_stock: int, 
                           change_type: str = "ADJUSTMENT", 
                           reference_id: Optional[int] = None,
                           notes: Optional[str] = None) -> bool:
        """Update product stock and log history"""
        try:
            with self.get_connection() as conn:
                # Get current stock
                cursor = conn.execute("SELECT current_stock FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                old_stock = result['current_stock']
                quantity_change = new_stock - old_stock
                
                # Update stock
                conn.execute(
                    "UPDATE products SET current_stock = ?, updated_at = ? WHERE id = ?",
                    (new_stock, datetime.now(), product_id)
                )
                
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
    
    # ============= CUSTOMER OPERATIONS =============
    
    def add_customer(self, customer_data: dict) -> Optional[int]:
        """Add a new customer"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO customers (name, phone, email, address, city, state, pin_code, gstin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_data['name'], customer_data.get('phone'),
                    customer_data.get('email'), customer_data.get('address'),
                    customer_data.get('city'), customer_data.get('state'),
                    customer_data.get('pin_code'), customer_data.get('gstin')
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
                """, (f"%{search_term}%", f"%{search_term}%"))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return []
    
    def get_customer_by_id(self, customer_id: int) -> Optional[dict]:
        """Get customer by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
                customer = cursor.fetchone()
                return dict(customer) if customer else None
        except Exception as e:
            logger.error(f"Error getting customer: {e}")
            return None

    # ============= BILL OPERATIONS =============
    
    def generate_invoice_number(self) -> str:
        """Generate next invoice number in format: NH/52/25-26"""
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
                """, (f"NH/%/{fy_suffix}",))
                
                last_invoice = cursor.fetchone()
                
                if last_invoice:
                    # Extract number from NH/52/25-26
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
    
    def create_bill(self, bill_data: dict, items: List[dict]) -> Optional[int]:
        """Create a new bill with items and update stock"""
        try:
            with self.get_connection() as conn:
                # Insert bill
                cursor = conn.execute("""
                    INSERT INTO bills (invoice_number, customer_id, customer_name, 
                                     customer_phone, customer_address, customer_city,
                                     customer_state, customer_pin_code, customer_gstin,
                                     subtotal, total_discount, round_off, grand_total,
                                     payment_mode, notes, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bill_data['invoice_number'], bill_data.get('customer_id'),
                    bill_data['customer_name'], bill_data.get('customer_phone'),
                    bill_data.get('customer_address'), bill_data.get('customer_city'),
                    bill_data.get('customer_state'), bill_data.get('customer_pin_code'),
                    bill_data.get('customer_gstin'), bill_data['subtotal'],
                    bill_data.get('total_discount', 0), bill_data.get('round_off', 0),
                    bill_data['grand_total'], bill_data.get('payment_mode', 'Cash'),
                    bill_data.get('notes'), bill_data.get('created_by')
                ))
                
                bill_id = cursor.lastrowid
                
                # Insert bill items and update stock
                for item in items:
                    conn.execute("""
                        INSERT INTO bill_items (bill_id, product_id, product_name, 
                                              hsn_code, batch_number, expiry_date,
                                              quantity, mrp, discount_percent, rate, amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        bill_id, item['product_id'], item['product_name'],
                        item.get('hsn_code'), item.get('batch_number'),
                        item.get('expiry_date'), item['quantity'],
                        item['mrp'], item['discount_percent'],
                        item['rate'], item['amount']
                    ))
                    
                    # Update product stock
                    conn.execute("""
                        UPDATE products 
                        SET current_stock = current_stock - ?, updated_at = ?
                        WHERE id = ?
                    """, (item['quantity'], datetime.now(), item['product_id']))
                    
                    # Log stock history
                    cursor_stock = conn.execute(
                        "SELECT current_stock FROM products WHERE id = ?",
                        (item['product_id'],)
                    )
                    new_stock = cursor_stock.fetchone()['current_stock']
                    
                    conn.execute("""
                        INSERT INTO stock_history 
                        (product_id, batch_number, change_type, quantity_change, 
                         old_stock, new_stock, reference_id, notes)
                        VALUES (?, ?, 'SALE', ?, ?, ?, ?, ?)
                    """, (
                        item['product_id'], item.get('batch_number'),
                        -item['quantity'], new_stock + item['quantity'],
                        new_stock, bill_id, f"Sale - Invoice {bill_data['invoice_number']}"
                    ))
                
                conn.commit()
                logger.info(f"Bill created: {bill_data['invoice_number']} with {len(items)} items")
                return bill_id
                
        except Exception as e:
            logger.error(f"Error creating bill: {e}")
            return None
    
    def get_bill_by_id(self, bill_id: int) -> Optional[dict]:
        """Get bill by ID with items"""
        try:
            with self.get_connection() as conn:
                # Get bill
                cursor = conn.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
                bill = cursor.fetchone()
                
                if not bill:
                    return None
                
                bill_dict = dict(bill)
                
                # Get bill items
                cursor = conn.execute(
                    "SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id",
                    (bill_id,)
                )
                bill_dict['items'] = [dict(row) for row in cursor.fetchall()]
                
                return bill_dict
        except Exception as e:
            logger.error(f"Error getting bill: {e}")
            return None
    
    def get_bill_by_invoice_number(self, invoice_number: str) -> Optional[dict]:
        """Get bill by invoice number with items"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM bills WHERE invoice_number = ?",
                    (invoice_number,)
                )
                bill = cursor.fetchone()
                
                if not bill:
                    return None
                
                bill_dict = dict(bill)
                
                # Get bill items
                cursor = conn.execute(
                    "SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id",
                    (bill_dict['id'],)
                )
                bill_dict['items'] = [dict(row) for row in cursor.fetchall()]
                
                return bill_dict
        except Exception as e:
            logger.error(f"Error getting bill by invoice: {e}")
            return None
    
    def search_bills(self, search_term: str = "", start_date: Optional[str] = None, 
                    end_date: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Search bills by invoice number or customer name"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM bills WHERE 1=1"
                params = []
                
                if search_term:
                    query += " AND (invoice_number LIKE ? OR customer_name LIKE ?)"
                    params.extend([f"%{search_term}%", f"%{search_term}%"])
                
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
    
    # ============= PRODUCT BATCH OPERATIONS =============
    
    def add_product_batch(self, batch_data: dict) -> Optional[int]:
        """Add a new product batch"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO product_batches 
                    (product_id, batch_number, expiry_date, quantity, mrp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    batch_data['product_id'], batch_data['batch_number'],
                    batch_data.get('expiry_date'), batch_data.get('quantity', 0),
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
                    WHERE product_id = ? AND quantity > 0
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
                    AND pb.expiry_date <= DATE('now', '+' || ? || ' days')
                    ORDER BY pb.expiry_date ASC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting expiring batches: {e}")
            return []
    
    # ============= REPORTING & ANALYTICS =============
    
    def get_sales_summary(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> dict:
        """Get sales summary for a date range"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT 
                        COUNT(*) as total_bills,
                        SUM(grand_total) as total_sales,
                        SUM(total_discount) as total_discount,
                        AVG(grand_total) as avg_bill_value
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
                
                cursor = conn.execute(query, params)
                result = cursor.fetchone()
                
                return {
                    'total_bills': result['total_bills'] or 0,
                    'total_sales': result['total_sales'] or 0.0,
                    'total_discount': result['total_discount'] or 0.0,
                    'avg_bill_value': result['avg_bill_value'] or 0.0
                }
        except Exception as e:
            logger.error(f"Error getting sales summary: {e}")
            return {
                'total_bills': 0,
                'total_sales': 0.0,
                'total_discount': 0.0,
                'avg_bill_value': 0.0
            }
    
    def get_top_selling_products(self, limit: int = 10, 
                                 start_date: Optional[str] = None,
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
    
    # ============= BACKUP OPERATIONS =============
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
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
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    # ============= UTILITY OPERATIONS =============
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Count tables
                tables = ['products', 'customers', 'bills', 'bill_items', 
                         'product_batches', 'users', 'stock_history']
                
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[table] = cursor.fetchone()['count']
                
                # Database file size
                import os
                stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
                
                return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    # ============= COMPANY SETTINGS OPERATIONS =============
    
    def get_company_settings(self) -> dict:
        """Get company settings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM company_settings WHERE id = 1")
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
                    WHERE id = 1
                """, (
                    settings['company_name'], settings['company_tagline'],
                    settings['company_subtitle'], settings['company_certifications'],
                    settings['office_address'], settings['factory_address'],
                    settings['phone'], settings['email'], settings['instagram'],
                    settings['bank_name'], settings['bank_account_no'],
                    settings['bank_ifsc'], settings['gstin'], settings['state_name'],
                    settings['state_code'], settings['invoice_prefix'],
                    settings['invoice_note'], datetime.now()
                ))
                conn.commit()
                logger.info("Company settings updated successfully")
                return True
        except Exception as e:
            logger.error(f"Error updating company settings: {e}")
            return False


# Create global instance
db = DatabaseManager()
