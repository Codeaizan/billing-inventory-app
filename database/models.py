from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model for authentication"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

@dataclass
class Product:
    """Product model for inventory"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    hsn_code: str = "30049012"
    unit: str = "Nos"
    mrp: float = 0.0
    discount_percent: float = 55.0
    selling_price: float = 0.0
    purchase_price: float = 0.0
    gst_rate: float = 12.0
    current_stock: int = 0
    min_stock_level: int = 10
    barcode: Optional[str] = None
    description: Optional[str] = None
    package_size: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_selling_price(self):
        """Calculate selling price from MRP and discount"""
        if self.mrp and self.discount_percent:
            self.selling_price = self.mrp * (1 - self.discount_percent / 100)
        return self.selling_price

@dataclass
class ProductBatch:
    """Product batch for tracking expiry and batch numbers"""
    id: Optional[int] = None
    product_id: int = 0
    batch_number: str = ""
    expiry_date: Optional[str] = None
    quantity: int = 0
    mrp: Optional[float] = None
    purchase_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

@dataclass
class Customer:
    """Customer model"""
    id: Optional[int] = None
    name: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    gstin: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class Bill:
    """Bill/Invoice model"""
    id: Optional[int] = None
    invoice_number: str = ""
    customer_id: Optional[int] = None
    customer_name: str = ""
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    customer_city: Optional[str] = None
    customer_state: Optional[str] = None
    customer_pin_code: Optional[str] = None
    customer_gstin: Optional[str] = None
    subtotal: float = 0.0
    total_discount: float = 0.0
    round_off: float = 0.0
    grand_total: float = 0.0
    payment_mode: str = "Cash"
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class BillItem:
    """Bill item model"""
    id: Optional[int] = None
    bill_id: int = 0
    product_id: int = 0
    product_name: str = ""
    hsn_code: str = ""
    batch_number: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity: int = 0
    mrp: float = 0.0
    discount_percent: float = 0.0
    rate: float = 0.0
    amount: float = 0.0
    
    def calculate_amount(self):
        """Calculate total amount for this item"""
        self.rate = self.mrp * (1 - self.discount_percent / 100)
        self.amount = self.rate * self.quantity
        return self.amount

@dataclass
class StockHistory:
    """Stock history model for tracking inventory changes"""
    id: Optional[int] = None
    product_id: int = 0
    batch_number: Optional[str] = None
    change_type: str = ""  # SALE, PURCHASE, ADJUSTMENT, RETURN
    quantity_change: int = 0
    old_stock: int = 0
    new_stock: int = 0
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
