import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    async def send_appointment_confirmation(self, patient_email: str, appointment_data: dict) -> bool:
        """Send appointment confirmation email"""
        try:
            subject = "MedAgg - Appointment Confirmation"
            
            # Create HTML email body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                    <h1>MedAgg Healthcare</h1>
                    <p>Your Appointment is Confirmed!</p>
                </div>
                
                <div style="padding: 20px; background-color: #f9f9f9;">
                    <h2>Appointment Details</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Patient Name:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['patient_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Hospital:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['hospital_name']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Address:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['hospital_address']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Date & Time:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['appointment_date']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Specialization:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['specialization']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Phone:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{appointment_data['hospital_phone']}</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 20px; padding: 15px; background-color: #e8f5e8; border-left: 4px solid #2E8B57;">
                        <h3>Important Reminders:</h3>
                        <ul>
                            <li>Please arrive 15 minutes early for your appointment</li>
                            <li>Bring a list of your current medications</li>
                            <li>Bring any previous test results or medical records</li>
                            <li>Bring a valid ID and insurance card</li>
                        </ul>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                        <h3>Need to Reschedule?</h3>
                        <p>If you need to reschedule or cancel your appointment, please contact us at least 24 hours in advance.</p>
                        <p>Phone: {appointment_data['hospital_phone']}</p>
                    </div>
                </div>
                
                <div style="background-color: #333; color: white; padding: 20px; text-align: center;">
                    <p>Thank you for choosing MedAgg Healthcare!</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
            MedAgg Healthcare - Appointment Confirmation
            
            Dear {appointment_data['patient_name']},
            
            Your appointment has been confirmed with the following details:
            
            Hospital: {appointment_data['hospital_name']}
            Address: {appointment_data['hospital_address']}
            Date & Time: {appointment_data['appointment_date']}
            Specialization: {appointment_data['specialization']}
            Phone: {appointment_data['hospital_phone']}
            
            Important Reminders:
            - Please arrive 15 minutes early
            - Bring current medications list
            - Bring previous test results
            - Bring valid ID and insurance card
            
            To reschedule or cancel, contact us at least 24 hours in advance.
            Phone: {appointment_data['hospital_phone']}
            
            Thank you for choosing MedAgg Healthcare!
            """
            
            return await self._send_email(patient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {e}")
            return False
    
    async def send_appointment_reminder(self, patient_email: str, appointment_data: dict) -> bool:
        """Send appointment reminder email"""
        try:
            subject = "MedAgg - Appointment Reminder"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #FF6B35; color: white; padding: 20px; text-align: center;">
                    <h1>MedAgg Healthcare</h1>
                    <p>Appointment Reminder</p>
                </div>
                
                <div style="padding: 20px;">
                    <h2>Your appointment is tomorrow!</h2>
                    <p>Dear {appointment_data['patient_name']},</p>
                    <p>This is a friendly reminder that you have an appointment scheduled for:</p>
                    
                    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Date & Time:</strong> {appointment_data['appointment_date']}<br>
                        <strong>Hospital:</strong> {appointment_data['hospital_name']}<br>
                        <strong>Address:</strong> {appointment_data['hospital_address']}<br>
                        <strong>Phone:</strong> {appointment_data['hospital_phone']}
                    </div>
                    
                    <p>Please don't forget to bring your ID, insurance card, and any relevant medical documents.</p>
                    
                    <p>If you need to reschedule, please contact us as soon as possible.</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            MedAgg Healthcare - Appointment Reminder
            
            Dear {appointment_data['patient_name']},
            
            This is a reminder that you have an appointment scheduled for:
            
            Date & Time: {appointment_data['appointment_date']}
            Hospital: {appointment_data['hospital_name']}
            Address: {appointment_data['hospital_address']}
            Phone: {appointment_data['hospital_phone']}
            
            Please don't forget to bring your ID, insurance card, and medical documents.
            
            If you need to reschedule, please contact us as soon as possible.
            """
            
            return await self._send_email(patient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending appointment reminder: {e}")
            return False
    
    async def send_welcome_email(self, patient_email: str, patient_name: str) -> bool:
        """Send welcome email to new patient"""
        try:
            subject = "Welcome to MedAgg Healthcare"
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                    <h1>Welcome to MedAgg Healthcare!</h1>
                </div>
                
                <div style="padding: 20px;">
                    <p>Dear {patient_name},</p>
                    <p>Thank you for choosing MedAgg Healthcare for your medical needs. We're committed to providing you with the best possible care.</p>
                    
                    <h3>What happens next?</h3>
                    <ul>
                        <li>Our AI assistant will call you shortly to discuss your symptoms</li>
                        <li>We'll schedule an appointment with the most suitable specialist</li>
                        <li>You'll receive a confirmation email with all the details</li>
                        <li>We'll send you a reminder before your appointment</li>
                    </ul>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p>Best regards,<br>The MedAgg Healthcare Team</p>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Welcome to MedAgg Healthcare!
            
            Dear {patient_name},
            
            Thank you for choosing MedAgg Healthcare for your medical needs. We're committed to providing you with the best possible care.
            
            What happens next?
            - Our AI assistant will call you shortly to discuss your symptoms
            - We'll schedule an appointment with the most suitable specialist
            - You'll receive a confirmation email with all the details
            - We'll send you a reminder before your appointment
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            The MedAgg Healthcare Team
            """
            
            return await self._send_email(patient_email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, text_body: str, html_body: str = None) -> bool:
        """Send email using SMTP"""
        try:
            # For POC, we'll simulate email sending
            # In production, use actual SMTP
            logger.info(f"Sending email to {to_email}: {subject}")
            logger.info(f"Email content: {text_body[:100]}...")
            
            # Simulate email sending delay
            import asyncio
            await asyncio.sleep(1)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
            # Uncomment below for actual SMTP sending
            """
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            """
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


