from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from modules.auth import auth_manager
from config import APP_NAME, COMPANY_NAME
from utils.logger import logger


class LoginWindow(QWidget):
    """Login window for user authentication"""
    
    login_successful = pyqtSignal(dict)  # Signal emitted on successful login
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} - Login")
        self.setFixedSize(700, 1000)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton#loginBtn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#loginBtn:hover {
                background-color: #45a049;
            }
            QPushButton#loginBtn:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Logo/Title section - SIMPLIFIED
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        # Company name - Simple plain text
        company_label = QLabel("Natural Health World")
        company_label.setAlignment(Qt.AlignCenter)
        company_label.setStyleSheet("""
            color: #4CAF50;
            font-size: 16pt;
            font-weight: bold;
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif;
        """)
        
        # Tagline
        tagline_label = QLabel("The Herbal Healing")
        tagline_label.setAlignment(Qt.AlignCenter)
        tagline_label.setStyleSheet("""
            color: #666;
            font-size: 10pt;
            font-style: italic;
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif;
        """)
        
        # App name
        app_label = QLabel("Billing & Inventory System")
        app_label.setAlignment(Qt.AlignCenter)
        app_label.setStyleSheet("""
            color: #666;
            font-size: 10pt;
            font-family: 'Calibri', 'Segoe UI', 'Arial', sans-serif;
        """)
        
        title_layout.addWidget(company_label)
        title_layout.addWidget(tagline_label)
        title_layout.addWidget(app_label)
        
        main_layout.addWidget(title_frame)
        main_layout.addSpacing(20)
        
        # Login form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.returnPressed.connect(self.on_login)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.on_login)
        
        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.on_login)
        
        # Add to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.login_btn)
        
        main_layout.addWidget(form_frame)
        
        # Info label
        info_label = QLabel("Default credentials: admin / admin123")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #999; font-size: 10pt;")
        main_layout.addWidget(info_label)
        
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Set focus to username
        self.username_input.setFocus()
    
    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password")
            return
        
        # Disable login button during authentication
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")
        
        # Authenticate
        success, message, user_data = auth_manager.login(username, password)
        
        # Re-enable login button
        self.login_btn.setEnabled(True)
        self.login_btn.setText("LOGIN")
        
        if success:
            logger.info(f"Login successful: {username}")
            self.login_successful.emit(user_data)
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", message)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close()
