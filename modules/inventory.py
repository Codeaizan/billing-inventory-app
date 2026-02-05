from typing import List, Optional, Tuple
from datetime import datetime
from database.db_manager import db
from modules.auth import auth_manager
from utils.signals import app_signals
from utils.logger import logger
from utils.validators import (validate_product_name, validate_price, 
                             validate_quantity, validate_discount)


class InventoryManager:
    """Manages inventory operations"""
    
    def add_product(self, product_data: dict) -> Tuple[bool, str, Optional[int]]:
        """
        Add new product
        Returns: (success, message, product_id)
        """
        # Validate product name
        valid, msg = validate_product_name(product_data.get('name', ''))
        if not valid:
            return False, msg, None
        
        # Validate MRP
        valid, msg, mrp = validate_price(str(product_data.get('mrp', 0)))
        if not valid:
            return False, f"MRP: {msg}", None
        product_data['mrp'] = mrp
        
        # Validate discount
        valid, msg, discount = validate_discount(str(product_data.get('discount_percent', 55)))
        if not valid:
            return False, f"Discount: {msg}", None
        product_data['discount_percent'] = discount
        
        # Calculate selling price
        from modules.gst_calculator import gst_calculator
        product_data['selling_price'] = gst_calculator.calculate_selling_price(
            mrp, discount
        )
        
        # Add to database
        product_id = db.add_product(product_data)
        
        if product_id:
            return True, "Product added successfully", product_id
        else:
            return False, "Failed to add product. Name or barcode may already exist.", None
    
    def update_product(self, product_id: int, product_data: dict) -> Tuple[bool, str]:
        """Update product details"""
        # Validate product name
        valid, msg = validate_product_name(product_data.get('name', ''))
        if not valid:
            return False, msg
        
        # Validate MRP
        valid, msg, mrp = validate_price(str(product_data.get('mrp', 0)))
        if not valid:
            return False, f"MRP: {msg}"
        product_data['mrp'] = mrp
        
        # Validate discount
        valid, msg, discount = validate_discount(str(product_data.get('discount_percent', 55)))
        if not valid:
            return False, f"Discount: {msg}"
        product_data['discount_percent'] = discount
        
        # Calculate selling price
        from modules.gst_calculator import gst_calculator
        product_data['selling_price'] = gst_calculator.calculate_selling_price(
            mrp, discount
        )
        
        # Update in database
        success = db.update_product(product_id, product_data)
        
        if success:
            return True, "Product updated successfully"
        else:
            return False, "Failed to update product"
    
    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        """Delete a product"""
        # Check if product exists
        product = db.get_product_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        # Check if product has stock
        if product['current_stock'] > 0:
            return False, "Cannot delete product with stock. Please adjust stock to zero first."
        
        success = db.delete_product(product_id)
        
        if success:
            return True, "Product deleted successfully"
        else:
            return False, "Failed to delete product"
    
    def search_products(self, search_term: str) -> List[dict]:
        """Search products"""
        return db.search_products(search_term)
    
    def get_all_products(self, category: Optional[str] = None) -> List[dict]:
        """Get all products"""
        return db.get_all_products(category)
    
    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """Get product by ID"""
        return db.get_product_by_id(product_id)
    
    def update_stock(self, product_id: int, quantity: int, change_type: str, notes: str = "") -> Tuple[bool, str]:
        """
        Update product stock
        change_type: 'ADD', 'REMOVE', 'ADJUST', 'PURCHASE', 'SALE', 'ADJUSTMENT'
        """
        try:
            product = db.get_product_by_id(product_id)
            if not product:
                return False, "Product not found"
            
            old_quantity = product['current_stock']
            
            # Handle different change types
            if change_type in ['ADD', 'PURCHASE']:
                new_quantity = old_quantity + quantity
                actual_change_type = 'PURCHASE'
            elif change_type in ['REMOVE', 'SALE']:
                if quantity > old_quantity:
                    return False, "Insufficient stock"
                new_quantity = old_quantity - quantity
                actual_change_type = 'SALE'
            elif change_type in ['ADJUST', 'ADJUSTMENT']:
                new_quantity = quantity
                actual_change_type = 'ADJUSTMENT'
            else:
                return False, f"Invalid change type: {change_type}"
            
            # Update stock
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE products SET current_stock = ?, updated_at = ? WHERE id = ?",
                    (new_quantity, datetime.now(), product_id)
                )
                
                # Record in stock history
                conn.execute("""
                    INSERT INTO stock_history 
                    (product_id, change_type, quantity_before, quantity_after, 
                     quantity_changed, notes, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    actual_change_type,
                    old_quantity,
                    new_quantity,
                    new_quantity - old_quantity,
                    notes,
                    auth_manager.get_current_user_id()
                ))
                
                conn.commit()
            
            logger.info(f"Stock updated for product {product_id}: {old_quantity} -> {new_quantity}")
             # Emit signal
            app_signals.inventory_updated.emit()
            return True, "Stock updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return False, str(e)

    
    def add_stock(self, product_id: int, quantity: int, 
                 notes: Optional[str] = None) -> Tuple[bool, str]:
        """Add stock to product"""
        product = db.get_product_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        new_stock = product['current_stock'] + quantity
        return self.update_stock(product_id, new_stock, "PURCHASE", notes)
    
    def reduce_stock(self, product_id: int, quantity: int,
                    notes: Optional[str] = None) -> Tuple[bool, str]:
        """Reduce stock from product"""
        product = db.get_product_by_id(product_id)
        if not product:
            return False, "Product not found"
        
        new_stock = product['current_stock'] - quantity
        if new_stock < 0:
            return False, "Insufficient stock"
        
        return self.update_stock(product_id, new_stock, "ADJUSTMENT", notes)
    
    def get_low_stock_products(self) -> List[dict]:
        """Get products with low stock"""
        return db.get_low_stock_products()
    
    def get_inventory_value(self) -> dict:
        """Get total inventory value"""
        return db.get_inventory_value()
    
    def add_product_batch(self, batch_data: dict) -> Tuple[bool, str, Optional[int]]:
        """Add product batch"""
        batch_id = db.add_product_batch(batch_data)
        
        if batch_id:
            return True, "Batch added successfully", batch_id
        else:
            return False, "Failed to add batch. Batch number may already exist.", None
    
    def get_product_batches(self, product_id: int) -> List[dict]:
        """Get all batches for a product"""
        return db.get_product_batches(product_id)
    
    def get_expiring_batches(self, days: int = 90) -> List[dict]:
        """Get batches expiring within specified days"""
        return db.get_expiring_batches(days)


# Create global instance
inventory_manager = InventoryManager()
