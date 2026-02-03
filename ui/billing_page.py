from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QSpinBox, QTextEdit, QMessageBox, QFrame,
                            QHeaderView, QCompleter, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QFont, QColor
from modules.billing import billing_manager
from modules.inventory import inventory_manager
from modules.gst_calculator import gst_calculator
from modules.auth import auth_manager
from database.db_manager import db
from utils.constants import PAYMENT_MODES
from utils.logger import logger

class BillingPage(QWidget):
    """Billing page for creating invoices"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        
        # Left panel - Product search and cart
        left_panel = self.create_left_panel()
        
        # Right panel - Customer info and billing
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 65)
        main_layout.addWidget(right_panel, 35)
        
        self.setLayout(main_layout)
    
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
        
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Add Products to Bill")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        # Product search section
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search Product:")
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Type product name or scan barcode...")
        self.product_search.returnPressed.connect(self.on_search_product)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setStyleSheet("background-color: #2196F3; color: white;")
        search_btn.clicked.connect(self.on_search_product)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.product_search, 1)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Product details section
        product_group = QGroupBox("Selected Product Details")
        product_layout = QGridLayout()
        
        self.selected_product_label = QLabel("No product selected")
        self.selected_product_label.setStyleSheet("color: #666; font-style: italic;")
        
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
        product_layout.addWidget(self.quantity_spin, 3, 1)
        
        add_btn = QPushButton("➕ Add to Cart")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
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
        
        layout.addWidget(self.cart_table)
        
        # Cart actions
        cart_actions = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.setStyleSheet("background-color: #f44336; color: white;")
        remove_btn.clicked.connect(self.remove_from_cart)
        
        clear_btn = QPushButton("🧹 Clear Cart")
        clear_btn.setStyleSheet("background-color: #FF9800; color: white;")
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
        
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Customer & Billing")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        layout.addWidget(title)
        
        # Customer info
        customer_group = QGroupBox("Customer Information")
        customer_layout = QVBoxLayout()
        
        customer_layout.addWidget(QLabel("Customer Name: *"))
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        customer_layout.addWidget(self.customer_name)
        
        customer_layout.addWidget(QLabel("Phone:"))
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Enter phone number")
        customer_layout.addWidget(self.customer_phone)
        
        customer_layout.addWidget(QLabel("Address:"))
        self.customer_address = QTextEdit()
        self.customer_address.setPlaceholderText("Enter address")
        self.customer_address.setMaximumHeight(60)
        customer_layout.addWidget(self.customer_address)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Bill summary
        summary_group = QGroupBox("Bill Summary")
        summary_layout = QVBoxLayout()
        
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
        
        # Payment mode
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Payment Mode:"))
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(PAYMENT_MODES)
        payment_layout.addWidget(self.payment_mode)
        layout.addLayout(payment_layout)
        
        # Generate bill button
        generate_btn = QPushButton("💰 Generate Bill")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        generate_btn.clicked.connect(self.generate_bill)
        layout.addWidget(generate_btn)
        
        layout.addStretch()
        
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
            from PyQt5.QtWidgets import QDialog, QListWidget, QDialogButtonBox
            
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
        """Refresh cart display"""
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
        
        # Update summary
        summary = billing_manager.get_cart_summary()
        self.item_count_label.setText(f"Items: {summary['item_count']}")
        self.subtotal_label.setText(f"Subtotal: ₹{summary['subtotal']:.2f}")
        self.discount_total_label.setText(f"Total Discount: ₹{summary['total_discount']:.2f}")
        self.roundoff_label.setText(f"Round Off: ₹{summary['round_off']:.2f}")
        self.grand_total_label.setText(f"₹{summary['grand_total']:.2f}")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        current_row = self.cart_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove")
            return
        
        success, message = billing_manager.remove_item_from_cart(current_row)
        
        if success:
            self.refresh_cart()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if not billing_manager.get_cart_items():
            return
        
        reply = QMessageBox.question(
            self, "Clear Cart",
            "Are you sure you want to clear the cart?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            billing_manager.clear_cart()
            self.refresh_cart()
            self.customer_name.clear()
            self.customer_phone.clear()
            self.customer_address.clear()
    
    def generate_bill(self):
        """Generate bill"""
        # Validate customer name
        customer_name = self.customer_name.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "Required", "Customer name is required")
            self.customer_name.setFocus()
            return
        
        # Check if cart has items
        if not billing_manager.get_cart_items():
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart")
            return
        
        # Set customer info
        customer_data = {
            'name': customer_name,
            'phone': self.customer_phone.text().strip(),
            'address': self.customer_address.toPlainText().strip()
        }
        
        billing_manager.set_customer_info(customer_data)
        
        # Get payment mode
        payment_mode = self.payment_mode.currentText()
        
        # Create bill
        user_id = auth_manager.get_current_user_id()
        success, message, bill_id = billing_manager.create_bill(
            payment_mode=payment_mode,
            created_by=user_id
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            
            # Ask if user wants to print
            reply = QMessageBox.question(
                self, "Print Bill",
                "Bill created successfully!\n\nDo you want to generate PDF?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.generate_pdf(bill_id)
            
            # Clear form
            self.clear_cart()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def generate_pdf(self, bill_id: int):
        """Generate PDF invoice"""
        try:
            from utils.pdf_generator import PDFGenerator
            
            bill = db.get_bill_by_id(bill_id)
            if not bill:
                QMessageBox.warning(self, "Error", "Bill not found")
                return
            
            pdf_gen = PDFGenerator()
            success, pdf_path = pdf_gen.generate_invoice(bill)
            
            if success:
                QMessageBox.information(
                    self, "PDF Generated",
                    f"Invoice PDF generated successfully!\n\n{pdf_path}"
                )
                
                # Open PDF
                import os
                os.startfile(pdf_path)
            else:
                QMessageBox.warning(self, "Error", "Failed to generate PDF")
                
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            QMessageBox.warning(self, "Error", f"PDF generation error: {str(e)}")
