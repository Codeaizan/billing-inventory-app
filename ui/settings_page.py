from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QGroupBox, QLineEdit, QTextEdit,
                            QMessageBox, QListWidget, QFrame, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.backup import backup_manager
from modules.auth import auth_manager
from database.db_manager import db
from config import (COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE, 
                   COMPANY_EMAIL, BANK_NAME, BANK_ACCOUNT_NO, BANK_IFSC,
                   APP_VERSION)
from utils.logger import logger

class SettingsPage(QWidget):
    """Settings and configuration page"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")
        main_layout.addWidget(title)
        
        # Company Information
        company_group = self.create_company_info()
        main_layout.addWidget(company_group)
        
        # Backup & Restore
        backup_group = self.create_backup_section()
        main_layout.addWidget(backup_group)
        
        # Database Statistics
        stats_group = self.create_stats_section()
        main_layout.addWidget(stats_group)
        
        # Change Password
        password_group = self.create_password_section()
        main_layout.addWidget(password_group)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Load initial data
        self.load_database_stats()
        self.load_backups()
    
    def create_company_info(self) -> QGroupBox:
        """Create company information section"""
        group = QGroupBox("Company Information")
        layout = QVBoxLayout()
        
        # Get current settings
        from utils.company_settings import company_settings
        settings = company_settings.get_all()
        
        # Create form
        from PyQt5.QtWidgets import QFormLayout, QTextEdit
        form = QFormLayout()
        
        self.company_name_input = QLineEdit(settings.get('company_name', ''))
        form.addRow("Company Name:", self.company_name_input)
        
        self.company_tagline_input = QLineEdit(settings.get('company_tagline', ''))
        form.addRow("Tagline:", self.company_tagline_input)
        
        self.company_subtitle_input = QLineEdit(settings.get('company_subtitle', ''))
        form.addRow("Subtitle:", self.company_subtitle_input)
        
        self.company_phone_input = QLineEdit(settings.get('phone', ''))
        form.addRow("Phone:", self.company_phone_input)
        
        self.company_email_input = QLineEdit(settings.get('email', ''))
        form.addRow("Email:", self.company_email_input)
        
        self.factory_address_input = QTextEdit(settings.get('factory_address', ''))
        self.factory_address_input.setMaximumHeight(60)
        form.addRow("Address:", self.factory_address_input)
        
        self.bank_name_input = QLineEdit(settings.get('bank_name', ''))
        form.addRow("Bank Name:", self.bank_name_input)
        
        self.bank_account_input = QLineEdit(settings.get('bank_account_no', ''))
        form.addRow("Account No:", self.bank_account_input)
        
        self.bank_ifsc_input = QLineEdit(settings.get('bank_ifsc', ''))
        form.addRow("IFSC Code:", self.bank_ifsc_input)
        
        self.gstin_input = QLineEdit(settings.get('gstin', ''))
        form.addRow("GSTIN:", self.gstin_input)
        
        self.invoice_prefix_input = QLineEdit(settings.get('invoice_prefix', ''))
        form.addRow("Invoice Prefix:", self.invoice_prefix_input)
        
        layout.addLayout(form)
        
        # Save button
        save_btn = QPushButton("💾 Save Company Information")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_company_info)
        layout.addWidget(save_btn)
        
        group.setLayout(layout)
        return group
    
    def save_company_info(self):
        """Save company information"""
        from utils.company_settings import company_settings
        
        # Get current settings
        settings = company_settings.get_all()
        
        # Update with form values
        settings['company_name'] = self.company_name_input.text().strip()
        settings['company_tagline'] = self.company_tagline_input.text().strip()
        settings['company_subtitle'] = self.company_subtitle_input.text().strip()
        settings['phone'] = self.company_phone_input.text().strip()
        settings['email'] = self.company_email_input.text().strip()
        settings['factory_address'] = self.factory_address_input.toPlainText().strip()
        settings['bank_name'] = self.bank_name_input.text().strip()
        settings['bank_account_no'] = self.bank_account_input.text().strip()
        settings['bank_ifsc'] = self.bank_ifsc_input.text().strip()
        settings['gstin'] = self.gstin_input.text().strip()
        settings['invoice_prefix'] = self.invoice_prefix_input.text().strip()
        
        # Validate
        if not settings['company_name']:
            QMessageBox.warning(self, "Validation Error", "Company name is required")
            return
        
        # Save
        success = company_settings.update(settings)
        
        if success:
            QMessageBox.information(self, "Success", "Company information saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save company information")

    
    def create_backup_section(self) -> QGroupBox:
        """Create backup and restore section"""
        group = QGroupBox("Backup & Restore")
        layout = QVBoxLayout()
        
        # Backup list
        list_label = QLabel("Available Backups:")
        list_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(list_label)
        
        self.backup_list = QListWidget()
        self.backup_list.setMaximumHeight(150)
        layout.addWidget(self.backup_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_backup_btn = QPushButton("📦 Create Backup")
        create_backup_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        create_backup_btn.clicked.connect(self.create_backup)
        
        restore_backup_btn = QPushButton("♻️ Restore Selected")
        restore_backup_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        restore_backup_btn.clicked.connect(self.restore_backup)
        
        delete_backup_btn = QPushButton("🗑️ Delete Selected")
        delete_backup_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        delete_backup_btn.clicked.connect(self.delete_backup)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        refresh_btn.clicked.connect(self.load_backups)
        
        button_layout.addWidget(create_backup_btn)
        button_layout.addWidget(restore_backup_btn)
        button_layout.addWidget(delete_backup_btn)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_stats_section(self) -> QGroupBox:
        """Create database statistics section"""
        group = QGroupBox("Database Statistics")
        layout = QVBoxLayout()
        
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("padding: 10px; background-color: #f9f9f9; border-radius: 5px;")
        layout.addWidget(self.stats_label)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        refresh_stats_btn.clicked.connect(self.load_database_stats)
        layout.addWidget(refresh_stats_btn)
        
        group.setLayout(layout)
        return group
    
    def create_password_section(self) -> QGroupBox:
        """Create password change section"""
        group = QGroupBox("Change Password")
        layout = QVBoxLayout()
        
        # Old password
        layout.addWidget(QLabel("Current Password:"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password)
        
        # New password
        layout.addWidget(QLabel("New Password:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)
        
        # Confirm password
        layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)
        
        # Change button
        change_btn = QPushButton("🔒 Change Password")
        change_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        change_btn.clicked.connect(self.change_password)
        layout.addWidget(change_btn)
        
        group.setLayout(layout)
        return group
    
    def load_backups(self):
        """Load list of backups"""
        self.backup_list.clear()
        backups = backup_manager.list_backups()
        
        for backup in backups:
            item_text = f"{backup['name']} - {backup['size_mb']} MB - {backup['created_at']}"
            self.backup_list.addItem(item_text)
            self.backup_list.item(self.backup_list.count() - 1).setData(Qt.UserRole, backup['path'])
    
    def create_backup(self):
        """Create new backup"""
        reply = QMessageBox.question(
            self, "Create Backup",
            "Do you want to create a backup of the database?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message, backup_path = backup_manager.create_backup()
            
            if success:
                QMessageBox.information(self, "Success", f"Backup created successfully!\n\n{backup_path}")
                self.load_backups()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def restore_backup(self):
        """Restore selected backup"""
        current_item = self.backup_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to restore")
            return
        
        backup_path = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.warning(
            self, "Restore Backup",
            "⚠️ WARNING: This will replace your current database!\n\n"
            "Are you sure you want to restore this backup?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = backup_manager.restore_backup(backup_path)
            
            if success:
                QMessageBox.information(
                    self, "Success",
                    "Database restored successfully!\n\nPlease restart the application."
                )
            else:
                QMessageBox.warning(self, "Error", message)
    
    def delete_backup(self):
        """Delete selected backup"""
        current_item = self.backup_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to delete")
            return
        
        backup_path = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Backup",
            "Are you sure you want to delete this backup?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = backup_manager.delete_backup(backup_path)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_backups()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def load_database_stats(self):
        """Load database statistics"""
        stats = db.get_database_stats()
        
        stats_text = f"""
        <b>Database Size:</b> {stats.get('db_size_mb', 0)} MB<br><br>
        <b>Record Counts:</b><br>
        Products: {stats.get('products', 0)}<br>
        Customers: {stats.get('customers', 0)}<br>
        Bills: {stats.get('bills', 0)}<br>
        Bill Items: {stats.get('bill_items', 0)}<br>
        Stock History: {stats.get('stock_history', 0)}<br>
        Users: {stats.get('users', 0)}
        """
        
        self.stats_label.setText(stats_text)
    
    def change_password(self):
        """Change user password"""
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        
        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Input Error", "Please fill all password fields")
            return
        
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Password Mismatch", "New password and confirm password do not match")
            return
        
        if len(new_pass) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters long")
            return
        
        success, message = auth_manager.change_password(old_pass, new_pass)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.old_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            QMessageBox.warning(self, "Error", message)
