from typing import List, Tuple, Optional, Dict
from datetime import datetime
from database.db_manager import db
from modules.gst_calculator import gst_calculator
from modules.auth import auth_manager
from utils.logger import logger

class BillingManager:
    """Manages billing operations"""
    
    def __init__(self):
        self.cart_items = []
        self.current_invoice_number = None
    
    def add_item_to_cart(self, product: dict, quantity: int, batch_number: str = "", expiry_date: str = "") -> Tuple[bool, str]:
        """Add item to cart"""
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        if quantity > product['current_stock']:
            return False, f"Insufficient stock. Available: {product['current_stock']}"
        
        # Check if product already in cart
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                # Update quantity
                new_quantity = item['quantity'] + quantity
                if new_quantity > product['current_stock']:
                    return False, f"Total quantity exceeds stock. Available: {product['current_stock']}"
                
                item['quantity'] = new_quantity
                item['amount'] = item['rate'] * new_quantity
                return True, "Quantity updated in cart"
        
        # Add new item
        item = {
            'product_id': product['id'],
            'product_name': product['name'],
            'hsn_code': product.get('hsn_code', '30049012'),
            'batch_number': batch_number,
            'expiry_date': expiry_date,
            'quantity': quantity,
            'unit': product.get('unit', 'Nos'),
            'mrp': product['mrp'],
            'discount_percent': product['discount_percent'],
            'rate': product['selling_price'],
            'amount': product['selling_price'] * quantity
        }
        
        self.cart_items.append(item)
        return True, "Item added to cart"
    
    def remove_item_from_cart(self, index: int) -> bool:
        """Remove item from cart by index"""
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)
            return True
        return False
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items = []
    
    def get_cart_items(self) -> List[dict]:
        """Get all items in cart"""
        return self.cart_items
    
    def calculate_totals(self, is_gst_bill: bool = False) -> dict:
        """
        Calculate bill totals with or without GST
        
        For Non-GST Bill:
            Subtotal = Sum of all item amounts
            Grand Total = Subtotal + Round Off
        
        For GST Bill:
            Subtotal (Taxable Amount) = Sum of all item amounts
            CGST = 2.5% of Subtotal
            SGST = 2.5% of Subtotal
            Total Tax = CGST + SGST (5%)
            Grand Total = Subtotal + Total Tax + Round Off
        """
        if not self.cart_items:
            return {
                'subtotal': 0.0,
                'discount_amount': 0.0,
                'taxable_amount': 0.0,
                'cgst_amount': 0.0,
                'sgst_amount': 0.0,
                'total_tax': 0.0,
                'round_off': 0.0,
                'grand_total': 0.0
            }
        
        # Calculate subtotal and discount
        subtotal = sum(item['amount'] for item in self.cart_items)
        
        # Calculate total discount given
        total_mrp = sum(item['mrp'] * item['quantity'] for item in self.cart_items)
        discount_amount = total_mrp - subtotal
        
        # Taxable amount is the subtotal (after discount)
        taxable_amount = subtotal
        
        # Calculate GST if applicable
        if is_gst_bill:
            cgst_amount = taxable_amount * 0.025  # 2.5%
            sgst_amount = taxable_amount * 0.025  # 2.5%
            total_tax = cgst_amount + sgst_amount  # 5%
        else:
            cgst_amount = 0.0
            sgst_amount = 0.0
            total_tax = 0.0
        
        # Calculate grand total
        grand_total_before_round = subtotal + total_tax
        
        # Round off
        grand_total = round(grand_total_before_round)
        round_off = grand_total - grand_total_before_round
        
        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'taxable_amount': taxable_amount,
            'cgst_amount': cgst_amount,
            'sgst_amount': sgst_amount,
            'total_tax': total_tax,
            'round_off': round_off,
            'grand_total': grand_total
        }
    
    def generate_invoice_number(self) -> str:
        """Generate next invoice number"""
        from utils.company_settings import company_settings
        
        # Get invoice prefix
        prefix = company_settings.get('invoice_prefix', 'NH')
        
        # Get financial year (Apr-Mar)
        now = datetime.now()
        if now.month >= 4:
            fy_start = now.year
            fy_end = now.year + 1
        else:
            fy_start = now.year - 1
            fy_end = now.year
        
        fy_str = f"{fy_start % 100}-{fy_end % 100}"
        
        # Get last invoice number for this financial year
        last_invoice = db.get_last_invoice_number(f"{prefix}/%/{fy_str}")
        
        if last_invoice:
            # Extract number from invoice like "NH/123/25-26"
            parts = last_invoice.split('/')
            if len(parts) >= 2:
                try:
                    last_num = int(parts[1])
                    next_num = last_num + 1
                except:
                    next_num = 1
            else:
                next_num = 1
        else:
            next_num = 1
        
        return f"{prefix}/{next_num}/{fy_str}"
    
    def create_bill(self, customer_data: dict, sales_person_id: int, is_gst_bill: bool = False) -> Tuple[bool, str, Optional[dict]]:
        """
        Create a bill
        Returns: (success, message, bill_data)
        """
        if not self.cart_items:
            return False, "Cart is empty", None
        
        if not customer_data.get('customer_name'):
            return False, "Customer name is required", None
        
        if not sales_person_id:
            return False, "Sales person is required", None
        
        # Validate GSTIN for GST bills
        if is_gst_bill and not customer_data.get('customer_gstin'):
            return False, "Customer GSTIN is required for GST bills", None
        
        try:
            # Save or update customer in database
            customer_save_data = {
                'name': customer_data['customer_name'],
                'phone': customer_data.get('customer_phone', ''),
                'address': customer_data.get('customer_address', ''),
                'city': customer_data.get('customer_city', ''),
                'gstin': customer_data.get('customer_gstin', '')
            }
            
            success_cust, msg_cust, customer_id = db.add_or_update_customer(customer_save_data)
            
            if not success_cust:
                logger.warning(f"Failed to save customer: {msg_cust}")
                customer_id = None
            
            # Generate invoice number
            invoice_number = self.generate_invoice_number()
            
            # Calculate totals
            totals = self.calculate_totals(is_gst_bill)
            
            # Prepare bill data
            bill_data = {
                'invoice_number': invoice_number,
                'customer_id': customer_id,
                'customer_name': customer_data['customer_name'],
                'customer_phone': customer_data.get('customer_phone', ''),
                'customer_address': customer_data.get('customer_address', ''),
                'customer_city': customer_data.get('customer_city', ''),
                'customer_pin_code': customer_data.get('customer_pin_code', ''),
                'customer_gstin': customer_data.get('customer_gstin', ''),
                'sales_person_id': sales_person_id,
                'is_gst_bill': 1 if is_gst_bill else 0,
                'subtotal': totals['subtotal'],
                'discount_amount': totals['discount_amount'],
                'taxable_amount': totals['taxable_amount'],
                'cgst_amount': totals['cgst_amount'],
                'sgst_amount': totals['sgst_amount'],
                'total_tax': totals['total_tax'],
                'round_off': totals['round_off'],
                'grand_total': totals['grand_total'],
                'created_by': auth_manager.get_current_user_id()
            }
            
            # Create bill in database
            success, message, bill_id = db.create_bill(bill_data, self.cart_items)
            
            if success:
                # Get complete bill data for PDF generation
                bill_data['id'] = bill_id
                bill_data['items'] = self.cart_items.copy()
                bill_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"Bill created: {invoice_number}")
                return True, "Bill created successfully", bill_data
            else:
                return False, message, None
                
        except Exception as e:
            logger.error(f"Error creating bill: {e}")
            return False, str(e), None


# Create global instance
billing_manager = BillingManager()
