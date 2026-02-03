from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QPushButton, QLabel, QMessageBox,
                            QStatusBar, QAction, QMenuBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime
from config import APP_NAME, COMPANY_NAME, APP_VERSION
from modules.auth import auth_manager
from utils.logger import logger

class MainWindow(QMainWindow):
    """Main application window with tabs"""
    
    def __init__(self):
        super().__init__()
        self.current_user = auth_manager.get_current_user()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} - {COMPANY_NAME}")
        self.setGeometry(100, 50, 1400, 800)
        
        # Set global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333;
                padding: 12px 25px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #4CAF50;
            }
            QTabBar::tab:hover {
                background-color: #d5d5d5;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QLabel {
                font-size: 12px;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Import and add tabs
        from ui.billing_page import BillingPage
        from ui.inventory_page import InventoryPage
        from ui.reports_page import ReportsPage
        from ui.settings_page import SettingsPage
        
        self.billing_page = BillingPage()
        self.inventory_page = InventoryPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()
        
        self.tab_widget.addTab(self.billing_page, "📝 Billing")
        self.tab_widget.addTab(self.inventory_page, "📦 Inventory")
        self.tab_widget.addTab(self.reports_page, "📊 Reports")
        self.tab_widget.addTab(self.settings_page, "⚙️ Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        backup_action = QAction("Create Backup", self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_header(self) -> QHBoxLayout:
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Left side - Company info
        left_layout = QVBoxLayout()
        company_label = QLabel(COMPANY_NAME)
        company_label.setFont(QFont("Arial", 16, QFont.Bold))
        company_label.setStyleSheet("color: #4CAF50;")
        
        date_time_label = QLabel()
        date_time_label.setStyleSheet("color: #666;")
        self.date_time_label = date_time_label
        self.update_datetime()
        
        left_layout.addWidget(company_label)
        left_layout.addWidget(date_time_label)
        
        # Right side - User info and logout
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)
        
        user_label = QLabel(f"👤 {self.current_user['full_name']}")
        user_label.setFont(QFont("Arial", 12, QFont.Bold))
        user_label.setStyleSheet("color: #333;")
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        
        right_layout.addWidget(user_label, alignment=Qt.AlignRight)
        right_layout.addWidget(logout_btn, alignment=Qt.AlignRight)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        header_layout.addLayout(right_layout)
        
        return header_layout
    
    def setup_timer(self):
        """Setup timer to update date/time"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second
    
    def update_datetime(self):
        """Update date and time display"""
        now = datetime.now()
        date_time_str = now.strftime("%A, %B %d, %Y  %I:%M:%S %p")
        self.date_time_label.setText(date_time_str)
    
    def create_backup(self):
        """Create database backup"""
        from modules.backup import backup_manager
        
        reply = QMessageBox.question(
            self, "Create Backup",
            "Do you want to create a backup of the database?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message, backup_path = backup_manager.create_backup()
            if success:
                QMessageBox.information(self, "Backup Created", f"Backup created successfully!\n\n{backup_path}")
            else:
                QMessageBox.warning(self, "Backup Failed", message)
    
    def logout(self):
        """Logout current user"""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            auth_manager.logout()
            self.close()
            
            # Show login window again
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.login_successful.connect(self.on_login_success)
            self.login_window.show()
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        # Reload main window with new user
        self.__init__()
        self.show()
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p><b>Company:</b> {COMPANY_NAME}</p>
        <br>
        <p>A complete billing and inventory management system for Ayurvedic medicine business.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>Bill Generation with Discount Management</li>
            <li>Inventory Management with Batch Tracking</li>
            <li>Sales Reports and Analytics</li>
            <li>Customer Management</li>
            <li>Database Backup and Restore</li>
        </ul>
        <br>
        <p>© 2026 {COMPANY_NAME}. All rights reserved.</p>
        """
        
        QMessageBox.about(self, "About", about_text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
