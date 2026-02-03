from typing import List, Optional
from datetime import datetime, timedelta
from database.db_manager import db
from utils.logger import logger

class ReportManager:
    """Manages reporting and analytics"""
    
    def get_sales_summary(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> dict:
        """Get sales summary for date range"""
        return db.get_sales_summary(start_date, end_date)
    
    def get_today_sales(self) -> dict:
        """Get today's sales summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_sales_summary(today, today)
    
    def get_this_month_sales(self) -> dict:
        """Get current month's sales summary"""
        today = datetime.now()
        month_start = today.replace(day=1).strftime('%Y-%m-%d')
        month_end = today.strftime('%Y-%m-%d')
        return self.get_sales_summary(month_start, month_end)
    
    def get_this_year_sales(self) -> dict:
        """Get current year's sales summary"""
        today = datetime.now()
        year_start = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        year_end = today.strftime('%Y-%m-%d')
        return self.get_sales_summary(year_start, year_end)
    
    def get_top_selling_products(self, limit: int = 10,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> List[dict]:
        """Get top selling products"""
        return db.get_top_selling_products(limit, start_date, end_date)
    
    def get_payment_mode_summary(self, start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> List[dict]:
        """Get payment mode wise summary"""
        return db.get_payment_mode_summary(start_date, end_date)
    
    def get_daily_sales(self, days: int = 30) -> List[dict]:
        """Get daily sales for last N days"""
        return db.get_daily_sales(days)
    
    def get_inventory_report(self) -> dict:
        """Get inventory report"""
        inventory_value = db.get_inventory_value()
        low_stock = db.get_low_stock_products()
        
        return {
            'inventory_value': inventory_value,
            'low_stock_count': len(low_stock),
            'low_stock_products': low_stock
        }
    
    def get_expiring_products(self, days: int = 90) -> List[dict]:
        """Get products expiring within specified days"""
        return db.get_expiring_batches(days)
    
    def export_sales_data(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[dict]:
        """Export sales data for specified period"""
        bills = db.search_bills("", start_date, end_date, limit=10000)
        
        export_data = []
        for bill in bills:
            bill_details = db.get_bill_by_id(bill['id'])
            if bill_details:
                for item in bill_details['items']:
                    export_data.append({
                        'invoice_number': bill['invoice_number'],
                        'date': bill['created_at'],
                        'customer_name': bill['customer_name'],
                        'customer_phone': bill['customer_phone'],
                        'product_name': item['product_name'],
                        'hsn_code': item['hsn_code'],
                        'batch_number': item['batch_number'],
                        'quantity': item['quantity'],
                        'mrp': item['mrp'],
                        'discount_percent': item['discount_percent'],
                        'rate': item['rate'],
                        'amount': item['amount'],
                        'payment_mode': bill['payment_mode'],
                        'grand_total': bill['grand_total']
                    })
        
        return export_data

# Create global instance
report_manager = ReportManager()
