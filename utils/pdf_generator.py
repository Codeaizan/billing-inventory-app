import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from modules.gst_calculator import gst_calculator
from config import (COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE, COMPANY_EMAIL,
                   BANK_NAME, BANK_ACCOUNT_NO, BANK_IFSC, PDF_OUTPUT_DIR,
                   COMPANY_TAGLINE, COMPANY_CERTIFICATIONS, INVOICE_NOTE)
from utils.logger import logger

class PDFGenerator:
    """Generate PDF invoices"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    
    def generate_invoice(self, bill: dict) -> tuple:
        """
        Generate invoice PDF
        Returns: (success, pdf_path)
        """
        try:
            # Create filename
            invoice_num = bill['invoice_number'].replace('/', '-')
            filename = f"Invoice_{invoice_num}.pdf"
            pdf_path = os.path.join(PDF_OUTPUT_DIR, filename)
            
            # Create PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                   rightMargin=30, leftMargin=30,
                                   topMargin=30, bottomMargin=30)
            
            # Container for elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4CAF50'),
                alignment=TA_CENTER,
                spaceAfter=5
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=3
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#333333'),
                spaceAfter=10
            )
            
            # Company Header
            elements.append(Paragraph(COMPANY_NAME, title_style))
            elements.append(Paragraph(COMPANY_TAGLINE, subtitle_style))
            elements.append(Paragraph(COMPANY_CERTIFICATIONS, subtitle_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Company details
            company_details = f"{COMPANY_ADDRESS}<br/>{COMPANY_PHONE} | {COMPANY_EMAIL}"
            elements.append(Paragraph(company_details, subtitle_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice title
            invoice_title = Paragraph("<b>INVOICE</b>", heading_style)
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.1*inch))
            
            # Invoice details and customer details side by side
            invoice_date = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
            
            details_data = [
                ['Invoice No:', bill['invoice_number'], 'Date:', invoice_date],
                ['', '', 'Payment Mode:', bill['payment_mode']]
            ]
            
            details_table = Table(details_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
            details_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ]))
            
            elements.append(details_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Customer details
            bill_to_data = [
                ['BILL TO:', '', 'SUPPLY TO:', ''],
                [bill['customer_name'], '', bill['customer_name'], ''],
            ]
            
            if bill.get('customer_address'):
                address_parts = bill['customer_address'].split(',')
                for part in address_parts:
                    bill_to_data.append([part.strip(), '', part.strip(), ''])
            
            if bill.get('customer_city'):
                bill_to_data.append([bill['customer_city'], '', bill['customer_city'], ''])
            
            if bill.get('customer_pin_code'):
                bill_to_data.append([f"PIN - {bill['customer_pin_code']}", '', f"PIN - {bill['customer_pin_code']}", ''])
            
            if bill.get('customer_phone'):
                bill_to_data.append([f"PHONE - {bill['customer_phone']}", '', '', ''])
            
            bill_to_table = Table(bill_to_data, colWidths=[3*inch, 0.2*inch, 3*inch, 0.2*inch])
            bill_to_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(bill_to_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Items table
            items_data = [
                ['S.NO', 'DESCRIPTION OF GOODS', 'HSN CODE', 'BATCH NO', 'EXP',
                 'QTY', 'MRP', 'DISC%', 'RATE', 'AMOUNT']
            ]
            
            for idx, item in enumerate(bill['items'], 1):
                items_data.append([
                    str(idx),
                    item['product_name'],
                    item.get('hsn_code', ''),
                    item.get('batch_number', ''),
                    item.get('expiry_date', ''),
                    str(item['quantity']),
                    f"{item['mrp']:.0f}",
                    f"{item['discount_percent']:.0f}",
                    f"{item['rate']:.0f}",
                    f"{item['amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[
                0.4*inch, 2.2*inch, 0.8*inch, 0.7*inch, 0.5*inch,
                0.5*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.9*inch
            ])
            
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Totals
            totals_data = [
                ['', '', 'TOTAL', f"{bill['subtotal']:.2f}"],
                ['', '', 'ROUND OFF', f"{bill['round_off']:.2f}"],
            ]
            
            # Convert grand total to words
            grand_total_int = int(bill['grand_total'])
            amount_in_words = gst_calculator.number_to_words(grand_total_int)
            
            totals_data.append(['RUPEES:', amount_in_words, 'GRAND TOTAL', f"{bill['grand_total']:.2f}"])
            
            totals_table = Table(totals_data, colWidths=[1*inch, 3.5*inch, 1.5*inch, 1*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTNAME', (3, -1), (3, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTSIZE', (3, -1), (3, -1), 12),
                ('TEXTCOLOR', (3, -1), (3, -1), colors.HexColor('#4CAF50')),
            ]))
            
            elements.append(totals_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bank details
            bank_info = f"<b>BANK NAME:</b> {BANK_NAME}<br/>" \
                       f"<b>ACCOUNT NO:</b> {BANK_ACCOUNT_NO} - <b>IFSC CODE:</b> {BANK_IFSC}"
            elements.append(Paragraph(bank_info, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Note
            if INVOICE_NOTE:
                note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
                elements.append(Paragraph(INVOICE_NOTE, note_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Signature
            signature_style = ParagraphStyle('Signature', parent=styles['Normal'], alignment=TA_RIGHT)
            elements.append(Paragraph(f"<b>FOR, {COMPANY_NAME}</b>", signature_style))
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("<b>AUTHORISED SIGNATORY</b>", signature_style))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Invoice PDF generated: {pdf_path}")
            return True, pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False, None

# Create global instance
pdf_generator = PDFGenerator()
