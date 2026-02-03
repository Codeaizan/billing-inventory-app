from typing import List, Optional, Tuple
from datetime import datetime
from database.db_manager import db
from modules.gst_calculator import gst_calculator
from utils.logger import logger
from utils.validators import validate_customer_name, validate_quantity

class BillingManager:
    """Manages billing operations"""
    
    def __init__(self):
        self.current_bill_items = []
        self.customer_info = {}
    
    def add_item_to_cart(self, product: dict, quantity: int, 
                         batch_number: Optional[str] = None,
                         expiry_date: Optional[str] = None) -> Tuple[bool, str]:
        """Add item to current bill"""
        
        # Validate quantity
        valid, msg, qty = validate_quantity(str(quantity))
        if not valid:
            return False, msg
        
        # Check stock availability
        if product['current_stock'] < qty:
            return False, f"Insufficient stock. Available: {product['current_stock']}"
        
        # Calculate item totals
        rate, amount = gst_calculator.calculate_item_total(
            product['mrp'], 
            product['discount_percent'], 
            qty
        )
        
        # Create bill item
        bill_item = {
            'product_id': product['id'],
            'product_name': product['name'],
            'hsn_code': product['hsn_code'],
            'batch_number': batch_number,
            'expiry_date': expiry_date,
            'quantity': qty,
            'mrp': product['mrp'],
            'discount_percent': product['discount_percent'],
            'rate': rate,
            'amount': amount
        }
        
        # Check if product already in cart
        existing_index = None
        for i, item in enumerate(self.current_bill_items):
            if item['product_id'] == product['id'] and item.get('batch_number') == batch_number:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update quantity
            old_qty = self.current_bill_items[existing_index]['quantity']
            new_qty = old_qty + qty
            
            # Check stock for new quantity
            if product['current_stock'] < new_qty:
                return False, f"Insufficient stock. Available: {product['current_stock']}"
            
            self.current_bill_items[existing_index]['quantity'] = new_qty
            rate, amount = gst_calculator.calculate_item_total(
                product['mrp'], 
                product['discount_percent'], 
                new_qty
            )
            self.current_bill_items[existing_index]['rate'] = rate
            self.current_bill_items[existing_index]['amount'] = amount
        else:
            # Add new item
            self.current_bill_items.append(bill_item)
        
        logger.info(f"Item added to cart: {product['name']} x {qty}")
        return True, "Item added to cart"
    
    def remove_item_from_cart(self, index: int) -> Tuple[bool, str]:
        """Remove item from cart by index"""
        if 0 <= index < len(self.current_bill_items):
            removed_item = self.current_bill_items.pop(index)
            logger.info(f"Item removed from cart: {removed_item['product_name']}")
            return True, "Item removed from cart"
        return False, "Invalid item index"
    
    def update_item_quantity(self, index: int, new_quantity: int) -> Tuple[bool, str]:
        """Update quantity of item in cart"""
        if not (0 <= index < len(self.current_bill_items)):
            return False, "Invalid item index"
        
        # Validate quantity
        valid, msg, qty = validate_quantity(str(new_quantity))
        if not valid:
            return False, msg
        
        item = self.current_bill_items[index]
        
        # Get product to check stock
        product = db.get_product_by_id(item['product_id'])
        if not product:
            return False, "Product not found"
        
        if product['current_stock'] < qty:
            return False, f"Insufficient stock. Available: {product['current_stock']}"
        
        # Update quantity and recalculate
        item['quantity'] = qty
        rate, amount = gst_calculator.calculate_item_total(
            item['mrp'], 
            item['discount_percent'], 
            qty
        )
        item['rate'] = rate
        item['amount'] = amount
        
        return True, "Quantity updated"
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.current_bill_items = []
        self.customer_info = {}
        logger.info("Cart cleared")
    
    def get_cart_items(self) -> List[dict]:
        """Get all items in cart"""
        return self.current_bill_items
    
    def get_cart_summary(self) -> dict:
        """Get cart summary with totals"""
        if not self.current_bill_items:
            return {
                'item_count': 0,
                'subtotal': 0.0,
                'total_discount': 0.0,
                'grand_total': 0.0,
                'round_off': 0.0
            }
        
        totals = gst_calculator.calculate_bill_totals(self.current_bill_items)
        totals['item_count'] = len(self.current_bill_items)
        
        return totals
    
    def set_customer_info(self, customer_data: dict) -> Tuple[bool, str]:
        """Set customer information for current bill"""
        
        # Validate customer name
        valid, msg = validate_customer_name(customer_data.get('name', ''))
        if not valid:
            return False, msg
        
        self.customer_info = customer_data
        return True, "Customer information saved"
    
    def create_bill(self, payment_mode: str = "Cash", 
                   notes: Optional[str] = None,
                   created_by: Optional[int] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Create bill from current cart
        Returns: (success, message, bill_id)
        """
        
        # Check if cart has items
        if not self.current_bill_items:
            return False, "Cart is empty", None
        
        # Check if customer info is set
        if not self.customer_info.get('name'):
            return False, "Customer information is required", None
        
        # Calculate totals
        totals = self.get_cart_summary()
        
        # Generate invoice number
        invoice_number = db.generate_invoice_number()
        
        # Prepare bill data
        bill_data = {
            'invoice_number': invoice_number,
            'customer_id': self.customer_info.get('id'),
            'customer_name': self.customer_info['name'],
            'customer_phone': self.customer_info.get('phone'),
            'customer_address': self.customer_info.get('address'),
            'customer_city': self.customer_info.get('city'),
            'customer_state': self.customer_info.get('state'),
            'customer_pin_code': self.customer_info.get('pin_code'),
            'customer_gstin': self.customer_info.get('gstin'),
            'subtotal': totals['subtotal'],
            'total_discount': totals['total_discount'],
            'round_off': totals['round_off'],
            'grand_total': totals['grand_total'],
            'payment_mode': payment_mode,
            'notes': notes,
            'created_by': created_by
        }
        
        # Create bill in database
        bill_id = db.create_bill(bill_data, self.current_bill_items)
        
        if bill_id:
            logger.info(f"Bill created: {invoice_number}")
            # Clear cart after successful bill creation
            self.clear_cart()
            return True, f"Bill created successfully: {invoice_number}", bill_id
        else:
            return False, "Failed to create bill", None
    
    def get_bill_by_id(self, bill_id: int) -> Optional[dict]:
        """Get bill details by ID"""
        return db.get_bill_by_id(bill_id)
    
    def get_bill_by_invoice_number(self, invoice_number: str) -> Optional[dict]:
        """Get bill details by invoice number"""
        return db.get_bill_by_invoice_number(invoice_number)
    
    def search_bills(self, search_term: str = "", 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[dict]:
        """Search bills"""
        return db.search_bills(search_term, start_date, end_date)
    
    def get_recent_bills(self, limit: int = 50) -> List[dict]:
        """Get recent bills"""
        return db.get_recent_bills(limit)
    
    def get_cart_total_items(self) -> int:
        """Get total number of items in cart"""
        return sum(item['quantity'] for item in self.current_bill_items)

# Create global instance
billing_manager = BillingManager()
