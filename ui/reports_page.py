from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QDateEdit, QGroupBox, QFrame,
                            QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from modules.reports import report_manager
from datetime import datetime
from utils.logger import logger

class ReportsPage(QWidget):
    """Reports and analytics page"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_dashboard()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        title = QLabel("Reports & Analytics")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(title)
        
        # Date range selector
        date_range_layout = self.create_date_range_selector()
        main_layout.addLayout(date_range_layout)
        
        # Dashboard cards
        dashboard = self.create_dashboard()
        main_layout.addWidget(dashboard)
        
        # Report tabs
        report_type_layout = QHBoxLayout()
        
        self.top_products_btn = QPushButton("Top Selling Products")
        self.top_products_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.top_products_btn.clicked.connect(self.show_top_products)
        
        self.payment_summary_btn = QPushButton("Payment Summary")
        self.payment_summary_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        self.payment_summary_btn.clicked.connect(self.show_payment_summary)
        
        self.daily_sales_btn = QPushButton("Daily Sales")
        self.daily_sales_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        self.daily_sales_btn.clicked.connect(self.show_daily_sales)
        
        export_btn = QPushButton("📥 Export to Excel")
        export_btn.setStyleSheet("background-color: #9C27B0; color: white; padding: 10px;")
        export_btn.clicked.connect(self.export_data)
        
        report_type_layout.addWidget(self.top_products_btn)
        report_type_layout.addWidget(self.payment_summary_btn)
        report_type_layout.addWidget(self.daily_sales_btn)
        report_type_layout.addWidget(export_btn)
        
        main_layout.addLayout(report_type_layout)
        
        # Report table
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.report_table)
        
        self.setLayout(main_layout)
    
    def create_date_range_selector(self) -> QHBoxLayout:
        """Create date range selector"""
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
        layout.addWidget(apply_btn)
        layout.addStretch()
        
        return layout
    
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
        self.total_discount_card = self.create_card("Total Discount", "₹0.00", "#f44336")
        
        layout.addWidget(self.total_sales_card)
        layout.addWidget(self.total_bills_card)
        layout.addWidget(self.avg_bill_card)
        layout.addWidget(self.total_discount_card)
        
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
        
        self.update_card(self.total_sales_card, f"₹{summary['total_sales']:.2f}")
        self.update_card(self.total_bills_card, str(summary['total_bills']))
        self.update_card(self.avg_bill_card, f"₹{summary['avg_bill_value']:.2f}")
        self.update_card(self.total_discount_card, f"₹{summary['total_discount']:.2f}")
    
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
        """Apply date filter"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        summary = report_manager.get_sales_summary(start, end)
        
        self.update_card(self.total_sales_card, f"₹{summary['total_sales']:.2f}")
        self.update_card(self.total_bills_card, str(summary['total_bills']))
        self.update_card(self.avg_bill_card, f"₹{summary['avg_bill_value']:.2f}")
        self.update_card(self.total_discount_card, f"₹{summary['total_discount']:.2f}")
    
    def show_top_products(self):
        """Show top selling products"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
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
    
    def show_payment_summary(self):
        """Show payment mode summary"""
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        payments = report_manager.get_payment_mode_summary(start, end)
        
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels([
            "Payment Mode", "Number of Transactions", "Total Amount"
        ])
        self.report_table.setRowCount(len(payments))
        
        for row, payment in enumerate(payments):
            self.report_table.setItem(row, 0, QTableWidgetItem(payment['payment_mode']))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(payment['count'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{payment['total_amount']:.2f}"))
        
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def show_daily_sales(self):
        """Show daily sales"""
        sales = report_manager.get_daily_sales(30)
        
        self.report_table.setColumnCount(3)
        self.report_table.setHorizontalHeaderLabels([
            "Date", "Number of Bills", "Total Sales"
        ])
        self.report_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            # Format date
            date_obj = datetime.strptime(sale['sale_date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
            
            self.report_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(sale['num_bills'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{sale['total_sales']:.2f}"))
        
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def export_data(self):
        """Export data to Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            data = report_manager.export_sales_data(start, end)
            
            if not data:
                QMessageBox.warning(self, "No Data", "No data available for export")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.xlsx"
            
            # Save to Excel
            df.to_excel(filename, index=False)
            
            QMessageBox.information(
                self, "Export Successful",
                f"Data exported successfully!\n\nFile: {filename}"
            )
            
            # Open file
            import os
            os.startfile(filename)
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            QMessageBox.warning(self, "Export Failed", f"Error: {str(e)}")
