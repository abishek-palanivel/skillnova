from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, Course, CourseEnrollment, CourseFinalProject, UserFinalProjectSubmission

final_projects_bp = Blueprint('final_projects', __name__)

@final_projects_bp.route('/courses/<course_id>/final-project', methods=['GET'])
@jwt_required()
def get_course_final_project(course_id):
    """Get final project for a course"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 403
        
        # Get final project for the course
        final_project = CourseFinalProject.query.filter_by(
            course_id=course_id,
            is_active=True
        ).first()
        
        if not final_project:
            return jsonify({
                'success': False,
                'message': 'No final project found for this course'
            }), 404
        
        # Get user's submission if exists
        submission = UserFinalProjectSubmission.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            final_project_id=final_project.id
        ).first()
        
        project_data = {
            'id': str(final_project.id),
            'title': final_project.title,
            'description': final_project.description,
            'requirements': final_project.requirements,
            'passing_percentage': final_project.passing_percentage,
            'submission': None
        }
        
        if submission:
            project_data['submission'] = {
                'id': str(submission.id),
                'completion_percentage': submission.completion_percentage,
                'status': submission.status,
                'mentor_feedback': submission.mentor_feedback,
                'mentor_score': submission.mentor_score,
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'reviewed_at': submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                'completed_at': submission.completed_at.isoformat() if submission.completed_at else None
            }
        
        return jsonify({
            'success': True,
            'final_project': project_data,
            'enrollment_status': {
                'course_unlocked': enrollment.course_unlocked,
                'final_project_completion': enrollment.final_project_completion_percentage
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get final project: {str(e)}'
        }), 500

@final_projects_bp.route('/courses/<course_id>/final-project/submit', methods=['POST'])
@jwt_required()
def submit_final_project(course_id):
    """Submit or update final project"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 403
        
        # Get final project for the course
        final_project = CourseFinalProject.query.filter_by(
            course_id=course_id,
            is_active=True
        ).first()
        
        if not final_project:
            return jsonify({
                'success': False,
                'message': 'No final project found for this course'
            }), 404
        
        # Get or create submission
        submission = UserFinalProjectSubmission.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            final_project_id=final_project.id
        ).first()
        
        if not submission:
            submission = UserFinalProjectSubmission(
                user_id=user_id,
                course_id=course_id,
                final_project_id=final_project.id
            )
            db.session.add(submission)
        
        # Update submission data
        submission.submission_data = data.get('submission_data', {})
        completion_percentage = data.get('completion_percentage', 0)
        submission.completion_percentage = max(0, min(100, completion_percentage))
        
        # Update status based on completion
        if completion_percentage >= 100:
            submission.status = 'submitted'
            submission.submitted_at = datetime.utcnow()
        elif completion_percentage > 0:
            submission.status = 'in_progress'
        
        # Update enrollment final project completion
        enrollment.final_project_completion_percentage = submission.completion_percentage
        
        # Check if course should be unlocked (75% completion)
        if submission.completion_percentage >= final_project.passing_percentage:
            enrollment.course_unlocked = True
        else:
            enrollment.course_unlocked = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Final project updated successfully',
            'submission': {
                'id': str(submission.id),
                'completion_percentage': submission.completion_percentage,
                'status': submission.status,
                'course_unlocked': enrollment.course_unlocked
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit final project: {str(e)}'
        }), 500

@final_projects_bp.route('/courses/<course_id>/final-project/mentor-review', methods=['POST'])
@jwt_required()
def mentor_review_final_project(course_id):
    """Mentor review and score final project (mentor only)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is a mentor (simplified check - in production, verify mentor permissions)
        from models import User
        user = User.query.get(user_id)
        if not user or not user.is_mentor:
            return jsonify({
                'success': False,
                'message': 'Only mentors can review final projects'
            }), 403
        
        submission_id = data.get('submission_id')
        mentor_score = data.get('mentor_score')
        mentor_feedback = data.get('mentor_feedback', '')
        
        if not submission_id or mentor_score is None:
            return jsonify({
                'success': False,
                'message': 'Submission ID and mentor score are required'
            }), 400
        
        # Validate score
        if not 0 <= mentor_score <= 100:
            return jsonify({
                'success': False,
                'message': 'Mentor score must be between 0 and 100'
            }), 400
        
        # Get submission
        submission = UserFinalProjectSubmission.query.get(submission_id)
        if not submission:
            return jsonify({
                'success': False,
                'message': 'Submission not found'
            }), 404
        
        # Update submission with mentor review
        submission.mentor_score = mentor_score
        submission.mentor_feedback = mentor_feedback
        submission.status = 'reviewed'
        submission.reviewed_at = datetime.utcnow()
        
        # If mentor score >= passing percentage, mark as completed
        final_project = submission.final_project
        if mentor_score >= final_project.passing_percentage:
            submission.status = 'completed'
            submission.completed_at = datetime.utcnow()
            
            # Update enrollment
            enrollment = CourseEnrollment.query.filter_by(
                user_id=submission.user_id,
                course_id=course_id
            ).first()
            
            if enrollment:
                enrollment.course_unlocked = True
                enrollment.final_project_completion_percentage = mentor_score
        else:
            submission.status = 'failed'
            
            # Update enrollment
            enrollment = CourseEnrollment.query.filter_by(
                user_id=submission.user_id,
                course_id=course_id
            ).first()
            
            if enrollment:
                enrollment.course_unlocked = False
                enrollment.final_project_completion_percentage = mentor_score
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Final project reviewed successfully',
            'submission': {
                'id': str(submission.id),
                'mentor_score': submission.mentor_score,
                'status': submission.status,
                'reviewed_at': submission.reviewed_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to review final project: {str(e)}'
        }), 500

@final_projects_bp.route('/mentor/final-projects', methods=['GET'])
@jwt_required()
def get_mentor_final_projects():
    """Get all final project submissions for mentor review"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is a mentor
        from models import User
        user = User.query.get(user_id)
        if not user or not user.is_mentor:
            return jsonify({
                'success': False,
                'message': 'Only mentors can access this endpoint'
            }), 403
        
        # Get all submissions that need review
        submissions = UserFinalProjectSubmission.query.filter(
            UserFinalProjectSubmission.status.in_(['submitted', 'in_progress'])
        ).all()
        
        submissions_data = []
        for submission in submissions:
            submissions_data.append({
                'id': str(submission.id),
                'user_name': submission.user.name,
                'course_title': submission.course.title,
                'final_project_title': submission.final_project.title,
                'completion_percentage': submission.completion_percentage,
                'status': submission.status,
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'submission_data': submission.submission_data
            })
        
        return jsonify({
            'success': True,
            'submissions': submissions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get final projects: {str(e)}'
        }), 500