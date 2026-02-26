#!/usr/bin/env python3
"""
Email service for SkillNova
Handles all email sending functionality
"""

import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.admin_email = os.getenv('ADMIN_EMAIL', 'abishekopennova@gmail.com')
        self.admin_password = os.getenv('ADMIN_APP_PASS', 'asqa lula byrf gunf')
        
    def send_email(self, to_email, subject, html_body, text_body=None):
        """
        Send email using Gmail SMTP
        """
        try:
            # Create message
            msg = EmailMessage()
            msg['From'] = self.admin_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Set content
            if text_body:
                msg.set_content(text_body)
            
            if html_body:
                msg.add_alternative(html_body, subtype='html')
            
            # Create secure connection and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.admin_email, self.admin_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False
    
    def send_password_reset_email(self, user_name, user_email, reset_link):
        """
        Send password reset email with proper formatting
        """
        subject = "SkillNova Password Reset Request"
        
        # HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - SkillNova</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">SkillNova</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">💫 "Shine with Skills. Grow with Guidance."</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Password Reset Request</h2>
                
                <p>Hello <strong>{user_name}</strong>,</p>
                
                <p>You requested a password reset for your SkillNova account. Click the button below to reset your password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #3B82F6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy and paste this link in your browser:</p>
                <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 14px;">
                    <a href="{reset_link}" style="color: #3B82F6;">{reset_link}</a>
                </p>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>⚠️ Important:</strong> This link will expire in 1 hour for security reasons.</p>
                </div>
                
                <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Team</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Developer: Abishek | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        SkillNova Password Reset Request
        
        Hello {user_name},
        
        You requested a password reset for your SkillNova account.
        
        Please visit this link to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        SkillNova Team
        
        Developer: Abishek
        LinkedIn: https://www.linkedin.com/in/abishek-p-9ab80a326
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_welcome_email(self, user_name, user_email):
        """
        Send welcome email to new users
        """
        subject = "Welcome to SkillNova! 🌟"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to SkillNova</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to SkillNova!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">💫 "Shine with Skills. Grow with Guidance."</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {user_name}! 👋</h2>
                
                <p>Thank you for joining SkillNova! Your journey to career excellence starts here.</p>
                
                <h3 style="color: #3B82F6;">Next Steps:</h3>
                <ul style="padding-left: 20px;">
                    <li>Complete your bio data profile</li>
                    <li>Take the initial skill assessment</li>
                    <li>Get personalized course recommendations</li>
                    <li>Connect with expert mentors</li>
                    <li>Practice with hands-on exercises</li>
                </ul>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #1565c0;"><strong>💡 Pro Tip:</strong> Complete your profile first to get the best personalized recommendations!</p>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>The SkillNova Team</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Developer: Abishek | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to SkillNova, {user_name}!
        
        💫 "Shine with Skills. Grow with Guidance."
        
        Thank you for joining SkillNova! Your journey to career excellence starts here.
        
        Next steps:
        - Complete your bio data
        - Take the initial assessment
        - Get personalized course recommendations
        - Connect with mentors
        
        Best regards,
        The SkillNova Team
        
        Developer: Abishek
        LinkedIn: https://www.linkedin.com/in/abishek-p-9ab80a326
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_scholarship_email(self, user_name, user_email, scholarship_details):
        """Send scholarship offer email"""
        subject = "🎓 Scholarship Opportunity - SkillNova"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scholarship Offer - SkillNova</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎓 Scholarship Awarded!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">SkillNova Excellence Program</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Congratulations {user_name}! 🎉</h2>
                
                <p>We are thrilled to inform you that you have been selected for a <strong>SkillNova Scholarship</strong> based on your outstanding performance!</p>
                
                <div style="background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #2e7d32;">📋 Scholarship Details</h3>
                    <ul style="color: #2e7d32; margin: 0;">
                        <li><strong>Amount:</strong> {scholarship_details.get('amount', 'Full Coverage')}</li>
                        <li><strong>Duration:</strong> {scholarship_details.get('duration', '6 months')}</li>
                        <li><strong>Coverage:</strong> {scholarship_details.get('coverage', 'All courses and mentorship')}</li>
                        <li><strong>Start Date:</strong> {scholarship_details.get('start_date', 'Immediate')}</li>
                    </ul>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>📞 Next Steps:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #856404;">Please reply to this email within 7 days to accept this scholarship offer. Our team will then contact you with enrollment details.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:{self.admin_email}?subject=Scholarship Acceptance - {user_name}" 
                       style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        Accept Scholarship
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Scholarship Committee</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Contact: {self.admin_email} | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        SkillNova Scholarship Awarded!
        
        Congratulations {user_name}!
        
        You have been selected for a SkillNova Scholarship based on your outstanding performance.
        
        Scholarship Details:
        - Amount: {scholarship_details.get('amount', 'Full Coverage')}
        - Duration: {scholarship_details.get('duration', '6 months')}
        - Coverage: {scholarship_details.get('coverage', 'All courses and mentorship')}
        - Start Date: {scholarship_details.get('start_date', 'Immediate')}
        
        Next Steps:
        Please reply to this email within 7 days to accept this scholarship offer.
        
        Best regards,
        SkillNova Scholarship Committee
        Contact: {self.admin_email}
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_internship_email(self, user_name, user_email, internship_details):
        """Send internship offer email"""
        subject = "🚀 Internship Opportunity - SkillNova"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Internship Offer - SkillNova</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🚀 Internship Offer!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">SkillNova Career Program</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Congratulations {user_name}! 🎉</h2>
                
                <p>We are excited to offer you an <strong>internship position</strong> with SkillNova based on your exceptional performance and skills!</p>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196F3; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #1565c0;">💼 Internship Details</h3>
                    <ul style="color: #1565c0; margin: 0;">
                        <li><strong>Position:</strong> {internship_details.get('position', 'Software Development Intern')}</li>
                        <li><strong>Duration:</strong> {internship_details.get('duration', '3-6 months')}</li>
                        <li><strong>Stipend:</strong> {internship_details.get('stipend', 'Competitive')}</li>
                        <li><strong>Location:</strong> {internship_details.get('location', 'Remote/Hybrid')}</li>
                        <li><strong>Start Date:</strong> {internship_details.get('start_date', 'Flexible')}</li>
                    </ul>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>📞 Next Steps:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #856404;">Please reply to this email within 5 days to accept this internship offer. We'll schedule an interview and provide detailed information.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:{self.admin_email}?subject=Internship Acceptance - {user_name}" 
                       style="background-color: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        Accept Internship
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova HR Team</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Contact: {self.admin_email} | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        SkillNova Internship Offer!
        
        Congratulations {user_name}!
        
        We are excited to offer you an internship position with SkillNova.
        
        Internship Details:
        - Position: {internship_details.get('position', 'Software Development Intern')}
        - Duration: {internship_details.get('duration', '3-6 months')}
        - Stipend: {internship_details.get('stipend', 'Competitive')}
        - Location: {internship_details.get('location', 'Remote/Hybrid')}
        - Start Date: {internship_details.get('start_date', 'Flexible')}
        
        Next Steps:
        Please reply to this email within 5 days to accept this internship offer.
        
        Best regards,
        SkillNova HR Team
        Contact: {self.admin_email}
        """
        
        return self.send_email(user_email, subject, html_body, text_body)

    def send_evaluation_result_email(self, user_email, subject, template_data):
        """
        Send evaluation result email to users
        """
        user_name = template_data['user_name']
        evaluation_title = template_data['evaluation_title']
        score = template_data['score']
        grade = template_data['grade']
        decision = template_data['decision']
        feedback = template_data['feedback']
        next_steps = template_data['next_steps']
        
        # Determine colors and icons based on decision
        if 'selected' in decision or 'scholarship' in decision or 'internship' in decision:
            header_color = "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)"
            icon = "🎉"
            decision_color = "#4CAF50"
        elif 'rejected' in decision:
            header_color = "linear-gradient(135deg, #f44336 0%, #d32f2f 100%)"
            icon = "📝"
            decision_color = "#f44336"
        else:
            header_color = "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)"
            icon = "📊"
            decision_color = "#2196F3"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: {header_color}; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">{icon} SkillNova</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">Weekly Evaluation Results</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {user_name}! 👋</h2>
                
                <p>Your results for <strong>{evaluation_title}</strong> are ready!</p>
                
                <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: {decision_color};">📊 Your Performance</h3>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span><strong>Score:</strong></span>
                        <span style="color: {decision_color}; font-weight: bold; font-size: 18px;">{score}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span><strong>Grade:</strong></span>
                        <span style="color: {decision_color}; font-weight: bold; font-size: 18px;">{grade}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span><strong>Status:</strong></span>
                        <span style="color: {decision_color}; font-weight: bold;">{decision.title()}</span>
                    </div>
                </div>
                
                <div style="background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #2e7d32;">💬 Feedback</h4>
                    <p style="margin: 0; color: #2e7d32;">{feedback}</p>
                </div>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #1565c0;">🚀 Next Steps</h4>
                    <p style="margin: 0; color: #1565c0;">{next_steps}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" 
                       style="background-color: {decision_color}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        View Detailed Results
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Team</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Developer: Abishek | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        SkillNova - Weekly Evaluation Results
        
        Hello {user_name},
        
        Your results for {evaluation_title} are ready!
        
        Performance Summary:
        - Score: {score}%
        - Grade: {grade}
        - Status: {decision.title()}
        
        Feedback: {feedback}
        
        Next Steps: {next_steps}
        
        Visit your dashboard to view detailed results: http://localhost:3000/dashboard
        
        Best regards,
        SkillNova Team
        
        Developer: Abishek
        LinkedIn: https://www.linkedin.com/in/abishek-p-9ab80a326
        """
        
        try:
            success = self.send_email(user_email, subject, html_body, text_body)
            return {
                'success': success,
                'message': 'Email sent successfully' if success else 'Failed to send email'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def send_session_schedule_email(self, student_name, student_email, mentor_name, mentor_email, session_details):
        """Send session scheduling email to student when mentor schedules a specific time"""
        
        subject = f"Session Scheduled with {mentor_name} - SkillNova"
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Session Scheduled</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎯 Session Scheduled!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">Your mentor has confirmed the session</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {student_name}! 👋</h2>
                
                <p>Great news! Your mentor <strong>{mentor_name}</strong> has scheduled your session.</p>
                
                <div style="background: #ECFDF5; border-left: 4px solid #10B981; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #065F46;">📅 Session Details</h3>
                    <ul style="color: #065F46; margin: 0;">
                        <li><strong>Mentor:</strong> {mentor_name}</li>
                        <li><strong>Date & Time:</strong> {session_details.get('scheduled_at', 'TBD')}</li>
                        <li><strong>Duration:</strong> {session_details.get('duration_minutes', 60)} minutes</li>
                        <li><strong>Meeting Link:</strong> {session_details.get('meeting_link', 'Will be provided by mentor')}</li>
                        <li><strong>Session ID:</strong> {session_details.get('session_id', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="background: #FEF3C7; border: 1px solid #F59E0B; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400E;"><strong>📝 Preparation:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #92400E;">Please be ready 5 minutes before the session starts. Make sure you have a stable internet connection and a quiet environment.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" 
                       style="background-color: #10B981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        View Session Details
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(student_email, subject, html_body)

    def send_session_booking_email(self, student_name, student_email, mentor_name, mentor_email, session_details):
        """Send session booking confirmation emails to both student and mentor"""
        
        # Email to student
        student_subject = f"Session Booked with {mentor_name} - SkillNova"
        student_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Session Booking Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📅 Session Booked!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">SkillNova Mentorship</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {student_name}! 👋</h2>
                
                <p>Great news! Your mentorship session has been successfully booked.</p>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196F3; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #1565c0;">📋 Session Details</h3>
                    <ul style="color: #1565c0; margin: 0;">
                        <li><strong>Mentor:</strong> {mentor_name}</li>
                        <li><strong>Scheduled Date:</strong> {session_details.get('scheduled_at', 'TBD')}</li>
                        <li><strong>Duration:</strong> {session_details.get('duration_minutes', 60)} minutes</li>
                        <li><strong>Session ID:</strong> {session_details.get('session_id', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>📞 What's Next:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #856404;">Your mentor will contact you soon to confirm the exact time and provide meeting details. Please check your email regularly.</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" 
                       style="background-color: #3B82F6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        View Dashboard
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        # Email to mentor
        mentor_subject = f"New Session Booking from {student_name} - SkillNova"
        mentor_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Session Booking</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎓 New Session Request!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">SkillNova Mentorship</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {mentor_name}! 👋</h2>
                
                <p>You have a new mentorship session request from a student.</p>
                
                <div style="background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #2e7d32;">👤 Student Details</h3>
                    <ul style="color: #2e7d32; margin: 0;">
                        <li><strong>Student:</strong> {student_name}</li>
                        <li><strong>Email:</strong> {student_email}</li>
                        <li><strong>Requested Date:</strong> {session_details.get('scheduled_at', 'TBD')}</li>
                        <li><strong>Duration:</strong> {session_details.get('duration_minutes', 60)} minutes</li>
                        <li><strong>Session ID:</strong> {session_details.get('session_id', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>📞 Action Required:</strong></p>
                    <p style="margin: 5px 0 0 0; color: #856404;">Please contact the student to confirm the session time and provide meeting details (Zoom link, phone number, etc.).</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/mentor/bookings" 
                       style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        View Mentor Dashboard
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        # Send both emails
        student_sent = self.send_email(student_email, student_subject, student_html)
        mentor_sent = self.send_email(mentor_email, mentor_subject, mentor_html)
        
        return {
            'student_email_sent': student_sent,
            'mentor_email_sent': mentor_sent,
            'success': student_sent and mentor_sent
        }

# Create global email service instance
email_service = EmailService()