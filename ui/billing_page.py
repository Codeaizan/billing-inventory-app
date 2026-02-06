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
        scroll.setStyleSheet("background-color: #EBF4DD;")
        
        # Content widget
        content = QWidget()
        content.setStyleSheet("background-color: #EBF4DD;")
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
                background-color: #EBF4DD;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #90AB8B;
            }
        """)
        panel.setMinimumWidth(500)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Add Products to Bill")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #5A7863; border: none;")
        layout.addWidget(title)
        
        # Product search section
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setMinimumWidth(60)
        search_label.setStyleSheet("color: #5A7863; font-weight: bold;")
        
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Type product name or scan barcode...")
        self.product_search.returnPressed.connect(self.on_search_product)
        self.product_search.setMinimumHeight(35)
        self.product_search.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px 10px;
                color: #3B4953;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        
        search_btn = QPushButton("🔍")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        search_btn.setMinimumHeight(35)
        search_btn.clicked.connect(self.on_search_product)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.product_search, 1)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Product details section
        product_group = QGroupBox("Selected Product Details")
        product_group.setStyleSheet("""
            QGroupBox {
                background-color: #5A7863;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: #5A7863;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        product_layout = QGridLayout()
        product_layout.setSpacing(8)
        
        self.selected_product_label = QLabel("No product selected")
        self.selected_product_label.setStyleSheet("color: #90AB8B; font-style: italic;")
        self.selected_product_label.setWordWrap(True)
        
        label_style = "color: #3B4953; font-weight: bold;"
        
        product_layout.addWidget(self.create_label("Product:", label_style), 0, 0)
        product_layout.addWidget(self.selected_product_label, 0, 1, 1, 3)
        
        product_layout.addWidget(self.create_label("MRP:", label_style), 1, 0)
        self.mrp_label = QLabel("₹0.00")
        self.mrp_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.mrp_label.setStyleSheet("color: #3B4953;")
        product_layout.addWidget(self.mrp_label, 1, 1)
        
        product_layout.addWidget(self.create_label("Discount:", label_style), 1, 2)
        self.discount_label = QLabel("0%")
        self.discount_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.discount_label.setStyleSheet("color: #3B4953;")
        product_layout.addWidget(self.discount_label, 1, 3)
        
        product_layout.addWidget(self.create_label("Rate:", label_style), 2, 0)
        self.rate_label = QLabel("₹0.00")
        self.rate_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.rate_label.setStyleSheet("color: #5A7863;")
        product_layout.addWidget(self.rate_label, 2, 1)
        
        product_layout.addWidget(self.create_label("Stock:", label_style), 2, 2)
        self.stock_label = QLabel("0")
        self.stock_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.stock_label.setStyleSheet("color: #3B4953;")
        product_layout.addWidget(self.stock_label, 2, 3)
        
        product_layout.addWidget(self.create_label("Quantity:", label_style), 3, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10000)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumHeight(30)
        self.quantity_spin.setStyleSheet("""
            QSpinBox {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
                font-weight: bold;
            }
            QSpinBox:focus {
                border: 2px solid #5A7863;
            }
        """)
        product_layout.addWidget(self.quantity_spin, 3, 1)
        
        add_btn = QPushButton("➕ Add to Cart")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;
                color: #EBF4DD;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        add_btn.setMinimumHeight(30)
        add_btn.clicked.connect(self.add_to_cart)
        product_layout.addWidget(add_btn, 3, 2, 1, 2)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)
        
        # Cart table
        cart_label = QLabel("Shopping Cart")
        cart_label.setFont(QFont("Arial", 12, QFont.Bold))
        cart_label.setStyleSheet("color: #5A7863; border: none;")
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
        self.cart_table.setMinimumHeight(200)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background-color: #90AB8B;
                alternate-background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                gridline-color: #90AB8B;
                color: #3B4953;
            }
            QTableWidget::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QHeaderView::section {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.cart_table)
        
        # Cart actions
        cart_actions = QHBoxLayout()
        
        remove_btn = QPushButton("🗑️ Remove Selected")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;
                color: #EBF4DD;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A7863;
            }
        """)
        remove_btn.clicked.connect(self.remove_from_cart)
        
        clear_btn = QPushButton("🧹 Clear Cart")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;
                color: #EBF4DD;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A7863;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        
        cart_actions.addWidget(remove_btn)
        cart_actions.addWidget(clear_btn)
        cart_actions.addStretch()
        
        layout.addLayout(cart_actions)
        
        return panel
    
    def create_label(self, text: str, style: str = "") -> QLabel:
        """Helper to create styled labels"""
        label = QLabel(text)
        if style:
            label.setStyleSheet(style)
        return label
    
    def create_right_panel(self) -> QFrame:
        """Create right panel with customer info and totals"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #EBF4DD;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #90AB8B;
            }
        """)
        panel.setMinimumWidth(350)
        panel.setMaximumWidth(500)
        
        # ✅ ADD SCROLL AREA FOR RIGHT PANEL
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Customer & Billing")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #5A7863; border: none;")
        layout.addWidget(title)
        
        # Sales Person Selection
        sp_layout = QHBoxLayout()
        sp_label = QLabel("Sales Person: *")
        sp_label.setStyleSheet("color: #3B4953; font-weight: bold;")
        sp_layout.addWidget(sp_label)
        
        self.sales_person_combo = QComboBox()
        self.sales_person_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                font-weight: bold;
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                color: #3B4953;
            }
            QComboBox:focus {
                border: 2px solid #5A7863;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #EBF4DD;
                selection-background-color: #90AB8B;
                selection-color: #EBF4DD;
            }
        """)
        self.sales_person_combo.setMinimumHeight(30)
        sp_layout.addWidget(self.sales_person_combo, 1)
        layout.addLayout(sp_layout)
        
        # GST Bill Toggle
        gst_layout = QHBoxLayout()
        self.gst_bill_checkbox = QCheckBox("GST Bill (5% Tax)")
        self.gst_bill_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #5A7863;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #90AB8B;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #5A7863;
                border: 2px solid #5A7863;
            }
        """)
        self.gst_bill_checkbox.stateChanged.connect(self.on_gst_toggle)
        gst_layout.addWidget(self.gst_bill_checkbox)
        gst_layout.addStretch()
        layout.addLayout(gst_layout)
        
        # Customer info
        customer_group = QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
            QGroupBox {
                background-color: #5A7863;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-weight: bold;
                color: #3B4953;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                padding-bottom: 15px;
            }
        """)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)
        
        # Customer search
        search_customer_layout = QHBoxLayout()
        search_customer_label = QLabel("Search:")
        search_customer_label.setMinimumWidth(60)
        search_customer_label.setStyleSheet("color: #EBF4DD; font-weight: bold;")
        
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Name or phone...")
        self.customer_search.textChanged.connect(self.on_customer_search)
        self.customer_search.setMinimumHeight(30)
        self.customer_search.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        
        search_customer_layout.addWidget(search_customer_label)
        search_customer_layout.addWidget(self.customer_search)
        customer_layout.addLayout(search_customer_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #90AB8B;")
        customer_layout.addWidget(separator)
        
        customer_layout.addWidget(self.create_label("Customer Name: *", "color: #EBF4DD; font-weight: bold;"))
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        self.customer_name.setMinimumHeight(30)
        self.customer_name.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        customer_layout.addWidget(self.customer_name)
        
        customer_layout.addWidget(self.create_label("Phone:", "color: #EBF4DD; font-weight: bold;"))
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Enter phone number")
        self.customer_phone.setMinimumHeight(30)
        self.customer_phone.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        customer_layout.addWidget(self.customer_phone)
        
        customer_layout.addWidget(self.create_label("Address:", "color: #EBF4DD; font-weight: bold;"))
        self.customer_address = QTextEdit()
        self.customer_address.setPlaceholderText("Enter address")
        self.customer_address.setMaximumHeight(60)
        self.customer_address.setStyleSheet("""
            QTextEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
            }
            QTextEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        customer_layout.addWidget(self.customer_address)
        
        # GSTIN field (shown only for GST bills)
        self.gstin_label = QLabel("GSTIN: *")
        self.gstin_label.setStyleSheet("color: #3B4953; font-weight: bold;")
        self.gstin_label.setVisible(False)
        customer_layout.addWidget(self.gstin_label)
        
        self.customer_gstin = QLineEdit()
        self.customer_gstin.setPlaceholderText("Enter GSTIN")
        self.customer_gstin.setMinimumHeight(30)
        self.customer_gstin.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 5px;
                color: #3B4953;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        self.customer_gstin.setVisible(False)
        customer_layout.addWidget(self.customer_gstin)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Bill summary
        summary_group = QGroupBox("Bill Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #5A7863;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(5)
        
        self.item_count_label = QLabel("Items: 0")
        self.item_count_label.setFont(QFont("Arial", 11))
        self.item_count_label.setStyleSheet("color: #3B4953;")
        summary_layout.addWidget(self.item_count_label)
        
        self.subtotal_label = QLabel("Subtotal: ₹0.00")
        self.subtotal_label.setFont(QFont("Arial", 11))
        self.subtotal_label.setStyleSheet("color: #3B4953;")
        summary_layout.addWidget(self.subtotal_label)
        
        self.discount_total_label = QLabel("Total Discount: ₹0.00")
        self.discount_total_label.setFont(QFont("Arial", 11))
        self.discount_total_label.setStyleSheet("color: #90AB8B; font-weight: bold;")
        summary_layout.addWidget(self.discount_total_label)
        
        # GST details (hidden by default)
        self.gst_frame = QFrame()
        self.gst_frame.setStyleSheet("background-color: transparent; border: none;")
        gst_details_layout = QVBoxLayout(self.gst_frame)
        gst_details_layout.setContentsMargins(0, 0, 0, 0)
        gst_details_layout.setSpacing(5)
        
        self.cgst_label = QLabel("CGST @ 2.5%: ₹0.00")
        self.cgst_label.setFont(QFont("Arial", 11))
        self.cgst_label.setStyleSheet("color: #5A7863;")
        gst_details_layout.addWidget(self.cgst_label)
        
        self.sgst_label = QLabel("SGST @ 2.5%: ₹0.00")
        self.sgst_label.setFont(QFont("Arial", 11))
        self.sgst_label.setStyleSheet("color: #5A7863;")
        gst_details_layout.addWidget(self.sgst_label)
        
        self.total_tax_label = QLabel("Total Tax: ₹0.00")
        self.total_tax_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.total_tax_label.setStyleSheet("color: #5A7863;")
        gst_details_layout.addWidget(self.total_tax_label)
        
        self.gst_frame.setVisible(False)
        summary_layout.addWidget(self.gst_frame)
        
        self.roundoff_label = QLabel("Round Off: ₹0.00")
        self.roundoff_label.setFont(QFont("Arial", 11))
        self.roundoff_label.setStyleSheet("color: #3B4953;")
        summary_layout.addWidget(self.roundoff_label)
        
        # Grand total
        grand_total_frame = QFrame()
        grand_total_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #3B4953);
                padding: 10px;
                border-radius: 8px;
            }
        """)
        grand_total_layout = QHBoxLayout(grand_total_frame)
        
        grand_label = QLabel("GRAND TOTAL:")
        grand_label.setStyleSheet("color: #EBF4DD; font-weight: bold;")
        grand_label.setFont(QFont("Arial", 12))
        
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setStyleSheet("color: #EBF4DD; font-weight: bold;")
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #90AB8B);
                color: #EBF4DD;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);
            }
            QPushButton:pressed {
                background: #3B4953;
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
            self.show_styled_message("Not Found", "Product not found", QMessageBox.Warning)
            return
        
        if len(results) == 1:
            self.current_product = results[0]
            self.display_product_details()
        else:
            # Show selection dialog
            self.show_product_selection_dialog(results)
    
    def show_product_selection_dialog(self, results):
        """Show dialog to select from multiple products"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Product")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
            }
            QListWidget {
                background-color: white;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                color: #3B4953;
            }
            QListWidget::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        
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
        self.selected_product_label.setStyleSheet("color: #5A7863; font-weight: bold;")
        
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
            self.show_styled_message("No Product", "Please select a product first", QMessageBox.Warning)
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
            self.selected_product_label.setStyleSheet("color: #5A7863; font-style: italic;")
            self.mrp_label.setText("₹0.00")
            self.discount_label.setText("0%")
            self.rate_label.setText("₹0.00")
            self.stock_label.setText("0")
        else:
            self.show_styled_message("Error", message, QMessageBox.Warning)
    
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
            self.show_styled_message("No Selection", "Please select an item to remove", QMessageBox.Warning)
            return
        
        billing_manager.remove_item_from_cart(current_row)
        self.refresh_cart()
    
    def clear_cart(self):
        """Clear entire cart"""
        if not billing_manager.get_cart_items():
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Clear Cart")
        msg_box.setText("Are you sure you want to clear the entire cart?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(self.get_message_box_style())
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            billing_manager.clear_cart()
            self.refresh_cart()
    
    def generate_bill(self):
        """Generate bill"""
        # Validate cart
        if not billing_manager.get_cart_items():
            self.show_styled_message("Empty Cart", "Please add items to cart first", QMessageBox.Warning)
            return
        
        # Validate customer name
        customer_name = self.customer_name.text().strip()
        if not customer_name:
            self.show_styled_message("Validation Error", "Customer name is required", QMessageBox.Warning)
            self.customer_name.setFocus()
            return
        
        # Validate sales person
        sales_person_id = self.sales_person_combo.currentData()
        if not sales_person_id:
            self.show_styled_message("Validation Error", "Please select a sales person", QMessageBox.Warning)
            return
        
        # Validate GSTIN for GST bills
        is_gst_bill = self.gst_bill_checkbox.isChecked()
        customer_gstin = self.customer_gstin.text().strip()
        
        if is_gst_bill and not customer_gstin:
            self.show_styled_message("Validation Error", "GSTIN is required for GST bills", QMessageBox.Warning)
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
                self.show_styled_message(
                    "PDF Error",
                    f"Bill saved but PDF generation failed.\n\nInvoice No: {bill_data['invoice_number']}",
                    QMessageBox.Warning
                )
        else:
            self.show_styled_message("Error", message, QMessageBox.Warning)
    
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
        dialog.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
            }
            QListWidget {
                background-color: white;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                color: #3B4953;
            }
            QListWidget::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        
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
        self.show_styled_message(
            "Customer Loaded",
            f"Customer details loaded: {customer['name']}\n\nYou can edit the information if needed.",
            QMessageBox.Information
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
    
    def show_styled_message(self, title: str, message: str, icon=QMessageBox.Information):
        """Show styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(self.get_message_box_style())
        msg_box.exec_()
    
    def get_message_box_style(self) -> str:
        """Get consistent message box styling"""
        return """
            QMessageBox {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """
