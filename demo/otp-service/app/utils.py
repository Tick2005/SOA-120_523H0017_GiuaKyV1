import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from .config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SMTP_FROM_EMAIL, SMTP_FROM_NAME
)

# OTP Email Template (from mail-service)
OTP_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .otp-code {
            background-color: #3498db;
            color: white;
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            letter-spacing: 8px;
            margin: 20px 0;
        }
        .info {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }
        .tuition-info {
            background-color: #e7f3ff;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 iBanking OTP Verification</h1>
            <p>TDTU - Payment Authentication</p>
        </div>
        
        <p>Hello <strong>{{ user_name }}</strong>,</p>
        
        <p>You are making a tuition payment through TDTU iBanking system. Please use the following OTP code:</p>
        
        <div class="otp-code">{{ otp_code }}</div>
        
        <div class="tuition-info">
            <strong>📋 Payment Details:</strong><br>
            Semester: <strong>{{ semester }}</strong> - Academic Year: <strong>{{ academic_year }}</strong><br>
            Amount: <strong>{{ amount }} VND</strong>
        </div>
        
        <div class="info">
            <strong>⏰ Important:</strong> This OTP code is valid for <strong>{{ expires_in_minutes }} minutes</strong>. 
            Please do not share this code with anyone.
        </div>
        
        <p>If you did not request this code, please ignore this email or contact our support team immediately.</p>
        
        <div class="footer">
            <p>This is an automated email from iBanking System.</p>
            <p>&copy; 2025 TDTU - Ton Duc Thang University. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_email(
    recipient: str,
    otp_code: str,
    user_name: str,
    tuition_info: dict,
    expires_in_minutes: int = 5
):
    """
    Send OTP email to customer using Jinja2 template
    
    Args:
        recipient: Email address
        otp_code: 6-digit OTP code
        user_name: Customer name
        tuition_info: Dict with semester, academic_year, amount
        expires_in_minutes: OTP validity in minutes
    """
    try:
        # Render email template
        template = Template(OTP_EMAIL_TEMPLATE)
        html_content = template.render(
            user_name=user_name,
            otp_code=otp_code,
            semester=tuition_info.get('semester', 'N/A'),
            academic_year=tuition_info.get('academic_year', 'N/A'),
            amount=f"{tuition_info.get('amount', 0):,.0f}",
            expires_in_minutes=expires_in_minutes
        )
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'🔐 iBanking OTP Verification - {otp_code}'
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = recipient
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        return False
