from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QSpinBox, QTextEdit, QMessageBox, QFrame,
                            QHeaderView, QCompleter, QGroupBox, QGridLayout, QCheckBox,
                            QDialog, QListWidget, QDialogButtonBox, QScrollArea)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QColor
from modules.billing import billing_manager
from modules.inventory import inventory_manager
from modules.gst_calculator import gst_calculator
from modules.auth import auth_manager
from database.db_manager import db
from utils.signals import app_signals
from utils.logger import logger


class BillingPage(QWidget):
    """Billing page for creating invoices"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        self.load_sales_persons()
        
        # Connect signal for real-time updates
        app_signals.inventory_updated.connect(self.load_products)
    
    def init_ui(self):
        """Initialize the user interface"""
        # ✅ CREATE SCROLL AREA
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Left panel - Product search and cart
        left_panel = self.create_left_panel()
        
        # Right panel - Customer info and billing
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 65)
        main_layout.addWidget(right_panel, 35)
        
        # ✅ SET CONTENT TO SCROLL AREA
        scroll.setWidget(content)
        
        # ✅ MAIN LAYOUT FOR PAGE
        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        self.setLayout(page_layout)
    
    def create_left_panel(self) -> QFrame:
        """Create left panel with product search and cart"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        panel.setMinimumWidth(500)  # ✅ SET MINIMUM WIDTH
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Add Products to Bill")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        # Product search section
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setMinimumWidth(60)
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Type product name or scan barcode...")
        self.product_search.returnPressed.connect(self.on_search_product)
        self.product_search.setMinimumHeight(35)
        
        search_btn = QPushButton("🔍")
        search_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 15px;")
        search_btn.setMinimumHeight(35)
        search_btn.clicked.connect(self.on_search_product)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.product_search, 1)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Product details section
        product_group = QGroupBox("Selected Product Details")
        product_layout = QGridLayout()
        product_layout.setSpacing(8)
        
        self.selected_product_label = QLabel("No product selected")
        self.selected_product_label.setStyleSheet("color: #666; font-style: italic;")
        self.selected_product_label.setWordWrap(True)
        
        product_layout.addWidget(QLabel("Product:"), 0, 0)
        product_layout.addWidget(self.selected_product_label, 0, 1, 1, 3)
        
        product_layout.addWidget(QLabel("MRP:"), 1, 0)
        self.mrp_label = QLabel("₹0.00")
        self.mrp_label.setFont(QFont("Arial", 11, QFont.Bold))
        product_layout.addWidget(self.mrp_label, 1, 1)
        
        product_layout.addWidget(QLabel("Discount:"), 1, 2)
        self.discount_label = QLabel("0%")
        self.discount_label.setFont(QFont("Arial", 11, QFont.Bold))
        product_layout.addWidget(self.discount_label, 1, 3)
        
        product_layout.addWidget(QLabel("Rate:"), 2, 0)
        self.rate_label = QLabel("₹0.00")
        self.rate_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.rate_label.setStyleSheet("color: #4CAF50;")
        product_layout.addWidget(self.rate_label, 2, 1)
        
        product_layout.addWidget(QLabel("Stock:"), 2, 2)
        self.stock_label = QLabel("0")
        self.stock_label.setFont(QFont("Arial", 11, QFont.Bold))
        product_layout.addWidget(self.stock_label, 2, 3)
        
        product_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10000)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(30)
        product_layout.addWidget(self.quantity_spin, 3, 1)
        
        add_btn = QPushButton("➕ Add to Cart")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        add_btn.setMinimumHeight(30)
        add_btn.clicked.connect(self.add_to_cart)
        product_layout.addWidget(add_btn, 3, 2, 1, 2)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)
        
        # Cart table
        cart_label = QLabel("Shopping Cart")
        cart_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(7)
        self.cart_table.setHorizontalHeaderLabels([
            "S.No", "Product", "MRP", "Disc%", "Rate", "Qty", "Amount"
        ])
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setMinimumHeight(200)  # ✅ SET MINIMUM HEIGHT
        
        layout.addWidget(self.cart_table)
        
        # Cart actions
        cart_actions = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        remove_btn.clicked.connect(self.remove_from_cart)
        
        clear_btn = QPushButton("🧹 Clear Cart")
        clear_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        clear_btn.clicked.connect(self.clear_cart)
        
        cart_actions.addWidget(remove_btn)
        cart_actions.addWidget(clear_btn)
        cart_actions.addStretch()
        
        layout.addLayout(cart_actions)
        
        return panel
    
    def create_right_panel(self) -> QFrame:
        """Create right panel with customer info and totals"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        panel.setMinimumWidth(350)  # ✅ SET MINIMUM WIDTH
        panel.setMaximumWidth(500)  # ✅ SET MAXIMUM WIDTH
        
        # ✅ ADD SCROLL AREA FOR RIGHT PANEL
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Customer & Billing")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        # Sales Person Selection
        sp_layout = QHBoxLayout()
        sp_layout.addWidget(QLabel("Sales Person: *"))
        self.sales_person_combo = QComboBox()
        self.sales_person_combo.setStyleSheet("padding: 5px; font-weight: bold;")
        self.sales_person_combo.setMinimumHeight(30)
        sp_layout.addWidget(self.sales_person_combo, 1)
        layout.addLayout(sp_layout)
        
        # GST Bill Toggle
        gst_layout = QHBoxLayout()
        self.gst_bill_checkbox = QCheckBox("GST Bill (5% Tax)")
        self.gst_bill_checkbox.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.gst_bill_checkbox.stateChanged.connect(self.on_gst_toggle)
        gst_layout.addWidget(self.gst_bill_checkbox)
        gst_layout.addStretch()
        layout.addLayout(gst_layout)
        
        # Customer info
        customer_group = QGroupBox("Customer Information")
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)
        
        # Customer search
        search_customer_layout = QHBoxLayout()
        search_customer_label = QLabel("Search:")
        search_customer_label.setMinimumWidth(60)
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Name or phone...")
        self.customer_search.textChanged.connect(self.on_customer_search)
        self.customer_search.setMinimumHeight(30)
        
        search_customer_layout.addWidget(search_customer_label)
        search_customer_layout.addWidget(self.customer_search)
        customer_layout.addLayout(search_customer_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd;")
        customer_layout.addWidget(separator)
        
        customer_layout.addWidget(QLabel("Customer Name: *"))
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        self.customer_name.setMinimumHeight(30)
        customer_layout.addWidget(self.customer_name)
        
        customer_layout.addWidget(QLabel("Phone:"))
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Enter phone number")
        self.customer_phone.setMinimumHeight(30)
        customer_layout.addWidget(self.customer_phone)
        
        customer_layout.addWidget(QLabel("Address:"))
        self.customer_address = QTextEdit()
        self.customer_address.setPlaceholderText("Enter address")
        self.customer_address.setMaximumHeight(60)
        customer_layout.addWidget(self.customer_address)
        
        # GSTIN field (shown only for GST bills)
        self.gstin_label = QLabel("GSTIN: *")
        self.gstin_label.setVisible(False)
        customer_layout.addWidget(self.gstin_label)
        
        self.customer_gstin = QLineEdit()
        self.customer_gstin.setPlaceholderText("Enter GSTIN")
        self.customer_gstin.setMinimumHeight(30)
        self.customer_gstin.setVisible(False)
        customer_layout.addWidget(self.customer_gstin)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Bill summary
        summary_group = QGroupBox("Bill Summary")
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(5)
        
        self.item_count_label = QLabel("Items: 0")
        self.item_count_label.setFont(QFont("Arial", 11))
        summary_layout.addWidget(self.item_count_label)
        
        self.subtotal_label = QLabel("Subtotal: ₹0.00")
        self.subtotal_label.setFont(QFont("Arial", 11))
        summary_layout.addWidget(self.subtotal_label)
        
        self.discount_total_label = QLabel("Total Discount: ₹0.00")
        self.discount_total_label.setFont(QFont("Arial", 11))
        self.discount_total_label.setStyleSheet("color: #f44336;")
        summary_layout.addWidget(self.discount_total_label)
        
        # GST details (hidden by default)
        self.gst_frame = QFrame()
        gst_details_layout = QVBoxLayout(self.gst_frame)
        gst_details_layout.setContentsMargins(0, 0, 0, 0)
        gst_details_layout.setSpacing(5)
        
        self.cgst_label = QLabel("CGST @ 2.5%: ₹0.00")
        self.cgst_label.setFont(QFont("Arial", 11))
        self.cgst_label.setStyleSheet("color: #2196F3;")
        gst_details_layout.addWidget(self.cgst_label)
        
        self.sgst_label = QLabel("SGST @ 2.5%: ₹0.00")
        self.sgst_label.setFont(QFont("Arial", 11))
        self.sgst_label.setStyleSheet("color: #2196F3;")
        gst_details_layout.addWidget(self.sgst_label)
        
        self.total_tax_label = QLabel("Total Tax: ₹0.00")
        self.total_tax_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.total_tax_label.setStyleSheet("color: #2196F3;")
        gst_details_layout.addWidget(self.total_tax_label)
        
        self.gst_frame.setVisible(False)
        summary_layout.addWidget(self.gst_frame)
        
        self.roundoff_label = QLabel("Round Off: ₹0.00")
        self.roundoff_label.setFont(QFont("Arial", 11))
        summary_layout.addWidget(self.roundoff_label)
        
        # Grand total
        grand_total_frame = QFrame()
        grand_total_frame.setStyleSheet("background-color: #4CAF50; padding: 10px; border-radius: 5px;")
        grand_total_layout = QHBoxLayout(grand_total_frame)
        
        grand_label = QLabel("GRAND TOTAL:")
        grand_label.setStyleSheet("color: white; font-weight: bold;")
        grand_label.setFont(QFont("Arial", 12))
        
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet("color: white; font-weight: bold;")
        self.grand_total_label.setFont(QFont("Arial", 16))
        
        grand_total_layout.addWidget(grand_label)
        grand_total_layout.addStretch()
        grand_total_layout.addWidget(self.grand_total_label)
        
        summary_layout.addWidget(grand_total_frame)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Generate bill button
        generate_btn = QPushButton("💰 Generate Bill")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        generate_btn.setMinimumHeight(50)
        generate_btn.clicked.connect(self.generate_bill)
        layout.addWidget(generate_btn)
        
        layout.addStretch()
        
        # Set scroll content
        scroll.setWidget(content)
        
        # Panel layout
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def load_products(self):
        """Load products for autocomplete"""
        products = inventory_manager.get_all_products()
        self.products_dict = {p['name']: p for p in products}
        
        # Setup autocomplete
        product_names = list(self.products_dict.keys())
        completer = QCompleter(product_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.product_search.setCompleter(completer)
        
        self.current_product = None
    
    def load_sales_persons(self):
        """Load sales persons into dropdown"""
        sales_persons = db.get_all_sales_persons(active_only=True)
        
        self.sales_person_combo.clear()
        self.sales_persons_dict = {}
        
        for sp in sales_persons:
            self.sales_person_combo.addItem(sp['name'], sp['id'])
            self.sales_persons_dict[sp['id']] = sp
    
    def on_gst_toggle(self):
        """Handle GST checkbox toggle"""
        is_gst = self.gst_bill_checkbox.isChecked()
        
        # Show/hide GSTIN field
        self.gstin_label.setVisible(is_gst)
        self.customer_gstin.setVisible(is_gst)
        
        # Recalculate totals
        self.refresh_cart()
    
    def on_search_product(self):
        """Handle product search"""
        search_text = self.product_search.text().strip()
        
        if not search_text:
            return
        
        # Check if exact match in autocomplete
        if search_text in self.products_dict:
            self.current_product = self.products_dict[search_text]
            self.display_product_details()
            return
        
        # Search in database
        results = inventory_manager.search_products(search_text)
        
        if not results:
            QMessageBox.warning(self, "Not Found", "Product not found")
            return
        
        if len(results) == 1:
            self.current_product = results[0]
            self.display_product_details()
        else:
            # Show selection dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Product")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout()
            list_widget = QListWidget()
            
            for product in results:
                list_widget.addItem(f"{product['name']} - Stock: {product['current_stock']}")
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            
            layout.addWidget(QLabel("Multiple products found. Please select one:"))
            layout.addWidget(list_widget)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted and list_widget.currentRow() >= 0:
                self.current_product = results[list_widget.currentRow()]
                self.display_product_details()
    
    def display_product_details(self):
        """Display selected product details"""
        if not self.current_product:
            return
        
        p = self.current_product
        
        self.selected_product_label.setText(p['name'])
        self.selected_product_label.setStyleSheet("color: #333; font-weight: bold;")
        
        self.mrp_label.setText(f"₹{p['mrp']:.2f}")
        self.discount_label.setText(f"{p['discount_percent']:.0f}%")
        self.rate_label.setText(f"₹{p['selling_price']:.2f}")
        self.stock_label.setText(str(p['current_stock']))
        
        # Set max quantity to available stock
        self.quantity_spin.setMaximum(p['current_stock'] if p['current_stock'] > 0 else 1)
        self.quantity_spin.setValue(1)
        
        # Focus on quantity
        self.quantity_spin.setFocus()
        self.quantity_spin.selectAll()
    
    def add_to_cart(self):
        """Add selected product to cart"""
        if not self.current_product:
            QMessageBox.warning(self, "No Product", "Please select a product first")
            return
        
        quantity = self.quantity_spin.value()
        
        success, message = billing_manager.add_item_to_cart(
            self.current_product, quantity
        )
        
        if success:
            self.refresh_cart()
            self.product_search.clear()
            self.product_search.setFocus()
            self.current_product = None
            self.selected_product_label.setText("No product selected")
            self.selected_product_label.setStyleSheet("color: #666; font-style: italic;")
            self.mrp_label.setText("₹0.00")
            self.discount_label.setText("0%")
            self.rate_label.setText("₹0.00")
            self.stock_label.setText("0")
        else:
            QMessageBox.warning(self, "Error", message)
    
    def refresh_cart(self):
        """Refresh cart display and totals"""
        items = billing_manager.get_cart_items()
        
        self.cart_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['product_name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"₹{item['mrp']:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item['discount_percent']:.0f}%"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"₹{item['rate']:.2f}"))
            self.cart_table.setItem(row, 5, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 6, QTableWidgetItem(f"₹{item['amount']:.2f}"))
        
        # Update totals
        is_gst_bill = self.gst_bill_checkbox.isChecked()
        totals = billing_manager.calculate_totals(is_gst_bill)
        
        self.item_count_label.setText(f"Items: {len(items)}")
        self.subtotal_label.setText(f"Subtotal: ₹{totals['subtotal']:.2f}")
        self.discount_total_label.setText(f"Total Discount: ₹{totals['discount_amount']:.2f}")
        
        # Show/hide GST details
        if is_gst_bill:
            self.gst_frame.setVisible(True)
            self.cgst_label.setText(f"CGST @ 2.5%: ₹{totals['cgst_amount']:.2f}")
            self.sgst_label.setText(f"SGST @ 2.5%: ₹{totals['sgst_amount']:.2f}")
            self.total_tax_label.setText(f"Total Tax: ₹{totals['total_tax']:.2f}")
        else:
            self.gst_frame.setVisible(False)
        
        self.roundoff_label.setText(f"Round Off: ₹{totals['round_off']:.2f}")
        self.grand_total_label.setText(f"₹{totals['grand_total']:.2f}")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        current_row = self.cart_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove")
            return
        
        billing_manager.remove_item_from_cart(current_row)
        self.refresh_cart()
    
    def clear_cart(self):
        """Clear entire cart"""
        if not billing_manager.get_cart_items():
            return
        
        reply = QMessageBox.question(
            self, "Clear Cart",
            "Are you sure you want to clear the entire cart?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            billing_manager.clear_cart()
            self.refresh_cart()
    
    def generate_bill(self):
        """Generate bill"""
        # Validate cart
        if not billing_manager.get_cart_items():
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart first")
            return
        
        # Validate customer name
        customer_name = self.customer_name.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "Validation Error", "Customer name is required")
            self.customer_name.setFocus()
            return
        
        # Validate sales person
        sales_person_id = self.sales_person_combo.currentData()
        if not sales_person_id:
            QMessageBox.warning(self, "Validation Error", "Please select a sales person")
            return
        
        # Validate GSTIN for GST bills
        is_gst_bill = self.gst_bill_checkbox.isChecked()
        customer_gstin = self.customer_gstin.text().strip()
        
        if is_gst_bill and not customer_gstin:
            QMessageBox.warning(self, "Validation Error", "GSTIN is required for GST bills")
            self.customer_gstin.setFocus()
            return
        
        # Prepare customer data
        customer_data = {
            'customer_name': customer_name,
            'customer_phone': self.customer_phone.text().strip(),
            'customer_address': self.customer_address.toPlainText().strip(),
            'customer_city': '',
            'customer_pin_code': '',
            'customer_gstin': customer_gstin
        }
        
        # Create bill
        success, message, bill_data = billing_manager.create_bill(
            customer_data, sales_person_id, is_gst_bill
        )
        
        if success:
            # Generate PDF
            from utils.pdf_generator import pdf_generator
            pdf_success, pdf_path = pdf_generator.generate_invoice(bill_data)
            
            if pdf_success:
                # Show preview dialog
                from ui.bill_preview_dialog import BillPreviewDialog
                preview_dialog = BillPreviewDialog(bill_data, pdf_path, self)
                preview_dialog.exec_()
                
                # Refresh entire app
                self.refresh_entire_app()
                
                # Clear cart and form after closing preview
                billing_manager.clear_cart()
                self.refresh_cart()
                self.clear_form()
            else:
                QMessageBox.warning(
                    self, "PDF Error",
                    f"Bill saved but PDF generation failed.\n\nInvoice No: {bill_data['invoice_number']}"
                )
        else:
            QMessageBox.warning(self, "Error", message)
    
    def clear_form(self):
        """Clear customer form"""
        self.customer_name.clear()
        self.customer_phone.clear()
        self.customer_address.clear()
        self.customer_gstin.clear()
        self.customer_search.clear()
        self.gst_bill_checkbox.setChecked(False)
        self.customer_name.setFocus()
    
    def on_customer_search(self):
        """Handle customer search with autocomplete"""
        search_text = self.customer_search.text().strip()
        
        if len(search_text) < 2:
            return
        
        # Search customers
        customers = db.search_customers(search_text)
        
        if not customers:
            return
        
        # If only one match and search text is exact phone, auto-fill
        if len(customers) == 1 and customers[0].get('phone') == search_text:
            self.fill_customer_data(customers[0])
            return
        
        # Show dropdown for multiple matches
        if len(customers) > 0:
            self.show_customer_selection_dialog(customers)
    
    def show_customer_selection_dialog(self, customers: list):
        """Show dialog to select from multiple customers"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Customer")
        dialog.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Found {len(customers)} customer(s). Select one:")
        layout.addWidget(info_label)
        
        list_widget = QListWidget()
        for customer in customers:
            phone = customer.get('phone', 'No phone')
            address = customer.get('address', 'No address')
            item_text = f"{customer['name']} - {phone}\n   {address[:50]}..."
            list_widget.addItem(item_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(list_widget)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted and list_widget.currentRow() >= 0:
            selected_customer = customers[list_widget.currentRow()]
            self.fill_customer_data(selected_customer)
    
    def fill_customer_data(self, customer: dict):
        """Fill customer form with data"""
        self.customer_name.setText(customer['name'])
        self.customer_phone.setText(customer.get('phone', ''))
        self.customer_address.setPlainText(customer.get('address', ''))
        self.customer_gstin.setText(customer.get('gstin', ''))
        
        # Show info message
        QMessageBox.information(
            self, "Customer Loaded",
            f"Customer details loaded: {customer['name']}\n\nYou can edit the information if needed."
        )
        
        # Clear search field
        self.customer_search.clear()
    
    def refresh_entire_app(self):
        """Refresh all components like app restart"""
        # Reload products in billing (this will fetch fresh data from database)
        self.load_products()
    
        # Reload sales persons
        self.load_sales_persons()
    
        # Emit signal to refresh other pages
        app_signals.inventory_updated.emit()
    
        logger.info("Application refreshed after bill generation")
