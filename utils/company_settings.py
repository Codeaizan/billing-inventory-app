from database.db_manager import db
from utils.logger import logger

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
            'bank_name': 'STATE BANK OF INDIA',
            'bank_account_no': '42567178838',
            'bank_ifsc': 'SBIN0011534',
            'gstin': '',
            'state_name': 'West Bengal',
            'state_code': '19',
            'invoice_prefix': 'NH',
            'invoice_note': 'Note - Please make cheques in favor of "NATURAL HEALTH WORLD"'
        }
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def get_all(self):
        """Get all settings"""
        return self._settings.copy()
    
    def update(self, settings: dict) -> bool:
        """Update settings"""
        success = db.update_company_settings(settings)
        if success:
            self.load_settings()  # Reload from database
        return success
    
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
    
    @property
    def bank_name(self):
        return self.get('bank_name', '')
    
    @property
    def bank_account_no(self):
        return self.get('bank_account_no', '')
    
    @property
    def bank_ifsc(self):
        return self.get('bank_ifsc', '')

# Global instance
company_settings = CompanySettings()
