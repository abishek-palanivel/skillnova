from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os

from models import db, User, Course, CourseEnrollment, Assessment, BioData
from certificate_service import CertificateGenerator
from ai_recommendations_simple import ai_engine

certificates_bp = Blueprint('certificates', __name__)
certificate_generator = CertificateGenerator()

@certificates_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_certificate():
    """Generate certificate after course completion with AI integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        course_id = data.get('course_id')
        if not course_id:
            return jsonify({
                'success': False,
                'message': 'Course ID is required'
            }), 400
        
        # Get user and course
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return jsonify({
                'success': False,
                'message': 'User or course not found'
            }), 404
        
        # Check if user has completed the course
        enrollment = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 400
        
        if enrollment.status != 'completed':
            return jsonify({
                'success': False,
                'message': 'Course must be completed before generating certificate'
            }), 400
        
        # Check if certificate already exists
        existing_certificate = Certificate.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            is_valid=True
        ).first()
        
        if existing_certificate:
            return jsonify({
                'success': False,
                'message': 'Certificate already exists for this course',
                'certificate_number': existing_certificate.certificate_number
            }), 409
        
        # Get user's final assessment score
        final_assessment = Assessment.query.filter_by(
            user_id=user_id,
            assessment_type='final'
        ).order_by(Assessment.completed_at.desc()).first()
        
        if not final_assessment:
            return jsonify({
                'success': False,
                'message': 'Final assessment must be completed before generating certificate'
            }), 400
        
        # Check if user passed (60% minimum)
        if final_assessment.score_percentage < 60:
            return jsonify({
                'success': False,
                'message': f'Minimum 60% score required for certificate. Your score: {final_assessment.score_percentage}%'
            }), 400
        
        # Get user profile for AI personalization
        biodata = BioData.query.filter_by(user_id=user_id).first()
        user_profile = None
        
        if biodata:
            bio_dict = {
                'skills': biodata.skills,
                'goals': biodata.goals,
                'interests': biodata.interests,
                'education': biodata.education,
                'experience_level': biodata.experience_level
            }
            user_profile = ai_engine.analyze_bio_data_with_ai(bio_dict)
        
        # Generate certificate with AI integration
        certificate_result = certificate_generator.generate_certificate(
            user_name=user.name,
            course_title=course.title,
            final_score=final_assessment.score_percentage,
            completion_date=enrollment.completed_at or datetime.utcnow()
        )
        
        # Save certificate to database
        certificate = Certificate(
            user_id=user_id,
            course_id=course_id,
            certificate_number=certificate_result['certificate_number'],
            final_score=final_assessment.score_percentage,
            pdf_path=certificate_result['pdf_path'],
            is_valid=True
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Certificate generated successfully',
            'certificate': {
                'certificate_number': certificate.certificate_number,
                'final_score': certificate.final_score,
                'issued_date': certificate.issued_at.isoformat(),
                'download_url': f'/api/certificates/download/{certificate.certificate_number}'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to generate certificate: {str(e)}'
        }), 500

@certificates_bp.route('/download/<certificate_number>', methods=['GET'])
def download_certificate(certificate_number):
    """Download certificate PDF"""
    try:
        certificate = Certificate.query.filter_by(
            certificate_number=certificate_number,
            is_valid=True
        ).first()
        
        if not certificate:
            return jsonify({
                'success': False,
                'message': 'Certificate not found'
            }), 404
        
        if not os.path.exists(certificate.pdf_path):
            return jsonify({
                'success': False,
                'message': 'Certificate file not found'
            }), 404
        
        return send_file(
            certificate.pdf_path,
            as_attachment=True,
            download_name=f"certificate_{certificate_number}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to download certificate: {str(e)}'
        }), 500

@certificates_bp.route('/verify/<certificate_number>', methods=['GET'])
def verify_certificate(certificate_number):
    """Verify certificate authenticity"""
    try:
        certificate = Certificate.query.filter_by(
            certificate_number=certificate_number,
            is_valid=True
        ).first()
        
        if not certificate:
            return jsonify({
                'valid': False,
                'message': 'Certificate not found or invalid'
            })
        
        user = User.query.get(certificate.user_id)
        course = Course.query.get(certificate.course_id)
        
        return jsonify({
            'valid': True,
            'certificate': {
                'certificate_number': certificate.certificate_number,
                'student_name': user.name,
                'course_title': course.title,
                'final_score': certificate.final_score,
                'issued_date': certificate.issued_at.isoformat(),
                'verification_date': datetime.utcnow().isoformat()
            },
            'message': 'Certificate is valid and authentic'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to verify certificate: {str(e)}'
        }), 500

@certificates_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_certificates():
    """Get all certificates for the current user"""
    try:
        user_id = get_jwt_identity()
        
        certificates = Certificate.query.filter_by(
            user_id=user_id,
            is_valid=True
        ).order_by(Certificate.issued_at.desc()).all()
        
        certificate_list = []
        for cert in certificates:
            course = Course.query.get(cert.course_id)
            certificate_list.append({
                'certificate_number': cert.certificate_number,
                'course_title': course.title if course else 'Unknown Course',
                'final_score': cert.final_score,
                'issued_date': cert.issued_at.isoformat(),
                'download_url': f'/api/certificates/download/{cert.certificate_number}',
                'verify_url': f'/api/certificates/verify/{cert.certificate_number}'
            })
        
        return jsonify({
            'success': True,
            'certificates': certificate_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get certificates: {str(e)}'
        }), 500

@certificates_bp.route('/eligible/<course_id>', methods=['GET'])
@jwt_required()
def check_certificate_eligibility(course_id):
    """Check if user is eligible for certificate"""
    try:
        user_id = get_jwt_identity()
        
        # Check enrollment
        enrollment = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'eligible': False,
                'reason': 'Not enrolled in this course'
            })
        
        if enrollment.status != 'completed':
            return jsonify({
                'eligible': False,
                'reason': 'Course not completed',
                'progress': enrollment.progress_percentage
            })
        
        # Check final assessment
        final_assessment = Assessment.query.filter_by(
            user_id=user_id,
            assessment_type='final'
        ).order_by(Assessment.completed_at.desc()).first()
        
        if not final_assessment:
            return jsonify({
                'eligible': False,
                'reason': 'Final assessment not completed'
            })
        
        if final_assessment.score_percentage < 60:
            return jsonify({
                'eligible': False,
                'reason': f'Minimum 60% score required. Your score: {final_assessment.score_percentage}%',
                'score': final_assessment.score_percentage
            })
        
        # Check if certificate already exists
        existing_certificate = Certificate.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            is_valid=True
        ).first()
        
        if existing_certificate:
            return jsonify({
                'eligible': False,
                'reason': 'Certificate already generated',
                'certificate_number': existing_certificate.certificate_number
            })
        
        return jsonify({
            'eligible': True,
            'final_score': final_assessment.score_percentage,
            'completion_date': enrollment.completed_at.isoformat() if enrollment.completed_at else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to check eligibility: {str(e)}'
        }), 500

@certificates_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_certificate_stats():
    """Get certificate statistics for the user"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's certificates
        certificates = Certificate.query.filter_by(
            user_id=user_id,
            is_valid=True
        ).all()
        
        # Calculate statistics
        total_certificates = len(certificates)
        average_score = sum([cert.final_score for cert in certificates]) / total_certificates if total_certificates > 0 else 0
        
        # Get achievement levels
        achievement_levels = {}
        for cert in certificates:
            if cert.final_score >= 90:
                level = 'Distinction'
            elif cert.final_score >= 80:
                level = 'Merit'
            elif cert.final_score >= 70:
                level = 'Credit'
            else:
                level = 'Pass'
            
            achievement_levels[level] = achievement_levels.get(level, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_certificates': total_certificates,
                'average_score': round(average_score, 1),
                'achievement_levels': achievement_levels,
                'latest_certificate': certificates[-1].issued_at.isoformat() if certificates else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get certificate stats: {str(e)}'
        }), 500