import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from .config import MAIL_SERVICE_URL
import os

# SMTP Configuration (fallback if Mail Service is down)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "soagk1tdtu@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "wveg zevy kdya rxbv")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "soagk1tdtu@gmail.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "iBanking TDTU")

# Invoice Email Template (from mail-service)
INVOICE_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            color: #27ae60;
            margin-bottom: 30px;
            border-bottom: 3px solid #27ae60;
            padding-bottom: 20px;
        }
        .invoice-details {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .detail-row:last-child {
            border-bottom: none;
        }
        .label {
            font-weight: bold;
            color: #495057;
        }
        .value {
            color: #212529;
        }
        .amount {
            background-color: #27ae60;
            color: white;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .success-badge {
            background-color: #d4edda;
            color: #155724;
            padding: 10px 20px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #6c757d;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Payment Invoice</h1>
            <p>Transaction Completed Successfully</p>
        </div>
        
        <div class="success-badge">
            ✓ PAYMENT SUCCESSFUL
        </div>
        
        <p>Dear <strong>{{ customer_name }}</strong>,</p>
        
        <p>Thank you for your payment. Below are the details of your transaction:</p>
        
        <div class="invoice-details">
            <div class="detail-row">
                <span class="label">Transaction ID:</span>
                <span class="value">#{{ transaction_id }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Transaction Code:</span>
                <span class="value">{{ transaction_code }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Tuition ID:</span>
                <span class="value">#{{ tuition_id }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Payment Date:</span>
                <span class="value">{{ payment_date }}</span>
            </div>
            <div class="detail-row">
                <span class="label">Status:</span>
                <span class="value" style="color: #27ae60; font-weight: bold;">COMPLETED</span>
            </div>
        </div>
        
        <div class="amount">
            {{ amount }} VND
        </div>
        
        <p>Your new account balance is: <strong>{{ new_balance }} VND</strong></p>
        
        <p>If you have any questions about this transaction, please contact our support team.</p>
        
        <div class="footer">
            <p>This is an automated receipt from TDTU iBanking System.</p>
            <p>Please keep this email for your records.</p>
            <p>&copy; 2025 TDTU - Ton Duc Thang University. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

def send_invoice_email(
    recipient: str,
    customer_name: str,
    transaction_id: int,
    transaction_code: str,
    tuition_id: int,
    amount: float,
    new_balance: float,
    payment_date: str
) -> bool:
    """
    Send invoice/receipt email to customer using Jinja2 template
    
    Args:
        recipient: Email address
        customer_name: Customer name
        transaction_id: Transaction ID
        transaction_code: Transaction code (e.g., TXN00000001)
        tuition_id: Tuition ID
        amount: Payment amount
        new_balance: Customer's new balance after payment
        payment_date: Payment date/time
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Render email template
        template = Template(INVOICE_EMAIL_TEMPLATE)
        html_content = template.render(
            customer_name=customer_name,
            transaction_id=transaction_id,
            transaction_code=transaction_code,
            tuition_id=tuition_id,
            amount=f"{amount:,.0f}",
            new_balance=f"{new_balance:,.0f}",
            payment_date=payment_date
        )
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'✅ Payment Invoice - {transaction_code}'
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = recipient
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"Invoice email sent successfully to {recipient}")
        return True
        
    except Exception as e:
        print(f"Failed to send invoice email: {str(e)}")
        return False
