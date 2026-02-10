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
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # ✅ CREATE SCROLL AREA for entire page content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: #EBF4DD;")
        
        # Create content widget
        content = QWidget()
        content.setStyleSheet("background-color: #EBF4DD;")
        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #5A7863; border: none;")
        main_layout.addWidget(title)
        
        # Sales Person Management section
        sales_person_group = self.create_sales_person_section()
        main_layout.addWidget(sales_person_group)
        
        # ✅ REMOVED: Company Information section
        # Now accessible only from Settings menu
        
        # Backup and Restore section
        backup_group = self.create_backup_section()
        main_layout.addWidget(backup_group)
        
        # Database Statistics section
        stats_group = self.create_stats_section()
        main_layout.addWidget(stats_group)
        
        # Password Change section
        password_group = self.create_password_section()
        main_layout.addWidget(password_group)
        
        # Add stretch to push content to top
        main_layout.addStretch()
        
        # Set content to scroll area
        scroll.setWidget(content)
        
        # Main layout for page
        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        self.setLayout(page_layout)
        
        # Load data on startup
        self.load_database_stats()
        self.load_backups()
        self.load_sales_persons()
    
    def create_sales_person_section(self) -> QGroupBox:
        """Create sales person management section"""
        group = QGroupBox("Sales Person Management")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #EBF4DD;
            }
            QGroupBox::title {
                color: #5A7863;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Info label
        info_label = QLabel("Manage sales persons who can create bills")
        info_label.setStyleSheet("color: #90AB8B; font-style: italic;")
        layout.addWidget(info_label)
        
        # Table
        self.sales_person_table = QTableWidget()
        self.sales_person_table.setColumnCount(4)
        self.sales_person_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Status"])
        self.sales_person_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sales_person_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_person_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_person_table.hideColumn(0)
        self.sales_person_table.setMinimumHeight(150)
        self.sales_person_table.setMaximumHeight(250)
        self.sales_person_table.setStyleSheet("""
            QTableWidget {
                background-color: #EBF4DD;
                alternate-background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
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
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.sales_person_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_sp_btn = QPushButton("➕ Add")
        add_sp_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        add_sp_btn.setMinimumHeight(35)
        add_sp_btn.clicked.connect(self.add_sales_person)
        
        edit_sp_btn = QPushButton("✏️ Edit")
        edit_sp_btn.setStyleSheet("""
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
        edit_sp_btn.setMinimumHeight(35)
        edit_sp_btn.clicked.connect(self.edit_sales_person)
        
        delete_sp_btn = QPushButton("🗑️ Delete")
        delete_sp_btn.setStyleSheet("""
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
        delete_sp_btn.setMinimumHeight(35)
        delete_sp_btn.clicked.connect(self.delete_sales_person)
        
        btn_layout.addWidget(add_sp_btn)
        btn_layout.addWidget(edit_sp_btn)
        btn_layout.addWidget(delete_sp_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def load_sales_persons(self):
        """Load sales persons into table"""
        sales_persons = db.get_all_sales_persons(active_only=False)
        
        self.sales_person_table.setRowCount(len(sales_persons))
        
        for row, sp in enumerate(sales_persons):
            self.sales_person_table.setItem(row, 0, QTableWidgetItem(str(sp['id'])))
            self.sales_person_table.setItem(row, 1, QTableWidgetItem(sp['name']))
            self.sales_person_table.setItem(row, 2, QTableWidgetItem(sp.get('phone', '')))
            
            status = "Active" if sp['is_active'] else "Inactive"
            status_item = QTableWidgetItem(status)
            if not sp['is_active']:
                status_item.setForeground(Qt.red)
            self.sales_person_table.setItem(row, 3, status_item)
    
    def add_sales_person(self):
        """Add new sales person"""
        dialog = SalesPersonDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            name, phone, email = dialog.get_data()
            
            success, message, sp_id = db.add_sales_person(name, phone, email)
            
            if success:
                self.show_styled_message("Success", message, QMessageBox.Information)
                self.load_sales_persons()
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def edit_sales_person(self):
        """Edit selected sales person"""
        current_row = self.sales_person_table.currentRow()
        
        if current_row < 0:
            self.show_styled_message("No Selection", "Please select a sales person to edit", QMessageBox.Warning)
            return
        
        sp_id = int(self.sales_person_table.item(current_row, 0).text())
        sp_data = db.get_sales_person_by_id(sp_id)
        
        if not sp_data:
            self.show_styled_message("Error", "Sales person not found", QMessageBox.Warning)
            return
        
        dialog = SalesPersonDialog(self, sp_data)
        
        if dialog.exec_() == QDialog.Accepted:
            name, phone, email = dialog.get_data()
            
            success, message = db.update_sales_person(sp_id, name, phone, email)
            
            if success:
                self.show_styled_message("Success", message, QMessageBox.Information)
                self.load_sales_persons()
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def delete_sales_person(self):
        """Delete selected sales person"""
        current_row = self.sales_person_table.currentRow()
        
        if current_row < 0:
            self.show_styled_message("No Selection", "Please select a sales person to delete", QMessageBox.Warning)
            return
        
        sp_id = int(self.sales_person_table.item(current_row, 0).text())
        sp_name = self.sales_person_table.item(current_row, 1).text()
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Sales Person")
        msg_box.setText(
            f"Are you sure you want to delete '{sp_name}'?\n\n"
            "Note: If this person has existing bills, they will be deactivated instead of deleted."
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(self.get_message_box_style())
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            success, message = db.delete_sales_person(sp_id)
            
            if success:
                self.show_styled_message("Success", message, QMessageBox.Information)
                self.load_sales_persons()
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    # ✅ REMOVED: create_company_info() method
    # ✅ REMOVED: save_company_info() method
    # Company settings now only accessible from Settings → Company Settings menu
    
    def create_backup_section(self) -> QGroupBox:
        """Create backup and restore section"""
        group = QGroupBox("Backup & Restore")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #EBF4DD;
            }
            QGroupBox::title {
                color: #5A7863;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        list_label = QLabel("Available Backups:")
        list_label.setFont(QFont("Arial", 11, QFont.Bold))
        list_label.setStyleSheet("color: #3B4953;")
        layout.addWidget(list_label)
        
        self.backup_list = QListWidget()
        self.backup_list.setMinimumHeight(100)
        self.backup_list.setMaximumHeight(150)
        self.backup_list.setStyleSheet("""
            QListWidget {
                background-color: #EBF4DD;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                color: #3B4953;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #EBF4DD;
            }
            QListWidget::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QListWidget::item:hover {
                background-color: #EBF4DD;
            }
        """)
        layout.addWidget(self.backup_list)
        
        button_layout = QHBoxLayout()
        
        create_backup_btn = QPushButton("📦 Create")
        create_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        create_backup_btn.setMinimumHeight(35)
        create_backup_btn.clicked.connect(self.create_backup)
        
        restore_backup_btn = QPushButton("♻️ Restore")
        restore_backup_btn.setStyleSheet("""
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
        restore_backup_btn.setMinimumHeight(35)
        restore_backup_btn.clicked.connect(self.restore_backup)
        
        delete_backup_btn = QPushButton("🗑️ Delete")
        delete_backup_btn.setStyleSheet("""
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
        delete_backup_btn.setMinimumHeight(35)
        delete_backup_btn.clicked.connect(self.delete_backup)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);
                color: #EBF4DD;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #90AB8B);
            }
        """)
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self.load_backups)
        
        button_layout.addWidget(create_backup_btn)
        button_layout.addWidget(restore_backup_btn)
        button_layout.addWidget(delete_backup_btn)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
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
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Create Backup")
        msg_box.setText("Do you want to create a backup of the database?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(self.get_message_box_style())
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            success, message, backup_path = backup_manager.create_backup()
            
            if success:
                self.show_styled_message("Success", f"Backup created successfully!\n\n{backup_path}", QMessageBox.Information)
                self.load_backups()
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def restore_backup(self):
        """Restore selected backup"""
        current_item = self.backup_list.currentItem()
        
        if not current_item:
            self.show_styled_message("No Selection", "Please select a backup to restore", QMessageBox.Warning)
            return
        
        backup_path = current_item.data(Qt.UserRole)
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Restore Backup")
        msg_box.setText(
            "⚠️ WARNING: This will replace your current database!\n\n"
            "Are you sure you want to restore this backup?"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(self.get_message_box_style())
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            success, message = backup_manager.restore_backup(backup_path)
            
            if success:
                self.show_styled_message(
                    "Success",
                    "Database restored successfully!\n\nPlease restart the application.",
                    QMessageBox.Information
                )
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def delete_backup(self):
        """Delete selected backup"""
        current_item = self.backup_list.currentItem()
        
        if not current_item:
            self.show_styled_message("No Selection", "Please select a backup to delete", QMessageBox.Warning)
            return
        
        backup_path = current_item.data(Qt.UserRole)
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Backup")
        msg_box.setText("Are you sure you want to delete this backup?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet(self.get_message_box_style())
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            success, message = backup_manager.delete_backup(backup_path)
            
            if success:
                self.show_styled_message("Success", message, QMessageBox.Information)
                self.load_backups()
            else:
                self.show_styled_message("Error", message, QMessageBox.Warning)
    
    def create_stats_section(self) -> QGroupBox:
        """Create database statistics section"""
        group = QGroupBox("Database Statistics")
        group.setStyleSheet("""
            QGroupBox {
                height: 300px;
                font-weight: bold;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #EBF4DD;
            }
            QGroupBox::title {
                color: #5A7863;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        main_group_layout = QVBoxLayout()
        main_group_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        scroll.setMaximumHeight(250)
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #EBF4DD;
                border-radius: 5px;
                color: #3B4953;
                font-size: 11pt;
            }
        """)
        self.stats_label.setMinimumHeight(200)
        self.stats_label.setWordWrap(True)
        self.stats_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.stats_label)
        
        scroll.setWidget(content)
        main_group_layout.addWidget(scroll)
        
        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.setStyleSheet("""
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
        refresh_stats_btn.setMinimumHeight(35)
        refresh_stats_btn.clicked.connect(self.load_database_stats)
        main_group_layout.addWidget(refresh_stats_btn)
        
        group.setLayout(main_group_layout)
        return group
    
    def load_database_stats(self):
        """Load database statistics"""
        stats = db.get_database_stats()
        
        stats_text = f"""
        <b style="color: #5A7863;">Database Size:</b> <span style="color: #3B4953;">{stats.get('db_size_mb', 0)} MB</span><br><br>
        <b style="color: #5A7863;">Record Counts:</b><br>
        <span style="color: #3B4953;">Products: {stats.get('products', 0)}</span><br>
        <span style="color: #3B4953;">Customers: {stats.get('customers', 0)}</span><br>
        <span style="color: #3B4953;">Bills: {stats.get('bills', 0)}</span><br>
        <span style="color: #3B4953;">Bill Items: {stats.get('bill_items', 0)}</span><br>
        <span style="color: #3B4953;">Stock History: {stats.get('stock_history', 0)}</span><br>
        <span style="color: #3B4953;">Users: {stats.get('users', 0)}</span><br>
        <span style="color: #3B4953;">Sales Persons: {stats.get('salespersons', 0)}</span>
        """
        
        self.stats_label.setText(stats_text)
    
    def create_password_section(self) -> QGroupBox:
        """Create password change section"""
        group = QGroupBox("Change Password")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #90AB8B;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #EBF4DD;
            }
            QGroupBox::title {
                color: #5A7863;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        layout.addWidget(self.create_form_label("Current Password:"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setMinimumHeight(30)
        self.old_password.setStyleSheet(self.get_input_style())
        layout.addWidget(self.old_password)
        
        layout.addWidget(self.create_form_label("New Password:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setMinimumHeight(30)
        self.new_password.setStyleSheet(self.get_input_style())
        layout.addWidget(self.new_password)
        
        layout.addWidget(self.create_form_label("Confirm Password:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(30)
        self.confirm_password.setStyleSheet(self.get_input_style())
        layout.addWidget(self.confirm_password)
        
        change_btn = QPushButton("🔒 Change Password")
        change_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #3B4953);
                color: #EBF4DD;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);
            }
        """)
        change_btn.setMinimumHeight(40)
        change_btn.clicked.connect(self.change_password)
        layout.addWidget(change_btn)
        
        group.setLayout(layout)
        return group
    
    def create_form_label(self, text: str) -> QLabel:
        """Create styled form label"""
        label = QLabel(text)
        label.setStyleSheet("color: #3B4953; font-weight: bold;")
        return label
    
    def get_input_style(self) -> str:
        """Get input field styling"""
        return """
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
        """
    
    def change_password(self):
        """Change user password"""
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        
        if not old_pass or not new_pass or not confirm_pass:
            self.show_styled_message("Input Error", "Please fill all password fields", QMessageBox.Warning)
            return
        
        if new_pass != confirm_pass:
            self.show_styled_message("Password Mismatch", "New password and confirm password do not match", QMessageBox.Warning)
            return
        
        if len(new_pass) < 6:
            self.show_styled_message("Weak Password", "Password must be at least 6 characters long", QMessageBox.Warning)
            return
        
        success, message = auth_manager.change_password(old_pass, new_pass)
        
        if success:
            self.show_styled_message("Success", message, QMessageBox.Information)
            self.old_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            self.show_styled_message("Error", message, QMessageBox.Warning)
    
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


class SalesPersonDialog(QDialog):
    """Dialog for adding/editing sales person"""
    
    def __init__(self, parent=None, sales_person=None):
        super().__init__(parent)
        self.sales_person = sales_person
        self.is_edit = sales_person is not None
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Sales Person" if self.is_edit else "Add Sales Person")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
                font-weight: bold;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(30)
        if self.sales_person:
            self.name_input.setText(self.sales_person['name'])
        self.name_input.setStyleSheet(self.get_input_style())
        layout.addRow("Name: *", self.name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(30)
        if self.sales_person:
            self.phone_input.setText(self.sales_person.get('phone', ''))
        self.phone_input.setStyleSheet(self.get_input_style())
        layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(30)
        if self.sales_person:
            self.email_input.setText(self.sales_person.get('email', ''))
        self.email_input.setStyleSheet(self.get_input_style())
        layout.addRow("Email:", self.email_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
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
        
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Get sales person data from form"""
        return (
            self.name_input.text().strip(),
            self.phone_input.text().strip(),
            self.email_input.text().strip()
        )
    
    def get_input_style(self) -> str:
        """Get input field styling"""
        return """
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
        """
