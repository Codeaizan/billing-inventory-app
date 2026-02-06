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
        # Initialize the parent QWidget class
        super().__init__()
        # Initialize the user interface components
        self.init_ui()
        # Load dashboard data with today's summary
        self.load_dashboard()
        # Load sales persons into filter dropdown
        self.load_sales_persons()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main vertical layout for the page
        main_layout = QVBoxLayout()
        # Set spacing between layout items to 15 pixels
        main_layout.setSpacing(15)
        # Set light cream background color for the entire widget
        self.setStyleSheet("background-color: #EBF4DD;")  # Light cream background
        
        # Create title label with "Reports & Analytics" text
        title = QLabel("Reports & Analytics")
        # Set font to Arial, 16pt, Bold
        title.setFont(QFont("Arial", 16, QFont.Bold))
        # Apply medium green color and remove border
        title.setStyleSheet("color: #5A7863; border: none;")  # Medium green text color
        # Add title to main layout
        main_layout.addWidget(title)
        
        # Create filter section with date range and sales person dropdown
        filter_layout = self.create_filter_section()
        # Add filter section to main layout
        main_layout.addLayout(filter_layout)
        
        # Create dashboard with summary cards
        dashboard = self.create_dashboard()
        # Add dashboard to main layout
        main_layout.addWidget(dashboard)
        
        # Create horizontal layout for report type buttons
        report_type_layout = QHBoxLayout()
        
        # Create "Top Products" button with package icon
        self.top_products_btn = QPushButton("📦 Top Products")
        # Apply medium green background styling with hover effect
        self.top_products_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;  /* Medium green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 10px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
                font-size: 11pt;  /* Font size */
            }
            QPushButton:hover {
                background-color: #90AB8B;  /* Sage green on hover */
            }
        """)
        # Connect click event to show_top_products method
        self.top_products_btn.clicked.connect(self.show_top_products)
        
        # Create "Daily Sales" button with calendar icon
        self.daily_sales_btn = QPushButton("📅 Daily Sales")
        # Apply sage green background styling with hover effect
        self.daily_sales_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;  /* Sage green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 10px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
                font-size: 11pt;  /* Font size */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Connect click event to show_daily_sales method
        self.daily_sales_btn.clicked.connect(self.show_daily_sales)
        
        # Create "Sales Person Performance" button with people icon
        self.sp_performance_btn = QPushButton("👥 Sales Person Performance")
        # Apply dark blue-grey background styling with hover effect
        self.sp_performance_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;  /* Dark blue-grey background */
                color: #EBF4DD;  /* Cream text color */
                padding: 10px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
                font-size: 11pt;  /* Font size */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Connect click event to show_sales_person_performance method
        self.sp_performance_btn.clicked.connect(self.show_sales_person_performance)
        
        # Create "Export to Excel" button with download icon
        export_btn = QPushButton("📥 Export to Excel")
        # Apply gradient background styling from medium green to sage
        export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #90AB8B);  /* Gradient from medium to sage green */
                color: #EBF4DD;  /* Cream text color */
                padding: 10px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
                font-size: 11pt;  /* Font size */
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);  /* Reversed gradient on hover */
            }
        """)
        # Connect click event to export_data method
        export_btn.clicked.connect(self.export_data)
        
        # Add "Top Products" button to layout
        report_type_layout.addWidget(self.top_products_btn)
        # Add "Daily Sales" button to layout
        report_type_layout.addWidget(self.daily_sales_btn)
        # Add "Sales Person Performance" button to layout
        report_type_layout.addWidget(self.sp_performance_btn)
        # Add "Export to Excel" button to layout
        report_type_layout.addWidget(export_btn)
        
        # Add report type button layout to main layout
        main_layout.addLayout(report_type_layout)
        
        # Create table widget for displaying report data
        self.report_table = QTableWidget()
        # Enable alternating row colors
        self.report_table.setAlternatingRowColors(True)
        # Disable editing of table cells
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Apply table styling with sage green theme
        self.report_table.setStyleSheet("""
            QTableWidget {
                background-color: #EBF4DD;  /* #EBF4DD background for main table */
                alternate-background-color: #EBF4DD;  /* Cream color for alternating rows */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                gridline-color: #90AB8B;  /* Sage green grid lines */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QTableWidget::item {
                padding: 8px;  /* Padding inside table cells */
            }
            QTableWidget::item:selected {
                background-color: #90AB8B;  /* Sage green background for selected items */
                color: #EBF4DD;  /* Cream text color for selected items */
            }
            QHeaderView::section {
                background-color: #5A7863;  /* Medium green background for headers */
                color: #EBF4DD;  /* Cream text color for headers */
                padding: 12px;  /* Padding inside header cells */
                border: none;  /* No border for header cells */
                font-weight: bold;  /* Bold text for headers */
                font-size: 11pt;  /* Font size for headers */
            }
        """)
        # Add report table to main layout
        main_layout.addWidget(self.report_table)
        
        # Set the main layout for this widget
        self.setLayout(main_layout)
    
    def create_filter_section(self) -> QHBoxLayout:
        """Create filter section with date range and sales person"""
        # Create horizontal layout for filters
        layout = QHBoxLayout()
        
        # Create dropdown for quick date filters
        self.quick_filter = QComboBox()
        # Add predefined date range options
        self.quick_filter.addItems([
            "Today", "This Month", "This Year", "Custom Range"
        ])
        # Connect selection change event to handler
        self.quick_filter.currentTextChanged.connect(self.on_quick_filter_changed)
        # Apply sage green styling to quick filter dropdown
        self.quick_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;  /* Internal padding */
                font-weight: bold;  /* Bold text */
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
                min-width: 120px;  /* Minimum width */
            }
            QComboBox:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
            QComboBox::drop-down {
                border: none;  /* No border for dropdown arrow */
            }
            QComboBox QAbstractItemView {
                background-color: #EBF4DD;  /* Cream background for dropdown list */
                selection-background-color: #90AB8B;  /* Sage green background for selected item */
                selection-color: #EBF4DD;  /* Cream text for selected item */
            }
        """)
        
        # Create date picker for start date
        self.start_date = QDateEdit()
        # Enable calendar popup for date selection
        self.start_date.setCalendarPopup(True)
        # Set initial date to today
        self.start_date.setDate(QDate.currentDate())
        # Set date display format to DD/MM/YYYY
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        # Apply date picker styling
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;  /* Internal padding */
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
                font-weight: bold;  /* Bold text */
                min-width: 120px;  /* Minimum width */
            }
            QDateEdit:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
            QDateEdit::drop-down {
                border: none;  /* No border for dropdown arrow */
                width: 20px;  /* Width of dropdown button */
            }
        """)
        
        # Create date picker for end date
        self.end_date = QDateEdit()
        # Enable calendar popup for date selection
        self.end_date.setCalendarPopup(True)
        # Set initial date to today
        self.end_date.setDate(QDate.currentDate())
        # Set date display format to DD/MM/YYYY
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        # Apply date picker styling (same as start date)
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;  /* Internal padding */
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
                font-weight: bold;  /* Bold text */
                min-width: 120px;  /* Minimum width */
            }
            QDateEdit:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
            QDateEdit::drop-down {
                border: none;  /* No border for dropdown arrow */
                width: 20px;  /* Width of dropdown button */
            }
        """)
        
        # Create dropdown for sales person filter
        self.sales_person_filter = QComboBox()
        # Set minimum width to prevent truncation
        self.sales_person_filter.setMinimumWidth(150)
        # Apply sage green styling to sales person dropdown
        self.sales_person_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;  /* Internal padding */
                font-weight: bold;  /* Bold text */
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QComboBox:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
            QComboBox::drop-down {
                border: none;  /* No border for dropdown arrow */
            }
            QComboBox QAbstractItemView {
                background-color: #EBF4DD;  /* Cream background for dropdown list */
                selection-background-color: #90AB8B;  /* Sage green background for selected item */
                selection-color: #EBF4DD;  /* Cream text for selected item */
            }
        """)
        
        # Create "Apply Filter" button
        apply_btn = QPushButton("Apply Filter")
        # Apply medium green styling
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;  /* Medium green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px 15px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #90AB8B;  /* Sage green on hover */
            }
        """)
        # Connect click event to apply_date_filter method
        apply_btn.clicked.connect(self.apply_date_filter)
        
        # Create "Quick Filter:" label with styling
        quick_label = QLabel("Quick Filter:")
        quick_label.setStyleSheet("color: #3B4953; font-weight: bold;")  # Dark text, bold
        
        # Create "From:" label with styling
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #3B4953; font-weight: bold;")  # Dark text, bold
        
        # Create "To:" label with styling
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #3B4953; font-weight: bold;")  # Dark text, bold
        
        # Create "Sales Person:" label with styling
        sp_label = QLabel("Sales Person:")
        sp_label.setStyleSheet("color: #3B4953; font-weight: bold;")  # Dark text, bold
        
        # Add "Quick Filter:" label to layout
        layout.addWidget(quick_label)
        # Add quick filter dropdown to layout
        layout.addWidget(self.quick_filter)
        # Add "From:" label to layout
        layout.addWidget(from_label)
        # Add start date picker to layout
        layout.addWidget(self.start_date)
        # Add "To:" label to layout
        layout.addWidget(to_label)
        # Add end date picker to layout
        layout.addWidget(self.end_date)
        # Add "Sales Person:" label to layout
        layout.addWidget(sp_label)
        # Add sales person dropdown to layout
        layout.addWidget(self.sales_person_filter)
        # Add apply button to layout
        layout.addWidget(apply_btn)
        # Add stretch to push all elements to the left
        layout.addStretch()
        
        # Return the configured filter layout
        return layout
    
    def load_sales_persons(self):
        """Load sales persons into filter dropdown"""
        # Fetch all sales persons from database (including inactive)
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        # Clear existing items from dropdown
        self.sales_person_filter.clear()
        # Add "All Sales Persons" option with None as data
        self.sales_person_filter.addItem("All Sales Persons", None)
        
        # Loop through each sales person
        for sp in sales_persons:
            # Add "(Inactive)" suffix if sales person is not active
            status = " (Inactive)" if not sp['is_active'] else ""
            # Add sales person to dropdown with name and status, store ID as data
            self.sales_person_filter.addItem(f"{sp['name']}{status}", sp['id'])
    
    def create_dashboard(self) -> QFrame:
        """Create dashboard with summary cards"""
        # Create frame container for dashboard
        dashboard = QFrame()
        # Apply #EBF4DD background with sage border
        dashboard.setStyleSheet("""
            QFrame {
                background-color: #EBF4DD;  /* #EBF4DD background */
                border-radius: 10px;  /* Rounded corners */
                padding: 15px;  /* Internal padding */
                border: 2px solid #90AB8B;  /* Sage green border */
            }
        """)
        
        # Create horizontal layout for dashboard cards
        layout = QHBoxLayout(dashboard)
        
        # Create "Total Sales" card with medium green color
        self.total_sales_card = self.create_card("Total Sales", "₹0.00", "#5A7863")
        # Create "Total Bills" card with sage green color
        self.total_bills_card = self.create_card("Total Bills", "0", "#90AB8B")
        # Create "Avg Bill Value" card with dark blue-grey color
        self.avg_bill_card = self.create_card("Avg Bill Value", "₹0.00", "#3B4953")
        # Create "Total GST" card with medium green color
        self.total_tax_card = self.create_card("Total GST", "₹0.00", "#5A7863")
        
        # Add "Total Sales" card to layout
        layout.addWidget(self.total_sales_card)
        # Add "Total Bills" card to layout
        layout.addWidget(self.total_bills_card)
        # Add "Avg Bill Value" card to layout
        layout.addWidget(self.avg_bill_card)
        # Add "Total GST" card to layout
        layout.addWidget(self.total_tax_card)
        
        # Return the configured dashboard frame
        return dashboard
    
    def create_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card"""
        # Create frame container for card
        card = QFrame()
        # Apply colored background with rounded corners
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};  /* Card background color */
                border-radius: 8px;  /* Rounded corners */
                padding: 15px;  /* Internal padding */
            }}
        """)
        
        # Create vertical layout for card content
        layout = QVBoxLayout(card)
        
        # Create label for card title
        title_label = QLabel(title)
        # Apply #EBF4DD text color and smaller font
        title_label.setStyleSheet("color: #EBF4DD; font-size: 12px; font-weight: bold;")  # Cream text
        
        # Create label for card value
        value_label = QLabel(value)
        # Apply #EBF4DD text color, large font, and bold weight
        value_label.setStyleSheet("color: #EBF4DD; font-size: 24px; font-weight: bold;")  # Cream text, large, bold
        # Set object name to identify label later for updates
        value_label.setObjectName(f"{title}_value")
        
        # Add title label to card layout
        layout.addWidget(title_label)
        # Add value label to card layout
        layout.addWidget(value_label)
        
        # Return the configured card frame
        return card
    
    def load_dashboard(self):
        """Load dashboard data"""
        # Get today's sales summary from report manager
        summary = report_manager.get_today_sales()
        
        # Update "Total Sales" card with revenue value
        self.update_card(self.total_sales_card, f"₹{summary.get('total_revenue', 0):.2f}")
        # Update "Total Bills" card with bill count
        self.update_card(self.total_bills_card, str(summary.get('total_bills', 0)))
        # Update "Avg Bill Value" card with average value
        self.update_card(self.avg_bill_card, f"₹{summary.get('avg_bill_value', 0):.2f}")
        # Update "Total GST" card with tax amount
        self.update_card(self.total_tax_card, f"₹{summary.get('total_tax', 0):.2f}")
    
    def update_card(self, card: QFrame, value: str):
        """Update card value"""
        # Loop through all child widgets in the card
        for child in card.children():
            # Check if child is a QLabel and has "_value" in its object name
            if isinstance(child, QLabel) and "_value" in child.objectName():
                # Update the label text with new value
                child.setText(value)
    
    def on_quick_filter_changed(self, filter_text):
        """Handle quick filter change"""
        # Get today's date
        today = QDate.currentDate()
        
        # Check if "Today" filter is selected
        if filter_text == "Today":
            # Set start date to today
            self.start_date.setDate(today)
            # Set end date to today
            self.end_date.setDate(today)
            # Apply the filter immediately
            self.apply_date_filter()
        # Check if "This Month" filter is selected
        elif filter_text == "This Month":
            # Set start date to first day of current month
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            # Set end date to today
            self.end_date.setDate(today)
            # Apply the filter immediately
            self.apply_date_filter()
        # Check if "This Year" filter is selected
        elif filter_text == "This Year":
            # Set start date to January 1st of current year
            self.start_date.setDate(QDate(today.year(), 1, 1))
            # Set end date to today
            self.end_date.setDate(today)
            # Apply the filter immediately
            self.apply_date_filter()
    
    def apply_date_filter(self):
        """Apply date and sales person filter"""
        # Get start date in YYYY-MM-DD format
        start = self.start_date.date().toString("yyyy-MM-dd")
        # Get end date in YYYY-MM-DD format
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Get selected sales person ID from dropdown
        sales_person_id = self.sales_person_filter.currentData()
        
        # Check if specific sales person is selected
        if sales_person_id:
            # Get summary filtered by sales person
            summary = self.get_sales_person_summary(sales_person_id, start, end)
        else:
            # Get summary for all sales persons
            summary = report_manager.get_sales_summary(start, end)
        
        # Update "Total Sales" card with filtered revenue
        self.update_card(self.total_sales_card, f"₹{summary.get('total_revenue', 0):.2f}")
        # Update "Total Bills" card with filtered bill count
        self.update_card(self.total_bills_card, str(summary.get('total_bills', 0)))
        # Update "Avg Bill Value" card with filtered average
        self.update_card(self.avg_bill_card, f"₹{summary.get('avg_bill_value', 0):.2f}")
        # Update "Total GST" card with filtered tax amount
        self.update_card(self.total_tax_card, f"₹{summary.get('total_tax', 0):.2f}")
    
    def get_sales_person_summary(self, sales_person_id: int, start_date: str, end_date: str) -> dict:
        """Get summary for specific sales person"""
        try:
            # Get database connection
            with db.get_connection() as conn:
                # Execute SQL query to get sales person summary
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
                
                # Fetch query result
                result = cursor.fetchone()
                # Return result as dictionary if exists, otherwise empty dict
                return dict(result) if result else {}
        except Exception as e:
            # Log error if query fails
            logger.error(f"Error getting sales person summary: {e}")
            # Return empty dictionary on error
            return {}
    
    def show_top_products(self):
        """Show top selling products"""
        # Get start date in YYYY-MM-DD format
        start = self.start_date.date().toString("yyyy-MM-dd")
        # Get end date in YYYY-MM-DD format
        end = self.end_date.date().toString("yyyy-MM-dd")
        # Get selected sales person ID from dropdown
        sales_person_id = self.sales_person_filter.currentData()
        
        # Check if specific sales person is selected
        if sales_person_id:
            # Get top products filtered by sales person
            products = self.get_top_products_by_sales_person(sales_person_id, start, end)
        else:
            # Get top 20 products for all sales persons
            products = report_manager.get_top_selling_products(20, start, end)
        
        # Set table to have 4 columns
        self.report_table.setColumnCount(4)
        # Set column headers
        self.report_table.setHorizontalHeaderLabels([
            "Product Name", "Quantity Sold", "Revenue", "No. of Bills"
        ])
        # Set number of rows to match number of products
        self.report_table.setRowCount(len(products))
        
        # Loop through each product with index
        for row, product in enumerate(products):
            # Set product name in column 0
            self.report_table.setItem(row, 0, QTableWidgetItem(product['product_name']))
            # Set quantity sold in column 1
            self.report_table.setItem(row, 1, QTableWidgetItem(str(product['total_quantity'])))
            # Set revenue with rupee symbol in column 2
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{product['total_revenue']:.2f}"))
            # Set number of bills in column 3
            self.report_table.setItem(row, 3, QTableWidgetItem(str(product['num_bills'])))
        
        # Make product name column stretch to fill available space
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def get_top_products_by_sales_person(self, sales_person_id: int, start_date: str, end_date: str) -> list:
        """Get top products for specific sales person"""
        try:
            # Get database connection
            with db.get_connection() as conn:
                # Execute SQL query to get top products by sales person
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
                
                # Return list of dictionaries for each row
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            # Log error if query fails
            logger.error(f"Error getting top products: {e}")
            # Return empty list on error
            return []
    
    def show_daily_sales(self):
        """Show daily sales"""
        # Get daily sales data for last 30 days
        sales = report_manager.get_daily_sales(30)
        
        # Set table to have 4 columns
        self.report_table.setColumnCount(4)
        # Set column headers
        self.report_table.setHorizontalHeaderLabels([
            "Date", "Number of Bills", "Total Sales", "Total GST"
        ])
        # Set number of rows to match number of sales records
        self.report_table.setRowCount(len(sales))
        
        # Loop through each sale record with index
        for row, sale in enumerate(sales):
            # Parse date string from YYYY-MM-DD format
            date_obj = datetime.strptime(sale['sale_date'], '%Y-%m-%d')
            # Format date to DD/MM/YYYY format
            formatted_date = date_obj.strftime('%d/%m/%Y')
            
            # Set formatted date in column 0
            self.report_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            # Set number of bills in column 1
            self.report_table.setItem(row, 1, QTableWidgetItem(str(sale['num_bills'])))
            # Set total sales with rupee symbol in column 2
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{sale['total_sales']:.2f}"))
            # Set total GST with rupee symbol in column 3
            self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{sale.get('total_tax', 0):.2f}"))
        
        # Make date column stretch to fill available space
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def show_sales_person_performance(self):
        """Show sales person performance report"""
        # Get start date in YYYY-MM-DD format
        start = self.start_date.date().toString("yyyy-MM-dd")
        # Get end date in YYYY-MM-DD format
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        # Fetch all sales persons from database (including inactive)
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        # Set table to have 5 columns
        self.report_table.setColumnCount(5)
        # Set column headers
        self.report_table.setHorizontalHeaderLabels([
            "Sales Person", "Total Bills", "Total Revenue", "Avg Bill Value", "Total GST"
        ])
        # Set number of rows to match number of sales persons
        self.report_table.setRowCount(len(sales_persons))
        
        # Loop through each sales person with index
        for row, sp in enumerate(sales_persons):
            # Get performance data for this sales person
            performance = db.get_sales_person_performance(sp['id'], start, end)
            
            # Get total tax collected by this sales person
            total_tax = self.get_sales_person_tax(sp['id'], start, end)
            
            # Create table item for sales person name
            name_item = QTableWidgetItem(sp['name'])
            # If sales person is inactive, set gray color
            if not sp['is_active']:
                name_item.setForeground(Qt.gray)  # Gray text for inactive sales persons
            
            # Set sales person name in column 0
            self.report_table.setItem(row, 0, name_item)
            # Set total bills in column 1
            self.report_table.setItem(row, 1, QTableWidgetItem(str(performance['total_bills'])))
            # Set total revenue with rupee symbol in column 2
            self.report_table.setItem(row, 2, QTableWidgetItem(f"₹{performance['total_revenue']:.2f}"))
            # Set average bill value with rupee symbol in column 3
            self.report_table.setItem(row, 3, QTableWidgetItem(f"₹{performance['avg_bill_value']:.2f}"))
            # Set total GST with rupee symbol in column 4
            self.report_table.setItem(row, 4, QTableWidgetItem(f"₹{total_tax:.2f}"))
        
        # Make sales person name column stretch to fill available space
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def get_sales_person_tax(self, sales_person_id: int, start_date: str, end_date: str) -> float:
        """Get total tax collected by sales person"""
        try:
            # Get database connection
            with db.get_connection() as conn:
                # Execute SQL query to get total tax by sales person
                cursor = conn.execute("""
                    SELECT COALESCE(SUM(total_tax), 0) as total_tax
                    FROM bills
                    WHERE sales_person_id = ?
                    AND DATE(created_at) BETWEEN ? AND ?
                """, (sales_person_id, start_date, end_date))
                
                # Fetch query result
                result = cursor.fetchone()
                # Return tax amount if exists, otherwise 0.0
                return result['total_tax'] if result else 0.0
        except Exception as e:
            # Log error if query fails
            logger.error(f"Error getting sales person tax: {e}")
            # Return 0.0 on error
            return 0.0
    
    def export_data(self):
        """Export data to Excel"""
        try:
            # Import pandas for Excel export
            import pandas as pd
            # Import datetime for timestamp
            from datetime import datetime
            # Import os for file path operations
            import os
            
            # Get start date in YYYY-MM-DD format
            start = self.start_date.date().toString("yyyy-MM-dd")
            # Get end date in YYYY-MM-DD format
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            # Get sales data from report manager
            data = report_manager.export_sales_data(start, end)
            
            # Check if no data is available
            if not data:
                # Show warning message to user
                self.show_styled_message("No Data", "No data available for export", QMessageBox.Warning)
                # Exit function
                return
            
            # Convert data list to pandas DataFrame
            df = pd.DataFrame(data)
            
            # Create exports folder path inside data directory
            exports_folder = os.path.join(os.getcwd(), "data", "exports")
            # Create exports folder if it doesn't exist
            os.makedirs(exports_folder, exist_ok=True)
            
            # Generate timestamp in YYYYMMDD_HHMMSS format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Format start date as DD-MM-YYYY for filename
            start_date = self.start_date.date().toString("dd-MM-yyyy")
            # Format end date as DD-MM-YYYY for filename
            end_date = self.end_date.date().toString("dd-MM-yyyy")
            # Create filename with date range and timestamp
            filename = f"Sales_Report_{start_date}_to_{end_date}_{timestamp}.xlsx"
            # Create full file path
            filepath = os.path.join(exports_folder, filename)
            
            # Create Excel writer with openpyxl engine
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write DataFrame to Excel file
                df.to_excel(writer, index=False, sheet_name='Sales Report')
                
                # Get worksheet for formatting
                worksheet = writer.sheets['Sales Report']
                # Loop through each column in worksheet
                for column in worksheet.columns:
                    # Initialize max length variable
                    max_length = 0
                    # Get column letter (A, B, C, etc.)
                    column_letter = column[0].column_letter
                    # Loop through each cell in column
                    for cell in column:
                        try:
                            # Check if cell value length is greater than max
                            if len(str(cell.value)) > max_length:
                                # Update max length
                                max_length = len(str(cell.value))
                        except:
                            # Skip if error occurs
                            pass
                    # Calculate adjusted width (add 2 for padding, max 50)
                    adjusted_width = min(max_length + 2, 50)
                    # Set column width
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Show success message with styled dialog
            self.show_styled_message(
                "Export Successful",
                f"Data exported successfully!\n\n"
                f"File: {filename}\n"
                f"Location: {exports_folder}\n"
                f"Records: {len(data)}\n"
                f"Date Range: {start_date} to {end_date}",
                QMessageBox.Information
            )
            
            # Check if file exists before opening
            if os.path.exists(filepath):
                # Open the Excel file in default application
                os.startfile(filepath)
            
        except Exception as e:
            # Log error if export fails
            logger.error(f"Export error: {e}")
            # Show error message to user
            self.show_styled_message("Export Failed", f"Error: {str(e)}", QMessageBox.Warning)
    
    def show_styled_message(self, title: str, message: str, icon=QMessageBox.Information):
        """Show styled message box"""
        # Create message box with this widget as parent
        msg_box = QMessageBox(self)
        # Set message box icon (Information, Warning, etc.)
        msg_box.setIcon(icon)
        # Set window title
        msg_box.setWindowTitle(title)
        # Set message text
        msg_box.setText(message)
        # Apply consistent styling with color palette
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #EBF4DD;  /* Light cream background */
            }
            QLabel {
                color: #3B4953;  /* Dark blue-grey text color */
                font-size: 11pt;  /* Font size */
            }
            QPushButton {
                background-color: #5A7863;  /* Medium green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px 20px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
                min-width: 80px;  /* Minimum button width */
            }
            QPushButton:hover {
                background-color: #90AB8B;  /* Sage green on hover */
            }
        """)
        # Show message box and wait for user response
        msg_box.exec_()
