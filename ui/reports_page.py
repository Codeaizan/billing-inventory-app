from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QDateEdit, QGroupBox, QFrame,
                            QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from modules.reports import report_manager
from database.db_manager import db
from datetime import datetime
from utils.logger import logger

class ReportsPage(QWidget):
    """Reports and analytics page"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_dashboard()
        self.load_sales_persons()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(title)
        
        # Date range and filters
        filter_layout = self.create_filter_section()
        main_layout.addLayout(filter_layout)
        
        # Dashboard cards
        dashboard = self.create_dashboard()
        main_layout.addWidget(dashboard)
        
        # Report tabs
        report_type_layout = QHBoxLayout()
        
        self.top_products_btn = QPushButton("📦 Top Products")
        self.top_products_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.top_products_btn.clicked.connect(self.show_top_products)
        
        self.daily_sales_btn = QPushButton("📅 Daily Sales")
        self.daily_sales_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.daily_sales_btn.clicked.connect(self.show_daily_sales)
        
        self.sp_performance_btn = QPushButton("👥 Sales Person Performance")
        self.sp_performance_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        self.sp_performance_btn.clicked.connect(self.show_sales_person_performance)
        
        export_btn = QPushButton("📥 Export to Excel")
        export_btn.setStyleSheet("background-color: #9C27B0; color: white; padding: 10px;")
        export_btn.clicked.connect(self.export_data)
        
        report_type_layout.addWidget(self.top_products_btn)
        report_type_layout.addWidget(self.daily_sales_btn)
        report_type_layout.addWidget(self.sp_performance_btn)
        report_type_layout.addWidget(export_btn)
        
        main_layout.addLayout(report_type_layout)
        
        # Report table
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.report_table)
        
        self.setLayout(main_layout)
    
    def create_filter_section(self) -> QHBoxLayout:
        """Create filter section with date range and sales person"""
        layout = QHBoxLayout()
        
        # Quick filters
        self.quick_filter = QComboBox()
        self.quick_filter.addItems([
            "Today", "This Month", "This Year", "Custom Range"
        ])
        self.quick_filter.currentTextChanged.connect(self.on_quick_filter_changed)
        
        # Date inputs
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        
        # Sales person filter (NEW)
        self.sales_person_filter = QComboBox()
        self.sales_person_filter.setMinimumWidth(150)
        
        # Apply button
        apply_btn = QPushButton("Apply Filter")
        apply_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        apply_btn.clicked.connect(self.apply_date_filter)
        
        layout.addWidget(QLabel("Quick Filter:"))
        layout.addWidget(self.quick_filter)
        layout.addWidget(QLabel("From:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("To:"))
        layout.addWidget(self.end_date)
        layout.addWidget(QLabel("Sales Person:"))
        layout.addWidget(self.sales_person_filter)
        layout.addWidget(apply_btn)
        layout.addStretch()
        
        return layout
    
    def load_sales_persons(self):
        """Load sales persons into filter dropdown"""
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        self.sales_person_filter.clear()
        self.sales_person_filter.addItem("All Sales Persons", None)
        
        for sp in sales_persons:
            status = " (Inactive)" if not sp['is_active'] else ""
            self.sales_person_filter.addItem(f"{sp['name']}{status}", sp['id'])
    
    def create_dashboard(self) -> QFrame:
        """Create dashboard with summary cards"""
        dashboard = QFrame()
        dashboard.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(dashboard)
        
        # Create cards
        self.total_sales_card = self.create_card("Total Sales", "₹0.00", "#4CAF50")
        self.total_bills_card = self.create_card("Total Bills", "0", "#2196F3")
        self.avg_bill_card = self.create_card("Avg Bill Value", "₹0.00", "#FF9800")
        self.total_tax_card = self.create_card("Total GST", "₹0.00", "#9C27B0")
        
        layout.addWidget(self.total_sales_card)
        layout.addWidget(self.total_bills_card)
        layout.addWidget(self.avg_bill_card)
        layout.addWidget(self.total_tax_card)
        
        return dashboard
    
    def create_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        value_label.setObjectName(f"{title}_value")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def load_dashboard(self):
        """Load dashboard data"""
        summary = report_manager.get_today_sales()
        
        self.update_card(self.total_sales_card, f"₹{summary.get('total_revenue', 0):.2f}")
        self.update_card(self.total_bills_card, str(summary.get('total_bills', 0)))
        self.update_card(self.avg_bill_card, f"₹{summary.get('avg_bill_value', 0):.2f}")
        self.update_card(self.total_tax_card, f"₹{summary.get('total_tax', 0):.2f}")
    
    def update_card(self, card: QFrame, value: str):
        """Update card value"""
        for child in card.children():
            if isinstance(child, QLabel) and "_value" in child.objectName():
                child.setText(value)
    
    def on_quick_filter_changed(self, filter_text):
        """Handle quick filter change"""
        today = QDate.currentDate()
        
        if filter_text == "Today":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
            self.apply_date_filter()
        elif filter_text == "This Month":
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
            self.apply_date_filter()
        elif filter_text == "This Year":
            self.start_date.setDate(QDate(today.year(), 1, 1))
            self.end_date.setDate(today)
            self.apply_date_filter()
    
    def apply_date_filter(self):
        """Apply date and sales person filter"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        sales_person_id = self.sales_person_filter.currentData()
        
        # Get summary with optional sales person filter
        if sales_person_id:
            # Filter by sales person
            summary = self.get_sales_person_summary(sales_person_id, start, end)
        else:
            # All sales persons
            summary = report_manager.get_sales_summary(start, end)
        
        self.update_card(self.total_sales_card, f"₹{summary.get('total_revenue', 0):.2f}")
        self.update_card(self.total_bills_card, str(summary.get('total_bills', 0)))
        self.update_card(self.avg_bill_card, f"₹{summary.get('avg_bill_value', 0):.2f}")
        self.update_card(self.total_tax_card, f"₹{summary.get('total_tax', 0):.2f}")
    
    def get_sales_person_summary(self, sales_person_id: int, start_date: str, end_date: str) -> dict:
        """Get summary for specific sales person"""
        try:
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_bills,
                        COALESCE(SUM(subtotal), 0) as total_sales,
                        COALESCE(SUM(total_tax), 0) as total_tax,
                        COALESCE(SUM(grand_total), 0) as total_revenue,
                        COALESCE(AVG(grand_total), 0) as avg_bill_value
                    FROM bills
                    WHERE sales_person_id = ?
                    AND DATE(created_at) BETWEEN ? AND ?
                """, (sales_person_id, start_date, end_date))
                
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error getting sales person summary: {e}")
            return {}
    
    def show_top_products(self):
        """Show top selling products"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        sales_person_id = self.sales_person_filter.currentData()
        
        if sales_person_id:
            products = self.get_top_products_by_sales_person(sales_person_id, start, end)
        else:
            products = report_manager.get_top_selling_products(20, start, end)
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "Product Name", "Quantity Sold", "Revenue", "No. of Bills"
        ])
        self.report_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.report_table.setItem(row, 0, QTableWidgetItem(product['product_name']))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(product['total_quantity'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{product['total_revenue']:.2f}"))
            self.report_table.setItem(row, 3, QTableWidgetItem(str(product['num_bills'])))
        
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def get_top_products_by_sales_person(self, sales_person_id: int, start_date: str, end_date: str) -> list:
        """Get top products for specific sales person"""
        try:
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        bi.product_name,
                        SUM(bi.quantity) as total_quantity,
                        SUM(bi.amount) as total_revenue,
                        COUNT(DISTINCT bi.bill_id) as num_bills
                    FROM bill_items bi
                    JOIN bills b ON bi.bill_id = b.id
                    WHERE b.sales_person_id = ?
                    AND DATE(b.created_at) BETWEEN ? AND ?
                    GROUP BY bi.product_name
                    ORDER BY total_revenue DESC
                    LIMIT 20
                """, (sales_person_id, start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    def show_daily_sales(self):
        """Show daily sales"""
        sales = report_manager.get_daily_sales(30)
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "Date", "Number of Bills", "Total Sales", "Total GST"
        ])
        self.report_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            # Format date
            date_obj = datetime.strptime(sale['sale_date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
            
            self.report_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(sale['num_bills'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{sale['total_sales']:.2f}"))
            self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{sale.get('total_tax', 0):.2f}"))
        
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def show_sales_person_performance(self):
        """Show sales person performance report"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "Sales Person", "Total Bills", "Total Revenue", "Avg Bill Value", "Total GST"
        ])
        self.report_table.setRowCount(len(sales_persons))
        
        for row, sp in enumerate(sales_persons):
            performance = db.get_sales_person_performance(sp['id'], start, end)
            
            # Get total tax
            total_tax = self.get_sales_person_tax(sp['id'], start, end)
            
            name_item = QTableWidgetItem(sp['name'])
            if not sp['is_active']:
                name_item.setForeground(Qt.gray)
            
            self.report_table.setItem(row, 0, name_item)
            self.report_table.setItem(row, 1, QTableWidgetItem(str(performance['total_bills'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{performance['total_revenue']:.2f}"))
            self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{performance['avg_bill_value']:.2f}"))
            self.report_table.setItem(row, 4, QTableWidgetItem(f"₹{total_tax:.2f}"))
        
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def get_sales_person_tax(self, sales_person_id: int, start_date: str, end_date: str) -> float:
        """Get total tax collected by sales person"""
        try:
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT COALESCE(SUM(total_tax), 0) as total_tax
                    FROM bills
                    WHERE sales_person_id = ?
                    AND DATE(created_at) BETWEEN ? AND ?
                """, (sales_person_id, start_date, end_date))
                
                result = cursor.fetchone()
                return result['total_tax'] if result else 0.0
        except Exception as e:
            logger.error(f"Error getting sales person tax: {e}")
            return 0.0
    
    def export_data(self):
        """Export data to Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            data = report_manager.export_sales_data(start, end)
            
            if not data:
                QMessageBox.warning(self, "No Data", "No data available for export")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # CREATE EXPORTS FOLDER (use absolute path)
            exports_folder = os.path.join(os.getcwd(), "data", "exports")
            os.makedirs(exports_folder, exist_ok=True)
            
            # Generate filename with date range
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            start_date = self.start_date.date().toString("dd-MM-yyyy")
            end_date = self.end_date.date().toString("dd-MM-yyyy")
            filename = f"Sales_Report_{start_date}_to_{end_date}_{timestamp}.xlsx"
            filepath = os.path.join(exports_folder, filename)
            
            # SAVE WITH FORMATTING
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Report')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Sales Report']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            QMessageBox.information(
                self, "Export Successful",
                f"Data exported successfully!\n\n"
                f"File: {filename}\n"
                f"Location: {exports_folder}\n"
                f"Records: {len(data)}\n"
                f"Date Range: {start_date} to {end_date}"
            )
            
            # Open file (only if it exists)
            if os.path.exists(filepath):
                os.startfile(filepath)
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            QMessageBox.warning(self, "Export Failed", f"Error: {str(e)}")
