# GST Tax Rates (in percentage)
GST_RATES = {
    "0%": 0.0,
    "5%": 5.0,
    "12%": 12.0,
    "18%": 18.0,
    "28%": 28.0
}

# Default GST Rate for Ayurvedic Medicines (Usually 12%)
DEFAULT_GST_RATE = 12.0

# HSN Code for Ayurvedic Medicines
DEFAULT_HSN_CODE = "30049012"

# Payment Modes
PAYMENT_MODES = [
    "Cash",
    "UPI",
    "Card",
    "Net Banking",
    "Cheque",
    "Credit"
]

# Product Categories (Based on your catalog)
PRODUCT_CATEGORIES = [
    "Capsules",
    "Oils",
    "Awaleh/Powder",
    "Ointment",
    "Syrup",
    "Pills",
    "Serum",
    "Tonic",
    "Honey",
    "Others"
]

# Units of Measurement (Based on your products)
UNITS = [
    "Nos",      # Numbers (for capsules, pills)
    "ml",       # Milliliters (for oils, syrups)
    "gm",       # Grams (for powders)
    "kg",       # Kilograms
    "Bottle",
    "Pack"
]

# Stock Alert Threshold
LOW_STOCK_THRESHOLD = 10

# Date Formats
DATE_FORMAT = "%d.%m.%Y"  # As per your invoice: 02.02.2026
DATETIME_FORMAT = "%d.%m.%Y %I:%M %p"

# Validation Patterns
GSTIN_PATTERN = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
PHONE_PATTERN = r'^[6-9]\d{9}$'
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PIN_CODE_PATTERN = r'^\d{6}$'

# UI Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 650

# Table Column Widths (for inventory/billing tables - Based on your invoice format)
COLUMN_WIDTHS = {
    'sno': 50,
    'description': 250,
    'hsn': 100,
    'batch': 80,
    'expiry': 80,
    'qty': 70,
    'mrp': 90,
    'disc': 70,
    'rate': 90,
    'amount': 120
}

# Invoice Display Settings
SHOW_RUPEES_IN_WORDS = True
ROUND_OFF_ENABLED = True
