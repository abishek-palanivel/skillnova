#!/usr/bin/env python3
"""
Certificate generation service with AI integration
"""

import os
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import qrcode
from io import BytesIO
import base64

class CertificateGenerator:
    def __init__(self):
        self.certificates_dir = os.path.join(os.path.dirname(__file__), '..', 'certificates')
        if not os.path.exists(self.certificates_dir):
            os.makedirs(self.certificates_dir)
    
    def generate_certificate_number(self):
        """Generate a unique certificate number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"SKILLNOVA-JAVA-{timestamp}-{unique_id}"
    
    def create_qr_code(self, certificate_number, user_name, course_title):
        """Create QR code for certificate verification"""
        verification_data = f"Certificate: {certificate_number}\nStudent: {user_name}\nCourse: {course_title}\nIssued: {datetime.now().strftime('%Y-%m-%d')}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def generate_ai_certificate_content(self, user_name, course_title, final_score, completion_date, user_profile=None):
        """Generate AI-powered certificate content with perfect alignment for 100% completion"""
        
        # Special AI-generated content for perfect 100% scores
        if final_score == 100.0:
            performance_message = "with absolute perfection and unparalleled mastery"
            achievement_level = "Perfect Excellence"
            performance_note = "Achieved flawless understanding with 100% accuracy, demonstrating exceptional dedication and complete mastery of all concepts"
            ai_recognition = "This rare achievement of perfect completion reflects extraordinary commitment to learning and exceptional intellectual capability."
        elif final_score >= 95:
            performance_message = "with near-perfect excellence and outstanding mastery"
            achievement_level = "Highest Distinction"
            performance_note = "Demonstrates exceptional mastery with near-perfect performance and outstanding problem-solving abilities"
            ai_recognition = "This exceptional performance places the recipient among the top achievers in the program."
        elif final_score >= 90:
            performance_message = "with exceptional excellence and outstanding dedication"
            achievement_level = "Distinction"
            performance_note = "Demonstrates mastery of advanced concepts and exceptional problem-solving abilities"
            ai_recognition = "This outstanding achievement reflects strong commitment and excellent understanding."
        elif final_score >= 80:
            performance_message = "with great proficiency and commendable effort"
            achievement_level = "Merit"
            performance_note = "Shows strong understanding and practical application of core concepts"
            ai_recognition = "This solid performance demonstrates good grasp of the subject matter."
        elif final_score >= 70:
            performance_message = "with solid competency and consistent performance"
            achievement_level = "Credit"
            performance_note = "Exhibits good grasp of fundamental principles and steady progress"
            ai_recognition = "This achievement shows consistent effort and understanding."
        elif final_score >= 60:
            performance_message = "with successful completion and dedicated effort"
            achievement_level = "Certificate of Completion"
            performance_note = "Successfully demonstrates understanding of core concepts and meets all course requirements"
            ai_recognition = "This achievement reflects commitment to learning and successful skill development."
        else:
            # This shouldn't happen as certificates are only generated for passing scores
            performance_message = "with completion of the course requirements"
            achievement_level = "Completion"
            performance_note = "Participated in the learning program"
            ai_recognition = "Participated in the learning experience."
        
        # AI-enhanced skills summary with perfect alignment for 100% scores
        if final_score == 100.0:
            base_skills = [
                "Mastery of Object-Oriented Programming Principles",
                "Expert-Level Java Collections Framework Implementation",
                "Advanced Exception Handling and File I/O Operations",
                "Professional Multithreading and Concurrency Management",
                "Complete Understanding of Advanced Java Features and Lambda Expressions",
                "Expert Implementation of Software Design Patterns",
                "Perfect Problem-Solving and Analytical Thinking",
                "Exceptional Code Quality and Best Practices"
            ]
        else:
            base_skills = [
                "Object-Oriented Programming Principles",
                "Java Collections Framework Understanding",
                "Exception Handling and File I/O Operations",
                "Multithreading and Concurrency Concepts",
                "Java Features and Lambda Expressions",
                "Software Design Patterns Implementation"
            ]
        
        # Add personalized skills based on user profile
        if user_profile:
            interests = user_profile.get('interests', [])
            if 'Web Development' in interests:
                skill_level = "Expert-Level" if final_score == 100.0 else "Practical"
                base_skills.append(f"{skill_level} Web Application Development with Java")
            if 'Data Science' in interests:
                skill_level = "Advanced" if final_score == 100.0 else "Basic"
                base_skills.append(f"{skill_level} Data Processing and Analysis Techniques")
            if 'Mobile Development' in interests:
                skill_level = "Professional" if final_score == 100.0 else "Fundamental"
                base_skills.append(f"{skill_level} Android Development Knowledge")
        
        certificate_content = {
            "performance_message": performance_message,
            "achievement_level": achievement_level,
            "performance_note": performance_note,
            "ai_recognition": ai_recognition,
            "skills_acquired": base_skills,
            "completion_date": completion_date,
            "final_score": final_score,
            "personalized": user_profile is not None,
            "perfect_score": final_score == 100.0
        }
        
        return certificate_content
    
    def create_certificate_pdf(self, user_name, course_title, certificate_number, final_score, completion_date):
        """Create a professional PDF certificate"""
        
        filename = f"certificate_{certificate_number}.pdf"
        filepath = os.path.join(self.certificates_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        name_style = ParagraphStyle(
            'CustomName',
            parent=styles['Normal'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        )
        
        # Generate AI content
        ai_content = self.generate_ai_certificate_content(user_name, course_title, final_score, completion_date)
        
        # Build certificate content
        story = []
        
        # Header
        story.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("SkillNova Learning Platform", subtitle_style))
        story.append(Spacer(1, 30))
        
        # Main content
        story.append(Paragraph("This is to certify that", body_style))
        story.append(Spacer(1, 10))
        
        # Student name
        story.append(Paragraph(f"<u>{user_name}</u>", name_style))
        story.append(Spacer(1, 20))
        
        # Course completion text
        story.append(Paragraph(f"has successfully completed the course", body_style))
        story.append(Spacer(1, 10))
        
        # Course title
        story.append(Paragraph(f"<b>{course_title}</b>", subtitle_style))
        story.append(Spacer(1, 20))
        
        # AI-generated performance message
        story.append(Paragraph(f"{ai_content['performance_message']}", body_style))
        story.append(Spacer(1, 15))
        
        # Special recognition for perfect scores
        if ai_content.get('perfect_score', False):
            perfect_style = ParagraphStyle(
                'PerfectScore',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=15,
                alignment=TA_CENTER,
                textColor=colors.gold,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("🏆 PERFECT SCORE ACHIEVEMENT 🏆", perfect_style))
            story.append(Spacer(1, 10))
        
        # Achievement details
        story.append(Paragraph(f"<b>Achievement Level:</b> {ai_content['achievement_level']}", body_style))
        story.append(Paragraph(f"<b>Final Score:</b> {final_score}%", body_style))
        story.append(Paragraph(f"<b>Completion Date:</b> {completion_date.strftime('%B %d, %Y')}", body_style))
        story.append(Spacer(1, 15))
        
        # AI Recognition
        story.append(Paragraph(f"<i>{ai_content['ai_recognition']}</i>", body_style))
        story.append(Spacer(1, 20))
        
        # Skills acquired
        story.append(Paragraph("<b>Skills Mastered:</b>", body_style))
        for skill in ai_content['skills_acquired']:
            story.append(Paragraph(f"• {skill}", body_style))
        
        story.append(Spacer(1, 30))
        
        # Certificate details
        story.append(Paragraph(f"<b>Certificate Number:</b> {certificate_number}", body_style))
        story.append(Paragraph(f"<b>Issued Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_certificate(self, user_name, course_title, final_score, completion_date=None):
        """Main method to generate a complete certificate"""
        
        if completion_date is None:
            completion_date = datetime.now()
        
        # Generate certificate number
        certificate_number = self.generate_certificate_number()
        
        # Create PDF certificate
        pdf_path = self.create_certificate_pdf(
            user_name, course_title, certificate_number, 
            final_score, completion_date
        )
        
        # Generate QR code
        qr_code_buffer = self.create_qr_code(certificate_number, user_name, course_title)
        
        # Prepare certificate data
        certificate_data = {
            "certificate_number": certificate_number,
            "user_name": user_name,
            "course_title": course_title,
            "final_score": final_score,
            "completion_date": completion_date.isoformat(),
            "issued_date": datetime.now().isoformat(),
            "skills_acquired": [
                "Object-Oriented Programming Principles",
                "Java Collections Framework Mastery", 
                "Exception Handling and File I/O Operations",
                "Multithreading and Concurrency Management",
                "Advanced Java Features and Lambda Expressions",
                "Software Design Patterns Implementation"
            ],
            "verification_qr": base64.b64encode(qr_code_buffer.getvalue()).decode('utf-8')
        }
        
        return {
            "success": True,
            "certificate_number": certificate_number,
            "pdf_path": pdf_path,
            "certificate_data": certificate_data,
            "message": f"Certificate generated successfully for {user_name}"
        }

# Test function
if __name__ == "__main__":
    generator = CertificateGenerator()
    result = generator.generate_certificate(
        user_name="John Doe",
        course_title="Complete Java Programming Mastery",
        final_score=85.5
    )
    print(f"Certificate generated: {result['certificate_number']}")
    print(f"PDF saved at: {result['pdf_path']}")