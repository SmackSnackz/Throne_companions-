"""
Email Authentication Service for Admin Access
Sends access codes via email for secure admin login
"""

import os
import random
import string
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
import asyncio

# Email imports with error handling
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_LIBS_AVAILABLE = True
except ImportError as e:
    EMAIL_LIBS_AVAILABLE = False
    logging.warning(f"Email libraries not available: {e}")

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

class EmailAuthService:
    """
    Email authentication service for admin access codes
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.access_codes = {}  # In-memory storage for demo
        
        # Email configuration
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', 'admin@thronecompanions.com')
        
        # Admin email whitelist
        self.admin_emails = [
            'admin@thronecompanions.com',
            'roy@thronecompanions.com',
            'roy.carnell.johnson@gmail.com',
            'roycarnelljohnson@gmail.com',
            'Rjohnson801915@gmail.com'
        ]
    
    def generate_access_code(self) -> str:
        """Generate a 6-digit access code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_admin_email(self, email: str) -> bool:
        """Check if email is authorized for admin access"""
        return email.lower() in [e.lower() for e in self.admin_emails]
    
    async def send_access_code_sendgrid(self, to_email: str, access_code: str) -> bool:
        """Send access code via SendGrid"""
        if not SENDGRID_AVAILABLE or not self.sendgrid_api_key:
            return False
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Throne Companions Admin Access Code',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #FFD700;">🔐 Admin Access Code</h2>
                    <p>Your access code for Throne Companions admin panel:</p>
                    <div style="background: #1a365d; color: #FFD700; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 8px; letter-spacing: 4px;">
                        {access_code}
                    </div>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">
                        This code expires in 10 minutes. Do not share this code with anyone.
                    </p>
                    <p style="color: #666; font-size: 12px;">
                        If you did not request this code, please ignore this email.
                    </p>
                </div>
                '''
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            self.logger.info(f"SendGrid email sent to {to_email}, status: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            self.logger.error(f"SendGrid email failed: {e}")
            return False
    
    async def send_access_code_smtp(self, to_email: str, access_code: str) -> bool:
        """Send access code via SMTP"""
        if not EMAIL_LIBS_AVAILABLE or not self.smtp_username or not self.smtp_password:
            return False
        
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = 'Throne Companions Admin Access Code'
            
            body = f'''
            Admin Access Code: {access_code}
            
            Your access code for Throne Companions admin panel is: {access_code}
            
            This code expires in 10 minutes.
            Do not share this code with anyone.
            
            If you did not request this code, please ignore this email.
            '''
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"SMTP email sent to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP email failed: {e}")
            return False
    
    async def send_access_code(self, email: str) -> Dict[str, any]:
        """
        Send access code to admin email
        Returns: {"success": bool, "message": str, "code": str (for demo)}
        """
        
        # Validate admin email
        if not self.is_admin_email(email):
            return {
                "success": False,
                "message": "Email not authorized for admin access",
                "code": None
            }
        
        # Generate code
        access_code = self.generate_access_code()
        
        # Store code with expiration (10 minutes)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        self.access_codes[email] = {
            "code": access_code,
            "expires": expiry,
            "attempts": 0
        }
        
        # Try sending via SendGrid first, then SMTP
        email_sent = False
        
        if self.sendgrid_api_key:
            email_sent = await self.send_access_code_sendgrid(email, access_code)
        
        if not email_sent and self.smtp_username:
            email_sent = await self.send_access_code_smtp(email, access_code)
        
        if email_sent:
            return {
                "success": True,
                "message": "Access code sent to your email",
                "code": access_code if os.environ.get('NODE_ENV') == 'development' else None  # Show code in dev
            }
        else:
            # For demo/staging, return the code directly
            self.logger.warning(f"Email service not configured, returning code directly for demo")
            return {
                "success": True,
                "message": f"Email service not configured. Your access code is: {access_code}",
                "code": access_code
            }
    
    def verify_access_code(self, email: str, code: str) -> Dict[str, any]:
        """
        Verify access code for admin login
        Returns: {"success": bool, "message": str}
        """
        
        if email not in self.access_codes:
            return {
                "success": False,
                "message": "No access code found for this email"
            }
        
        code_data = self.access_codes[email]
        
        # Check expiration
        if datetime.now(timezone.utc) > code_data["expires"]:
            del self.access_codes[email]
            return {
                "success": False,
                "message": "Access code has expired"
            }
        
        # Check attempts
        if code_data["attempts"] >= 3:
            del self.access_codes[email]
            return {
                "success": False,
                "message": "Too many failed attempts"
            }
        
        # Verify code
        if code_data["code"] == code:
            del self.access_codes[email]  # Remove used code
            return {
                "success": True,
                "message": "Access code verified"
            }
        else:
            code_data["attempts"] += 1
            return {
                "success": False,
                "message": f"Invalid access code. {3 - code_data['attempts']} attempts remaining"
            }
    
    def cleanup_expired_codes(self):
        """Clean up expired access codes"""
        now = datetime.now(timezone.utc)
        expired_emails = [
            email for email, data in self.access_codes.items()
            if now > data["expires"]
        ]
        
        for email in expired_emails:
            del self.access_codes[email]
        
        if expired_emails:
            self.logger.info(f"Cleaned up {len(expired_emails)} expired access codes")

# Global instance
email_auth_service = EmailAuthService()