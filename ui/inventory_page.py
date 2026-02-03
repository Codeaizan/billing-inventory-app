from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QMessageBox, QFrame, QHeaderView,
                            QDialog, QFormLayout, QDialogButtonBox, QSpinBox,
                            QDoubleSpinBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from modules.inventory import inventory_manager
from utils.constants import PRODUCT_CATEGORIES, UNITS, DEFAULT_HSN_CODE
from utils.logger import logger

class InventoryPage(QWidget):
    """Inventory management page"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Inventory Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.search_products)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(PRODUCT_CATEGORIES)
        self.category_filter.currentTextChanged.connect(self.filter_by_category)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(QLabel("Category:"))
        search_layout.addWidget(self.category_filter)
        
        main_layout.addLayout(search_layout)
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(10)
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "HSN", "MRP", "Disc%", 
            "Selling Price", "Stock", "Min Stock", "Actions"
        ])
        
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.hideColumn(0)  # Hide ID column
        
        main_layout.addWidget(self.inventory_table)
        
        # Summary
        summary_layout = self.create_summary()
        main_layout.addWidget(summary_layout)
        
        self.setLayout(main_layout)
    
    def create_toolbar(self) -> QFrame:
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        
        add_btn = QPushButton("➕ Add Product")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 15px;")
        add_btn.clicked.connect(self.add_product)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 15px;")
        refresh_btn.clicked.connect(self.load_inventory)
        
        low_stock_btn = QPushButton("⚠️ Low Stock")
        low_stock_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 15px;")
        low_stock_btn.clicked.connect(self.show_low_stock)
        
        layout.addWidget(add_btn)
        layout.addWidget(refresh_btn)
        layout.addWidget(low_stock_btn)
        layout.addStretch()
        
        return toolbar
    
    def create_summary(self) -> QFrame:
        """Create summary section"""
        summary = QFrame()
        summary.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(summary)
        
        self.total_products_label = QLabel("Total Products: 0")
        self.total_products_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.total_stock_label = QLabel("Total Stock: 0")
        self.total_stock_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.inventory_value_label = QLabel("Inventory Value: ₹0.00")
        self.inventory_value_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.inventory_value_label.setStyleSheet("color: #4CAF50;")
        
        layout.addWidget(self.total_products_label)
        layout.addWidget(self.total_stock_label)
        layout.addWidget(self.inventory_value_label)
        layout.addStretch()
        
        return summary
    
    def load_inventory(self):
        """Load inventory data"""
        products = inventory_manager.get_all_products()
        self.display_products(products)
        self.update_summary()
    
    def display_products(self, products):
        """Display products in table"""
        self.inventory_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(product['category']))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(product['hsn_code']))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(f"₹{product['mrp']:.2f}"))
            self.inventory_table.setItem(row, 5, QTableWidgetItem(f"{product['discount_percent']:.0f}%"))
            self.inventory_table.setItem(row, 6, QTableWidgetItem(f"₹{product['selling_price']:.2f}"))
            
            # Stock with color coding
            stock_item = QTableWidgetItem(str(product['current_stock']))
            if product['current_stock'] <= product['min_stock_level']:
                stock_item.setBackground(QColor(255, 200, 200))
                stock_item.setForeground(QColor(200, 0, 0))
            self.inventory_table.setItem(row, 7, stock_item)
            
            self.inventory_table.setItem(row, 8, QTableWidgetItem(str(product['min_stock_level'])))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.setStyleSheet("background-color: #2196F3; color: white;")
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            
            stock_btn = QPushButton("📦")
            stock_btn.setMaximumWidth(30)
            stock_btn.setStyleSheet("background-color: #FF9800; color: white;")
            stock_btn.clicked.connect(lambda checked, p=product: self.adjust_stock(p))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(30)
            delete_btn.setStyleSheet("background-color: #f44336; color: white;")
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(stock_btn)
            actions_layout.addWidget(delete_btn)
            
            self.inventory_table.setCellWidget(row, 9, actions_widget)
    
    def update_summary(self):
        """Update summary labels"""
        try:
            inventory_value = inventory_manager.get_inventory_value()
            
            # Safely get values with defaults
            total_products = inventory_value.get('total_products') if inventory_value.get('total_products') is not None else 0
            total_stock = inventory_value.get('total_stock') if inventory_value.get('total_stock') is not None else 0
            selling_value = inventory_value.get('selling_value') if inventory_value.get('selling_value') is not None else 0.0
            
            self.total_products_label.setText(f"Total Products: {total_products}")
            self.total_stock_label.setText(f"Total Stock: {total_stock}")
            self.inventory_value_label.setText(f"Inventory Value: ₹{selling_value:.2f}")
        except Exception as e:
            logger.error(f"Error updating summary: {e}")
            self.total_products_label.setText("Total Products: 0")
            self.total_stock_label.setText("Total Stock: 0")
            self.inventory_value_label.setText("Inventory Value: ₹0.00")
            
    def search_products(self):
        """Search products"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            self.load_inventory()
            return
        
        products = inventory_manager.search_products(search_text)
        self.display_products(products)
    
    def filter_by_category(self):
        """Filter products by category"""
        category = self.category_filter.currentText()
        
        if category == "All Categories":
            products = inventory_manager.get_all_products()
        else:
            products = inventory_manager.get_all_products(category)
        
        self.display_products(products)
    
    def add_product(self):
        """Open add product dialog"""
        dialog = ProductDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            success, message, product_id = inventory_manager.add_product(product_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def edit_product(self, product):
        """Open edit product dialog"""
        dialog = ProductDialog(self, product)
        
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            success, message = inventory_manager.update_product(product['id'], product_data)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def adjust_stock(self, product):
        """Open stock adjustment dialog"""
        dialog = StockAdjustmentDialog(self, product)
        
        if dialog.exec_() == QDialog.Accepted:
            new_stock, notes = dialog.get_stock_data()
            success, message = inventory_manager.update_stock(
                product['id'], new_stock, "ADJUSTMENT", notes
            )
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_product(self, product):
        """Delete product"""
        reply = QMessageBox.question(
            self, "Delete Product",
            f"Are you sure you want to delete '{product['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = inventory_manager.delete_product(product['id'])
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_inventory()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def show_low_stock(self):
        """Show low stock products"""
        low_stock = inventory_manager.get_low_stock_products()
        
        if not low_stock:
            QMessageBox.information(self, "Low Stock", "No products with low stock")
            return
        
        self.display_products(low_stock)
        self.search_input.clear()
        self.category_filter.setCurrentIndex(0)


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.is_edit = product is not None
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Product" if self.is_edit else "Add Product")
        self.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        # Product name
        self.name_input = QLineEdit()
        if self.product:
            self.name_input.setText(self.product['name'])
        layout.addRow("Product Name: *", self.name_input)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(PRODUCT_CATEGORIES)
        if self.product:
            index = self.category_combo.findText(self.product['category'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        layout.addRow("Category: *", self.category_combo)
        
        # HSN Code
        self.hsn_input = QLineEdit()
        self.hsn_input.setText(self.product['hsn_code'] if self.product else DEFAULT_HSN_CODE)
        layout.addRow("HSN Code:", self.hsn_input)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(UNITS)
        if self.product:
            index = self.unit_combo.findText(self.product['unit'])
            if index >= 0:
                self.unit_combo.setCurrentIndex(index)
        layout.addRow("Unit:", self.unit_combo)
        
        # Package size
        self.package_input = QLineEdit()
        if self.product and self.product.get('package_size'):
            self.package_input.setText(self.product['package_size'])
        self.package_input.setPlaceholderText("e.g., 30 Nos, 100 ml")
        layout.addRow("Package Size:", self.package_input)
        
        # MRP
        self.mrp_input = QDoubleSpinBox()
        self.mrp_input.setMaximum(999999.99)
        self.mrp_input.setDecimals(2)
        self.mrp_input.setPrefix("₹ ")
        if self.product:
            self.mrp_input.setValue(self.product['mrp'])
        layout.addRow("MRP: *", self.mrp_input)
        
        # Discount
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix(" %")
        self.discount_input.setValue(self.product['discount_percent'] if self.product else 55.0)
        layout.addRow("Discount %:", self.discount_input)
        
        # Purchase price
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setMaximum(999999.99)
        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setPrefix("₹ ")
        if self.product:
            self.purchase_price_input.setValue(self.product.get('purchase_price', 0))
        layout.addRow("Purchase Price:", self.purchase_price_input)
        
        # Min stock level
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(99999)
        self.min_stock_input.setValue(self.product['min_stock_level'] if self.product else 10)
        layout.addRow("Min Stock Level:", self.min_stock_input)
        
        # Initial stock (only for new products)
        if not self.is_edit:
            self.initial_stock_input = QSpinBox()
            self.initial_stock_input.setMaximum(99999)
            self.initial_stock_input.setValue(0)
            layout.addRow("Initial Stock:", self.initial_stock_input)
        
        # Description
        self.description_input = QLineEdit()
        if self.product and self.product.get('description'):
            self.description_input.setText(self.product['description'])
        layout.addRow("Description:", self.description_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_product_data(self):
        """Get product data from form"""
        data = {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'hsn_code': self.hsn_input.text().strip(),
            'unit': self.unit_combo.currentText(),
            'package_size': self.package_input.text().strip(),
            'mrp': self.mrp_input.value(),
            'discount_percent': self.discount_input.value(),
            'purchase_price': self.purchase_price_input.value(),
            'min_stock_level': self.min_stock_input.value(),
            'description': self.description_input.text().strip()
        }
        
        if not self.is_edit:
            data['current_stock'] = self.initial_stock_input.value()
        
        # Calculate selling price
        from modules.gst_calculator import gst_calculator
        data['selling_price'] = gst_calculator.calculate_selling_price(
            data['mrp'], data['discount_percent']
        )
        
        return data


class StockAdjustmentDialog(QDialog):
    """Dialog for adjusting stock"""
    
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle(f"Adjust Stock - {self.product['name']}")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        # Current stock
        current_label = QLabel(f"<b>{self.product['current_stock']}</b>")
        layout.addRow("Current Stock:", current_label)
        
        # New stock
        self.new_stock_input = QSpinBox()
        self.new_stock_input.setMaximum(999999)
        self.new_stock_input.setValue(self.product['current_stock'])
        layout.addRow("New Stock: *", self.new_stock_input)
        
        # Notes
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Reason for adjustment...")
        layout.addRow("Notes:", self.notes_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_stock_data(self):
        """Get stock adjustment data"""
        return self.new_stock_input.value(), self.notes_input.text().strip()
