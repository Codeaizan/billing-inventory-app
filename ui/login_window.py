from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QLinearGradient, QColor, QBrush, QPainter
from modules.auth import auth_manager
from config import APP_NAME, COMPANY_NAME
from utils.logger import logger


class LoginWindow(QWidget):
    """Modern login window with gradient background"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{APP_NAME} - Login")
        self.setFixedSize(800, 800)
        
        # Set gradient background using color palette
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColor("#90AB8B"))  # Muted sage green
        gradient.setColorAt(0.5, QColor("#5A7863"))  # Medium dark green
        gradient.setColorAt(1, QColor("#3B4953"))  # Dark blue-grey
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Add stretch at top
        main_layout.addStretch(1)
        
        # Login card
        login_card = self.create_login_card()
        main_layout.addWidget(login_card)
        
        # Add stretch at bottom
        main_layout.addStretch(2)
        
        # Footer
        footer = QLabel("© 2026 Natural Health World")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #EBF4DD; font-size: 10pt; opacity: 0.9;")
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
        
        # Set focus
        self.username_input.setFocus()
    
    def create_login_card(self) -> QFrame:
        """Create the login card with shadow effect"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #EBF4DD;
                border-radius: 15px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(59, 73, 83, 100))  # #3B4953 with transparency
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo/Icon section
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(5)
        
        # Icon
        icon_label = QLabel("🌿")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48pt;")
        
        # Company name
        company_label = QLabel("Natural Health World")
        company_label.setAlignment(Qt.AlignCenter)
        company_label.setStyleSheet("""
            color: #5A7863;
            font-size: 20pt;
            font-weight: bold;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        """)
        
        # Tagline
        tagline_label = QLabel("The Herbal Healing")
        tagline_label.setAlignment(Qt.AlignCenter)
        tagline_label.setStyleSheet("""
            color: #90AB8B;
            font-size: 11pt;
            font-style: italic;
            margin-bottom: 10px;
        """)
        
        logo_layout.addWidget(icon_label)
        logo_layout.addWidget(company_label)
        logo_layout.addWidget(tagline_label)
        
        layout.addLayout(logo_layout)
        layout.addSpacing(10)
        
        # Login title
        login_title = QLabel("Sign In")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("""
            color: #3B4953;
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        layout.addWidget(login_title)
        
        # Username field
        username_container = self.create_input_field(
            "👤", "Username", False
        )
        self.username_input = username_container.findChild(QLineEdit)
        layout.addWidget(username_container)
        
        # Password field
        password_container = self.create_input_field(
            "🔒", "Password", True
        )
        self.password_input = password_container.findChild(QLineEdit)
        layout.addWidget(password_container)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("LOGIN")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5A7863, stop:1 #3B4953);
                color: #EBF4DD;
                font-size: 14pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #90AB8B, stop:1 #5A7863);
            }
            QPushButton:pressed {
                background: #3B4953;
            }
            QPushButton:disabled {
                background: #90AB8B;
                opacity: 0.6;
            }
        """)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.on_login)
        layout.addWidget(self.login_btn)
        
        # Default credentials hint
        hint_label = QLabel("Default: admin / admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("""
            color: #90AB8B;
            font-size: 9pt;
            margin-top: 10px;
        """)
        layout.addWidget(hint_label)
        
        # Connect return key
        self.username_input.returnPressed.connect(self.on_login)
        self.password_input.returnPressed.connect(self.on_login)
        
        return card
    
    def create_input_field(self, icon: str, placeholder: str, is_password: bool) -> QFrame:
        """Create a styled input field with icon"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #90AB8B;
            }
            QFrame:focus-within {
                border: 2px solid #5A7863;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18pt; color: #90AB8B;")
        layout.addWidget(icon_label)
        
        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 12pt;
                color: #3B4953;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(input_field)
        
        return container
    
    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Disable login button
        self.login_btn.setEnabled(False)
        self.login_btn.setText("LOGGING IN...")
        
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
            self.show_error(message)
            self.password_input.clear()
            self.password_input.setFocus()
    
    def show_error(self, message: str):
        """Show error message with custom styling"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Login Error")
        msg_box.setText(message)
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
        msg_box.exec_()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            reply = QMessageBox.question(
                self, "Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.close()
                import sys
                sys.exit(0)
