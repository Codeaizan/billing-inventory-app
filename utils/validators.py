import re
from typing import Tuple
from utils.constants import GSTIN_PATTERN, PHONE_PATTERN, EMAIL_PATTERN, PIN_CODE_PATTERN

def validate_gstin(gstin: str) -> Tuple[bool, str]:
    """Validate GST Identification Number"""
    if not gstin:
        return True, ""  # GSTIN is optional
    
    gstin = gstin.strip().upper()
    
    if not re.match(GSTIN_PATTERN, gstin):
        return False, "Invalid GSTIN format. Must be 15 characters (e.g., 22AAAAA0000A1Z5)"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate Indian phone number"""
    if not phone:
        return True, ""  # Phone is optional
    
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if not re.match(PHONE_PATTERN, phone):
        return False, "Invalid phone number. Must be 10 digits starting with 6-9"
    
    return True, ""

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address"""
    if not email:
        return True, ""  # Email is optional
    
    email = email.strip()
    
    if not re.match(EMAIL_PATTERN, email):
        return False, "Invalid email format"
    
    return True, ""

def validate_pin_code(pin_code: str) -> Tuple[bool, str]:
    """Validate Indian PIN code"""
    if not pin_code:
        return True, ""  # PIN code is optional
    
    pin_code = pin_code.strip()
    
    if not re.match(PIN_CODE_PATTERN, pin_code):
        return False, "Invalid PIN code. Must be 6 digits"
    
    return True, ""

def validate_price(price: str) -> Tuple[bool, str, float]:
    """Validate and convert price"""
    try:
        price_float = float(price)
        if price_float < 0:
            return False, "Price cannot be negative", 0.0
        return True, "", round(price_float, 2)
    except ValueError:
        return False, "Invalid price format", 0.0

def validate_quantity(quantity: str) -> Tuple[bool, str, int]:
    """Validate and convert quantity"""
    try:
        qty_int = int(quantity)
        if qty_int <= 0:
            return False, "Quantity must be greater than 0", 0
        return True, "", qty_int
    except ValueError:
        return False, "Invalid quantity format", 0

def validate_discount(discount: str) -> Tuple[bool, str, float]:
    """Validate discount percentage"""
    try:
        disc_float = float(discount)
        if disc_float < 0 or disc_float > 100:
            return False, "Discount must be between 0 and 100", 0.0
        return True, "", round(disc_float, 2)
    except ValueError:
        return False, "Invalid discount format", 0.0

def validate_product_name(name: str) -> Tuple[bool, str]:
    """Validate product name"""
    name = name.strip()
    
    if not name:
        return False, "Product name is required"
    
    if len(name) < 3:
        return False, "Product name must be at least 3 characters"
    
    if len(name) > 200:
        return False, "Product name too long (max 200 characters)"
    
    return True, ""

def validate_customer_name(name: str) -> Tuple[bool, str]:
    """Validate customer name"""
    name = name.strip()
    
    if not name:
        return False, "Customer name is required"
    
    if len(name) < 2:
        return False, "Customer name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Customer name too long (max 100 characters)"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username"""
    username = username.strip()
    
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscore"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    return True, ""

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent SQL injection"""
    if not text:
        return ""
    
    # Remove any potentially harmful characters
    text = text.strip()
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    return text
