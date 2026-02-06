from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QGroupBox, QLineEdit, QTextEdit,
                            QMessageBox, QListWidget, QFrame, QFileDialog,
                            QDialog, QFormLayout, QDialogButtonBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.backup import backup_manager
from modules.auth import auth_manager
from database.db_manager import db
from config import APP_VERSION
from utils.logger import logger


class SettingsPage(QWidget):
    """Settings and configuration page"""
    
    def __init__(self):
        # Initialize the parent QWidget class
        super().__init__()
        # Initialize the user interface components
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # ✅ CREATE SCROLL AREA for entire page content
        scroll = QScrollArea()
        # Enable automatic resizing of scroll area content
        scroll.setWidgetResizable(True)
        # Show horizontal scrollbar only when needed
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Show vertical scrollbar only when needed
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Remove frame border from scroll area
        scroll.setFrameShape(QFrame.NoFrame)
        # Apply light cream background to scroll area
        scroll.setStyleSheet("background-color: #EBF4DD;")  # Light cream background
        
        # Create content widget to hold all settings sections
        content = QWidget()
        # Apply light cream background to content widget
        content.setStyleSheet("background-color: #EBF4DD;")  # Light cream background
        # Create main vertical layout for content
        main_layout = QVBoxLayout(content)
        # Set spacing between layout items to 15 pixels
        main_layout.setSpacing(15)
        # Set margins around the layout (left, top, right, bottom)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create title label with "Settings" text
        title = QLabel("Settings")
        # Set font to Arial, 16pt, Bold
        title.setFont(QFont("Arial", 16, QFont.Bold))
        # Apply medium green color and remove border
        title.setStyleSheet("color: #5A7863; border: none;")  # Medium green text color
        # Add title to main layout
        main_layout.addWidget(title)
        
        # Create sales person management section
        sales_person_group = self.create_sales_person_section()
        # Add sales person section to main layout
        main_layout.addWidget(sales_person_group)
        
        # Create company information section
        company_group = self.create_company_info()
        # Add company info section to main layout
        main_layout.addWidget(company_group)
        
        # Create backup and restore section
        backup_group = self.create_backup_section()
        # Add backup section to main layout
        main_layout.addWidget(backup_group)
        
        # Create database statistics section
        stats_group = self.create_stats_section()
        # Add stats section to main layout
        main_layout.addWidget(stats_group)
        
        # Create password change section
        password_group = self.create_password_section()
        # Add password section to main layout
        main_layout.addWidget(password_group)
        
        # Add stretch to push all content to the top
        main_layout.addStretch()
        
        # ✅ SET CONTENT TO SCROLL AREA
        scroll.setWidget(content)
        
        # ✅ MAIN LAYOUT FOR PAGE
        # Create page layout to hold scroll area
        page_layout = QVBoxLayout()
        # Set zero margins for page layout
        page_layout.setContentsMargins(0, 0, 0, 0)
        # Add scroll area to page layout
        page_layout.addWidget(scroll)
        
        # Set page layout as widget layout
        self.setLayout(page_layout)
        
        # Load database statistics on startup
        self.load_database_stats()
        # Load backup files list on startup
        self.load_backups()
        # Load sales persons into table on startup
        self.load_sales_persons()
    
    def create_sales_person_section(self) -> QGroupBox:
        """Create sales person management section"""
        # Create group box for sales person section
        group = QGroupBox("Sales Person Management")
        # Apply styling with sage green theme
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;  /* Bold text for group title */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                margin-top: 10px;  /* Top margin for title spacing */
                padding-top: 15px;  /* Top padding for content spacing */
                background-color: #EBF4DD;  /* #EBF4DD background */
            }
            QGroupBox::title {
                color: #5A7863;  /* Medium green title color */
                subcontrol-origin: margin;  /* Position title on margin */
                left: 10px;  /* Left offset for title */
                padding: 0 5px;  /* Horizontal padding around title */
            }
        """)
        
        # Create vertical layout for group content
        layout = QVBoxLayout()
        # Set spacing between layout items
        layout.setSpacing(10)
        
        # Create info label with descriptive text
        info_label = QLabel("Manage sales persons who can create bills")
        # Apply sage green color and italic style
        info_label.setStyleSheet("color: #90AB8B; font-style: italic;")  # Sage green, italic
        # Add info label to layout
        layout.addWidget(info_label)
        
        # Create table widget for sales persons
        self.sales_person_table = QTableWidget()
        # Set table to have 4 columns
        self.sales_person_table.setColumnCount(4)
        # Set column headers
        self.sales_person_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Status"])
        # Make "Name" column stretch to fill available space
        self.sales_person_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # Disable editing of table cells
        self.sales_person_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Select entire rows when clicking
        self.sales_person_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Hide the ID column (column 0)
        self.sales_person_table.hideColumn(0)
        # Set minimum height for table
        self.sales_person_table.setMinimumHeight(150)
        # Set maximum height for table
        self.sales_person_table.setMaximumHeight(250)
        # Apply table styling with sage green theme
        self.sales_person_table.setStyleSheet("""
            QTableWidget {
                background-color: #EBF4DD;  /* #EBF4DD background for table */
                alternate-background-color: #EBF4DD;  /* Cream color for alternating rows */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                gridline-color: #90AB8B;  /* Sage green grid lines */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QTableWidget::item {
                padding: 5px;  /* Padding inside table cells */
            }
            QTableWidget::item:selected {
                background-color: #90AB8B;  /* Sage green background for selected items */
                color: #EBF4DD;  /* Cream text color for selected items */
            }
            QHeaderView::section {
                background-color: #5A7863;  /* Medium green background for headers */
                color: #EBF4DD;  /* Cream text color for headers */
                padding: 8px;  /* Padding inside header cells */
                border: none;  /* No border for header cells */
                font-weight: bold;  /* Bold text for headers */
            }
        """)
        # Add table to layout
        layout.addWidget(self.sales_person_table)
        
        # Create horizontal layout for action buttons
        btn_layout = QHBoxLayout()
        
        # Create "Add" button with plus icon
        add_sp_btn = QPushButton("➕ Add")
        # Apply medium green styling
        add_sp_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;  /* Medium green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #90AB8B;  /* Sage green on hover */
            }
        """)
        # Set minimum height for button
        add_sp_btn.setMinimumHeight(35)
        # Connect click event to add_sales_person method
        add_sp_btn.clicked.connect(self.add_sales_person)
        
        # Create "Edit" button with pencil icon
        edit_sp_btn = QPushButton("✏️ Edit")
        # Apply sage green styling
        edit_sp_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;  /* Sage green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Set minimum height for button
        edit_sp_btn.setMinimumHeight(35)
        # Connect click event to edit_sales_person method
        edit_sp_btn.clicked.connect(self.edit_sales_person)
        
        # Create "Delete" button with trash icon
        delete_sp_btn = QPushButton("🗑️ Delete")
        # Apply dark blue-grey styling
        delete_sp_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;  /* Dark blue-grey background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Set minimum height for button
        delete_sp_btn.setMinimumHeight(35)
        # Connect click event to delete_sales_person method
        delete_sp_btn.clicked.connect(self.delete_sales_person)
        
        # Add "Add" button to button layout
        btn_layout.addWidget(add_sp_btn)
        # Add "Edit" button to button layout
        btn_layout.addWidget(edit_sp_btn)
        # Add "Delete" button to button layout
        btn_layout.addWidget(delete_sp_btn)
        # Add stretch to push buttons to the left
        btn_layout.addStretch()
        
        # Add button layout to main layout
        layout.addLayout(btn_layout)
        
        # Set layout for group box
        group.setLayout(layout)
        # Return configured group box
        return group
    
    def load_sales_persons(self):
        """Load sales persons into table"""
        # Fetch all sales persons from database (including inactive)
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        # Set table row count to match number of sales persons
        self.sales_person_table.setRowCount(len(sales_persons))
        
        # Loop through each sales person with index
        for row, sp in enumerate(sales_persons):
            # Set ID in column 0 (hidden column)
            self.sales_person_table.setItem(row, 0, QTableWidgetItem(str(sp['id'])))
            # Set name in column 1
            self.sales_person_table.setItem(row, 1, QTableWidgetItem(sp['name']))
            # Set phone in column 2 (empty string if not present)
            self.sales_person_table.setItem(row, 2, QTableWidgetItem(sp.get('phone', '')))
            
            # Determine status text based on is_active flag
            status = "Active" if sp['is_active'] else "Inactive"
            # Create table item for status
            status_item = QTableWidgetItem(status)
            # If inactive, set red foreground color
            if not sp['is_active']:
                status_item.setForeground(Qt.red)  # Red text for inactive
            # Set status item in column 3
            self.sales_person_table.setItem(row, 3, status_item)
    
    def add_sales_person(self):
        """Add new sales person"""
        # Create sales person dialog without existing data (add mode)
        dialog = SalesPersonDialog(self)
        
        # Check if user clicked Save button
        if dialog.exec_() == QDialog.Accepted:
            # Get sales person data from dialog form
            name, phone, email = dialog.get_data()
            
            # Add sales person to database
            success, message, sp_id = db.add_sales_person(name, phone, email)
            
            # Check if addition was successful
            if success:
                # Show success message
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload sales persons table
                self.load_sales_persons()
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def edit_sales_person(self):
        """Edit selected sales person"""
        # Get currently selected row index
        current_row = self.sales_person_table.currentRow()
        
        # Check if no row is selected
        if current_row < 0:
            # Show warning message
            self.show_styled_message("No Selection", "Please select a sales person to edit", QMessageBox.Warning)
            # Exit function
            return
        
        # Get sales person ID from hidden column 0
        sp_id = int(self.sales_person_table.item(current_row, 0).text())
        # Fetch sales person data from database
        sp_data = db.get_sales_person_by_id(sp_id)
        
        # Check if sales person data was not found
        if not sp_data:
            # Show error message
            self.show_styled_message("Error", "Sales person not found", QMessageBox.Warning)
            # Exit function
            return
        
        # Create sales person dialog with existing data (edit mode)
        dialog = SalesPersonDialog(self, sp_data)
        
        # Check if user clicked Save button
        if dialog.exec_() == QDialog.Accepted:
            # Get updated sales person data from dialog form
            name, phone, email = dialog.get_data()
            
            # Update sales person in database
            success, message = db.update_sales_person(sp_id, name, phone, email)
            
            # Check if update was successful
            if success:
                # Show success message
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload sales persons table
                self.load_sales_persons()
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def delete_sales_person(self):
        """Delete selected sales person"""
        # Get currently selected row index
        current_row = self.sales_person_table.currentRow()
        
        # Check if no row is selected
        if current_row < 0:
            # Show warning message
            self.show_styled_message("No Selection", "Please select a sales person to delete", QMessageBox.Warning)
            # Exit function
            return
        
        # Get sales person ID from hidden column 0
        sp_id = int(self.sales_person_table.item(current_row, 0).text())
        # Get sales person name from column 1
        sp_name = self.sales_person_table.item(current_row, 1).text()
        
        # Create confirmation dialog
        msg_box = QMessageBox(self)
        # Set window title
        msg_box.setWindowTitle("Delete Sales Person")
        # Set confirmation message
        msg_box.setText(
            f"Are you sure you want to delete '{sp_name}'?\n\n"
            "Note: If this person has existing bills, they will be deactivated instead of deleted."
        )
        # Add Yes and No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Apply styled message box styling
        msg_box.setStyleSheet(self.get_message_box_style())
        
        # Show dialog and get user response
        reply = msg_box.exec_()
        
        # Check if user clicked Yes
        if reply == QMessageBox.Yes:
            # Delete sales person from database
            success, message = db.delete_sales_person(sp_id)
            
            # Check if deletion was successful
            if success:
                # Show success message
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload sales persons table
                self.load_sales_persons()
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def create_company_info(self) -> QGroupBox:
        """Create company information section"""
        # Create group box for company info section
        group = QGroupBox("Company Information")
        # Apply styling with sage green theme
        group.setStyleSheet("""
            QGroupBox {
                height: 500px;
                font-weight: bold;  /* Bold text for group title */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                margin-top: 15px;  /* Top margin for title spacing */
                padding-top: 15px;  /* Top padding for content spacing */
                background-color: #90AB8B;  /* #EBF4DD background */
            }
            QGroupBox::title {
                color: #5A7863;  /* Medium green title color */
                subcontrol-origin: margin;  /* Position title on margin */
                left: 10px;  /* Left offset for title */
                padding: 0 5px;  /* Horizontal padding around title */
            }
        """)
        
        # ✅ CREATE MAIN LAYOUT FOR GROUP BOX
        # Create main vertical layout for group box
        main_group_layout = QVBoxLayout()
        # Set zero margins for tight fit
        main_group_layout.setContentsMargins(0, 0, 0, 0)
        
        # ✅ CREATE SCROLL AREA FOR COMPANY INFO
        # Create scroll area for company information content
        scroll = QScrollArea()
        # Enable automatic resizing of scroll area content
        scroll.setWidgetResizable(True)
        # Remove frame border from scroll area
        scroll.setFrameShape(QFrame.NoFrame)
        # Hide horizontal scrollbar (not needed)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Show vertical scrollbar only when needed
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Apply transparent background to scroll area
        scroll.setStyleSheet("background-color: transparent; border: none;")
        # Set maximum height for scroll area to 400 pixels
        scroll.setMaximumHeight(400)
        
        # ✅ CREATE CONTENT WIDGET FOR SCROLL AREA
        # Create content widget to hold form
        content = QWidget()
        # Apply transparent background to content widget
        content.setStyleSheet("background-color: transparent;")
        # Create vertical layout for content
        layout = QVBoxLayout(content)
        # Set spacing between layout items
        layout.setSpacing(10)
        # Set margins for layout (left, top, right, bottom)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Import company settings module
        from utils.company_settings import company_settings
        # Get all current company settings
        settings = company_settings.get_all()
        
        # Create form layout for input fields
        form = QFormLayout()
        # Set spacing between form rows
        form.setSpacing(10)
        
        # Create input field for company name
        self.company_name_input = QLineEdit(settings.get('company_name', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.company_name_input.setMinimumHeight(40)
        # Apply input field styling
        self.company_name_input.setStyleSheet(self.get_input_style())
        # Add company name field to form with label
        form.addRow(self.create_form_label("Company Name:"), self.company_name_input)
        
        # Create input field for company tagline
        self.company_tagline_input = QLineEdit(settings.get('company_tagline', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.company_tagline_input.setMinimumHeight(40)
        # Apply input field styling
        self.company_tagline_input.setStyleSheet(self.get_input_style())
        # Add tagline field to form with label
        form.addRow(self.create_form_label("Tagline:"), self.company_tagline_input)
        
        # Create input field for company subtitle
        self.company_subtitle_input = QLineEdit(settings.get('company_subtitle', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.company_subtitle_input.setMinimumHeight(40)
        # Apply input field styling
        self.company_subtitle_input.setStyleSheet(self.get_input_style())
        # Add subtitle field to form with label
        form.addRow(self.create_form_label("Subtitle:"), self.company_subtitle_input)
        
        # Create input field for company phone
        self.company_phone_input = QLineEdit(settings.get('phone', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.company_phone_input.setMinimumHeight(40)
        # Apply input field styling
        self.company_phone_input.setStyleSheet(self.get_input_style())
        # Add phone field to form with label
        form.addRow(self.create_form_label("Phone:"), self.company_phone_input)
        
        # Create input field for company email
        self.company_email_input = QLineEdit(settings.get('email', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.company_email_input.setMinimumHeight(40)
        # Apply input field styling
        self.company_email_input.setStyleSheet(self.get_input_style())
        # Add email field to form with label
        form.addRow(self.create_form_label("Email:"), self.company_email_input)
        
        # Create text area for factory address
        self.factory_address_input = QTextEdit(settings.get('factory_address', ''))
        # ✅ INCREASED HEIGHT from 60 to 80 pixels
        self.factory_address_input.setMinimumHeight(80)
        # Set maximum height for text area
        self.factory_address_input.setMaximumHeight(100)
        # Apply text area styling
        self.factory_address_input.setStyleSheet("""
            QTextEdit {
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                padding: 8px;  /* Internal padding */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QTextEdit:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
        """)
        # Add address field to form with label
        form.addRow(self.create_form_label("Address:"), self.factory_address_input)
        
        # Create input field for bank name
        self.bank_name_input = QLineEdit(settings.get('bank_name', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.bank_name_input.setMinimumHeight(40)
        # Apply input field styling
        self.bank_name_input.setStyleSheet(self.get_input_style())
        # Add bank name field to form with label
        form.addRow(self.create_form_label("Bank Name:"), self.bank_name_input)
        
        # Create input field for bank account number
        self.bank_account_input = QLineEdit(settings.get('bank_account_no', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.bank_account_input.setMinimumHeight(40)
        # Apply input field styling
        self.bank_account_input.setStyleSheet(self.get_input_style())
        # Add account number field to form with label
        form.addRow(self.create_form_label("Account No:"), self.bank_account_input)
        
        # Create input field for bank IFSC code
        self.bank_ifsc_input = QLineEdit(settings.get('bank_ifsc', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.bank_ifsc_input.setMinimumHeight(40)
        # Apply input field styling
        self.bank_ifsc_input.setStyleSheet(self.get_input_style())
        # Add IFSC field to form with label
        form.addRow(self.create_form_label("IFSC Code:"), self.bank_ifsc_input)
        
        # Create input field for GSTIN
        self.gstin_input = QLineEdit(settings.get('gstin', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.gstin_input.setMinimumHeight(40)
        # Apply input field styling
        self.gstin_input.setStyleSheet(self.get_input_style())
        # Add GSTIN field to form with label
        form.addRow(self.create_form_label("GSTIN:"), self.gstin_input)
        
        # Create input field for invoice prefix
        self.invoice_prefix_input = QLineEdit(settings.get('invoice_prefix', ''))
        # ✅ INCREASED HEIGHT from 30 to 40 pixels
        self.invoice_prefix_input.setMinimumHeight(40)
        # Apply input field styling
        self.invoice_prefix_input.setStyleSheet(self.get_input_style())
        # Add invoice prefix field to form with label
        form.addRow(self.create_form_label("Invoice Prefix:"), self.invoice_prefix_input)
        
        # Add form layout to content layout
        layout.addLayout(form)
        
        # ✅ SET CONTENT WIDGET TO SCROLL AREA
        # Set content widget as scroll area's widget
        scroll.setWidget(content)
        
        # ✅ ADD SCROLL AREA TO MAIN GROUP LAYOUT
        # Add scroll area to main group layout
        main_group_layout.addWidget(scroll)
        
        # Create "Save Company Information" button with disk icon
        save_btn = QPushButton("💾 Save Company Information")
        # Apply gradient background styling
        save_btn.setStyleSheet("""
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
        # Set minimum height for button
        save_btn.setMinimumHeight(40)
        # Connect click event to save_company_info method
        save_btn.clicked.connect(self.save_company_info)
        # Add save button to main group layout (outside scroll area)
        main_group_layout.addWidget(save_btn)
        
        # Set main layout for group box
        group.setLayout(main_group_layout)
        # Return configured group box
        return group
    
    def create_form_label(self, text: str) -> QLabel:
        """Create styled form label"""
        # Create label with specified text
        label = QLabel(text)
        # Apply dark text color and bold font
        label.setStyleSheet("color: #3B4953; font-weight: bold;")  # Dark blue-grey, bold
        # Return configured label
        return label
    
    def get_input_style(self) -> str:
        """Get input field styling"""
        # Return CSS stylesheet for line edit fields
        return """
            QLineEdit {
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                padding: 8px;  /* Internal padding */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
        """
    
    def save_company_info(self):
        """Save company information"""
        # Import company settings module
        from utils.company_settings import company_settings
        
        # Get current settings dictionary
        settings = company_settings.get_all()
        
        # Update company name from input field
        settings['company_name'] = self.company_name_input.text().strip()
        # Update tagline from input field
        settings['company_tagline'] = self.company_tagline_input.text().strip()
        # Update subtitle from input field
        settings['company_subtitle'] = self.company_subtitle_input.text().strip()
        # Update phone from input field
        settings['phone'] = self.company_phone_input.text().strip()
        # Update email from input field
        settings['email'] = self.company_email_input.text().strip()
        # Update address from text area
        settings['factory_address'] = self.factory_address_input.toPlainText().strip()
        # Update bank name from input field
        settings['bank_name'] = self.bank_name_input.text().strip()
        # Update bank account number from input field
        settings['bank_account_no'] = self.bank_account_input.text().strip()
        # Update bank IFSC code from input field
        settings['bank_ifsc'] = self.bank_ifsc_input.text().strip()
        # Update GSTIN from input field
        settings['gstin'] = self.gstin_input.text().strip()
        # Update invoice prefix from input field
        settings['invoice_prefix'] = self.invoice_prefix_input.text().strip()
        
        # Validate that company name is not empty
        if not settings['company_name']:
            # Show validation error message
            self.show_styled_message("Validation Error", "Company name is required", QMessageBox.Warning)
            # Exit function
            return
        
        # Save settings to database/file
        success = company_settings.update(settings)
        
        # Check if save was successful
        if success:
            # Show success message
            self.show_styled_message("Success", "Company information saved successfully!", QMessageBox.Information)
        else:
            # Show error message
            self.show_styled_message("Error", "Failed to save company information", QMessageBox.Warning)
    
    def create_backup_section(self) -> QGroupBox:
        """Create backup and restore section"""
        # Create group box for backup section
        group = QGroupBox("Backup & Restore")
        # Apply styling with sage green theme
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;  /* Bold text for group title */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                margin-top: 10px;  /* Top margin for title spacing */
                padding-top: 15px;  /* Top padding for content spacing */
                background-color: #EBF4DD;  /* #EBF4DD background */
            }
            QGroupBox::title {
                color: #5A7863;  /* Medium green title color */
                subcontrol-origin: margin;  /* Position title on margin */
                left: 10px;  /* Left offset for title */
                padding: 0 5px;  /* Horizontal padding around title */
            }
        """)
        
        # Create vertical layout for group content
        layout = QVBoxLayout()
        # Set spacing between layout items
        layout.setSpacing(10)
        
        # Create label for backup list section
        list_label = QLabel("Available Backups:")
        # Set font to Arial, 11pt, Bold
        list_label.setFont(QFont("Arial", 11, QFont.Bold))
        # Apply dark text color
        list_label.setStyleSheet("color: #3B4953;")  # Dark blue-grey text
        # Add label to layout
        layout.addWidget(list_label)
        
        # Create list widget for displaying backups
        self.backup_list = QListWidget()
        # Set minimum height for list
        self.backup_list.setMinimumHeight(100)
        # Set maximum height for list
        self.backup_list.setMaximumHeight(150)
        # Apply list widget styling
        self.backup_list.setStyleSheet("""
            QListWidget {
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
                padding: 5px;  /* Internal padding */
            }
            QListWidget::item {
                padding: 5px;  /* Padding for list items */
                border-bottom: 1px solid #EBF4DD;  /* Light cream separator */
            }
            QListWidget::item:selected {
                background-color: #90AB8B;  /* Sage green background for selected item */
                color: #EBF4DD;  /* Cream text color for selected item */
            }
            QListWidget::item:hover {
                background-color: #EBF4DD;  /* Light cream background on hover */
            }
        """)
        # Add list widget to layout
        layout.addWidget(self.backup_list)
        
        # Create horizontal layout for action buttons
        button_layout = QHBoxLayout()
        
        # Create "Create" button with package icon
        create_backup_btn = QPushButton("📦 Create")
        # Apply medium green styling
        create_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;  /* Medium green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #90AB8B;  /* Sage green on hover */
            }
        """)
        # Set minimum height for button
        create_backup_btn.setMinimumHeight(35)
        # Connect click event to create_backup method
        create_backup_btn.clicked.connect(self.create_backup)
        
        # Create "Restore" button with recycle icon
        restore_backup_btn = QPushButton("♻️ Restore")
        # Apply sage green styling
        restore_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;  /* Sage green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Set minimum height for button
        restore_backup_btn.setMinimumHeight(35)
        # Connect click event to restore_backup method
        restore_backup_btn.clicked.connect(self.restore_backup)
        
        # Create "Delete" button with trash icon
        delete_backup_btn = QPushButton("🗑️ Delete")
        # Apply dark blue-grey styling
        delete_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;  /* Dark blue-grey background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Set minimum height for button
        delete_backup_btn.setMinimumHeight(35)
        # Connect click event to delete_backup method
        delete_backup_btn.clicked.connect(self.delete_backup)
        
        # Create "Refresh" button with refresh icon
        refresh_btn = QPushButton("🔄 Refresh")
        # Apply gradient styling from medium to sage green
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);  /* Gradient from sage to medium green */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #90AB8B);  /* Reversed gradient on hover */
            }
        """)
        # Set minimum height for button
        refresh_btn.setMinimumHeight(35)
        # Connect click event to load_backups method
        refresh_btn.clicked.connect(self.load_backups)
        
        # Add "Create" button to button layout
        button_layout.addWidget(create_backup_btn)
        # Add "Restore" button to button layout
        button_layout.addWidget(restore_backup_btn)
        # Add "Delete" button to button layout
        button_layout.addWidget(delete_backup_btn)
        # Add "Refresh" button to button layout
        button_layout.addWidget(refresh_btn)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
        
        # Set layout for group box
        group.setLayout(layout)
        # Return configured group box
        return group
    
    def load_backups(self):
        """Load list of backups"""
        # Clear existing items from backup list
        self.backup_list.clear()
        # Get list of backup files from backup manager
        backups = backup_manager.list_backups()
        
        # Loop through each backup
        for backup in backups:
            # Format backup info as text string
            item_text = f"{backup['name']} - {backup['size_mb']} MB - {backup['created_at']}"
            # Add backup to list widget
            self.backup_list.addItem(item_text)
            # Store backup file path in item's UserRole data
            self.backup_list.item(self.backup_list.count() - 1).setData(Qt.UserRole, backup['path'])
    
    def create_backup(self):
        """Create new backup"""
        # Create confirmation dialog
        msg_box = QMessageBox(self)
        # Set window title
        msg_box.setWindowTitle("Create Backup")
        # Set confirmation message
        msg_box.setText("Do you want to create a backup of the database?")
        # Add Yes and No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Apply styled message box styling
        msg_box.setStyleSheet(self.get_message_box_style())
        
        # Show dialog and get user response
        reply = msg_box.exec_()
        
        # Check if user clicked Yes
        if reply == QMessageBox.Yes:
            # Create backup using backup manager
            success, message, backup_path = backup_manager.create_backup()
            
            # Check if backup was created successfully
            if success:
                # Show success message with backup path
                self.show_styled_message("Success", f"Backup created successfully!\n\n{backup_path}", QMessageBox.Information)
                # Reload backup list
                self.load_backups()
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def restore_backup(self):
        """Restore selected backup"""
        # Get currently selected list item
        current_item = self.backup_list.currentItem()
        
        # Check if no item is selected
        if not current_item:
            # Show warning message
            self.show_styled_message("No Selection", "Please select a backup to restore", QMessageBox.Warning)
            # Exit function
            return
        
        # Get backup file path from item's UserRole data
        backup_path = current_item.data(Qt.UserRole)
        
        # Create warning dialog
        msg_box = QMessageBox(self)
        # Set warning icon
        msg_box.setIcon(QMessageBox.Warning)
        # Set window title
        msg_box.setWindowTitle("Restore Backup")
        # Set warning message
        msg_box.setText(
            "⚠️ WARNING: This will replace your current database!\n\n"
            "Are you sure you want to restore this backup?"
        )
        # Add Yes and No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Apply styled message box styling
        msg_box.setStyleSheet(self.get_message_box_style())
        
        # Show dialog and get user response
        reply = msg_box.exec_()
        
        # Check if user clicked Yes
        if reply == QMessageBox.Yes:
            # Restore backup using backup manager
            success, message = backup_manager.restore_backup(backup_path)
            
            # Check if restore was successful
            if success:
                # Show success message with restart instruction
                self.show_styled_message(
                    "Success",
                    "Database restored successfully!\n\nPlease restart the application.",
                    QMessageBox.Information
                )
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def delete_backup(self):
        """Delete selected backup"""
        # Get currently selected list item
        current_item = self.backup_list.currentItem()
        
        # Check if no item is selected
        if not current_item:
            # Show warning message
            self.show_styled_message("No Selection", "Please select a backup to delete", QMessageBox.Warning)
            # Exit function
            return
        
        # Get backup file path from item's UserRole data
        backup_path = current_item.data(Qt.UserRole)
        
        # Create confirmation dialog
        msg_box = QMessageBox(self)
        # Set window title
        msg_box.setWindowTitle("Delete Backup")
        # Set confirmation message
        msg_box.setText("Are you sure you want to delete this backup?")
        # Add Yes and No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        # Apply styled message box styling
        msg_box.setStyleSheet(self.get_message_box_style())
        
        # Show dialog and get user response
        reply = msg_box.exec_()
        
        # Check if user clicked Yes
        if reply == QMessageBox.Yes:
            # Delete backup using backup manager
            success, message = backup_manager.delete_backup(backup_path)
            
            # Check if deletion was successful
            if success:
                # Show success message
                self.show_styled_message("Success", message, QMessageBox.Information)
                # Reload backup list
                self.load_backups()
            else:
                # Show error message
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def create_stats_section(self) -> QGroupBox:
        """Create database statistics section"""
        # Create group box for statistics section
        group = QGroupBox("Database Statistics")
        # Apply styling with sage green theme
        group.setStyleSheet("""
            QGroupBox {
                height: 300px;
                font-weight: bold;  /* Bold text for group title */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                margin-top: 10px;  /* Top margin for title spacing */
                padding-top: 15px;  /* Top padding for content spacing */
                background-color: #EBF4DD;  /* #EBF4DD background */
            }
            QGroupBox::title {
                color: #5A7863;  /* Medium green title color */
                subcontrol-origin: margin;  /* Position title on margin */
                left: 10px;  /* Left offset for title */
                padding: 0 5px;  /* Horizontal padding around title */
            }
        """)
        
        # ✅ CREATE MAIN LAYOUT FOR GROUP BOX
        # Create main vertical layout for group box
        main_group_layout = QVBoxLayout()
        # Set zero margins for tight fit
        main_group_layout.setContentsMargins(0, 0, 0, 0)
        
        # ✅ CREATE SCROLL AREA FOR DATABASE STATS
        # Create scroll area for statistics content
        scroll = QScrollArea()
        # Enable automatic resizing of scroll area content
        scroll.setWidgetResizable(True)
        # Remove frame border from scroll area
        scroll.setFrameShape(QFrame.NoFrame)
        # Hide horizontal scrollbar (not needed)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Show vertical scrollbar only when needed
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Apply transparent background to scroll area
        scroll.setStyleSheet("background-color: transparent; border: none;")
        # Set maximum height for scroll area to 250 pixels
        scroll.setMaximumHeight(250)
        
        # ✅ CREATE CONTENT WIDGET FOR SCROLL AREA
        # Create content widget to hold statistics label
        content = QWidget()
        # Apply transparent background to content widget
        content.setStyleSheet("background-color: transparent;")
        # Create vertical layout for content
        layout = QVBoxLayout(content)
        # Set spacing between layout items
        layout.setSpacing(10)
        # Set margins for layout (left, top, right, bottom)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create label for displaying statistics
        self.stats_label = QLabel("Loading...")
        # Apply styling with light cream background
        self.stats_label.setStyleSheet("""
            QLabel {
                padding: 15px;  /* Internal padding */
                background-color: #EBF4DD;  /* Light cream background */
                border-radius: 5px;  /* Rounded corners */
                color: #3B4953;  /* Dark blue-grey text color */
                font-size: 11pt;  /* Font size */
            }
        """)
        # ✅ INCREASED MINIMUM HEIGHT from 150 to 200 pixels
        self.stats_label.setMinimumHeight(200)
        # Enable word wrap for long text
        self.stats_label.setWordWrap(True)
        # Set alignment to top left
        self.stats_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # Add label to content layout
        layout.addWidget(self.stats_label)
        
        # ✅ SET CONTENT WIDGET TO SCROLL AREA
        # Set content widget as scroll area's widget
        scroll.setWidget(content)
        
        # ✅ ADD SCROLL AREA TO MAIN GROUP LAYOUT
        # Add scroll area to main group layout
        main_group_layout.addWidget(scroll)
        
        # Create "Refresh Statistics" button with refresh icon
        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        # Apply sage green styling
        refresh_stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #90AB8B;  /* Sage green background */
                color: #EBF4DD;  /* Cream text color */
                padding: 8px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background-color: #5A7863;  /* Medium green on hover */
            }
        """)
        # Set minimum height for button
        refresh_stats_btn.setMinimumHeight(35)
        # Connect click event to load_database_stats method
        refresh_stats_btn.clicked.connect(self.load_database_stats)
        # Add button to main group layout (outside scroll area)
        main_group_layout.addWidget(refresh_stats_btn)
        
        # Set main layout for group box
        group.setLayout(main_group_layout)
        # Return configured group box
        return group
    
    def load_database_stats(self):
        """Load database statistics"""
        # Get database statistics from database manager
        stats = db.get_database_stats()
        
        # Format statistics as HTML string
        stats_text = f"""
        <b style="color: #5A7863;">Database Size:</b> <span style="color: #3B4953;">{stats.get('db_size_mb', 0)} MB</span><br><br>
        <b style="color: #5A7863;">Record Counts:</b><br>
        <span style="color: #3B4953;">Products: {stats.get('products', 0)}</span><br>
        <span style="color: #3B4953;">Customers: {stats.get('customers', 0)}</span><br>
        <span style="color: #3B4953;">Bills: {stats.get('bills', 0)}</span><br>
        <span style="color: #3B4953;">Bill Items: {stats.get('bill_items', 0)}</span><br>
        <span style="color: #3B4953;">Stock History: {stats.get('stock_history', 0)}</span><br>
        <span style="color: #3B4953;">Users: {stats.get('users', 0)}</span><br>
        <span style="color: #3B4953;">Sales Persons: {stats.get('sales_persons', 0)}</span>
        """
        
        # Set formatted text to statistics label
        self.stats_label.setText(stats_text)
    
    def create_password_section(self) -> QGroupBox:
        """Create password change section"""
        # Create group box for password section
        group = QGroupBox("Change Password")
        # Apply styling with sage green theme
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;  /* Bold text for group title */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 8px;  /* Rounded corners */
                margin-top: 10px;  /* Top margin for title spacing */
                padding-top: 15px;  /* Top padding for content spacing */
                background-color: #EBF4DD;  /* #EBF4DD background */
            }
            QGroupBox::title {
                color: #5A7863;  /* Medium green title color */
                subcontrol-origin: margin;  /* Position title on margin */
                left: 10px;  /* Left offset for title */
                padding: 0 5px;  /* Horizontal padding around title */
            }
        """)
        
        # Create vertical layout for group content
        layout = QVBoxLayout()
        # Set spacing between layout items
        layout.setSpacing(10)
        
        # Add label for current password field
        layout.addWidget(self.create_form_label("Current Password:"))
        # Create password input field for current password
        self.old_password = QLineEdit()
        # Set echo mode to hide password characters
        self.old_password.setEchoMode(QLineEdit.Password)
        # Set minimum height for input
        self.old_password.setMinimumHeight(30)
        # Apply input field styling
        self.old_password.setStyleSheet(self.get_input_style())
        # Add current password field to layout
        layout.addWidget(self.old_password)
        
        # Add label for new password field
        layout.addWidget(self.create_form_label("New Password:"))
        # Create password input field for new password
        self.new_password = QLineEdit()
        # Set echo mode to hide password characters
        self.new_password.setEchoMode(QLineEdit.Password)
        # Set minimum height for input
        self.new_password.setMinimumHeight(30)
        # Apply input field styling
        self.new_password.setStyleSheet(self.get_input_style())
        # Add new password field to layout
        layout.addWidget(self.new_password)
        
        # Add label for confirm password field
        layout.addWidget(self.create_form_label("Confirm Password:"))
        # Create password input field for confirm password
        self.confirm_password = QLineEdit()
        # Set echo mode to hide password characters
        self.confirm_password.setEchoMode(QLineEdit.Password)
        # Set minimum height for input
        self.confirm_password.setMinimumHeight(30)
        # Apply input field styling
        self.confirm_password.setStyleSheet(self.get_input_style())
        # Add confirm password field to layout
        layout.addWidget(self.confirm_password)
        
        # Create "Change Password" button with lock icon
        change_btn = QPushButton("🔒 Change Password")
        # Apply gradient background styling
        change_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #3B4953);  /* Gradient from medium green to dark blue-grey */
                color: #EBF4DD;  /* Cream text color */
                padding: 10px;  /* Internal padding */
                border-radius: 5px;  /* Rounded corners */
                font-weight: bold;  /* Bold text */
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);  /* Lighter gradient on hover */
            }
        """)
        # Set minimum height for button
        change_btn.setMinimumHeight(40)
        # Connect click event to change_password method
        change_btn.clicked.connect(self.change_password)
        # Add button to layout
        layout.addWidget(change_btn)
        
        # Set layout for group box
        group.setLayout(layout)
        # Return configured group box
        return group
    
    def change_password(self):
        """Change user password"""
        # Get current password from input field
        old_pass = self.old_password.text()
        # Get new password from input field
        new_pass = self.new_password.text()
        # Get confirm password from input field
        confirm_pass = self.confirm_password.text()
        
        # Check if any password field is empty
        if not old_pass or not new_pass or not confirm_pass:
            # Show validation error message
            self.show_styled_message("Input Error", "Please fill all password fields", QMessageBox.Warning)
            # Exit function
            return
        
        # Check if new password matches confirm password
        if new_pass != confirm_pass:
            # Show password mismatch error
            self.show_styled_message("Password Mismatch", "New password and confirm password do not match", QMessageBox.Warning)
            # Exit function
            return
        
        # Check if new password is at least 6 characters long
        if len(new_pass) < 6:
            # Show weak password error
            self.show_styled_message("Weak Password", "Password must be at least 6 characters long", QMessageBox.Warning)
            # Exit function
            return
        
        # Attempt to change password using auth manager
        success, message = auth_manager.change_password(old_pass, new_pass)
        
        # Check if password change was successful
        if success:
            # Show success message
            self.show_styled_message("Success", message, QMessageBox.Information)
            # Clear current password field
            self.old_password.clear()
            # Clear new password field
            self.new_password.clear()
            # Clear confirm password field
            self.confirm_password.clear()
        else:
            # Show error message
            self.show_styled_message("Error", message, QMessageBox.Warning)
    
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
        """


class SalesPersonDialog(QDialog):
    """Dialog for adding/editing sales person"""
    
    def __init__(self, parent=None, sales_person=None):
        # Initialize the parent QDialog class
        super().__init__(parent)
        # Store sales person data (None for add mode, dict for edit mode)
        self.sales_person = sales_person
        # Determine if dialog is in edit mode
        self.is_edit = sales_person is not None
        # Initialize dialog user interface
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        # Set window title based on mode (Edit or Add)
        self.setWindowTitle("Edit Sales Person" if self.is_edit else "Add Sales Person")
        # Set minimum dialog width to 400 pixels
        self.setMinimumWidth(400)
        # Apply cream background to dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;  /* Light cream background */
            }
            QLabel {
                color: #3B4953;  /* Dark blue-grey text color */
                font-weight: bold;  /* Bold text */
            }
        """)
        
        # Create form layout for input fields
        layout = QFormLayout()
        # Set spacing between form rows
        layout.setSpacing(10)
        
        # Create input field for sales person name
        self.name_input = QLineEdit()
        # Set minimum height for input
        self.name_input.setMinimumHeight(30)
        # If editing, populate with existing name
        if self.sales_person:
            self.name_input.setText(self.sales_person['name'])
        # Apply input field styling
        self.name_input.setStyleSheet(self.get_input_style())
        # Add name field to form with label
        layout.addRow("Name: *", self.name_input)
        
        # Create input field for phone number
        self.phone_input = QLineEdit()
        # Set minimum height for input
        self.phone_input.setMinimumHeight(30)
        # If editing, populate with existing phone
        if self.sales_person:
            self.phone_input.setText(self.sales_person.get('phone', ''))
        # Apply input field styling
        self.phone_input.setStyleSheet(self.get_input_style())
        # Add phone field to form with label
        layout.addRow("Phone:", self.phone_input)
        
        # Create input field for email address
        self.email_input = QLineEdit()
        # Set minimum height for input
        self.email_input.setMinimumHeight(30)
        # If editing, populate with existing email
        if self.sales_person:
            self.email_input.setText(self.sales_person.get('email', ''))
        # Apply input field styling
        self.email_input.setStyleSheet(self.get_input_style())
        # Add email field to form with label
        layout.addRow("Email:", self.email_input)
        
        # Create dialog button box with Save and Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        # Connect accepted signal to dialog accept (Save button)
        buttons.accepted.connect(self.accept)
        # Connect rejected signal to dialog reject (Cancel button)
        buttons.rejected.connect(self.reject)
        # Apply button styling
        buttons.setStyleSheet("""
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
        
        # Add button box to form layout
        layout.addRow(buttons)
        
        # Set form layout as dialog layout
        self.setLayout(layout)
    
    def get_data(self):
        """Get sales person data from form"""
        # Return tuple of name, phone, and email (with #EBF4DDspace removed)
        return (
            self.name_input.text().strip(),
            self.phone_input.text().strip(),
            self.email_input.text().strip()
        )
    
    def get_input_style(self) -> str:
        """Get input field styling"""
        # Return CSS stylesheet for line edit fields
        return """
            QLineEdit {
                background-color: #EBF4DD;  /* #EBF4DD background */
                border: 2px solid #90AB8B;  /* Sage green border */
                border-radius: 5px;  /* Rounded corners */
                padding: 8px;  /* Internal padding */
                color: #3B4953;  /* Dark blue-grey text color */
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;  /* Medium green border on focus */
            }
        """
