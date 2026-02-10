from typing import List, Tuple, Optional, Dict
from datetime import datetime
from database.db_manager import db
from modules.gst_calculator import gst_calculator
from modules.auth import auth_manager
from utils.gst_states import get_state_from_gstin
from utils.company_settings import company_settings
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
            GST at 5% total on taxable amount
            Distribution (CGST/SGST vs IGST) is decided later in create_bill,
            but we still need total_tax and grand_total here.
        """
        if not self.cart_items:
            return {
                'subtotal': 0.0,
                'discount_amount': 0.0,
                'taxable_amount': 0.0,
                'cgst_amount': 0.0,
                'sgst_amount': 0.0,
                'igst_amount': 0.0,
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
        
        if is_gst_bill:
            # Total GST at 5% on taxable amount
            total_tax = taxable_amount * 0.05
        else:
            total_tax = 0.0
        
        # For now, keep cgst/sgst/igst at 0 here; we will
        # set correct distribution (CGST+SGST vs IGST) in create_bill
        cgst_amount = 0.0
        sgst_amount = 0.0
        igst_amount = 0.0
        
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
            'igst_amount': igst_amount,
            'total_tax': total_tax,
            'round_off': round_off,
            'grand_total': grand_total
        }
    
    def generate_invoice_number(self) -> str:
        """Generate next invoice number based on prefix, FY, and configurable start"""
        prefix = company_settings.get('invoice_prefix', 'NH')

        now = datetime.now()
        if now.month >= 4:
            fy_start = now.year
            fy_end = now.year + 1
        else:
            fy_start = now.year - 1
            fy_end = now.year
        fy_str = f"{fy_start % 100}-{fy_end % 100}"

        running = company_settings.next_invoice_number

        # Find a free invoice number (avoid UNIQUE constraint issues)
        for _ in range(1000):
            candidate = f"{prefix}/{running}/{fy_str}"
            # Your existing helper returns None if bill does not exist
            if db.get_bill_by_invoice_number(candidate) is None:
                invoice_number = candidate
                break
            running += 1
        else:
            # Fallback if something very wrong
            invoice_number = f"{prefix}/{running}/{fy_str}"

        # Store the next number for the future
        company_settings.set_next_invoice_number(running + 1)

        return invoice_number

    
    def _split_tax_by_state(self, totals: dict, customer_gstin: str) -> dict:
        """
        Decide CGST+SGST vs IGST based on company state vs customer GSTIN state.

        - Company state_code is in company_settings['state_code'] (e.g. "19" for West Bengal).
        - Customer state_code is first 2 digits of GSTIN (or "" if invalid).
        """
        total_tax = totals.get('total_tax', 0.0)
        
        # Defaults
        totals['cgst_amount'] = 0.0
        totals['sgst_amount'] = 0.0
        totals['igst_amount'] = 0.0
        
        # If no GST or total_tax is 0, nothing to split
        if total_tax <= 0 or not customer_gstin:
            logger.warning(f"_split_tax_by_state: total_tax={total_tax}, customer_gstin='{customer_gstin}' - returning zeros")
            return totals
        
        company_state_code = company_settings.get('state_code', '').strip()
        customer_state_code = customer_gstin[:2] if len(customer_gstin) >= 2 else ""
        
        logger.info(f"Tax split logic: company_state={company_state_code}, customer_state={customer_state_code}, total_tax={total_tax}")
        
        if company_state_code and customer_state_code == company_state_code:
            # Intra-state: CGST + SGST (2.5% + 2.5%)
            cgst = total_tax / 2
            sgst = total_tax / 2
            totals['cgst_amount'] = round(cgst, 2)
            totals['sgst_amount'] = round(sgst, 2)
            totals['igst_amount'] = 0.0
            logger.info(f"Intra-state transaction: CGST={totals['cgst_amount']}, SGST={totals['sgst_amount']}")
        else:
            # Inter-state: IGST 5%
            totals['cgst_amount'] = 0.0
            totals['sgst_amount'] = 0.0
            totals['igst_amount'] = round(total_tax, 2)
            logger.info(f"Inter-state transaction: IGST={totals['igst_amount']}")
        
        return totals
    
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
            
            # Calculate totals (total_tax at 5% if GST bill)
            totals = self.calculate_totals(is_gst_bill)
            
            # If GST bill, split total_tax into CGST+SGST or IGST based on state
            customer_gstin = customer_data.get('customer_gstin', '').strip()
            if is_gst_bill:
                totals = self._split_tax_by_state(totals, customer_gstin)
            else:
                totals['cgst_amount'] = 0.0
                totals['sgst_amount'] = 0.0
                totals['igst_amount'] = 0.0
            
            # Log final tax values
            logger.info(f"Final tax split: cgst={totals['cgst_amount']}, sgst={totals['sgst_amount']}, igst={totals['igst_amount']}, total_tax={totals['total_tax']}")
            
            # Prepare bill data
            bill_data = {
                'invoice_number': invoice_number,
                'customer_id': customer_id,
                'customer_name': customer_data['customer_name'],
                'customer_phone': customer_data.get('customer_phone', ''),
                'customer_address': customer_data.get('customer_address', ''),
                'customer_city': customer_data.get('customer_city', ''),
                'customer_pin_code': customer_data.get('customer_pin_code', ''),
                'customer_gstin': customer_gstin,
                'sales_person_id': sales_person_id,
                'is_gst_bill': 1 if is_gst_bill else 0,
                'subtotal': totals['subtotal'],
                'discount_amount': totals['discount_amount'],
                'taxable_amount': totals['taxable_amount'],
                'cgst_amount': totals['cgst_amount'],
                'sgst_amount': totals['sgst_amount'],
                'igst_amount': totals['igst_amount'],
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
