from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTabWidget, QWidget,
                             QFormLayout, QMessageBox, QGroupBox,
                             QTextEdit, QSpinBox)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.company_settings import company_settings


class CompanySettingsDialog(QDialog):
    """Dialog for managing company settings including dual banking"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Company Settings")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        # Apply sage green theme
        self.setStyleSheet("""
            QDialog {
                background-color: #EBF4DD;
            }
            QLabel {
                color: #3B4953;
                font-weight: bold;
            }
            QGroupBox {
                font-weight: bold;
                color: #5A7863;
                border: 2px solid #90AB8B;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #90AB8B;
                background-color: #EBF4DD;
            }
            QTabBar::tab {
                background-color: #90AB8B;
                color: #EBF4DD;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #5A7863;
            }
        """)
        
        # Company Info Tab
        company_tab = self.create_company_tab()
        tabs.addTab(company_tab, "📋 Company Info")
        
        # Banking Details Tab
        banking_tab = self.create_banking_tab()
        tabs.addTab(banking_tab, "🏦 Banking Details")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5A7863;
                color: #EBF4DD;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #90AB8B;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B4953;
                color: #EBF4DD;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #5A7863;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_company_tab(self) -> QWidget:
        """Create company information tab"""
        tab = QWidget()
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # Company fields
        self.company_name_input = QLineEdit()
        self.company_name_input.setStyleSheet(self.get_input_style())
        layout.addRow("Company Name:", self.company_name_input)
        
        self.company_tagline_input = QLineEdit()
        self.company_tagline_input.setStyleSheet(self.get_input_style())
        layout.addRow("Tagline:", self.company_tagline_input)
        
        self.company_subtitle_input = QLineEdit()
        self.company_subtitle_input.setStyleSheet(self.get_input_style())
        layout.addRow("Subtitle:", self.company_subtitle_input)
        
        self.company_cert_input = QLineEdit()
        self.company_cert_input.setStyleSheet(self.get_input_style())
        layout.addRow("Certifications:", self.company_cert_input)
        
        self.factory_address_input = QLineEdit()
        self.factory_address_input.setStyleSheet(self.get_input_style())
        layout.addRow("Factory Address:", self.factory_address_input)
        
        self.office_address_input = QLineEdit()
        self.office_address_input.setStyleSheet(self.get_input_style())
        layout.addRow("Office Address:", self.office_address_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet(self.get_input_style())
        layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(self.get_input_style())
        layout.addRow("Email:", self.email_input)

        self.instagram_input = QLineEdit()
        self.instagram_input.setStyleSheet(self.get_input_style())
        layout.addRow("Instagram:", self.instagram_input)

        self.gstin_input = QLineEdit()
        self.gstin_input.setStyleSheet(self.get_input_style())
        layout.addRow("GSTIN:", self.gstin_input)
        
        self.state_name_input = QLineEdit()
        self.state_name_input.setStyleSheet(self.get_input_style())
        layout.addRow("State Name:", self.state_name_input)
        
        self.state_code_input = QLineEdit()
        self.state_code_input.setStyleSheet(self.get_input_style())
        layout.addRow("State Code:", self.state_code_input)

        self.invoice_note_input = QTextEdit()
        self.invoice_note_input.setStyleSheet(self.get_input_style())
        self.invoice_note_input.setFixedHeight(60)
        layout.addRow("Invoice Note:", self.invoice_note_input)

        self.invoice_note_input = QTextEdit()
        self.invoice_note_input.setStyleSheet(self.get_input_style())
        self.invoice_note_input.setFixedHeight(60)
        layout.addRow("Invoice Note:", self.invoice_note_input)

        self.invoice_prefix_input = QLineEdit()
        self.invoice_prefix_input.setStyleSheet(self.get_input_style())
        layout.addRow("Invoice Prefix:", self.invoice_prefix_input)

        # Next Invoice Number
        self.next_invoice_input = QSpinBox()
        self.next_invoice_input.setRange(1, 9999999)
        self.next_invoice_input.setStyleSheet(self.get_input_style())
        layout.addRow("Next Invoice Number:", self.next_invoice_input)
        
        tab.setLayout(layout)
        return tab
    
    def create_banking_tab(self) -> QWidget:
        """Create banking details tab with GST and Non-GST sections"""
        tab = QWidget()
        main_layout = QVBoxLayout()
        
        # GST Banking Details Group
        gst_group = QGroupBox("🏦 GST Banking Details")
        gst_layout = QFormLayout()
        gst_layout.setSpacing(10)
        
        self.gst_bank_name_input = QLineEdit()
        self.gst_bank_name_input.setStyleSheet(self.get_input_style())
        gst_layout.addRow("Bank Name:", self.gst_bank_name_input)
        
        self.gst_account_no_input = QLineEdit()
        self.gst_account_no_input.setStyleSheet(self.get_input_style())
        gst_layout.addRow("Account Number:", self.gst_account_no_input)
        
        self.gst_ifsc_input = QLineEdit()
        self.gst_ifsc_input.setStyleSheet(self.get_input_style())
        gst_layout.addRow("IFSC Code:", self.gst_ifsc_input)
        
        self.gst_branch_input = QLineEdit()
        self.gst_branch_input.setStyleSheet(self.get_input_style())
        self.gst_branch_input.setPlaceholderText("Optional")
        gst_layout.addRow("Branch:", self.gst_branch_input)
        
        self.gst_upi_input = QLineEdit()
        self.gst_upi_input.setStyleSheet(self.get_input_style())
        self.gst_upi_input.setPlaceholderText("Optional - e.g., business@paytm")
        gst_layout.addRow("UPI ID:", self.gst_upi_input)
        
        gst_group.setLayout(gst_layout)
        main_layout.addWidget(gst_group)
        
        # Non-GST Banking Details Group
        non_gst_group = QGroupBox("💰 Non-GST Banking Details")
        non_gst_layout = QFormLayout()
        non_gst_layout.setSpacing(10)
        
        # Info label
        info_label = QLabel("⚠️ Leave empty to use GST banking details for Non-GST bills")
        info_label.setStyleSheet("color: #5A7863; font-size: 9pt; font-style: italic;")
        non_gst_layout.addRow("", info_label)
        
        self.non_gst_bank_name_input = QLineEdit()
        self.non_gst_bank_name_input.setStyleSheet(self.get_input_style())
        self.non_gst_bank_name_input.setPlaceholderText("Optional - Different bank for Non-GST")
        non_gst_layout.addRow("Bank Name:", self.non_gst_bank_name_input)
        
        self.non_gst_account_no_input = QLineEdit()
        self.non_gst_account_no_input.setStyleSheet(self.get_input_style())
        self.non_gst_account_no_input.setPlaceholderText("Optional")
        non_gst_layout.addRow("Account Number:", self.non_gst_account_no_input)
        
        self.non_gst_ifsc_input = QLineEdit()
        self.non_gst_ifsc_input.setStyleSheet(self.get_input_style())
        self.non_gst_ifsc_input.setPlaceholderText("Optional")
        non_gst_layout.addRow("IFSC Code:", self.non_gst_ifsc_input)
        
        self.non_gst_branch_input = QLineEdit()
        self.non_gst_branch_input.setStyleSheet(self.get_input_style())
        self.non_gst_branch_input.setPlaceholderText("Optional")
        non_gst_layout.addRow("Branch:", self.non_gst_branch_input)
        
        self.non_gst_upi_input = QLineEdit()
        self.non_gst_upi_input.setStyleSheet(self.get_input_style())
        self.non_gst_upi_input.setPlaceholderText("Optional")
        non_gst_layout.addRow("UPI ID:", self.non_gst_upi_input)
        
        non_gst_group.setLayout(non_gst_layout)
        main_layout.addWidget(non_gst_group)
        
        main_layout.addStretch()
        tab.setLayout(main_layout)
        return tab
    
    def load_settings(self):
        """Load current settings into form"""
        settings = company_settings.get_all()
        
        # Company info
        self.company_name_input.setText(settings.get('company_name', ''))
        self.company_tagline_input.setText(settings.get('company_tagline', ''))
        self.company_subtitle_input.setText(settings.get('company_subtitle', ''))
        self.company_cert_input.setText(settings.get('company_certifications', ''))
        self.factory_address_input.setText(settings.get('factory_address', ''))
        self.office_address_input.setText(settings.get('office_address', ''))
        self.phone_input.setText(settings.get('phone', ''))
        self.email_input.setText(settings.get('email', ''))
        self.instagram_input.setText(settings.get('instagram', ''))
        self.gstin_input.setText(settings.get('gstin', ''))
        self.state_name_input.setText(settings.get('state_name', ''))
        self.state_code_input.setText(settings.get('state_code', ''))
        self.invoice_prefix_input.setText(settings.get('invoice_prefix', 'NH'))
        self.invoice_note_input.setPlainText(settings.get('invoice_note', ''))
        # Next invoice number (default 1)
        self.next_invoice_input.setValue(int(settings.get('next_invoice_number', 1) or 1))
        
        # GST Banking
        self.gst_bank_name_input.setText(settings.get('gst_bank_name', ''))
        self.gst_account_no_input.setText(settings.get('gst_bank_account_no', ''))
        self.gst_ifsc_input.setText(settings.get('gst_bank_ifsc', ''))
        self.gst_branch_input.setText(settings.get('gst_bank_branch', ''))
        self.gst_upi_input.setText(settings.get('gst_upi_id', ''))
        
        # Non-GST Banking
        self.non_gst_bank_name_input.setText(settings.get('non_gst_bank_name', ''))
        self.non_gst_account_no_input.setText(settings.get('non_gst_bank_account_no', ''))
        self.non_gst_ifsc_input.setText(settings.get('non_gst_bank_ifsc', ''))
        self.non_gst_branch_input.setText(settings.get('non_gst_bank_branch', ''))
        self.non_gst_upi_input.setText(settings.get('non_gst_upi_id', ''))
    
    def save_settings(self):
        """Save settings to database"""
        settings = {
            # Company info
            'company_name': self.company_name_input.text().strip(),
            'company_tagline': self.company_tagline_input.text().strip(),
            'company_subtitle': self.company_subtitle_input.text().strip(),
            'company_certifications': self.company_cert_input.text().strip(),
            'factory_address': self.factory_address_input.text().strip(),
            'office_address': self.office_address_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'instagram': self.instagram_input.text().strip(),
            'gstin': self.gstin_input.text().strip(),
            'state_name': self.state_name_input.text().strip(),
            'state_code': self.state_code_input.text().strip(),
            'invoice_prefix': self.invoice_prefix_input.text().strip(),
            'invoice_note': self.invoice_note_input.toPlainText().strip(),
            'next_invoice_number': self.next_invoice_input.value(),
            
            # GST Banking
            'gst_bank_name': self.gst_bank_name_input.text().strip(),
            'gst_bank_account_no': self.gst_account_no_input.text().strip(),
            'gst_bank_ifsc': self.gst_ifsc_input.text().strip(),
            'gst_bank_branch': self.gst_branch_input.text().strip(),
            'gst_upi_id': self.gst_upi_input.text().strip(),
            
            # Non-GST Banking
            'non_gst_bank_name': self.non_gst_bank_name_input.text().strip(),
            'non_gst_bank_account_no': self.non_gst_account_no_input.text().strip(),
            'non_gst_bank_ifsc': self.non_gst_ifsc_input.text().strip(),
            'non_gst_bank_branch': self.non_gst_branch_input.text().strip(),
            'non_gst_upi_id': self.non_gst_upi_input.text().strip(),
            
            # Legacy fields (for backward compatibility)
            'bank_name': self.gst_bank_name_input.text().strip(),
            'bank_account_no': self.gst_account_no_input.text().strip(),
            'bank_ifsc': self.gst_ifsc_input.text().strip(),
        }
        
        success = company_settings.update(settings)
        
        if success:
            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Failed to save settings. Please try again."
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
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #5A7863;
            }
        """
