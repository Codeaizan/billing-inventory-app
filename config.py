import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'billing.db')

# Backup configuration
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
AUTO_BACKUP = True
BACKUP_INTERVAL_DAYS = 7

# Logging configuration
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Company/Business Details (From your invoice)
COMPANY_NAME = "NATURAL HEALTH WORLD"
COMPANY_TAGLINE = "The Herbal Healing"
COMPANY_SUBTITLE = "Manufacturer & Supplier of Ayurvedic Medicine"
COMPANY_CERTIFICATIONS = "(An ISO 9001 : 2015) Vegan, Halal & GMP Certified Company"

# Addresses
COMPANY_OFFICE = "4, Circus Range, Kolkata - 700 019"
COMPANY_FACTORY = "260A, Rajdanga Nabapally, Kasba, Kolkata - 700107"
COMPANY_ADDRESS = COMPANY_FACTORY  # Primary address for invoice

# Contact Details
COMPANY_PHONE = "9143746966, 9836623186"
COMPANY_EMAIL = "skr.nhw@gmail.com"
COMPANY_INSTAGRAM = "@naturalhealthworld_"

# Bank Details
BANK_NAME = "STATE BANK OF INDIA"
BANK_ACCOUNT_NO = "42567178838"
BANK_IFSC = "SBIN0011534"

# GST Details
COMPANY_GSTIN = ""  # Add your GST number if registered
COMPANY_STATE = "West Bengal"
COMPANY_STATE_CODE = "19"  # West Bengal state code

# Invoice Settings
INVOICE_PREFIX = "NH"  # As per your invoice format: NH/52/25-26
FINANCIAL_YEAR_START_MONTH = 4  # April
INVOICE_NOTE = 'Note - Please make cheques in favor of "NATURAL HEALTH WORLD"'

# Application Settings
APP_NAME = "Natural Health World - Billing System"
APP_VERSION = "1.0.0"
SESSION_TIMEOUT_MINUTES = 30

# PDF Settings
INVOICE_LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'images', 'logo.png')
PDF_OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'invoices')

# Invoice Features (Based on your format)
SHOW_BATCH_NO = True  # Your invoice shows batch numbers
SHOW_EXPIRY_DATE = True  # Your invoice shows expiry dates
SHOW_MRP = True  # Your invoice shows MRP
SHOW_DISCOUNT_PERCENT = True  # Your invoice shows discount percentage
DEFAULT_DISCOUNT_PERCENT = 55  # Default discount shown in your invoice

# Create necessary directories
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
