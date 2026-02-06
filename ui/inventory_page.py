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
        # Initialize the parent QWidget class
        super().__init__()
        # Initialize the user interface components
        self.init_ui()
        # Load inventory data from database
        self.load_inventory()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create main vertical layout for the page
        main_layout = QVBoxLayout()
        # Set spacing between layout items to 10 pixels
        main_layout.setSpacing(10)
        # Set light cream background color for the entire widget
        self.setStyleSheet("background-color: #EBF4DD;")
        
        # Header section with title
        header_layout = QHBoxLayout()
        
        # Create title label with "Inventory Management" text
        title = QLabel("Inventory Management")
        # Set font to Arial, 16pt, Bold
        title.setFont(QFont("Arial", 16, QFont.Bold))
        # Apply medium green color and remove border
        title.setStyleSheet("color: #5A7863; border: none;")
        
        # Add title to header layout
        header_layout.addWidget(title)
        # Add stretch to push title to the left
        header_layout.addStretch()
        
        # Add header layout to main layout
        main_layout.addLayout(header_layout)
        
        # Create toolbar with action buttons
        toolbar = self.create_toolbar()
        # Add toolbar to main layout
        main_layout.addWidget(toolbar)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        # Create search input field
        self.search_input = QLineEdit()
        # Set placeholder text for search field
        self.search_input.setPlaceholderText("Search products...")
        # Connect text change event to search function
        self.search_input.textChanged.connect(self.search_products)
        # Apply styling with cream background and sage border
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 8px;
                color: #3B4953;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        
        # Create category filter dropdown
        self.category_filter = QComboBox()
        # Add "All Categories" as first option
        self.category_filter.addItem("All Categories")
        # Add all product categories from constants
        self.category_filter.addItems(PRODUCT_CATEGORIES)
        # Connect selection change event to filter function
        self.category_filter.currentTextChanged.connect(self.filter_by_category)
        # Apply sage green styling to dropdown
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-weight: bold;
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                color: #3B4953;
                min-width: 150px;
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
        
        # Create "Search:" label
        search_label = QLabel("Search:")
        # Apply dark text color and bold font
        search_label.setStyleSheet("color: #3B4953; font-weight: bold;")
        
        # Create "Category:" label
        category_label = QLabel("Category:")
        # Apply dark text color and bold font
        category_label.setStyleSheet("color: #3B4953; font-weight: bold;")
        
        # Add search label to layout
        search_layout.addWidget(search_label)
        # Add search input with stretch factor of 1
        search_layout.addWidget(self.search_input, 1)
        # Add category label to layout
        search_layout.addWidget(category_label)
        # Add category dropdown to layout
        search_layout.addWidget(self.category_filter)
        
        # Add search layout to main layout
        main_layout.addLayout(search_layout)
        
        # Create inventory table widget
        self.inventory_table = QTableWidget()
        # Set number of columns to 10
        self.inventory_table.setColumnCount(10)
        # Set column headers
        self.inventory_table.setHorizontalHeaderLabels([
            "ID", "Name", "Category", "HSN", "MRP", "Disc%", 
            "Selling Price", "Stock", "Min Stock", "Actions"
        ])
        
        # Make "Name" column stretch to fill available space
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # Disable editing of table cells
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Select entire rows when clicking
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Enable alternating row colors
        self.inventory_table.setAlternatingRowColors(True)
        # Hide the ID column (column 0)
        self.inventory_table.hideColumn(0)
        # Apply table styling with sage green theme
        self.inventory_table.setStyleSheet("""
            QTableWidget {
                background-color: #EBF4DD;
                alternate-background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                gridline-color: #90AB8B;
                color: #3B4953;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QHeaderView::section {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        
        # Add inventory table to main layout
        main_layout.addWidget(self.inventory_table)
        
        # Create summary section with statistics
        summary_layout = self.create_summary()
        # Add summary to main layout
        main_layout.addWidget(summary_layout)
        
        # Set the main layout for this widget
        self.setLayout(main_layout)
    
    def create_toolbar(self) -> QFrame:
        """Create toolbar with action buttons"""
        # Create frame container for toolbar
        toolbar = QFrame()
        # Apply #EBF4DD background with sage border
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #EBF4DD;
                border-radius: 8px;
                padding: 10px;
                border: 2px solid #90AB8B;
            }
        """)
        
        # Create horizontal layout for toolbar
        layout = QHBoxLayout(toolbar)
        
        # Create "Add Product" button with plus icon
        add_btn = QPushButton("➕ Add Product")
        # Apply medium green background with cream text
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        # Connect click event to add_product method
        add_btn.clicked.connect(self.add_product)
        
        # Create "Refresh" button with refresh icon
        refresh_btn = QPushButton("🔄 Refresh")
        # Apply sage green background with cream text
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;
                color: #EBF4DD;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #5A7863;
            }
        """)
        # Connect click event to load_inventory method
        refresh_btn.clicked.connect(self.load_inventory)
        
        # Create "Low Stock" button with warning icon
        low_stock_btn = QPushButton("⚠️ Low Stock")
        # Apply dark blue-grey background with cream text
        low_stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;
                color: #EBF4DD;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #5A7863;
            }
        """)
        # Connect click event to show_low_stock method
        low_stock_btn.clicked.connect(self.show_low_stock)
        
        # Add "Add Product" button to layout
        layout.addWidget(add_btn)
        # Add "Refresh" button to layout
        layout.addWidget(refresh_btn)
        # Add "Low Stock" button to layout
        layout.addWidget(low_stock_btn)
        # Add stretch to push buttons to the left
        layout.addStretch()
        
        # Return the configured toolbar frame
        return toolbar
    
    def create_summary(self) -> QFrame:
        """Create summary section"""
        # Create frame container for summary
        summary = QFrame()
        # Apply #EBF4DD background with sage border
        summary.setStyleSheet("""
            QFrame {
                background-color: #5A7863;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #90AB8B;
            }
        """)
        
        # Create horizontal layout for summary items
        layout = QHBoxLayout(summary)
        
        # Create label for total products count
        self.total_products_label = QLabel("Total Products: 0")
        # Set font to Arial, 11pt, Bold
        self.total_products_label.setFont(QFont("Arial", 11, QFont.Bold))
        # Apply dark text color
        self.total_products_label.setStyleSheet("color: #EBF4DD;")
        
        # Create label for total stock quantity
        self.total_stock_label = QLabel("Total Stock: 0")
        # Set font to Arial, 11pt, Bold
        self.total_stock_label.setFont(QFont("Arial", 11, QFont.Bold))
        # Apply dark text color
        self.total_stock_label.setStyleSheet("color: #EBF4DD;")
        
        # Create label for inventory value in rupees
        self.inventory_value_label = QLabel("Inventory Value: ₹0.00")
        # Set font to Arial, 11pt, Bold
        self.inventory_value_label.setFont(QFont("Arial", 11, QFont.Bold))
        # Apply medium green color to highlight value
        self.inventory_value_label.setStyleSheet("color: #EBF4DD; font-weight: bold;")
        
        # Add total products label to layout
        layout.addWidget(self.total_products_label)
        # Add total stock label to layout
        layout.addWidget(self.total_stock_label)
        # Add inventory value label to layout
        layout.addWidget(self.inventory_value_label)
        # Add stretch to push labels to the left
        layout.addStretch()
        
        # Return the configured summary frame
        return summary
    
    def load_inventory(self):
        """Load inventory data"""
        # Fetch all products from inventory manager
        products = inventory_manager.get_all_products()
        # Display products in the table
        self.display_products(products)
        # Update summary statistics
        self.update_summary()
    
    def display_products(self, products):
        """Display products in table"""
        # Set table row count to match number of products
        self.inventory_table.setRowCount(len(products))
        
        # Loop through each product with index
        for row, product in enumerate(products):
            # Set ID in column 0 (hidden column)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
            # Set product name in column 1
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product['name']))
            # Set category in column 2
            self.inventory_table.setItem(row, 2, QTableWidgetItem(product['category']))
            # Set HSN code in column 3
            self.inventory_table.setItem(row, 3, QTableWidgetItem(product['hsn_code']))
            # Set MRP with rupee symbol and 2 decimal places in column 4
            self.inventory_table.setItem(row, 4, QTableWidgetItem(f"₹{product['mrp']:.2f}"))
            # Set discount percentage with no decimals in column 5
            self.inventory_table.setItem(row, 5, QTableWidgetItem(f"{product['discount_percent']:.0f}%"))
            # Set selling price with rupee symbol and 2 decimals in column 6
            self.inventory_table.setItem(row, 6, QTableWidgetItem(f"₹{product['selling_price']:.2f}"))
            
            # Create stock item for column 7
            stock_item = QTableWidgetItem(str(product['current_stock']))
            # Check if stock is at or below minimum level
            if product['current_stock'] <= product['min_stock_level']:
                # Set light red background for low stock warning
                stock_item.setBackground(QColor(255, 200, 200))
                # Set dark red text for low stock warning
                stock_item.setForeground(QColor(200, 0, 0))
            # Set stock item in column 7
            self.inventory_table.setItem(row, 7, stock_item)
            
            # Set minimum stock level in column 8
            self.inventory_table.setItem(row, 8, QTableWidgetItem(str(product['min_stock_level'])))
            
            # Create widget container for action buttons
            actions_widget = QWidget()
            # Create horizontal layout for action buttons
            actions_layout = QHBoxLayout(actions_widget)
            # Set minimal margins for compact button layout
            actions_layout.setContentsMargins(2, 2, 2, 2)
            # Set spacing between buttons to 2 pixels
            actions_layout.setSpacing(2)
            
            # Create edit button with pencil icon
            edit_btn = QPushButton("✏️")
            # Set maximum width to 30 pixels for compact size
            edit_btn.setMaximumWidth(30)
            # Apply medium green background
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #5A7863;
                    color: #EBF4DD;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #90AB8B;
                }
            """)
            # Connect click event to edit_product method with product data
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            
            # Create stock adjustment button with package icon
            stock_btn = QPushButton("📦")
            # Set maximum width to 30 pixels
            stock_btn.setMaximumWidth(30)
            # Apply sage green background
            stock_btn.setStyleSheet("""
                QPushButton {
                    background-color: #90AB8B;
                    color: #EBF4DD;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5A7863;
                }
            """)
            # Connect click event to adjust_stock method with product data
            stock_btn.clicked.connect(lambda checked, p=product: self.adjust_stock(p))
            
            # Create delete button with trash icon
            delete_btn = QPushButton("🗑️")
            # Set maximum width to 30 pixels
            delete_btn.setMaximumWidth(30)
            # Apply dark blue-grey background
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B4953;
                    color: #3B4953;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5A7863;
                }
            """)
            # Connect click event to delete_product method with product data
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            
            # Add edit button to actions layout
            actions_layout.addWidget(edit_btn)
            # Add stock button to actions layout
            actions_layout.addWidget(stock_btn)
            # Add delete button to actions layout
            actions_layout.addWidget(delete_btn)
            
            # Set actions widget in column 9
            self.inventory_table.setCellWidget(row, 9, actions_widget)
    
    def update_summary(self):
        """Update summary labels"""
        try:
            # Fetch inventory value statistics from inventory manager
            inventory_value = inventory_manager.get_inventory_value()
            
            # Safely get total products with default 0 if None
            total_products = inventory_value.get('total_products') if inventory_value.get('total_products') is not None else 0
            # Safely get total stock with default 0 if None
            total_stock = inventory_value.get('total_stock') if inventory_value.get('total_stock') is not None else 0
            # Safely get selling value with default 0.0 if None
            selling_value = inventory_value.get('selling_value') if inventory_value.get('selling_value') is not None else 0.0
            
            # Update total products label with fetched value
            self.total_products_label.setText(f"Total Products: {total_products}")
            # Update total stock label with fetched value
            self.total_stock_label.setText(f"Total Stock: {total_stock}")
            # Update inventory value label with rupee symbol and 2 decimals
            self.inventory_value_label.setText(f"Inventory Value: ₹{selling_value:.2f}")
        except Exception as e:
            # Log error message if update fails
            logger.error(f"Error updating summary: {e}")
            # Set total products to 0 on error
            self.total_products_label.setText("Total Products: 0")
            # Set total stock to 0 on error
            self.total_stock_label.setText("Total Stock: 0")
            # Set inventory value to 0.00 on error
            self.inventory_value_label.setText("Inventory Value: ₹0.00")
            
    def search_products(self):
        """Search products"""
        # Get search text from input and remove #EBF4DDspace
        search_text = self.search_input.text().strip()
        
        # Check if search text is empty
        if not search_text:
            # Load all inventory if search is empty
            self.load_inventory()
            # Exit function
            return
        
        # Search products using inventory manager
        products = inventory_manager.search_products(search_text)
        # Display filtered products in table
        self.display_products(products)
    
    def filter_by_category(self):
        """Filter products by category"""
        # Get selected category from dropdown
        category = self.category_filter.currentText()
        
        # Check if "All Categories" is selected
        if category == "All Categories":
            # Get all products without category filter
            products = inventory_manager.get_all_products()
        else:
            # Get products filtered by selected category
            products = inventory_manager.get_all_products(category)
        
        # Display filtered products in table
        self.display_products(products)
    
    def add_product(self):
        """Open add product dialog"""
        # Create product dialog without existing product (add mode)
        dialog = ProductDialog(self)
        
        # Check if user clicked Save button
        if dialog.exec_() == QDialog.Accepted:
            # Get product data from dialog form
            product_data = dialog.get_product_data()
            # Add product using inventory manager
            success, message, product_id = inventory_manager.add_product(product_data)
            
            # Check if product was added successfully
            if success:
                # Show success message to user
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload inventory to show new product
                self.load_inventory()
            else:
                # Show error message to user
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def edit_product(self, product):
        """Open edit product dialog"""
        # Create product dialog with existing product data (edit mode)
        dialog = ProductDialog(self, product)
        
        # Check if user clicked Save button
        if dialog.exec_() == QDialog.Accepted:
            # Get updated product data from dialog form
            product_data = dialog.get_product_data()
            # Update product using inventory manager with product ID
            success, message = inventory_manager.update_product(product['id'], product_data)
            
            # Check if product was updated successfully
            if success:
                # Show success message to user
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload inventory to show updated product
                self.load_inventory()
            else:
                # Show error message to user
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def adjust_stock(self, product):
        """Open stock adjustment dialog"""
        # Create stock adjustment dialog with product data
        dialog = StockAdjustmentDialog(self, product)
        
        # Check if user clicked Save button
        if dialog.exec_() == QDialog.Accepted:
            # Get new stock quantity and notes from dialog
            new_stock, notes = dialog.get_stock_data()
            # Update stock using inventory manager
            success, message = inventory_manager.update_stock(
                product['id'], new_stock, "ADJUSTMENT", notes
            )
            
            # Check if stock was updated successfully
            if success:
                # Show success message to user
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload inventory to show updated stock
                self.load_inventory()
            else:
                # Show error message to user
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def delete_product(self, product):
        """Delete product"""
        # Create confirmation dialog
        msg_box = QMessageBox(self)
        # Set window title
        msg_box.setWindowTitle("Delete Product")
        # Set confirmation message with product name
        msg_box.setText(f"Are you sure you want to delete '{product['name']}'?")
        # Add Yes and No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Apply styled message box styling
        msg_box.setStyleSheet(self.get_message_box_style())
        
        # Show dialog and get user response
        reply = msg_box.exec_()
        
        # Check if user clicked Yes
        if reply == QMessageBox.Yes:
            # Delete product using inventory manager with product ID
            success, message = inventory_manager.delete_product(product['id'])
            
            # Check if product was deleted successfully
            if success:
                # Show success message to user
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload inventory to remove deleted product
                self.load_inventory()
            else:
                # Show error message to user
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def show_low_stock(self):
        """Show low stock products"""
        # Get list of low stock products from inventory manager
        low_stock = inventory_manager.get_low_stock_products()
        
        # Check if no low stock products found
        if not low_stock:
            # Show information message
            self.show_styled_message("Low Stock", "No products with low stock", QMessageBox.Information)
            # Exit function
            return
        
        # Display low stock products in table
        self.display_products(low_stock)
        # Clear search input field
        self.search_input.clear()
        # Reset category filter to "All Categories"
        self.category_filter.setCurrentIndex(0)
    
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
        # Apply consistent styling
        msg_box.setStyleSheet(self.get_message_box_style())
        # Show message box and wait for user response
        msg_box.exec_()
    
    def get_message_box_style(self) -> str:
        """Get consistent message box styling"""
        # Return CSS stylesheet for message boxes
        return """
            QMessageBox {
                background-color: #3B4953;
            }
            QLabel {
                color: #3B4953;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #3B4953;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: white;
            }
        """


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    
    def __init__(self, parent=None, product=None):
        # Initialize parent QDialog class
        super().__init__(parent)
        # Store product data (None for add mode, dict for edit mode)
        self.product = product
        # Determine if dialog is in edit mode
        self.is_edit = product is not None
        # Initialize dialog user interface
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        # Set window title based on mode (Edit or Add)
        self.setWindowTitle("Edit Product" if self.is_edit else "Add Product")
        # Set minimum dialog width to 500 pixels
        self.setMinimumWidth(500)
        # Apply cream background to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
                font-weight: bold;
            }
        """)
        
        # Create form layout for input fields
        layout = QFormLayout()
        # Set spacing between form rows
        layout.setSpacing(10)
        
        # Product name input field
        self.name_input = QLineEdit()
        # If editing, populate with existing product name
        if self.product:
            self.name_input.setText(self.product['name'])
        # Apply input field styling
        self.name_input.setStyleSheet(self.get_input_style())
        # Add product name field to form with label
        layout.addRow("Product Name: *", self.name_input)
        
        # Category dropdown
        self.category_combo = QComboBox()
        # Add all product categories to dropdown
        self.category_combo.addItems(PRODUCT_CATEGORIES)
        # If editing, select existing category
        if self.product:
            # Find index of product's category in dropdown
            index = self.category_combo.findText(self.product['category'])
            # If category found, select it
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        # Apply dropdown styling
        self.category_combo.setStyleSheet(self.get_combo_style())
        # Add category field to form with label
        layout.addRow("Category: *", self.category_combo)
        
        # HSN Code input field
        self.hsn_input = QLineEdit()
        # If editing, use existing HSN, otherwise use default
        self.hsn_input.setText(self.product['hsn_code'] if self.product else DEFAULT_HSN_CODE)
        # Apply input field styling
        self.hsn_input.setStyleSheet(self.get_input_style())
        # Add HSN code field to form with label
        layout.addRow("HSN Code:", self.hsn_input)
        
        # Unit dropdown
        self.unit_combo = QComboBox()
        # Add all unit types to dropdown
        self.unit_combo.addItems(UNITS)
        # If editing, select existing unit
        if self.product:
            # Find index of product's unit in dropdown
            index = self.unit_combo.findText(self.product['unit'])
            # If unit found, select it
            if index >= 0:
                self.unit_combo.setCurrentIndex(index)
        # Apply dropdown styling
        self.unit_combo.setStyleSheet(self.get_combo_style())
        # Add unit field to form with label
        layout.addRow("Unit:", self.unit_combo)
        
        # Package size input field
        self.package_input = QLineEdit()
        # If editing and package size exists, populate field
        if self.product and self.product.get('package_size'):
            self.package_input.setText(self.product['package_size'])
        # Set placeholder text as example
        self.package_input.setPlaceholderText("e.g., 30 Nos, 100 ml")
        # Apply input field styling
        self.package_input.setStyleSheet(self.get_input_style())
        # Add package size field to form with label
        layout.addRow("Package Size:", self.package_input)
        
        # MRP (Maximum Retail Price) spin box
        self.mrp_input = QDoubleSpinBox()
        # Set maximum value to 999999.99
        self.mrp_input.setMaximum(999999.99)
        # Set decimal places to 2
        self.mrp_input.setDecimals(2)
        # Set rupee symbol prefix
        self.mrp_input.setPrefix("₹ ")
        # If editing, populate with existing MRP
        if self.product:
            self.mrp_input.setValue(self.product['mrp'])
        # Apply spin box styling
        self.mrp_input.setStyleSheet(self.get_spinbox_style())
        # Add MRP field to form with label
        layout.addRow("MRP: *", self.mrp_input)
        
        # Discount percentage spin box
        self.discount_input = QDoubleSpinBox()
        # Set maximum discount to 100%
        self.discount_input.setMaximum(100)
        # Set decimal places to 2
        self.discount_input.setDecimals(2)
        # Set percentage symbol suffix
        self.discount_input.setSuffix(" %")
        # If editing, use existing discount, otherwise default 55%
        self.discount_input.setValue(self.product['discount_percent'] if self.product else 55.0)
        # Apply spin box styling
        self.discount_input.setStyleSheet(self.get_spinbox_style())
        # Add discount field to form with label
        layout.addRow("Discount %:", self.discount_input)
        
        # Purchase price spin box
        self.purchase_price_input = QDoubleSpinBox()
        # Set maximum value to 999999.99
        self.purchase_price_input.setMaximum(999999.99)
        # Set decimal places to 2
        self.purchase_price_input.setDecimals(2)
        # Set rupee symbol prefix
        self.purchase_price_input.setPrefix("₹ ")
        # If editing, populate with existing purchase price
        if self.product:
            self.purchase_price_input.setValue(self.product.get('purchase_price', 0))
        # Apply spin box styling
        self.purchase_price_input.setStyleSheet(self.get_spinbox_style())
        # Add purchase price field to form with label
        layout.addRow("Purchase Price:", self.purchase_price_input)
        
        # Minimum stock level spin box
        self.min_stock_input = QSpinBox()
        # Set maximum value to 99999
        self.min_stock_input.setMaximum(99999)
        # If editing, use existing min stock, otherwise default 10
        self.min_stock_input.setValue(self.product['min_stock_level'] if self.product else 10)
        # Apply spin box styling
        self.min_stock_input.setStyleSheet(self.get_spinbox_style())
        # Add min stock field to form with label
        layout.addRow("Min Stock Level:", self.min_stock_input)
        
        # Initial stock field (only shown when adding new product)
        if not self.is_edit:
            # Create spin box for initial stock quantity
            self.initial_stock_input = QSpinBox()
            # Set maximum value to 99999
            self.initial_stock_input.setMaximum(99999)
            # Set default value to 0
            self.initial_stock_input.setValue(0)
            # Apply spin box styling
            self.initial_stock_input.setStyleSheet(self.get_spinbox_style())
            # Add initial stock field to form with label
            layout.addRow("Initial Stock:", self.initial_stock_input)
        
        # Description input field
        self.description_input = QLineEdit()
        # If editing and description exists, populate field
        if self.product and self.product.get('description'):
            self.description_input.setText(self.product['description'])
        # Apply input field styling
        self.description_input.setStyleSheet(self.get_input_style())
        # Add description field to form with label
        layout.addRow("Description:", self.description_input)
        
        # Create dialog button box with Save and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        # Connect accepted signal to dialog accept (Save button)
        buttons.accepted.connect(self.accept)
        # Connect rejected signal to dialog reject (Cancel button)
        buttons.rejected.connect(self.reject)
        # Apply button styling
        buttons.setStyleSheet("""
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
        
        # Add button box to form layout
        layout.addRow(buttons)
        
        # Set form layout as dialog layout
        self.setLayout(layout)
    
    def get_product_data(self):
        """Get product data from form"""
        # Create dictionary to store form data
        data = {
            # Get product name and remove #EBF4DDspace
            'name': self.name_input.text().strip(),
            # Get selected category
            'category': self.category_combo.currentText(),
            # Get HSN code and remove #EBF4DDspace
            'hsn_code': self.hsn_input.text().strip(),
            # Get selected unit
            'unit': self.unit_combo.currentText(),
            # Get package size and remove #EBF4DDspace
            'package_size': self.package_input.text().strip(),
            # Get MRP value
            'mrp': self.mrp_input.value(),
            # Get discount percentage
            'discount_percent': self.discount_input.value(),
            # Get purchase price
            'purchase_price': self.purchase_price_input.value(),
            # Get minimum stock level
            'min_stock_level': self.min_stock_input.value(),
            # Get description and remove #EBF4DDspace
            'description': self.description_input.text().strip()
        }
        
        # If adding new product (not editing)
        if not self.is_edit:
            # Add initial stock quantity to data
            data['current_stock'] = self.initial_stock_input.value()
        
        # Import GST calculator module
        from modules.gst_calculator import gst_calculator
        # Calculate selling price based on MRP and discount
        data['selling_price'] = gst_calculator.calculate_selling_price(
            data['mrp'], data['discount_percent']
        )
        
        # Return complete product data dictionary
        return data
    
    def get_input_style(self) -> str:
        """Get input field styling"""
        # Return CSS stylesheet for line edit fields
        return """
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 8px;
                color: #3B4953;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """
    
    def get_combo_style(self) -> str:
        """Get combo box styling"""
        # Return CSS stylesheet for combo boxes
        return """
            QComboBox {
                padding: 8px;
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
        """
    
    def get_spinbox_style(self) -> str:
        """Get spin box styling"""
        # Return CSS stylesheet for spin boxes
        return """
            QSpinBox, QDoubleSpinBox {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 8px;
                color: #3B4953;
                font-weight: bold;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #5A7863;
            }
        """


class StockAdjustmentDialog(QDialog):
    """Dialog for adjusting stock"""
    
    def __init__(self, parent=None, product=None):
        # Initialize parent QDialog class
        super().__init__(parent)
        # Store product data for stock adjustment
        self.product = product
        # Initialize dialog user interface
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        # Set window title with product name
        self.setWindowTitle(f"Adjust Stock - {self.product['name']}")
        # Set minimum dialog width to 400 pixels
        self.setMinimumWidth(400)
        # Apply cream background to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
                font-weight: bold;
            }
        """)
        
        # Create form layout for input fields
        layout = QFormLayout()
        # Set spacing between form rows
        layout.setSpacing(10)
        
        # Create label to display current stock in bold
        current_label = QLabel(f"<b>{self.product['current_stock']}</b>")
        # Apply dark text color
        current_label.setStyleSheet("color: #5A7863; font-size: 14pt;")
        # Add current stock to form with label
        layout.addRow("Current Stock:", current_label)
        
        # Create spin box for new stock value
        self.new_stock_input = QSpinBox()
        # Set maximum value to 999999
        self.new_stock_input.setMaximum(999999)
        # Set initial value to current stock
        self.new_stock_input.setValue(self.product['current_stock'])
        # Apply spin box styling
        self.new_stock_input.setStyleSheet("""
            QSpinBox {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 8px;
                color: #3B4953;
                font-weight: bold;
                font-size: 11pt;
            }
            QSpinBox:focus {
                border: 2px solid #5A7863;
            }
        """)
        # Add new stock field to form with label
        layout.addRow("New Stock: *", self.new_stock_input)
        
        # Create input field for adjustment notes
        self.notes_input = QLineEdit()
        # Set placeholder text
        self.notes_input.setPlaceholderText("Reason for adjustment...")
        # Apply input field styling
        self.notes_input.setStyleSheet("""
            QLineEdit {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                padding: 8px;
                color: #3B4953;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """)
        # Add notes field to form with label
        layout.addRow("Notes:", self.notes_input)
        
        # Create dialog button box with Save and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        # Connect accepted signal to dialog accept (Save button)
        buttons.accepted.connect(self.accept)
        # Connect rejected signal to dialog reject (Cancel button)
        buttons.rejected.connect(self.reject)
        # Apply button styling
        buttons.setStyleSheet("""
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
        
        # Add button box to form layout
        layout.addRow(buttons)
        
        # Set form layout as dialog layout
        self.setLayout(layout)
    
    def get_stock_data(self):
        """Get stock adjustment data"""
        # Return tuple of new stock value and notes (with #EBF4DDspace removed)
        return self.new_stock_input.value(), self.notes_input.text().strip()
