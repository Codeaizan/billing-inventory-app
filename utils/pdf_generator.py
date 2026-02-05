import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from modules.gst_calculator import gst_calculator
from config import PDF_OUTPUT_DIR
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
            # Get company settings
            from utils.company_settings import company_settings
            
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
                fontSize=22,
                textColor=colors.HexColor('#4CAF50'),
                alignment=TA_CENTER,
                spaceAfter=3
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                spaceAfter=2
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#333333'),
                spaceAfter=10
            )
            
            # Company Header
            elements.append(Paragraph(company_settings.get('company_name', 'Natural Health World'), title_style))
            elements.append(Paragraph(company_settings.get('company_tagline', 'The Herbal Healing'), subtitle_style))
            elements.append(Paragraph(company_settings.get('company_subtitle', ''), subtitle_style))
            elements.append(Paragraph(company_settings.get('company_certifications', ''), subtitle_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Company details
            company_details = f"{company_settings.get('factory_address', '')}<br/>"
            company_details += f"{company_settings.get('phone', '')} | {company_settings.get('email', '')}"
            
            # Add GSTIN if available
            gstin = company_settings.get('gstin', '')
            if gstin:
                company_details += f"<br/>GSTIN: {gstin}"
            
            elements.append(Paragraph(company_details, subtitle_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice title
            is_gst_bill = bill.get('is_gst_bill', 0) == 1
            invoice_title_text = "<b>TAX INVOICE</b>" if is_gst_bill else "<b>INVOICE</b>"
            invoice_title = Paragraph(invoice_title_text, heading_style)
            elements.append(invoice_title)
            elements.append(Spacer(1, 0.1*inch))
            
            # Invoice details and customer details side by side
            invoice_date = datetime.strptime(bill['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
            
            details_data = [
                ['Invoice No:', bill['invoice_number'], 'Date:', invoice_date],
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
                address_parts = bill['customer_address'].split('\n')
                for part in address_parts[:3]:  # Limit to 3 lines
                    if part.strip():
                        bill_to_data.append([part.strip(), '', part.strip(), ''])
            
            if bill.get('customer_phone'):
                bill_to_data.append([f"Phone: {bill['customer_phone']}", '', '', ''])
            
            # Add customer GSTIN if GST bill
            if is_gst_bill and bill.get('customer_gstin'):
                bill_to_data.append([f"GSTIN: {bill['customer_gstin']}", '', f"GSTIN: {bill['customer_gstin']}", ''])
            
            bill_to_table = Table(bill_to_data, colWidths=[3*inch, 0.2*inch, 3*inch, 0.2*inch])
            bill_to_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(bill_to_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Items table
            if is_gst_bill:
                # GST Bill - Show tax columns
                items_data = [
                    ['S.No', 'DESCRIPTION', 'HSN', 'QTY', 'MRP', 'DISC%', 'RATE', 'AMOUNT']
                ]
                
                for idx, item in enumerate(bill['items'], 1):
                    items_data.append([
                        str(idx),
                        item['product_name'],
                        item.get('hsn_code', ''),
                        str(item['quantity']),
                        f"{item['mrp']:.0f}",
                        f"{item['discount_percent']:.0f}",
                        f"{item['rate']:.2f}",
                        f"{item['amount']:.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[
                    0.4*inch, 2.5*inch, 0.7*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.9*inch
                ])
            else:
                # Non-GST Bill - Simple format
                items_data = [
                    ['S.No', 'DESCRIPTION OF GOODS', 'HSN', 'QTY', 'MRP', 'DISC%', 'RATE', 'AMOUNT']
                ]
                
                for idx, item in enumerate(bill['items'], 1):
                    items_data.append([
                        str(idx),
                        item['product_name'],
                        item.get('hsn_code', ''),
                        str(item['quantity']),
                        f"{item['mrp']:.0f}",
                        f"{item['discount_percent']:.0f}",
                        f"{item['rate']:.0f}",
                        f"{item['amount']:.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[
                    0.4*inch, 2.5*inch, 0.7*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.9*inch
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
            
            # Totals section
            if is_gst_bill:
                # GST Bill - Show tax breakdown
                totals_data = [
                    ['', '', 'SUBTOTAL (Taxable Amount)', f"{bill['subtotal']:.2f}"],
                    ['', '', f"CGST @ 2.5%", f"{bill['cgst_amount']:.2f}"],
                    ['', '', f"SGST @ 2.5%", f"{bill['sgst_amount']:.2f}"],
                    ['', '', 'TOTAL TAX', f"{bill['total_tax']:.2f}"],
                    ['', '', 'ROUND OFF', f"{bill['round_off']:.2f}"],
                ]
            else:
                # Non-GST Bill - Simple totals
                totals_data = [
                    ['', '', 'SUBTOTAL', f"{bill['subtotal']:.2f}"],
                    ['', '', 'ROUND OFF', f"{bill['round_off']:.2f}"],
                ]
            
            # Convert grand total to words
            grand_total_int = int(bill['grand_total'])
            amount_in_words = gst_calculator.number_to_words(grand_total_int)
            
            totals_data.append(['RUPEES:', amount_in_words.upper(), 'GRAND TOTAL', f"{bill['grand_total']:.2f}"])
            
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
                ('LINEABOVE', (2, -1), (3, -1), 2, colors.HexColor('#4CAF50')),
            ]))
            
            elements.append(totals_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bank details
            bank_info = f"<b>BANK NAME:</b> {company_settings.get('bank_name', '')}<br/>" \
                       f"<b>ACCOUNT NO:</b> {company_settings.get('bank_account_no', '')} - " \
                       f"<b>IFSC CODE:</b> {company_settings.get('bank_ifsc', '')}"
            elements.append(Paragraph(bank_info, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Note
            invoice_note = company_settings.get('invoice_note', '')
            if invoice_note:
                note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
                elements.append(Paragraph(invoice_note, note_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Terms and conditions for GST bills
            if is_gst_bill:
                terms_text = "<b>Terms & Conditions:</b><br/>1. Goods once sold will not be taken back.<br/>" \
                           "2. Interest @ 18% will be charged if payment is not made within 7 days."
                terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8)
                elements.append(Paragraph(terms_text, terms_style))
                elements.append(Spacer(1, 0.2*inch))
            
            # Signature
            signature_style = ParagraphStyle('Signature', parent=styles['Normal'], alignment=TA_RIGHT)
            elements.append(Paragraph(f"<b>FOR, {company_settings.get('company_name', 'NATURAL HEALTH WORLD')}</b>", signature_style))
            elements.append(Spacer(1, 0.5*inch))
            elements.append(Paragraph("<b>AUTHORISED SIGNATORY</b>", signature_style))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"Invoice PDF generated: {pdf_path}")
            return True, pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False, None

# Create global instance
pdf_generator = PDFGenerator()
