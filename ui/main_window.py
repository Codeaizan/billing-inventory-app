from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTabWidget, QPushButton, QLabel, QMessageBox,
                            QStatusBar, QAction, QMenuBar, QApplication)
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
        
        # ✅ SET RESPONSIVE WINDOW SIZE
        # Get screen dimensions
        screen = QApplication.primaryScreen().geometry()
        
        # Set minimum size to prevent UI breaking
        self.setMinimumSize(1200, 700)
        
        # Start with 85% of screen size, centered
        width = int(screen.width() * 0.85)
        height = int(screen.height() * 0.85)
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.setGeometry(x, y, width, height)
        
        # Set global stylesheet with color palette
        self.setStyleSheet("""
            QMainWindow {
                background-color: #EBF4DD;
            }
            QTabWidget::pane {
                border: 2px solid #90AB8B;
                background-color: #EBF4DD;
                border-radius: 8px;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #90AB8B;
                color: #EBF4DD;
                padding: 12px 25px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #5A7863;
                color: #EBF4DD;
            }
            QTabBar::tab:hover {
                background-color: #5A7863;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                background-color: #5A7863;
                color: #EBF4DD;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
            QPushButton:pressed {
                background-color: #3B4953;
            }
            QLabel {
                font-size: 12px;
                color: #3B4953;
            }
            QMenuBar {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #EBF4DD;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #90AB8B;
            }
            QMenu {
                background-color: #EBF4DD;
                color: #3B4953;
                border: 2px solid #90AB8B;
            }
            QMenu::item:selected {
                background-color: #90AB8B;
                color: #EBF4DD;
            }
            QStatusBar {
                background-color: #5A7863;
                color: #EBF4DD;
                font-weight: bold;
            }
            /* ✅ SCROLLBAR STYLING */
            QScrollBar:vertical {
                border: none;
                background: #EBF4DD;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #90AB8B;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5A7863;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #EBF4DD;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #90AB8B;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #5A7863;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
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
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        maximize_action = QAction("Maximize", self)
        maximize_action.triggered.connect(self.showMaximized)
        view_menu.addAction(maximize_action)
        
        normal_action = QAction("Normal Size", self)
        normal_action.triggered.connect(self.showNormal)
        view_menu.addAction(normal_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_header(self) -> QHBoxLayout:
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Create header container with styled background
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: #EBF4DD;
                border-radius: 8px;
                padding: 10px;
                border: 2px solid #90AB8B;
            }
        """)
        
        container_layout = QHBoxLayout(header_container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        
        # Left side - Company info
        left_layout = QVBoxLayout()
        company_label = QLabel(COMPANY_NAME)
        company_label.setFont(QFont("Arial", 16, QFont.Bold))
        company_label.setStyleSheet("color: #5A7863; border: none;")
        
        date_time_label = QLabel()
        date_time_label.setStyleSheet("color: #90AB8B; font-weight: bold; border: none;")
        self.date_time_label = date_time_label
        self.update_datetime()
        
        left_layout.addWidget(company_label)
        left_layout.addWidget(date_time_label)
        
        # Right side - User info and logout
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)
        
        user_label = QLabel(f"👤 {self.current_user['full_name']}")
        user_label.setFont(QFont("Arial", 12, QFont.Bold))
        user_label.setStyleSheet("color: #3B4953; border: none;")
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #3B4953);
                color: #EBF4DD;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);
            }
            QPushButton:pressed {
                background: #3B4953;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        
        right_layout.addWidget(user_label, alignment=Qt.AlignRight)
        right_layout.addWidget(logout_btn, alignment=Qt.AlignRight)
        
        container_layout.addLayout(left_layout)
        container_layout.addStretch()
        container_layout.addLayout(right_layout)
        
        header_layout.addWidget(header_container)
        
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
        
        # Custom styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Create Backup")
        msg_box.setText("Do you want to create a backup of the database?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
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
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            success, message, backup_path = backup_manager.create_backup()
            
            result_box = QMessageBox(self)
            result_box.setStyleSheet(msg_box.styleSheet())
            
            if success:
                result_box.setIcon(QMessageBox.Information)
                result_box.setWindowTitle("Backup Created")
                result_box.setText(f"Backup created successfully!\n\n{backup_path}")
            else:
                result_box.setIcon(QMessageBox.Warning)
                result_box.setWindowTitle("Backup Failed")
                result_box.setText(message)
            
            result_box.exec_()
    
    def logout(self):
        """Logout current user"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
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
        """)
        
        reply = msg_box.exec_()
        
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
        <h2 style="color: #5A7863;">{APP_NAME}</h2>
        <p style="color: #3B4953;"><b>Version:</b> {APP_VERSION}</p>
        <p style="color: #3B4953;"><b>Company:</b> {COMPANY_NAME}</p>
        <br>
        <p style="color: #3B4953;">A complete billing and inventory management system for Ayurvedic medicine business.</p>
        <br>
        <p style="color: #3B4953;"><b>Features:</b></p>
        <ul style="color: #3B4953;">
            <li>GST & Non-GST Bill Generation</li>
            <li>Sales Person Management</li>
            <li>Inventory Management with Batch Tracking</li>
            <li>Real-time Stock Updates</li>
            <li>Sales Reports and Analytics</li>
            <li>Customer Management</li>
            <li>Excel Export with Sales Data</li>
            <li>Database Backup and Restore</li>
        </ul>
        <br>
        <p style="color: #90AB8B;">© 2026 {COMPANY_NAME}. All rights reserved.</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
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
        msg_box.exec_()
    
    def closeEvent(self, event):
        """Handle window close event"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Exit Application")
        msg_box.setText("Are you sure you want to exit?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
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
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
