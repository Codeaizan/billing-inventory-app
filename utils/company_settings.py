from database.db_manager import db
from utils.logger import logger
import re


class CompanySettings:
    """Manage company settings"""
    
    def __init__(self):
        self._settings = None
        self.load_settings()
    
    def load_settings(self):
        """Load settings from database"""
        self._settings = db.get_company_settings()
        if not self._settings:
            logger.warning("Company settings not found in database, using defaults")
            self._settings = self._get_defaults()

        # Extract next_invoice_number from invoice_note if present
        note = self._settings.get('invoice_note', '') or ''

        # Support both old [NEXT_INV=..] and new <!--NEXT_INV=..-->
        m = re.search(r'<!--NEXT_INV=(\d+)-->', note)
        if not m:
            m = re.search(r'\[NEXT_INV=(\d+)\]', note)

        if m:
            self._settings['next_invoice_number'] = int(m.group(1))
        else:
            self._settings.setdefault('next_invoice_number', 1)


    
    def _get_defaults(self):
        """Get default settings"""
        return {
            'company_name': 'Natural Health World',
            'company_tagline': 'The Herbal Healing',
            'company_subtitle': 'Manufacturer & Supplier of Ayurvedic Medicine',
            'company_certifications': '(An ISO 9001 : 2015) Vegan, Halal & GMP Certified Company',
            'office_address': '4, Circus Range, Kolkata - 700 019',
            'factory_address': '260A, Rajdanga Nabapally, Kasba, Kolkata - 700107',
            'phone': '9143746966, 9836623186',
            'email': 'skr.nhw@gmail.com',
            'instagram': '@naturalhealthworld_',
            
            # GST Banking Details
            'gst_bank_name': 'STATE BANK OF INDIA',
            'gst_bank_account_no': '42567178838',
            'gst_bank_ifsc': 'SBIN0011534',
            'gst_bank_branch': '',
            'gst_upi_id': '',
            
            # Non-GST Banking Details
            'non_gst_bank_name': '',
            'non_gst_bank_account_no': '',
            'non_gst_bank_ifsc': '',
            'non_gst_bank_branch': '',
            'non_gst_upi_id': '',
            
            # Legacy fields (for backward compatibility)
            'bank_name': 'STATE BANK OF INDIA',
            'bank_account_no': '42567178838',
            'bank_ifsc': 'SBIN0011534',
            
            'gstin': '',
            'state_name': 'West Bengal',
            'state_code': '19',
            'invoice_prefix': 'NH',
            # logical default; physical storage is inside invoice_note marker
            'next_invoice_number': 1,
            'logo_path': 'assets/logo.jpeg',
            'invoice_note': 'Note - Please make cheques in favor of "NATURAL HEALTH WORLD"',
        }
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def get_all(self):
        """Get all settings"""
        return self._settings.copy()
    
    def update(self, settings: dict) -> bool:
        """
        Update settings.
        db.update_company_settings expects a fixed set of keys.
        """
        current = self.get_all()
        merged = current.copy()
        merged.update(settings)
        
        # Ensure next_invoice_number is encoded into invoice_note before saving
        ninv = int(merged.get('next_invoice_number', 1) or 1)
        note = merged.get('invoice_note', '') or ''
        # strip both old visible and new hidden markers
        note = re.sub(r'<next_inv_hidden>(\d+)</next_inv_hidden>', '', note)
        note = re.sub(r'\[NEXT_INV=\d+\]', '', note)
        note = note.strip()
        # append fresh hidden marker
        note = f"{note} <next_inv_hidden>{ninv}</next_inv_hidden>".strip()
        merged['invoice_note'] = note
        
        full_for_db = {
            'company_name': merged.get('company_name', ''),
            'company_tagline': merged.get('company_tagline', ''),
            'company_subtitle': merged.get('company_subtitle', ''),
            'company_certifications': merged.get('company_certifications', ''),
            'office_address': merged.get('office_address', ''),
            'factory_address': merged.get('factory_address', ''),
            'phone': merged.get('phone', ''),
            'email': merged.get('email', ''),
            'instagram': merged.get('instagram', ''),
            'gstin': merged.get('gstin', ''),
            'state_name': merged.get('state_name', ''),
            'state_code': merged.get('state_code', ''),
            'invoice_prefix': merged.get('invoice_prefix', 'NH'),
            'invoice_note': merged.get('invoice_note', ''),
            
            # ✅ ADD NEW GST BANKING FIELDS
            'gst_bank_name': merged.get('gst_bank_name', ''),
            'gst_bank_account_no': merged.get('gst_bank_account_no', ''),
            'gst_bank_ifsc': merged.get('gst_bank_ifsc', ''),
            'gst_bank_branch': merged.get('gst_bank_branch', ''),
            'gst_upi_id': merged.get('gst_upi_id', ''),
            
            # ✅ ADD NEW NON-GST BANKING FIELDS
            'non_gst_bank_name': merged.get('non_gst_bank_name', ''),
            'non_gst_bank_account_no': merged.get('non_gst_bank_account_no', ''),
            'non_gst_bank_ifsc': merged.get('non_gst_bank_ifsc', ''),
            'non_gst_bank_branch': merged.get('non_gst_bank_branch', ''),
            'non_gst_upi_id': merged.get('non_gst_upi_id', ''),
            
            # Legacy fields (for backward compatibility)
            'bank_name': merged.get('bank_name', ''),
            'bank_account_no': merged.get('bank_account_no', ''),
            'bank_ifsc': merged.get('bank_ifsc', ''),
        }
        
        success = db.update_company_settings(full_for_db)
        
        if not success:
            return False
        
        # keep full merged state in memory, including next_invoice_number, banking, etc.
        self._settings = merged
        return True

    
    def get_bank_details(self, is_gst_bill: bool = False) -> dict:
        """
        Get appropriate bank details based on bill type
        """
        if is_gst_bill:
            return {
                'bank_name': self.get('gst_bank_name', ''),
                'bank_account_no': self.get('gst_bank_account_no', ''),
                'bank_ifsc': self.get('gst_bank_ifsc', ''),
                'bank_branch': self.get('gst_bank_branch', ''),
                'upi_id': self.get('gst_upi_id', ''),
            }
        else:
            non_gst_bank = self.get('non_gst_bank_name', '')
            if not non_gst_bank:
                return {
                    'bank_name': self.get('gst_bank_name', ''),
                    'bank_account_no': self.get('gst_bank_account_no', ''),
                    'bank_ifsc': self.get('gst_bank_ifsc', ''),
                    'bank_branch': self.get('gst_bank_branch', ''),
                    'upi_id': self.get('gst_upi_id', ''),
                }
            return {
                'bank_name': self.get('non_gst_bank_name', ''),
                'bank_account_no': self.get('non_gst_bank_account_no', ''),
                'bank_ifsc': self.get('non_gst_bank_ifsc', ''),
                'bank_branch': self.get('non_gst_bank_branch', ''),
                'upi_id': self.get('non_gst_upi_id', ''),
            }
    
    @property
    def company_name(self):
        return self.get('company_name', 'Natural Health World')
    
    @property
    def company_address(self):
        return self.get('factory_address', '')
    
    @property
    def company_phone(self):
        return self.get('phone', '')
    
    @property
    def company_email(self):
        return self.get('email', '')
    
    # Legacy properties
    @property
    def bank_name(self):
        return self.get('bank_name', '')
    
    @property
    def bank_account_no(self):
        return self.get('bank_account_no', '')
    
    @property
    def bank_ifsc(self):
        return self.get('bank_ifsc', '')
    
    # GST banking
    @property
    def gst_bank_name(self):
        return self.get('gst_bank_name', '')
    
    @property
    def gst_bank_account_no(self):
        return self.get('gst_bank_account_no', '')
    
    @property
    def gst_bank_ifsc(self):
        return self.get('gst_bank_ifsc', '')
    
    # Non-GST banking
    @property
    def non_gst_bank_name(self):
        return self.get('non_gst_bank_name', '')
    
    @property
    def non_gst_bank_account_no(self):
        return self.get('non_gst_bank_account_no', '')
    
    @property
    def non_gst_bank_ifsc(self):
        return self.get('non_gst_bank_ifsc', '')
    
    @property
    def logo_path(self):
        return self.get('logo_path', 'assets/logo.jpeg')
    
    @property
    def next_invoice_number(self) -> int:
        return int(self.get('next_invoice_number', 1) or 1)
    
    def set_next_invoice_number(self, value: int) -> bool:
        try:
            value_int = int(value)
        except ValueError:
            value_int = 1
        return self.update({'next_invoice_number': value_int})


# Global instance
company_settings = CompanySettings()
