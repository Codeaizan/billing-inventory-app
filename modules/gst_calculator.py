from typing import Tuple
from utils.constants import DEFAULT_GST_RATE

class GSTCalculator:
    """Calculate GST and totals for billing"""
    
    @staticmethod
    def calculate_selling_price(mrp: float, discount_percent: float) -> float:
        """Calculate selling price after discount"""
        if discount_percent < 0 or discount_percent > 100:
            discount_percent = 0
        
        selling_price = mrp * (1 - discount_percent / 100)
        return round(selling_price, 2)
    
    @staticmethod
    def calculate_item_total(mrp: float, discount_percent: float, quantity: int) -> Tuple[float, float]:
        """
        Calculate item total
        Returns: (rate, amount)
        """
        rate = GSTCalculator.calculate_selling_price(mrp, discount_percent)
        amount = rate * quantity
        return round(rate, 2), round(amount, 2)
    
    @staticmethod
    def calculate_gst_amount(base_price: float, gst_rate: float) -> Tuple[float, float, float]:
        """
        Calculate GST amount (CGST, SGST, IGST)
        For intra-state: CGST + SGST
        For inter-state: IGST
        
        Returns: (cgst, sgst, igst)
        """
        total_gst = (base_price * gst_rate) / 100
        
        # For simplicity, we'll use CGST + SGST (intra-state)
        # In real scenario, check if state codes match
        cgst = total_gst / 2
        sgst = total_gst / 2
        igst = 0.0
        
        return round(cgst, 2), round(sgst, 2), round(igst, 2)
    
    @staticmethod
    def calculate_bill_totals(items: list) -> dict:
        """
        Calculate bill totals from items
        
        Items should have: mrp, discount_percent, quantity
        Returns: dict with subtotal, total_discount, grand_total, round_off
        """
        subtotal = 0.0
        total_mrp = 0.0
        
        for item in items:
            mrp = item.get('mrp', 0.0)
            discount_percent = item.get('discount_percent', 0.0)
            quantity = item.get('quantity', 0)
            
            # Calculate for this item
            rate, amount = GSTCalculator.calculate_item_total(mrp, discount_percent, quantity)
            
            subtotal += amount
            total_mrp += (mrp * quantity)
        
        # Calculate total discount
        total_discount = total_mrp - subtotal
        
        # Round off to nearest rupee
        grand_total_exact = subtotal
        grand_total_rounded = round(grand_total_exact)
        round_off = grand_total_rounded - grand_total_exact
        
        return {
            'subtotal': round(subtotal, 2),
            'total_discount': round(total_discount, 2),
            'grand_total': grand_total_rounded,
            'round_off': round(round_off, 2)
        }
    
    @staticmethod
    def calculate_discount_amount(mrp: float, discount_percent: float) -> float:
        """Calculate discount amount"""
        discount_amount = mrp * (discount_percent / 100)
        return round(discount_amount, 2)
    
    @staticmethod
    def number_to_words(number: int) -> str:
        """Convert number to words (for invoice)"""
        if number == 0:
            return "Zero"
        
        # Arrays for conversion
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(n):
            result = ""
            if n >= 100:
                result += ones[n // 100] + " Hundred "
                n %= 100
            if n >= 20:
                result += tens[n // 10] + " "
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + " "
                return result
            if n > 0:
                result += ones[n] + " "
            return result
        
        if number < 0:
            return "Minus " + GSTCalculator.number_to_words(abs(number))
        
        # Indian numbering system
        if number >= 10000000:  # Crore
            crores = number // 10000000
            result = convert_hundreds(crores) + "Crore "
            number %= 10000000
        else:
            result = ""
        
        if number >= 100000:  # Lakh
            lakhs = number // 100000
            result += convert_hundreds(lakhs) + "Lakh "
            number %= 100000
        
        if number >= 1000:  # Thousand
            thousands = number // 1000
            result += convert_hundreds(thousands) + "Thousand "
            number %= 1000
        
        if number > 0:
            result += convert_hundreds(number)
        
        return result.strip() + " Only"

# Create global instance
gst_calculator = GSTCalculator()
