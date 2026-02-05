import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QFrame, QGroupBox, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from utils.logger import logger

class BillPreviewDialog(QDialog):
    """Dialog to preview bill after generation"""
    
    def __init__(self, bill_data: dict, pdf_path: str, parent=None):
        super().__init__(parent)
        self.bill_data = bill_data
        self.pdf_path = pdf_path
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Bill Generated Successfully")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Success header
        header = self.create_header()
        layout.addWidget(header)
        
        # Bill details
        details = self.create_details_section()
        layout.addWidget(details)
        
        # Items table
        items_label = QLabel("Items:")
        items_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(items_label)
        
        items_table = self.create_items_table()
        layout.addWidget(items_table)
        
        # Totals section
        totals = self.create_totals_section()
        layout.addWidget(totals)
        
        # Action buttons
        buttons = self.create_buttons()
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def create_header(self) -> QFrame:
        """Create success header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #4CAF50;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(header)
        
        # Success icon and text
        title = QLabel("✓ BILL GENERATED SUCCESSFULLY")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Review the bill details below")
        subtitle.setStyleSheet("color: white; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return header
    
    def create_details_section(self) -> QGroupBox:
        """Create bill details section"""
        group = QGroupBox("Bill Information")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Invoice details
        invoice_layout = QHBoxLayout()
        
        # Left column
        left_col = QVBoxLayout()
        left_col.addWidget(self.create_detail_label("Invoice No:", self.bill_data['invoice_number']))
        left_col.addWidget(self.create_detail_label("Customer:", self.bill_data['customer_name']))
        
        if self.bill_data.get('customer_phone'):
            left_col.addWidget(self.create_detail_label("Phone:", self.bill_data['customer_phone']))
        
        # Right column
        right_col = QVBoxLayout()
        
        from datetime import datetime
        bill_date = datetime.strptime(self.bill_data['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %I:%M %p')
        right_col.addWidget(self.create_detail_label("Date & Time:", bill_date))
        
        # Get sales person name
        from database.db_manager import db
        sp = db.get_sales_person_by_id(self.bill_data['sales_person_id'])
        sp_name = sp['name'] if sp else 'Unknown'
        right_col.addWidget(self.create_detail_label("Sales Person:", sp_name))
        
        is_gst = "Yes" if self.bill_data.get('is_gst_bill', 0) == 1 else "No"
        gst_label = self.create_detail_label("GST Bill:", is_gst)
        if is_gst == "Yes":
            gst_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        right_col.addWidget(gst_label)
        
        invoice_layout.addLayout(left_col, 1)
        invoice_layout.addLayout(right_col, 1)
        
        layout.addLayout(invoice_layout)
        
        group.setLayout(layout)
        return group
    
    def create_detail_label(self, title: str, value: str) -> QLabel:
        """Create a detail label"""
        label = QLabel(f"<b>{title}</b> {value}")
        label.setStyleSheet("padding: 5px; font-size: 11px;")
        return label
    
    def create_items_table(self) -> QTableWidget:
        """Create items table"""
        table = QTableWidget()
        
        is_gst_bill = self.bill_data.get('is_gst_bill', 0) == 1
        
        if is_gst_bill:
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "S.No", "Product", "Qty", "MRP", "Disc%", "Rate", "Amount"
            ])
        else:
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "S.No", "Product", "Qty", "MRP", "Disc%", "Rate", "Amount"
            ])
        
        table.setRowCount(len(self.bill_data['items']))
        
        for row, item in enumerate(self.bill_data['items']):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(item['product_name']))
            table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            table.setItem(row, 3, QTableWidgetItem(f"₹{item['mrp']:.2f}"))
            table.setItem(row, 4, QTableWidgetItem(f"{item['discount_percent']:.0f}%"))
            table.setItem(row, 5, QTableWidgetItem(f"₹{item['rate']:.2f}"))
            table.setItem(row, 6, QTableWidgetItem(f"₹{item['amount']:.2f}"))
        
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setMaximumHeight(250)
        
        return table
    
    def create_totals_section(self) -> QFrame:
        """Create totals section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Subtotal
        subtotal_label = QLabel(f"<b>Subtotal:</b> ₹{self.bill_data['subtotal']:.2f}")
        subtotal_label.setStyleSheet("font-size: 12px; padding: 3px;")
        layout.addWidget(subtotal_label)
        
        # GST breakdown if applicable
        if self.bill_data.get('is_gst_bill', 0) == 1:
            cgst_label = QLabel(f"<b>CGST @ 2.5%:</b> ₹{self.bill_data['cgst_amount']:.2f}")
            cgst_label.setStyleSheet("font-size: 12px; padding: 3px; color: #2196F3;")
            layout.addWidget(cgst_label)
            
            sgst_label = QLabel(f"<b>SGST @ 2.5%:</b> ₹{self.bill_data['sgst_amount']:.2f}")
            sgst_label.setStyleSheet("font-size: 12px; padding: 3px; color: #2196F3;")
            layout.addWidget(sgst_label)
            
            total_tax_label = QLabel(f"<b>Total Tax:</b> ₹{self.bill_data['total_tax']:.2f}")
            total_tax_label.setStyleSheet("font-size: 12px; padding: 3px; color: #2196F3; font-weight: bold;")
            layout.addWidget(total_tax_label)
        
        # Round off
        roundoff_label = QLabel(f"<b>Round Off:</b> ₹{self.bill_data['round_off']:.2f}")
        roundoff_label.setStyleSheet("font-size: 12px; padding: 3px;")
        layout.addWidget(roundoff_label)
        
        # Grand total
        grand_total = QLabel(f"<b>GRAND TOTAL:</b> ₹{self.bill_data['grand_total']:.2f}")
        grand_total.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #4CAF50; 
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            margin-top: 5px;
        """)
        grand_total.setAlignment(Qt.AlignRight)
        layout.addWidget(grand_total)
        
        return frame
    
    def create_buttons(self) -> QHBoxLayout:
        """Create action buttons"""
        layout = QHBoxLayout()
        
        # View PDF button
        view_pdf_btn = QPushButton("📄 View PDF")
        view_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        view_pdf_btn.clicked.connect(self.view_pdf)
        
        # Print button
        print_btn = QPushButton("🖨️ Print Invoice")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        print_btn.clicked.connect(self.print_invoice)
        
        # Close button
        close_btn = QPushButton("✓ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(view_pdf_btn)
        layout.addWidget(print_btn)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        return layout
    
    def view_pdf(self):
        """Open PDF file"""
        try:
            if os.path.exists(self.pdf_path):
                os.startfile(self.pdf_path)
            else:
                QMessageBox.warning(self, "File Not Found", "PDF file not found!")
        except Exception as e:
            logger.error(f"Error opening PDF: {e}")
            QMessageBox.warning(self, "Error", f"Failed to open PDF: {str(e)}")
    
    def print_invoice(self):
        """Print the invoice"""
        try:
            if os.path.exists(self.pdf_path):
                # Open PDF for printing (will open default PDF viewer in print mode)
                os.startfile(self.pdf_path, "print")
            else:
                QMessageBox.warning(self, "File Not Found", "PDF file not found!")
        except Exception as e:
            logger.error(f"Error printing PDF: {e}")
            # Fallback: just open the file
            self.view_pdf()
