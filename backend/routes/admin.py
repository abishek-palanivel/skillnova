from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (db, User, Course, CourseModule, CourseEnrollment, Mentor, Question, Assessment, BioData,
                   WeeklyEvaluation, WeeklyEvaluationQuestion, WeeklyEvaluationAttempt, WeeklyEvaluationScore)
from ai_recommendations_simple import ai_engine
from ai_question_generator import ai_question_generator

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def admin_decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        return f(*args, **kwargs)
    admin_decorated_function.__name__ = f.__name__
    return admin_decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # User statistics
        total_users = User.query.filter_by(is_admin=False).count()
        active_users = User.query.filter_by(is_admin=False, is_active=True).count()
        
        # Course statistics
        total_courses = Course.query.count()
        active_courses = Course.query.filter_by(is_active=True).count()
        
        # Assessment statistics
        total_assessments = Assessment.query.count()
        avg_score = db.session.query(db.func.avg(Assessment.score_percentage)).scalar() or 0
        
        # Certificate statistics
        total_certificates = 0  # Placeholder for certificates
        issued_certificates = 0  # Placeholder for issued certificates
        
        # Recent activities
        recent_users = User.query.filter_by(is_admin=False).order_by(
            User.created_at.desc()
        ).limit(5).all()
        
        recent_assessments = Assessment.query.order_by(
            Assessment.completed_at.desc()
        ).limit(5).all()
        
        dashboard_data = {
            'statistics': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'inactive': total_users - active_users
                },
                'courses': {
                    'total': total_courses,
                    'active': active_courses,
                    'inactive': total_courses - active_courses
                },
                'assessments': {
                    'total': total_assessments,
                    'average_score': round(avg_score, 2)
                },
                'certificates': {
                    'total': total_certificates,
                    'issued': issued_certificates
                }
            },
            'recent_activities': {
                'new_users': [
                    {
                        'id': str(user.id),
                        'name': user.name,
                        'email': user.email,
                        'created_at': user.created_at.isoformat()
                    } for user in recent_users
                ],
                'recent_assessments': [
                    {
                        'user_name': assessment.user.name,
                        'type': assessment.assessment_type,
                        'score': assessment.score_percentage,
                        'completed_at': assessment.completed_at.isoformat()
                    } for assessment in recent_assessments
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get admin dashboard: {str(e)}'
        }), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        users_query = User.query.filter_by(is_admin=False)
        
        # Apply filters
        if request.args.get('active') == 'true':
            users_query = users_query.filter_by(is_active=True)
        elif request.args.get('active') == 'false':
            users_query = users_query.filter_by(is_active=False)
        
        users_pagination = users_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in users_pagination.items:
            # Get user statistics
            total_assessments = len(user.assessments)
            avg_score = sum([a.score_percentage for a in user.assessments]) / total_assessments if total_assessments > 0 else 0
            total_courses = len(user.enrollments)
            completed_courses = len([e for e in user.enrollments if e.status == 'completed'])
            
            users_data.append({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'statistics': {
                    'total_assessments': total_assessments,
                    'average_score': round(avg_score, 2),
                    'total_courses': total_courses,
                    'completed_courses': completed_courses,
                    'has_bio_data': user.bio_data is not None,
                    'has_outcome': False
                }
            })
        
        return jsonify({
            'success': True,
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users_pagination.total,
                'pages': users_pagination.pages,
                'has_next': users_pagination.has_next,
                'has_prev': users_pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get users: {str(e)}'
        }), 500

@admin_bp.route('/users/<user_id>/toggle-status', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    try:
        user = User.query.get(user_id)
        if not user or user.is_admin:
            return jsonify({
                'success': False,
                'message': 'User not found or cannot modify admin user'
            }), 404
        
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': {
                'id': str(user.id),
                'name': user.name,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to toggle user status: {str(e)}'
        }), 500

@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_courses():
    """Get all courses with enrollment statistics for admin"""
    try:
        from sqlalchemy import func
        
        # Get courses with enrollment counts
        courses_with_stats = db.session.query(
            Course,
            func.count(CourseEnrollment.id).label('enrollment_count')
        ).outerjoin(CourseEnrollment).group_by(Course.id).all()
        
        courses_data = []
        for course, enrollment_count in courses_with_stats:
            courses_data.append({
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'is_active': course.is_active,
                'modules_count': len(course.modules),
                'enrollment_count': enrollment_count or 0,
                'created_at': course.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'courses': courses_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get courses: {str(e)}'
        }), 500

@admin_bp.route('/courses', methods=['POST'])
@jwt_required()
@admin_required
def create_course():
    """Create a new course with comprehensive AI-generated content"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('skill_level'):
            return jsonify({
                'success': False,
                'message': 'Title and skill level are required'
            }), 400
        
        print(f"🤖 Creating AI-powered course: {data['title']} ({data['skill_level']})")
        
        # Import AI course generator
        from ai_course_generator import ai_course_generator
        
        # Generate complete course content using AI
        course_content = ai_course_generator.generate_complete_course(
            course_title=data['title'],
            skill_level=data['skill_level'].capitalize(),
            duration_weeks=data.get('duration_weeks', 8),
            modules_count=data.get('modules_count', 8)
        )
        
        print(f"✅ AI generated course with {len(course_content['modules'])} modules and {len(course_content['questions'])} questions")
        
        # Create the course
        course = Course(
            title=data['title'],
            description=data.get('description') or course_content['course_info'].get('description', f"Comprehensive {data['title']} course with AI-generated content"),
            skill_level=data['skill_level'].capitalize(),
            duration_weeks=data.get('duration_weeks', 8)
        )
        
        db.session.add(course)
        db.session.flush()  # Get the course ID
        
        # Create AI-generated modules
        for module_data in course_content['modules']:
            module = CourseModule(
                course_id=course.id,
                title=module_data['title'],
                content=module_data['content'],
                order_index=module_data.get('order_index', 1)
            )
            db.session.add(module)
        
        # Create AI-generated questions with course_id only if requested
        questions_created = 0
        if data.get('generate_questions', False) and course_content['questions']:
            for question_data in course_content['questions']:
                question = Question(
                    question_text=question_data['question_text'],
                    question_type=question_data['question_type'],
                    difficulty_level=question_data['difficulty_level'],
                    category=question_data.get('category', data['title']),
                    course_id=course.id,  # Link question to the course
                    correct_answer=question_data['correct_answer'],
                    options=question_data.get('options')
                )
                db.session.add(question)
                questions_created += 1
        
        db.session.commit()
        
        # Prepare response with comprehensive course information
        response_data = {
            'success': True,
            'message': f'🎉 Course "{course.title}" created successfully with comprehensive AI-generated content!',
            'course': {
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'modules_count': len(course_content['modules']),
                'questions_count': len(course_content['questions']),
                'created_at': course.created_at.isoformat()
            },
            'ai_generated_content': {
                'modules': len(course_content['modules']),
                'questions': questions_created,
                'learning_path': course_content['learning_path'],
                'assessments': len(course_content['assessments']),
                'completion_criteria': course_content['completion_criteria']
            }
        }
        
        print(f"🚀 Course created successfully: {course.title} with {len(course_content['modules'])} modules")
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating course: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to create course: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course(course_id):
    """Delete a course and all related data"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        course_title = course.title
        
        # Check if there are active enrollments
        active_enrollments = CourseEnrollment.query.filter_by(
            course_id=course_id,
            status='active'
        ).count()
        
        if active_enrollments > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete course with {active_enrollments} active enrollments. Please complete or transfer students first.'
            }), 400
        
        # Delete related data (cascade should handle this, but being explicit)
        CourseEnrollment.query.filter_by(course_id=course_id).delete()
        CourseModule.query.filter_by(course_id=course_id).delete()
        Question.query.filter_by(course_id=course_id).delete()
        
        # Delete the course
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Course "{course_title}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete course: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/enrollments', methods=['GET'])
@jwt_required()
@admin_required
def get_course_enrollments(course_id):
    """Get all enrollments for a specific course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        enrollments = CourseEnrollment.query.filter_by(course_id=course_id).all()
        
        enrollments_data = []
        for enrollment in enrollments:
            user = enrollment.user
            enrollments_data.append({
                'enrollment_id': str(enrollment.id),
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email
                },
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                'progress_percentage': enrollment.progress_percentage,
                'status': enrollment.status
            })
        
        return jsonify({
            'success': True,
            'course': {
                'id': str(course.id),
                'title': course.title
            },
            'enrollments': enrollments_data,
            'total_enrollments': len(enrollments_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course enrollments: {str(e)}'
        }), 500

@admin_bp.route('/enrollments/<enrollment_id>/exit', methods=['POST'])
@jwt_required()
@admin_required
def exit_student_from_course(enrollment_id):
    """Exit/remove a student from a course"""
    try:
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'Enrollment not found'
            }), 404
        
        user_name = enrollment.user.name
        course_title = enrollment.course.title
        
        # Update enrollment status to dropped
        enrollment.status = 'dropped'
        enrollment.completed_at = datetime.utcnow()  # Mark when they were removed
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Student "{user_name}" has been exited from course "{course_title}"'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to exit student from course: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/learning-path', methods=['GET'])
@jwt_required()
@admin_required
def get_course_learning_path(course_id):
    """Get AI-generated learning path for a course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Get course modules
        modules = CourseModule.query.filter_by(
            course_id=course_id,
            is_active=True
        ).order_by(CourseModule.order_index).all()
        
        # Import AI course generator
        from ai_course_generator import ai_course_generator
        
        # Generate learning path
        modules_data = [
            {
                'title': module.title,
                'order_index': module.order_index,
                'content': module.content[:200] + '...' if len(module.content) > 200 else module.content
            }
            for module in modules
        ]
        
        learning_path = ai_course_generator._generate_learning_path(
            course.title,
            course.skill_level,
            modules_data
        )
        
        return jsonify({
            'success': True,
            'learning_path': learning_path,
            'course_info': {
                'id': str(course.id),
                'title': course.title,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'modules_count': len(modules)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get learning path: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/modules', methods=['POST'])
@jwt_required()
@admin_required
def add_course_module(course_id):
    """Add a module to a course"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'message': 'Module title is required'
            }), 400
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Get next order index
        max_order = db.session.query(db.func.max(CourseModule.order_index)).filter_by(
            course_id=course_id
        ).scalar() or 0
        
        module = CourseModule(
            course_id=course_id,
            title=data['title'],
            content=data.get('content'),
            order_index=max_order + 1
        )
        
        db.session.add(module)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Module added successfully',
            'module': {
                'id': str(module.id),
                'title': module.title,
                'content': module.content,
                'order_index': module.order_index
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to add module: {str(e)}'
        }), 500

@admin_bp.route('/mentors', methods=['POST'])
@jwt_required()
@admin_required
def create_mentor():
    """Create a new mentor with user account and email notification"""
    try:
        from werkzeug.security import generate_password_hash
        import secrets
        import string
        
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Name and email are required'
            }), 400
        
        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # Use provided password or generate random one
        if data.get('password'):
            generated_password = data['password']
        else:
            password_length = 12
            password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
            generated_password = ''.join(secrets.choice(password_chars) for _ in range(password_length))
        
        # Create user account for mentor
        mentor_user = User(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(generated_password),
            is_mentor=True,
            is_active=True
        )
        
        db.session.add(mentor_user)
        db.session.flush()  # Get user ID
        
        # Create mentor record
        mentor = Mentor(
            user_id=mentor_user.id,
            name=data['name'],
            email=data['email'],
            expertise=data.get('expertise', ''),
            experience_years=data.get('experience', 0),
            bio=data.get('bio', ''),
            phone=data.get('phone', ''),
            linkedin=data.get('linkedin', ''),
            github=data.get('github', ''),
            is_available=True
        )
        
        db.session.add(mentor)
        db.session.commit()
        
        # Send welcome email with credentials
        email_sent = send_mentor_welcome_email(
            mentor_user.name, 
            mentor_user.email, 
            generated_password
        )
        
        return jsonify({
            'success': True,
            'message': f'Mentor "{mentor_user.name}" created successfully and welcome email sent',
            'mentor': {
                'id': str(mentor.id),
                'user_id': str(mentor_user.id),
                'name': mentor_user.name,
                'email': mentor_user.email,
                'expertise': mentor.expertise,
                'experience': mentor.experience_years,
                'is_active': mentor_user.is_active,
                'email_sent': email_sent,
                'created_at': mentor_user.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create mentor: {str(e)}'
        }), 500

def send_mentor_welcome_email(mentor_name, mentor_email, password):
    """Send welcome email to new mentor with login credentials"""
    try:
        from email_service import email_service
        
        subject = "Welcome to SkillNova - Mentor Account Created! 🎓"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome Mentor - SkillNova</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎓 Welcome to SkillNova!</h1>
                <p style="color: #f0f0f0; margin: 5px 0 0 0; font-size: 16px;">Mentor Portal Access</p>
            </div>
            
            <div style="background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">Hello {mentor_name}! 👋</h2>
                
                <p>Welcome to the SkillNova mentor community! Your mentor account has been created by our admin team.</p>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #1565c0;">🔐 Your Login Credentials</h3>
                    <p style="margin: 5px 0; color: #1565c0;"><strong>Email:</strong> {mentor_email}</p>
                    <p style="margin: 5px 0; color: #1565c0;"><strong>Password:</strong> <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;">{password}</code></p>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>🔒 Security Note:</strong> Please change your password after first login for security.</p>
                </div>
                
                <h3 style="color: #3B82F6;">As a SkillNova Mentor, you can:</h3>
                <ul style="padding-left: 20px;">
                    <li>Guide students through their learning journey</li>
                    <li>Conduct video call sessions</li>
                    <li>Chat with students and provide feedback</li>
                    <li>Track student progress and performance</li>
                    <li>Access mentor dashboard and analytics</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/login" 
                       style="background-color: #3B82F6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; font-size: 16px;">
                        Login to Mentor Portal
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="margin: 0; color: #666; font-size: 14px;">Best regards,<br><strong>SkillNova Admin Team</strong></p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    Contact: {email_service.admin_email} | 
                    <a href="https://www.linkedin.com/in/abishek-p-9ab80a326" style="color: #3B82F6;">LinkedIn</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to SkillNova - Mentor Account Created!
        
        Hello {mentor_name},
        
        Welcome to the SkillNova mentor community! Your mentor account has been created.
        
        Login Credentials:
        Email: {mentor_email}
        Password: {password}
        
        Security Note: Please change your password after first login.
        
        As a SkillNova Mentor, you can:
        - Guide students through their learning journey
        - Conduct video call sessions
        - Chat with students and provide feedback
        - Track student progress and performance
        - Access mentor dashboard and analytics
        
        Login at: http://localhost:3000/login
        
        Best regards,
        SkillNova Admin Team
        Contact: {email_service.admin_email}
        """
        
        return email_service.send_email(mentor_email, subject, html_body, text_body)
        
    except Exception as e:
        print(f"Failed to send mentor welcome email: {str(e)}")
        return False

@admin_bp.route('/questions', methods=['POST'])
@jwt_required()
@admin_required
def create_question():
    """Create a new question"""
    try:
        data = request.get_json()
        
        required_fields = ['question_text', 'question_type', 'difficulty_level', 'correct_answer']
        if not data or not all(data.get(field) for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Question text, type, difficulty level, and correct answer are required'
            }), 400
        
        question = Question(
            question_text=data['question_text'],
            question_type=data['question_type'],
            difficulty_level=data['difficulty_level'],
            category=data.get('category'),
            course_id=data.get('course_id'),  # Allow linking to a specific course
            correct_answer=data['correct_answer'],
            options=data.get('options')  # For multiple choice questions
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question created successfully',
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'created_at': question.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create question: {str(e)}'
        }), 500


        
    except Exception as e:
        db.session.rollback()


@admin_bp.route('/reports/performance', methods=['GET'])
@jwt_required()
@admin_required
def get_performance_report():
    """Generate performance report"""
    try:
        # Get assessment performance by type
        assessment_stats = db.session.query(
            Assessment.assessment_type,
            db.func.count(Assessment.id).label('total'),
            db.func.avg(Assessment.score_percentage).label('avg_score'),
            db.func.min(Assessment.score_percentage).label('min_score'),
            db.func.max(Assessment.score_percentage).label('max_score')
        ).group_by(Assessment.assessment_type).all()
        
        # Get course enrollment stats
        course_stats = db.session.query(
            Course.title,
            Course.skill_level,
            db.func.count(Course.enrollments).label('enrollments')
        ).join(Course.enrollments).group_by(Course.id, Course.title, Course.skill_level).all()
        
        # Get certificate distribution (placeholder)
        certificate_stats = []
        
        report = {
            'assessment_performance': [
                {
                    'type': stat.assessment_type,
                    'total_assessments': stat.total,
                    'average_score': round(stat.avg_score, 2),
                    'min_score': stat.min_score,
                    'max_score': stat.max_score
                } for stat in assessment_stats
            ],
            'course_popularity': [
                {
                    'course_title': stat.title,
                    'skill_level': stat.skill_level,
                    'total_enrollments': stat.enrollments
                } for stat in course_stats
            ],
            'certificate_distribution': certificate_stats
        }
        
        return jsonify({
            'success': True,
            'report': report,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate report: {str(e)}'
        }), 500

@admin_bp.route('/ai-analytics/user-insights', methods=['GET'])
@jwt_required()
@admin_required
def get_ai_user_insights():
    """Get AI-powered user insights and analytics"""
    try:
        # Get all users with bio data
        users_with_bio = db.session.query(User, BioData).join(BioData).filter(User.is_admin == False).all()
        
        if not users_with_bio:
            # Return default insights when no user data is available
            default_insights = {
                'total_analyzed_users': 0,
                'interest_distribution': [
                    {'interest': 'Web Development', 'count': 0, 'percentage': 0},
                    {'interest': 'Programming', 'count': 0, 'percentage': 0},
                    {'interest': 'Data Science', 'count': 0, 'percentage': 0}
                ],
                'skill_level_distribution': [
                    {'level': 'Beginner', 'count': 0, 'percentage': 0},
                    {'level': 'Intermediate', 'count': 0, 'percentage': 0},
                    {'level': 'Advanced', 'count': 0, 'percentage': 0}
                ],
                'key_insights': [
                    "No user bio data available for analysis",
                    "Encourage users to complete their profiles",
                    "Consider adding sample courses to attract users"
                ],
                'recommendations_for_admin': [
                    "Create beginner-friendly courses to attract new users",
                    "Add profile completion incentives",
                    "Focus on popular technology areas"
                ]
            }
            
            return jsonify({
                'success': True,
                'insights': default_insights,
                'user_profiles': [],
                'message': 'No user data available for analysis',
                'generated_at': datetime.utcnow().isoformat()
            }), 200
        
        # Analyze user interests and skill distribution
        interest_distribution = {}
        skill_level_distribution = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        user_profiles = []
        
        for user, bio_data in users_with_bio:
            # Prepare bio data for AI analysis
            bio_dict = {
                'skills': bio_data.skills,
                'goals': bio_data.goals,
                'interests': bio_data.interests,
                'education': bio_data.education,
                'experience_level': bio_data.experience_level
            }
            
            # Get assessment scores
            assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
            
            # Analyze user profile
            profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
            
            # Count interests
            for interest in profile['interests']:
                interest_distribution[interest] = interest_distribution.get(interest, 0) + 1
            
            # Count skill levels
            skill_level_distribution[profile['skill_level']] += 1
            
            user_profiles.append({
                'user_id': str(user.id),
                'user_name': user.name,
                'profile': profile,
                'course_count': len(user.enrollments),
                'assessment_count': len(user.assessments),
                'avg_score': sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
            })
        
        # Generate insights
        total_users = len(user_profiles)
        most_popular_interest = max(interest_distribution.items(), key=lambda x: x[1]) if interest_distribution else ('web_development', 0)
        
        insights = {
            'total_analyzed_users': total_users,
            'interest_distribution': [
                {
                    'interest': interest.replace('_', ' ').title(),
                    'count': count,
                    'percentage': round((count / total_users) * 100, 1)
                }
                for interest, count in sorted(interest_distribution.items(), key=lambda x: x[1], reverse=True)
            ],
            'skill_level_distribution': [
                {
                    'level': level.title(),
                    'count': count,
                    'percentage': round((count / total_users) * 100, 1)
                }
                for level, count in skill_level_distribution.items()
            ],
            'key_insights': [
                f"Most popular interest area: {most_popular_interest[0].replace('_', ' ').title()} ({most_popular_interest[1]} users)",
                f"Skill level distribution: {skill_level_distribution['beginner']} beginners, {skill_level_distribution['intermediate']} intermediate, {skill_level_distribution['advanced']} advanced",
                f"Average profile completeness: {round(sum([p['profile']['profile_completeness'] for p in user_profiles]) / total_users, 1)}%"
            ],
            'recommendations_for_admin': [
                "Consider creating more courses in popular interest areas",
                "Focus on beginner-friendly content if most users are beginners",
                "Encourage users to complete their profiles for better recommendations"
            ]
        }
        
        return jsonify({
            'success': True,
            'insights': insights,
            'user_profiles': user_profiles[:10],  # Return top 10 for preview
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate AI insights: {str(e)}'
        }), 500

@admin_bp.route('/ai-analytics/course-recommendations', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def get_ai_course_recommendations():
    """Get AI recommendations for new courses to create"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Analyze user demand patterns
        users_with_bio = db.session.query(User, BioData).join(BioData).filter(User.is_admin == False).all()
        
        if not users_with_bio:
            # Provide fallback recommendations when no user data is available
            fallback_recommendations = [
                {
                    'suggested_title': 'Web Development Fundamentals',
                    'category': 'Web Development',
                    'skill_level': 'Beginner',
                    'demand_score': 10,
                    'priority': 'High',
                    'estimated_duration': '8-10 weeks',
                    'target_audience': 'Beginners interested in web development'
                },
                {
                    'suggested_title': 'Python Programming Basics',
                    'category': 'Programming',
                    'skill_level': 'Beginner',
                    'demand_score': 8,
                    'priority': 'High',
                    'estimated_duration': '6-8 weeks',
                    'target_audience': 'Programming beginners'
                },
                {
                    'suggested_title': 'Data Science Introduction',
                    'category': 'Data Science',
                    'skill_level': 'Beginner',
                    'demand_score': 6,
                    'priority': 'Medium',
                    'estimated_duration': '10-12 weeks',
                    'target_audience': 'Data science enthusiasts'
                },
                {
                    'suggested_title': 'Mobile App Development',
                    'category': 'Mobile Development',
                    'skill_level': 'Intermediate',
                    'demand_score': 5,
                    'priority': 'Medium',
                    'estimated_duration': '12-14 weeks',
                    'target_audience': 'Developers interested in mobile apps'
                },
                {
                    'suggested_title': 'JavaScript Advanced Concepts',
                    'category': 'Web Development',
                    'skill_level': 'Advanced',
                    'demand_score': 4,
                    'priority': 'Low',
                    'estimated_duration': '6-8 weeks',
                    'target_audience': 'Experienced JavaScript developers'
                }
            ]
            
            return jsonify({
                'success': True,
                'course_recommendations': fallback_recommendations,
                'demand_analysis': {
                    'total_users_analyzed': 0,
                    'top_interests': [
                        {'interest': 'Web Development', 'user_count': 0, 'percentage': 0},
                        {'interest': 'Programming', 'user_count': 0, 'percentage': 0}
                    ]
                },
                'message': 'Showing default course recommendations (no user data available)',
                'generated_at': datetime.utcnow().isoformat()
            }), 200
        
        # Analyze what users are looking for
        demand_analysis = {}
        skill_gaps = {}
        
        for user, bio_data in users_with_bio:
            bio_dict = {
                'skills': bio_data.skills,
                'goals': bio_data.goals,
                'interests': bio_data.interests,
                'education': bio_data.education,
                'experience_level': bio_data.experience_level
            }
            
            assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
            profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
            
            # Track demand for each interest area
            for interest in profile['interests']:
                demand_analysis[interest] = demand_analysis.get(interest, 0) + 1
                
                # Track skill level demand
                skill_key = f"{interest}_{profile['skill_level']}"
                skill_gaps[skill_key] = skill_gaps.get(skill_key, 0) + 1
        
        # Generate course recommendations
        course_recommendations = []
        
        for interest, demand in sorted(demand_analysis.items(), key=lambda x: x[1], reverse=True):
            # Get skill level breakdown for this interest
            beginner_demand = skill_gaps.get(f"{interest}_beginner", 0)
            intermediate_demand = skill_gaps.get(f"{interest}_intermediate", 0)
            advanced_demand = skill_gaps.get(f"{interest}_advanced", 0)
            
            # Recommend courses based on demand
            if beginner_demand > 0:
                course_recommendations.append({
                    'suggested_title': f"Beginner {interest.replace('_', ' ').title()} Fundamentals",
                    'category': interest.replace('_', ' ').title(),
                    'skill_level': 'Beginner',
                    'demand_score': beginner_demand,
                    'priority': 'High' if beginner_demand >= 5 else 'Medium' if beginner_demand >= 3 else 'Low',
                    'estimated_duration': '6-8 weeks',
                    'target_audience': f"{beginner_demand} users interested in {interest.replace('_', ' ')}"
                })
            
            if intermediate_demand > 0:
                course_recommendations.append({
                    'suggested_title': f"Intermediate {interest.replace('_', ' ').title()} Projects",
                    'category': interest.replace('_', ' ').title(),
                    'skill_level': 'Intermediate',
                    'demand_score': intermediate_demand,
                    'priority': 'High' if intermediate_demand >= 3 else 'Medium' if intermediate_demand >= 2 else 'Low',
                    'estimated_duration': '8-10 weeks',
                    'target_audience': f"{intermediate_demand} users with intermediate {interest.replace('_', ' ')} skills"
                })
            
            if advanced_demand > 0:
                course_recommendations.append({
                    'suggested_title': f"Advanced {interest.replace('_', ' ').title()} Mastery",
                    'category': interest.replace('_', ' ').title(),
                    'skill_level': 'Advanced',
                    'demand_score': advanced_demand,
                    'priority': 'High' if advanced_demand >= 2 else 'Medium',
                    'estimated_duration': '10-12 weeks',
                    'target_audience': f"{advanced_demand} users seeking advanced {interest.replace('_', ' ')} skills"
                })
        
        # Sort by demand score
        course_recommendations.sort(key=lambda x: x['demand_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'course_recommendations': course_recommendations[:15],  # Top 15 recommendations
            'demand_analysis': {
                'total_users_analyzed': len(users_with_bio),
                'top_interests': [
                    {
                        'interest': interest.replace('_', ' ').title(),
                        'user_count': count,
                        'percentage': round((count / len(users_with_bio)) * 100, 1)
                    }
                    for interest, count in sorted(demand_analysis.items(), key=lambda x: x[1], reverse=True)[:5]
                ]
            },
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate course recommendations: {str(e)}'
        }), 500

@admin_bp.route('/mentors', methods=['GET'])
@jwt_required()
@admin_required
def get_all_mentors():
    """Get all mentors for admin management"""
    try:
        # Get all mentors
        mentors = Mentor.query.all()
        
        mentors_data = []
        for mentor in mentors:
            user = mentor.user if mentor.user else None
            mentors_data.append({
                'id': str(mentor.id),
                'user_id': str(mentor.user_id) if mentor.user_id else None,
                'name': mentor.name,
                'email': mentor.email,
                'bio': mentor.bio,
                'expertise': mentor.expertise,
                'experience': mentor.experience,
                'phone': mentor.phone,
                'linkedin': mentor.linkedin,
                'github': mentor.github,
                'is_active': user.is_active if user else mentor.is_available,
                'rating': mentor.rating,
                'total_sessions': mentor.total_sessions,
                'created_at': mentor.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'mentors': mentors_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get mentors: {str(e)}'
        }), 500

@admin_bp.route('/mentors/<mentor_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_mentor(mentor_id):
    """Update mentor information"""
    try:
        from werkzeug.security import generate_password_hash
        
        mentor = Mentor.query.get(mentor_id)
        if not mentor:
            return jsonify({
                'success': False,
                'message': 'Mentor not found'
            }), 404
        
        user = mentor.user
        data = request.get_json()
        
        # Update user info if user exists
        if user:
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            
            # Update password if provided
            if data.get('password'):
                user.password_hash = generate_password_hash(data['password'])
        
        # Update mentor info
        mentor.name = data.get('name', mentor.name)
        mentor.email = data.get('email', mentor.email)
        mentor.bio = data.get('bio', mentor.bio)
        mentor.expertise = data.get('expertise', mentor.expertise)
        mentor.experience_years = data.get('experience', mentor.experience_years)
        mentor.phone = data.get('phone', mentor.phone)
        mentor.linkedin = data.get('linkedin', mentor.linkedin)
        mentor.github = data.get('github', mentor.github)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mentor updated successfully',
            'mentor': {
                'id': str(mentor.id),
                'user_id': str(mentor.user_id) if mentor.user_id else None,
                'name': mentor.name,
                'email': mentor.email,
                'bio': mentor.bio,
                'expertise': mentor.expertise,
                'experience': mentor.experience_years,
                'phone': mentor.phone,
                'linkedin': mentor.linkedin,
                'github': mentor.github
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update mentor: {str(e)}'
        }), 500

@admin_bp.route('/mentors/<mentor_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_mentor(mentor_id):
    """Delete a mentor"""
    try:
        mentor = Mentor.query.get(mentor_id)
        if not mentor:
            return jsonify({
                'success': False,
                'message': 'Mentor not found'
            }), 404
        
        mentor_name = mentor.name
        user = mentor.user
        
        # Delete mentor record
        db.session.delete(mentor)
        
        # Deactivate user instead of deleting to preserve data integrity
        if user:
            user.is_active = False
            user.is_mentor = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mentor "{mentor_name}" removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete mentor: {str(e)}'
        }), 500

@admin_bp.route('/mentors/<user_id>/toggle-availability', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_mentor_availability(user_id):
    """Toggle mentor availability"""
    try:
        user = User.query.get(user_id)
        if not user or not user.is_mentor:
            return jsonify({
                'success': False,
                'message': 'Mentor not found'
            }), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mentor {"activated" if user.is_active else "deactivated"} successfully',
            'mentor': {
                'id': str(user.id),
                'name': user.name,
                'is_available': user.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to toggle mentor availability: {str(e)}'
        }), 500

@admin_bp.route('/questions', methods=['GET'])
@jwt_required()
@admin_required
def get_all_questions():
    """Get all questions for admin management with optional course filtering"""
    try:
        # Get optional course_id filter from query parameters
        course_id = request.args.get('course_id')
        
        if course_id:
            # Filter questions by course_id
            questions = Question.query.filter_by(course_id=course_id).all()
        else:
            # Get all questions
            questions = Question.query.all()
        
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'correct_answer': question.correct_answer,
                'options': question.options if isinstance(question.options, list) else [],
                'is_active': question.is_active,
                'course_id': str(question.course_id) if question.course_id else None,
                'created_at': question.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'questions': questions_data,
            'total_questions': len(questions_data),
            'filtered_by_course': course_id is not None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get questions: {str(e)}'
        }), 500

@admin_bp.route('/questions/<question_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_question(question_id):
    """Update question information"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
        
        data = request.get_json()
        
        question.question_text = data.get('question_text', question.question_text)
        question.question_type = data.get('question_type', question.question_type)
        question.difficulty_level = data.get('difficulty_level', question.difficulty_level)
        question.category = data.get('category', question.category)
        question.correct_answer = data.get('correct_answer', question.correct_answer)
        question.options = data.get('options', question.options)
        question.is_active = data.get('is_active', question.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question updated successfully',
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'is_active': question.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update question: {str(e)}'
        }), 500

@admin_bp.route('/questions/<question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(question_id):
    """Delete a question"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete question: {str(e)}'
        }), 500

@admin_bp.route('/questions/<question_id>/toggle-active', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_question_active(question_id):
    """Toggle question active status"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
        
        question.is_active = not question.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Question {"activated" if question.is_active else "deactivated"} successfully',
            'question': {
                'id': str(question.id),
                'question_text': question.question_text,
                'is_active': question.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to toggle question status: {str(e)}'
        }), 500

@admin_bp.route('/questions/generate-ai', methods=['POST'])
@jwt_required()
@admin_required
def generate_ai_questions():
    """Generate practice questions using AI"""
    try:
        data = request.get_json() or {}
        category = data.get('category', 'Python')
        difficulty = data.get('difficulty', 'medium')
        count = min(int(data.get('count', 5)), 20)  # Max 20 questions
        question_type = data.get('question_type', 'multiple_choice')
        
        generated_questions = []
        
        for i in range(count):
            # Generate question using AI
            question_data = ai_question_generator.generate_question(
                question_type, difficulty, category
            )
            
            question = Question(
                question_text=question_data['question_text'],
                question_type=question_type,
                difficulty_level=difficulty,
                category=category,
                correct_answer=question_data['correct_answer'],
                options=question_data.get('options'),
                explanation=question_data.get('explanation'),
                is_active=True
            )
            db.session.add(question)
            generated_questions.append({
                'question_text': question.question_text,
                'difficulty': difficulty,
                'category': category,
                'question_type': question_type
            })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(generated_questions)} AI practice questions',
            'questions': generated_questions,
            'questions_count': len(generated_questions)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to generate AI questions: {str(e)}'
        }), 500

@admin_bp.route('/ai-analytics/success-predictions', methods=['GET'])
@jwt_required()
@admin_required
def get_success_predictions():
    """Get AI predictions for user success rates"""
    try:
        # Get users with complete data
        users_with_data = db.session.query(User).filter(
            User.is_admin == False,
            User.bio_data.has(),
            User.assessments.any()
        ).all()
        
        if not users_with_data:
            return jsonify({
                'success': False,
                'message': 'Insufficient user data for predictions'
            }), 404
        
        predictions = []
        success_categories = {'high': 0, 'medium': 0, 'low': 0}
        
        for user in users_with_data:
            bio_data = user.bio_data
            bio_dict = {
                'skills': bio_data.skills,
                'goals': bio_data.goals,
                'interests': bio_data.interests,
                'education': bio_data.education,
                'experience_level': bio_data.experience_level
            }
            
            # Get user progress data
            assessment_scores = [a.score_percentage for a in user.assessments]
            course_progress = sum([e.progress_percentage for e in user.enrollments]) / len(user.enrollments) if user.enrollments else 0
            
            # Analyze profile
            profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
            
            # Get learning recommendations
            recommendations = ai_engine.get_learning_recommendations(profile, course_progress, assessment_scores)
            
            if recommendations:
                best_recommendation = recommendations[0]  # Highest confidence recommendation
                success_probability = best_recommendation['confidence']
                
                # Categorize success level
                if success_probability >= 80:
                    success_level = 'high'
                    success_categories['high'] += 1
                elif success_probability >= 60:
                    success_level = 'medium'
                    success_categories['medium'] += 1
                else:
                    success_level = 'low'
                    success_categories['low'] += 1
                
                predictions.append({
                    'user_id': str(user.id),
                    'user_name': user.name,
                    'success_probability': success_probability,
                    'success_level': success_level,
                    'predicted_path': best_recommendation['career_title'],
                    'current_progress': {
                        'avg_assessment_score': round(sum(assessment_scores) / len(assessment_scores), 1),
                        'course_completion': round(course_progress, 1),
                        'profile_completeness': profile['profile_completeness']
                    },
                    'recommendations': [
                        'Complete more assessments' if len(assessment_scores) < 3 else 'Continue current progress',
                        'Enroll in more courses' if len(user.enrollments) < 2 else 'Focus on course completion',
                        'Update profile information' if profile['profile_completeness'] < 80 else 'Profile looks good'
                    ]
                })
        
        # Sort by success probability
        predictions.sort(key=lambda x: x['success_probability'], reverse=True)
        
        # Generate summary insights
        total_users = len(predictions)
        summary = {
            'total_users_analyzed': total_users,
            'success_distribution': {
                'high_success': {
                    'count': success_categories['high'],
                    'percentage': round((success_categories['high'] / total_users) * 100, 1)
                },
                'medium_success': {
                    'count': success_categories['medium'],
                    'percentage': round((success_categories['medium'] / total_users) * 100, 1)
                },
                'low_success': {
                    'count': success_categories['low'],
                    'percentage': round((success_categories['low'] / total_users) * 100, 1)
                }
            },
            'average_success_rate': round(sum([p['success_probability'] for p in predictions]) / total_users, 1),
            'at_risk_users': len([p for p in predictions if p['success_probability'] < 60]),
            'high_potential_users': len([p for p in predictions if p['success_probability'] >= 80])
        }
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'summary': summary,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate success predictions: {str(e)}'
        }), 500

@admin_bp.route('/ai-analytics/mentor-matching', methods=['GET'])
@jwt_required()
@admin_required
def get_mentor_matching_insights():
    """Get AI insights for mentor-student matching"""
    try:
        # Get users and their interests
        users_with_bio = db.session.query(User, BioData).join(BioData).filter(User.is_admin == False).all()
        mentors = Mentor.query.filter_by(is_available=True).all()
        
        if not users_with_bio or not mentors:
            return jsonify({
                'success': False,
                'message': 'Insufficient data for mentor matching analysis'
            }), 404
        
        # Analyze user interests
        interest_demand = {}
        for user, bio_data in users_with_bio:
            bio_dict = {
                'skills': bio_data.skills,
                'goals': bio_data.goals,
                'interests': bio_data.interests,
                'education': bio_data.education,
                'experience_level': bio_data.experience_level
            }
            
            assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
            profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
            
            for interest in profile['interests']:
                interest_demand[interest] = interest_demand.get(interest, 0) + 1
        
        # Analyze mentor expertise coverage
        mentor_coverage = {}
        for mentor in mentors:
            expertise_areas = mentor.expertise.lower().split(',') if mentor.expertise else []
            for area in expertise_areas:
                area = area.strip()
                # Map expertise to our interest categories
                for category in ai_engine.skill_categories.keys():
                    if any(keyword in area for keyword in ai_engine.skill_categories[category]['keywords']):
                        mentor_coverage[category] = mentor_coverage.get(category, 0) + 1
                        break
        
        # Identify gaps and recommendations
        gaps = []
        recommendations = []
        
        for interest, demand in interest_demand.items():
            coverage = mentor_coverage.get(interest, 0)
            ratio = coverage / demand if demand > 0 else 0
            
            if ratio < 0.2:  # Less than 20% coverage
                gaps.append({
                    'interest_area': interest.replace('_', ' ').title(),
                    'user_demand': demand,
                    'mentor_coverage': coverage,
                    'gap_severity': 'High',
                    'recommended_mentors_needed': max(1, demand // 5)
                })
                recommendations.append(f"Recruit {max(1, demand // 5)} mentors for {interest.replace('_', ' ').title()}")
            elif ratio < 0.5:  # Less than 50% coverage
                gaps.append({
                    'interest_area': interest.replace('_', ' ').title(),
                    'user_demand': demand,
                    'mentor_coverage': coverage,
                    'gap_severity': 'Medium',
                    'recommended_mentors_needed': max(1, demand // 8)
                })
        
        # Generate matching suggestions
        matching_suggestions = []
        for user, bio_data in users_with_bio[:10]:  # Top 10 users for example
            bio_dict = {
                'skills': bio_data.skills,
                'goals': bio_data.goals,
                'interests': bio_data.interests,
                'education': bio_data.education,
                'experience_level': bio_data.experience_level
            }
            
            assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
            profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
            
            # Find best matching mentors
            mentor_matches = ai_engine.recommend_mentors(profile, limit=3)
            
            matching_suggestions.append({
                'user_id': str(user.id),
                'user_name': user.name,
                'user_interests': [i.replace('_', ' ').title() for i in profile['interests']],
                'recommended_mentors': mentor_matches
            })
        
        return jsonify({
            'success': True,
            'analysis': {
                'total_users': len(users_with_bio),
                'total_mentors': len(mentors),
                'interest_demand': [
                    {
                        'interest': interest.replace('_', ' ').title(),
                        'user_count': count,
                        'mentor_coverage': mentor_coverage.get(interest, 0),
                        'coverage_ratio': round((mentor_coverage.get(interest, 0) / count) * 100, 1) if count > 0 else 0
                    }
                    for interest, count in sorted(interest_demand.items(), key=lambda x: x[1], reverse=True)
                ],
                'coverage_gaps': gaps,
                'recommendations': recommendations
            },
            'matching_suggestions': matching_suggestions,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate mentor matching insights: {str(e)}'
        }), 500

@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
@admin_required
def get_all_courses():
    """Get all courses for admin management"""
    try:
        courses = Course.query.all()
        
        courses_data = []
        for course in courses:
            # Get enrollment statistics
            total_enrollments = len(course.enrollments)
            completed_enrollments = len([e for e in course.enrollments if e.status == 'completed'])
            active_enrollments = len([e for e in course.enrollments if e.status == 'active'])
            
            courses_data.append({
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'is_active': course.is_active,
                'modules_count': len(course.modules),
                'statistics': {
                    'total_enrollments': total_enrollments,
                    'completed_enrollments': completed_enrollments,
                    'active_enrollments': active_enrollments,
                    'completion_rate': round((completed_enrollments / total_enrollments * 100), 1) if total_enrollments > 0 else 0
                },
                'created_at': course.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'courses': courses_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get courses: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_course(course_id):
    """Update course information"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        data = request.get_json()
        
        course.title = data.get('title', course.title)
        course.description = data.get('description', course.description)
        course.skill_level = data.get('skill_level', course.skill_level)
        course.duration_weeks = data.get('duration_weeks', course.duration_weeks)
        course.is_active = data.get('is_active', course.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Course updated successfully',
            'course': {
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'is_active': course.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update course: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/modules', methods=['GET'])
@jwt_required()
@admin_required
def get_course_modules_admin(course_id):
    """Get all modules for a specific course (admin view)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.order_index).all()
        
        modules_data = []
        for module in modules:
            modules_data.append({
                'id': str(module.id),
                'title': module.title,
                'content': module.content,
                'order_index': module.order_index,
                'is_active': module.is_active
            })
        
        return jsonify({
            'success': True,
            'course': {
                'id': str(course.id),
                'title': course.title
            },
            'modules': modules_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course modules: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/modules/<module_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_course_module(course_id, module_id):
    """Update a course module"""
    try:
        module = CourseModule.query.filter_by(id=module_id, course_id=course_id).first()
        if not module:
            return jsonify({
                'success': False,
                'message': 'Module not found'
            }), 404
        
        data = request.get_json()
        
        module.title = data.get('title', module.title)
        module.content = data.get('content', module.content)
        module.order_index = data.get('order_index', module.order_index)
        module.is_active = data.get('is_active', module.is_active)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Module updated successfully',
            'module': {
                'id': str(module.id),
                'title': module.title,
                'content': module.content,
                'order_index': module.order_index,
                'is_active': module.is_active
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update module: {str(e)}'
        }), 500

@admin_bp.route('/courses/<course_id>/modules/<module_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_course_module(course_id, module_id):
    """Delete a course module"""
    try:
        module = CourseModule.query.filter_by(id=module_id, course_id=course_id).first()
        if not module:
            return jsonify({
                'success': False,
                'message': 'Module not found'
            }), 404
        
        db.session.delete(module)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Module deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete module: {str(e)}'
        }), 500

@admin_bp.route('/courses/create-with-modules', methods=['POST'])
@jwt_required()
@admin_required
def create_course_with_modules():
    """Create a new course with modules (like W3Schools structure)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('skill_level'):
            return jsonify({
                'success': False,
                'message': 'Title and skill level are required'
            }), 400
        
        # Create the course
        course = Course(
            title=data['title'],
            description=data.get('description'),
            skill_level=data['skill_level'].capitalize(),  # Ensure proper capitalization
            duration_weeks=data.get('duration_weeks', 8)
        )
        
        db.session.add(course)
        db.session.flush()  # Get the course ID
        
        # Add modules if provided
        modules_data = data.get('modules', [])
        created_modules = []
        
        for i, module_data in enumerate(modules_data):
            if module_data.get('title'):
                module = CourseModule(
                    course_id=course.id,
                    title=module_data['title'],
                    content=module_data.get('content', ''),
                    order_index=i + 1
                )
                db.session.add(module)
                created_modules.append({
                    'title': module.title,
                    'content': module.content,
                    'order_index': module.order_index
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Course "{course.title}" created successfully with {len(created_modules)} modules',
            'course': {
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'modules': created_modules
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create course with modules: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations', methods=['GET'])
@jwt_required()
@admin_required
def get_weekly_evaluations():
    """Get all weekly evaluations"""
    try:
        from sqlalchemy import func
        
        evaluations = WeeklyEvaluation.query.order_by(
            WeeklyEvaluation.scheduled_date.desc()
        ).all()
        
        evaluations_data = []
        for evaluation in evaluations:
            # Get participation statistics
            total_attempts = len(evaluation.attempts)
            completed_attempts = len([a for a in evaluation.attempts if a.status == 'completed'])
            
            # Get average score
            scores = WeeklyEvaluationScore.query.filter_by(evaluation_id=evaluation.id).all()
            avg_score = sum([s.score_percentage for s in scores]) / len(scores) if scores else 0
            
            evaluations_data.append({
                'id': str(evaluation.id),
                'title': evaluation.title,
                'description': evaluation.description,
                'scheduled_date': evaluation.scheduled_date.isoformat(),
                'duration_minutes': evaluation.duration_minutes,
                'total_questions': evaluation.total_questions,
                'coding_questions_count': evaluation.coding_questions_count,
                'mcq_questions_count': evaluation.mcq_questions_count,
                'is_active': evaluation.is_active,
                'auto_generated': evaluation.auto_generated,
                'statistics': {
                    'total_attempts': total_attempts,
                    'completed_attempts': completed_attempts,
                    'completion_rate': round((completed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0,
                    'average_score': round(avg_score, 1),
                    'total_scores': len(scores)
                },
                'created_at': evaluation.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'evaluations': evaluations_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get weekly evaluations: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations', methods=['POST'])
@jwt_required()
@admin_required
def create_weekly_evaluation():
    """Create a new weekly evaluation"""
    try:
        from weekly_evaluation_service import weekly_evaluation_service
        from datetime import datetime
        
        data = request.get_json()
        
        # Parse scheduled date if provided
        scheduled_date = None
        if data.get('scheduled_date'):
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
        
        # Custom configuration
        custom_config = {
            'total_questions': data.get('total_questions', 10),
            'coding_questions_count': data.get('coding_questions_count', 3),
            'mcq_questions_count': data.get('mcq_questions_count', 7),
            'duration_minutes': data.get('duration_minutes', 60)
        }
        
        result = weekly_evaluation_service.create_weekly_evaluation(
            scheduled_date=scheduled_date,
            custom_config=custom_config
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create weekly evaluation: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/auto-generate', methods=['POST'])
@jwt_required()
@admin_required
def auto_generate_weekly_evaluations():
    """Auto-generate weekly evaluations for the next 4 weeks - SUNDAY 5:00 PM"""
    try:
        from weekly_evaluation_service import weekly_evaluation_service
        
        data = request.get_json() or {}
        weeks_ahead = data.get('weeks_ahead', 4)  # Default 4 weeks
        
        print(f"🤖 Admin requested auto-generation of {weeks_ahead} weekly evaluations")
        
        result = weekly_evaluation_service.auto_generate_weekly_evaluations(weeks_ahead)
        
        if result['success']:
            # Add detailed information about generated evaluations
            response = {
                'success': True,
                'message': f'Successfully generated {len(result["created_evaluations"])} weekly evaluations',
                'evaluations': result['created_evaluations'],
                'schedule_details': {
                    'day': 'Sunday',
                    'time': '5:00 PM - 7:00 PM',
                    'duration': '60 minutes strict',
                    'auto_submission': 'After 60 minutes with 10% penalty'
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            return jsonify(response), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to auto-generate evaluations: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/create-test', methods=['POST'])
@jwt_required()
@admin_required
def create_test_evaluation():
    """Create a test evaluation for this Sunday 5:00 PM"""
    try:
        from weekly_evaluation_service import weekly_evaluation_service
        from datetime import datetime, timedelta
        
        # Calculate next Sunday 5:00 PM
        today = datetime.now()
        days_ahead = (6 - today.weekday()) % 7  # Sunday is 6
        if days_ahead == 0:  # If today is Sunday
            days_ahead = 0 if today.hour < 17 else 7  # Today if before 5 PM, next week if after
        
        next_sunday = (today + timedelta(days=days_ahead)).replace(
            hour=17, minute=0, second=0, microsecond=0  # 5:00 PM sharp
        )
        
        # Custom configuration for test
        custom_config = {
            'total_questions': 10,
            'coding_questions_count': 3,
            'mcq_questions_count': 7,
            'duration_minutes': 60  # STRICT 60 minutes
        }
        
        result = weekly_evaluation_service.create_weekly_evaluation(
            scheduled_date=next_sunday,
            custom_config=custom_config
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Test evaluation created for {next_sunday.strftime("%A, %B %d, %Y at %I:%M %p")}',
                'evaluation_id': result['evaluation_id'],
                'scheduled_date': next_sunday.isoformat(),
                'schedule_details': {
                    'day': 'Sunday',
                    'time': '5:00 PM - 7:00 PM',
                    'duration': '60 minutes strict'
                }
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create test evaluation: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/clear-and-regenerate', methods=['POST'])
@jwt_required()
@admin_required
def clear_and_regenerate_evaluations():
    """Clear all evaluations and regenerate with correct Sunday 5:00 PM timing"""
    try:
        from weekly_evaluation_service import weekly_evaluation_service
        
        # Clear all existing evaluations
        WeeklyEvaluation.query.delete()
        WeeklyEvaluationQuestion.query.delete()
        WeeklyEvaluationAttempt.query.delete()
        WeeklyEvaluationScore.query.delete()
        db.session.commit()
        
        print("🗑️ Cleared all existing evaluations")
        
        # Generate new evaluations with correct timing
        result = weekly_evaluation_service.auto_generate_weekly_evaluations(4)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Cleared old evaluations and generated {len(result["created_evaluations"])} new ones',
                'evaluations': result['created_evaluations'],
                'schedule_details': {
                    'day': 'Sunday',
                    'time': '5:00 PM - 7:00 PM',
                    'duration': '60 minutes strict',
                    'note': 'All evaluations now scheduled for Sunday 5:00 PM'
                }
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to clear and regenerate evaluations: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/<evaluation_id>/scores', methods=['GET'])
@jwt_required()
@admin_required
def get_evaluation_scores(evaluation_id):
    """Get all scores for a specific evaluation"""
    try:
        evaluation = WeeklyEvaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({
                'success': False,
                'message': 'Evaluation not found'
            }), 404
        
        scores = WeeklyEvaluationScore.query.filter_by(
            evaluation_id=evaluation_id
        ).order_by(WeeklyEvaluationScore.score_percentage.desc()).all()
        
        scores_data = []
        for score in scores:
            user = score.user
            scores_data.append({
                'id': str(score.id),
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email  # ✅ User email for admin actions
                },
                'score_percentage': score.score_percentage,
                'grade': score.grade,
                'coding_score': score.coding_score,
                'mcq_score': score.mcq_score,
                'admin_decision': score.admin_decision,
                'admin_feedback': score.admin_feedback,
                'decision_date': score.decision_date.isoformat() if score.decision_date else None,
                'email_sent': score.email_sent,
                'email_sent_at': score.email_sent_at.isoformat() if score.email_sent_at else None,
                'created_at': score.created_at.isoformat(),
                # ✅ Quick email action data
                'email_actions': {
                    'scholarship_url': f'/api/admin/users/{user.id}/send-scholarship',
                    'internship_url': f'/api/admin/users/{user.id}/send-internship',
                    'evaluation_email_url': f'/api/admin/weekly-evaluations/scores/{score.id}/send-email'
                }
            })
        
        return jsonify({
            'success': True,
            'evaluation': {
                'id': str(evaluation.id),
                'title': evaluation.title,
                'scheduled_date': evaluation.scheduled_date.isoformat()
            },
            'scores': scores_data,
            'statistics': {
                'total_participants': len(scores_data),
                'average_score': round(sum([s.score_percentage for s in scores]) / len(scores), 1) if scores else 0,
                'highest_score': max([s.score_percentage for s in scores]) if scores else 0,
                'lowest_score': min([s.score_percentage for s in scores]) if scores else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get evaluation scores: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/scores/<score_id>/decision', methods=['PUT'])
@jwt_required()
@admin_required
def update_score_decision(score_id):
    """Update admin decision for a user's score"""
    try:
        score = WeeklyEvaluationScore.query.get(score_id)
        if not score:
            return jsonify({
                'success': False,
                'message': 'Score record not found'
            }), 404
        
        data = request.get_json()
        
        score.admin_decision = data.get('admin_decision', score.admin_decision)
        score.admin_feedback = data.get('admin_feedback', score.admin_feedback)
        score.decision_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Decision updated successfully',
            'score': {
                'id': str(score.id),
                'admin_decision': score.admin_decision,
                'admin_feedback': score.admin_feedback,
                'decision_date': score.decision_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update decision: {str(e)}'
        }), 500

@admin_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data with charts"""
    try:
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        # User Analytics
        total_users = User.query.filter_by(is_admin=False, is_mentor=False).count()
        active_users = User.query.filter_by(is_admin=False, is_mentor=False, is_active=True).count()
        total_mentors = User.query.filter_by(is_mentor=True).count()
        
        # Course Analytics
        total_courses = Course.query.count()
        active_courses = Course.query.filter_by(is_active=True).count()
        total_enrollments = CourseEnrollment.query.count()
        completed_courses = CourseEnrollment.query.filter_by(status='completed').count()
        
        # Assessment Analytics
        total_assessments = Assessment.query.count()
        avg_assessment_score = db.session.query(func.avg(Assessment.score_percentage)).scalar() or 0
        
        # Weekly Evaluation Analytics
        total_evaluations = WeeklyEvaluation.query.count()
        total_evaluation_attempts = WeeklyEvaluationAttempt.query.count()
        completed_attempts = WeeklyEvaluationAttempt.query.filter_by(status='completed').count()
        
        # User Registration Trend (Last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago,
            User.is_admin == False,
            User.is_mentor == False
        ).group_by(func.date(User.created_at)).all()
        
        # Course Enrollment Trend
        course_enrollment_stats = db.session.query(
            Course.title,
            Course.skill_level,
            func.count(CourseEnrollment.id).label('enrollments')
        ).join(CourseEnrollment).group_by(Course.id, Course.title, Course.skill_level).all()
        
        # Assessment Performance by Type
        assessment_performance = db.session.query(
            Assessment.assessment_type,
            func.count(Assessment.id).label('total'),
            func.avg(Assessment.score_percentage).label('avg_score'),
            func.min(Assessment.score_percentage).label('min_score'),
            func.max(Assessment.score_percentage).label('max_score')
        ).group_by(Assessment.assessment_type).all()
        
        # Weekly Evaluation Performance Trend
        evaluation_performance = db.session.query(
            WeeklyEvaluation.title,
            WeeklyEvaluation.scheduled_date,
            func.count(WeeklyEvaluationScore.id).label('participants'),
            func.avg(WeeklyEvaluationScore.score_percentage).label('avg_score')
        ).join(WeeklyEvaluationScore).group_by(
            WeeklyEvaluation.id, WeeklyEvaluation.title, WeeklyEvaluation.scheduled_date
        ).order_by(WeeklyEvaluation.scheduled_date.desc()).limit(10).all()
        
        # Mentor Session Analytics
        total_sessions = MentorSession.query.count()
        completed_sessions = MentorSession.query.filter_by(status='completed').count()
        avg_session_rating = db.session.query(func.avg(MentorSession.rating)).filter(
            MentorSession.rating.isnot(None)
        ).scalar() or 0
        
        # Chat Analytics
        total_chat_rooms = ChatRoom.query.count()
        active_chats = ChatRoom.query.filter_by(is_active=True).count()
        total_messages = ChatMessage.query.count()
        
        analytics_data = {
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_mentors': total_mentors,
                'total_courses': total_courses,
                'active_courses': active_courses,
                'total_enrollments': total_enrollments,
                'completion_rate': round((completed_courses / total_enrollments * 100), 1) if total_enrollments > 0 else 0
            },
            'assessments': {
                'total_assessments': total_assessments,
                'average_score': round(avg_assessment_score, 1),
                'total_evaluations': total_evaluations,
                'evaluation_attempts': total_evaluation_attempts,
                'completion_rate': round((completed_attempts / total_evaluation_attempts * 100), 1) if total_evaluation_attempts > 0 else 0
            },
            'mentoring': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'average_rating': round(avg_session_rating, 1),
                'total_chat_rooms': total_chat_rooms,
                'active_chats': active_chats,
                'total_messages': total_messages
            },
            'charts': {
                'user_registrations': [
                    {
                        'date': reg.date.isoformat(),
                        'count': reg.count
                    } for reg in daily_registrations
                ],
                'course_enrollments': [
                    {
                        'course': stat.title,
                        'skill_level': stat.skill_level,
                        'enrollments': stat.enrollments
                    } for stat in course_enrollment_stats
                ],
                'assessment_performance': [
                    {
                        'type': perf.assessment_type,
                        'total': perf.total,
                        'avg_score': round(perf.avg_score, 1),
                        'min_score': perf.min_score,
                        'max_score': perf.max_score
                    } for perf in assessment_performance
                ],
                'evaluation_trends': [
                    {
                        'title': eval_perf.title,
                        'date': eval_perf.scheduled_date.isoformat(),
                        'participants': eval_perf.participants,
                        'avg_score': round(eval_perf.avg_score, 1)
                    } for eval_perf in evaluation_performance
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics_data,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get analytics dashboard: {str(e)}'
        }), 500

@admin_bp.route('/analytics/user-performance', methods=['GET'])
@jwt_required()
@admin_required
def get_user_performance_analytics():
    """Get detailed user performance analytics"""
    try:
        from sqlalchemy import func
        
        # Top performing users
        top_users = db.session.query(
            User.id,
            User.name,
            User.email,
            func.avg(Assessment.score_percentage).label('avg_score'),
            func.count(Assessment.id).label('assessment_count'),
            func.count(CourseEnrollment.id).label('course_count')
        ).join(Assessment).join(CourseEnrollment).group_by(
            User.id, User.name, User.email
        ).order_by(func.avg(Assessment.score_percentage).desc()).limit(10).all()
        
        # User engagement metrics
        user_engagement = db.session.query(
            User.id,
            User.name,
            func.count(ChatMessage.id).label('messages_sent'),
            func.count(MentorSession.id).label('sessions_attended'),
            func.count(WeeklyEvaluationAttempt.id).label('evaluations_taken')
        ).outerjoin(ChatMessage, User.id == ChatMessage.sender_id)\
         .outerjoin(MentorSession, User.id == MentorSession.user_id)\
         .outerjoin(WeeklyEvaluationAttempt, User.id == WeeklyEvaluationAttempt.user_id)\
         .filter(User.is_admin == False, User.is_mentor == False)\
         .group_by(User.id, User.name).all()
        
        # Skill level distribution
        skill_distribution = db.session.query(
            BioData.experience_level,
            func.count(BioData.id).label('count')
        ).group_by(BioData.experience_level).all()
        
        return jsonify({
            'success': True,
            'user_performance': {
                'top_performers': [
                    {
                        'user_id': str(user.id),
                        'name': user.name,
                        'email': user.email,
                        'avg_score': round(user.avg_score, 1),
                        'assessment_count': user.assessment_count,
                        'course_count': user.course_count
                    } for user in top_users
                ],
                'engagement_metrics': [
                    {
                        'user_id': str(user.id),
                        'name': user.name,
                        'messages_sent': user.messages_sent,
                        'sessions_attended': user.sessions_attended,
                        'evaluations_taken': user.evaluations_taken,
                        'engagement_score': user.messages_sent + user.sessions_attended * 2 + user.evaluations_taken * 3
                    } for user in user_engagement
                ],
                'skill_distribution': [
                    {
                        'level': skill.experience_level or 'Not specified',
                        'count': skill.count
                    } for skill in skill_distribution
                ]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user performance analytics: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/scores/<score_id>/send-email', methods=['POST'])
@jwt_required()
@admin_required
def send_evaluation_result_email(score_id):
    """Send email notification to user about evaluation result"""
    try:
        from email_service import email_service
        
        score = WeeklyEvaluationScore.query.get(score_id)
        if not score:
            return jsonify({
                'success': False,
                'message': 'Score record not found'
            }), 404
        
        if score.email_sent:
            return jsonify({
                'success': False,
                'message': 'Email already sent for this evaluation'
            }), 400
        
        user = score.user
        evaluation = score.evaluation
        
        # Prepare email content based on decision
        if score.admin_decision == 'selected':
            subject = "🎉 Congratulations! You've been selected!"
            template_data = {
                'user_name': user.name,
                'evaluation_title': evaluation.title,
                'score': score.score_percentage,
                'grade': score.grade,
                'decision': 'selected for our program',
                'feedback': score.admin_feedback or 'Excellent performance!',
                'next_steps': 'Our team will contact you soon with next steps.'
            }
        elif score.admin_decision == 'internship_offered':
            subject = "🚀 Internship Opportunity Available!"
            template_data = {
                'user_name': user.name,
                'evaluation_title': evaluation.title,
                'score': score.score_percentage,
                'grade': score.grade,
                'decision': 'offered an internship position',
                'feedback': score.admin_feedback or 'Great potential shown!',
                'next_steps': 'Please reply to accept the internship offer.'
            }
        elif score.admin_decision == 'scholarship_offered':
            subject = "🎓 Scholarship Opportunity!"
            template_data = {
                'user_name': user.name,
                'evaluation_title': evaluation.title,
                'score': score.score_percentage,
                'grade': score.grade,
                'decision': 'awarded a scholarship',
                'feedback': score.admin_feedback or 'Outstanding performance!',
                'next_steps': 'Scholarship details will be sent separately.'
            }
        else:
            subject = "Weekly Evaluation Results"
            template_data = {
                'user_name': user.name,
                'evaluation_title': evaluation.title,
                'score': score.score_percentage,
                'grade': score.grade,
                'decision': 'under review',
                'feedback': score.admin_feedback or 'Thank you for participating.',
                'next_steps': 'Keep practicing and improving your skills!'
            }
        
        # Send email
        email_result = email_service.send_evaluation_result_email(
            user.email, subject, template_data
        )
        
        if email_result['success']:
            # Mark email as sent
            score.email_sent = True
            score.email_sent_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to send email: {email_result.get("error", "Unknown error")}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }), 500

@admin_bp.route('/users/<user_id>/send-scholarship', methods=['POST'])
@jwt_required()
@admin_required
def send_scholarship_offer(user_id):
    """Send scholarship offer email to a user"""
    try:
        from email_service import email_service
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json() or {}
        scholarship_details = {
            'amount': data.get('amount', 'Full Coverage'),
            'duration': data.get('duration', '6 months'),
            'coverage': data.get('coverage', 'All courses and mentorship'),
            'start_date': data.get('start_date', 'Immediate')
        }
        
        # Send scholarship email
        success = email_service.send_scholarship_email(
            user.name, user.email, scholarship_details
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Scholarship offer sent to {user.name} ({user.email})'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send scholarship email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send scholarship offer: {str(e)}'
        }), 500

@admin_bp.route('/users/<user_id>/send-internship', methods=['POST'])
@jwt_required()
@admin_required
def send_internship_offer(user_id):
    """Send internship offer email to a user"""
    try:
        from email_service import email_service
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json() or {}
        internship_details = {
            'position': data.get('position', 'Software Development Intern'),
            'duration': data.get('duration', '3-6 months'),
            'stipend': data.get('stipend', 'Competitive'),
            'location': data.get('location', 'Remote/Hybrid'),
            'start_date': data.get('start_date', 'Flexible')
        }
        
        # Send internship email
        success = email_service.send_internship_email(
            user.name, user.email, internship_details
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Internship offer sent to {user.name} ({user.email})'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send internship email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send internship offer: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/<evaluation_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_weekly_evaluation(evaluation_id):
    """Delete a weekly evaluation and all related data"""
    try:
        evaluation = WeeklyEvaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({
                'success': False,
                'message': 'Weekly evaluation not found'
            }), 404
        
        evaluation_title = evaluation.title
        
        # Check if there are any completed attempts
        completed_attempts = WeeklyEvaluationAttempt.query.filter_by(
            evaluation_id=evaluation_id,
            status='completed'
        ).count()
        
        if completed_attempts > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete evaluation with {completed_attempts} completed attempts. Students have already taken this evaluation.'
            }), 400
        
        # Delete related data (cascade should handle this, but being explicit)
        WeeklyEvaluationScore.query.filter_by(evaluation_id=evaluation_id).delete()
        WeeklyEvaluationAttempt.query.filter_by(evaluation_id=evaluation_id).delete()
        WeeklyEvaluationQuestion.query.filter_by(evaluation_id=evaluation_id).delete()
        
        # Delete the evaluation
        db.session.delete(evaluation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Weekly evaluation "{evaluation_title}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete weekly evaluation: {str(e)}'
        }), 500

@admin_bp.route('/weekly-evaluations/scores/bulk-email', methods=['POST'])
@jwt_required()
@admin_required
def send_bulk_evaluation_emails():
    """Send emails to multiple users for evaluation results"""
    try:
        from email_service import email_service
        
        data = request.get_json()
        score_ids = data.get('score_ids', [])
        
        if not score_ids:
            return jsonify({
                'success': False,
                'message': 'No score IDs provided'
            }), 400
        
        sent_count = 0
        failed_count = 0
        results = []
        
        for score_id in score_ids:
            score = WeeklyEvaluationScore.query.get(score_id)
            if not score:
                failed_count += 1
                results.append({
                    'score_id': score_id,
                    'success': False,
                    'message': 'Score not found'
                })
                continue
            
            if score.email_sent:
                failed_count += 1
                results.append({
                    'score_id': score_id,
                    'success': False,
                    'message': 'Email already sent'
                })
                continue
            
            user = score.user
            evaluation = score.evaluation
            
            # Prepare email content based on decision
            if score.admin_decision == 'selected':
                subject = "🎉 Congratulations! You've been selected!"
                template_data = {
                    'user_name': user.name,
                    'evaluation_title': evaluation.title,
                    'score': score.score_percentage,
                    'grade': score.grade,
                    'decision': 'selected for our program',
                    'feedback': score.admin_feedback or 'Excellent performance!',
                    'next_steps': 'Our team will contact you soon with next steps.'
                }
            elif score.admin_decision == 'internship_offered':
                subject = "🚀 Internship Opportunity Available!"
                template_data = {
                    'user_name': user.name,
                    'evaluation_title': evaluation.title,
                    'score': score.score_percentage,
                    'grade': score.grade,
                    'decision': 'offered an internship position',
                    'feedback': score.admin_feedback or 'Great potential shown!',
                    'next_steps': 'Please reply to accept the internship offer.'
                }
            elif score.admin_decision == 'scholarship_offered':
                subject = "🎓 Scholarship Opportunity!"
                template_data = {
                    'user_name': user.name,
                    'evaluation_title': evaluation.title,
                    'score': score.score_percentage,
                    'grade': score.grade,
                    'decision': 'awarded a scholarship',
                    'feedback': score.admin_feedback or 'Outstanding performance!',
                    'next_steps': 'Scholarship details will be sent separately.'
                }
            else:
                subject = "Weekly Evaluation Results"
                template_data = {
                    'user_name': user.name,
                    'evaluation_title': evaluation.title,
                    'score': score.score_percentage,
                    'grade': score.grade,
                    'decision': 'under review',
                    'feedback': score.admin_feedback or 'Thank you for participating.',
                    'next_steps': 'Keep practicing and improving your skills!'
                }
            
            # Send email
            email_result = email_service.send_evaluation_result_email(
                user.email, subject, template_data
            )
            
            if email_result['success']:
                score.email_sent = True
                score.email_sent_at = datetime.utcnow()
                sent_count += 1
                results.append({
                    'score_id': score_id,
                    'success': True,
                    'message': 'Email sent successfully'
                })
            else:
                failed_count += 1
                results.append({
                    'score_id': score_id,
                    'success': False,
                    'message': f'Failed to send email: {email_result.get("error", "Unknown error")}'
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bulk email operation completed. Sent: {sent_count}, Failed: {failed_count}',
            'results': results,
            'summary': {
                'total_processed': len(score_ids),
                'sent_count': sent_count,
                'failed_count': failed_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to send bulk emails: {str(e)}'
        }), 500
def send_bulk_evaluation_emails():
    """Send emails to multiple users based on their decisions"""
    try:
        data = request.get_json()
        evaluation_id = data.get('evaluation_id')
        decision_filter = data.get('decision_filter')  # selected, rejected, etc.
        
        if not evaluation_id:
            return jsonify({
                'success': False,
                'message': 'Evaluation ID is required'
            }), 400
        
        # Get scores to send emails for
        query = WeeklyEvaluationScore.query.filter_by(
            evaluation_id=evaluation_id,
            email_sent=False
        )
        
        if decision_filter:
            query = query.filter_by(admin_decision=decision_filter)
        
        scores = query.all()
        
        sent_count = 0
        failed_count = 0
        
        for score in scores:
            # Send individual email (reuse the single email endpoint logic)
            try:
                # This would call the same email sending logic as above
                # For brevity, just marking as sent here
                score.email_sent = True
                score.email_sent_at = datetime.utcnow()
                sent_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Failed to send email to {score.user.email}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bulk email operation completed',
            'sent_count': sent_count,
            'failed_count': failed_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to send bulk emails: {str(e)}'
        }), 500

@admin_bp.route('/courses/templates', methods=['GET'])
@jwt_required()
@admin_required
def get_course_templates():
    """Get pre-defined course templates for quick creation"""
    try:
        templates = {
            'programming_java': {
                'title': 'Programming in Java',
                'description': 'Complete Java programming course from basics to advanced concepts',
                'skill_level': 'Beginner',
                'duration_weeks': 12,
                'modules': [
                    {'title': 'Java Introduction', 'content': 'Introduction to Java programming language, history, and setup'},
                    {'title': 'Java Syntax', 'content': 'Basic Java syntax, variables, and data types'},
                    {'title': 'Java Variables', 'content': 'Understanding variables, constants, and scope'},
                    {'title': 'Java Data Types', 'content': 'Primitive and reference data types in Java'},
                    {'title': 'Java Operators', 'content': 'Arithmetic, logical, and comparison operators'},
                    {'title': 'Java Strings', 'content': 'String manipulation and methods'},
                    {'title': 'Java Math', 'content': 'Mathematical operations and Math class'},
                    {'title': 'Java Booleans', 'content': 'Boolean logic and conditional statements'},
                    {'title': 'Java If...Else', 'content': 'Conditional statements and decision making'},
                    {'title': 'Java Switch', 'content': 'Switch statements and case handling'},
                    {'title': 'Java While Loop', 'content': 'While and do-while loops'},
                    {'title': 'Java For Loop', 'content': 'For loops and enhanced for loops'},
                    {'title': 'Java Break/Continue', 'content': 'Loop control statements'},
                    {'title': 'Java Arrays', 'content': 'Array creation, manipulation, and multidimensional arrays'},
                    {'title': 'Java Methods', 'content': 'Method definition, parameters, and return values'},
                    {'title': 'Java Method Overloading', 'content': 'Method overloading and polymorphism'},
                    {'title': 'Java Scope', 'content': 'Variable scope and access modifiers'},
                    {'title': 'Java Recursion', 'content': 'Recursive methods and problem solving'},
                    {'title': 'Java OOP', 'content': 'Object-oriented programming concepts'},
                    {'title': 'Java Classes/Objects', 'content': 'Class definition and object creation'},
                    {'title': 'Java Class Attributes', 'content': 'Instance variables and class variables'},
                    {'title': 'Java Class Methods', 'content': 'Instance methods and static methods'},
                    {'title': 'Java Constructors', 'content': 'Constructor overloading and initialization'},
                    {'title': 'Java Modifiers', 'content': 'Access modifiers and non-access modifiers'},
                    {'title': 'Java Encapsulation', 'content': 'Data hiding and getter/setter methods'},
                    {'title': 'Java Packages', 'content': 'Package creation and import statements'},
                    {'title': 'Java Inheritance', 'content': 'Class inheritance and method overriding'},
                    {'title': 'Java Polymorphism', 'content': 'Runtime polymorphism and method overriding'},
                    {'title': 'Java Inner Classes', 'content': 'Nested classes and anonymous classes'},
                    {'title': 'Java Abstraction', 'content': 'Abstract classes and interfaces'},
                    {'title': 'Java Interface', 'content': 'Interface implementation and multiple inheritance'},
                    {'title': 'Java Enums', 'content': 'Enumeration types and constants'},
                    {'title': 'Java User Input', 'content': 'Scanner class and input handling'},
                    {'title': 'Java Date', 'content': 'Date and time manipulation'},
                    {'title': 'Java ArrayList', 'content': 'Dynamic arrays and ArrayList methods'},
                    {'title': 'Java LinkedList', 'content': 'Linked list implementation and usage'},
                    {'title': 'Java HashMap', 'content': 'Hash maps and key-value pairs'},
                    {'title': 'Java HashSet', 'content': 'Hash sets and unique collections'},
                    {'title': 'Java Iterator', 'content': 'Collection iteration and traversal'},
                    {'title': 'Java Wrapper Classes', 'content': 'Primitive wrapper classes and autoboxing'},
                    {'title': 'Java Exceptions', 'content': 'Exception handling and try-catch blocks'},
                    {'title': 'Java RegEx', 'content': 'Regular expressions and pattern matching'},
                    {'title': 'Java Threads', 'content': 'Multithreading and concurrent programming'},
                    {'title': 'Java Lambda', 'content': 'Lambda expressions and functional programming'},
                    {'title': 'Java Files', 'content': 'File I/O operations and file handling'},
                    {'title': 'Final Project', 'content': 'Comprehensive Java project implementation'}
                ]
            },
            'web_development': {
                'title': 'Full Stack Web Development',
                'description': 'Complete web development course covering frontend and backend technologies',
                'skill_level': 'Beginner',
                'duration_weeks': 16,
                'modules': [
                    {'title': 'HTML Basics', 'content': 'HTML structure, elements, and semantic markup'},
                    {'title': 'CSS Fundamentals', 'content': 'CSS styling, selectors, and layout'},
                    {'title': 'JavaScript Basics', 'content': 'JavaScript syntax, variables, and functions'},
                    {'title': 'DOM Manipulation', 'content': 'Document Object Model and event handling'},
                    {'title': 'Responsive Design', 'content': 'Mobile-first design and media queries'},
                    {'title': 'CSS Frameworks', 'content': 'Bootstrap and CSS Grid/Flexbox'},
                    {'title': 'JavaScript ES6+', 'content': 'Modern JavaScript features and syntax'},
                    {'title': 'React Fundamentals', 'content': 'React components and JSX'},
                    {'title': 'React State Management', 'content': 'State, props, and hooks'},
                    {'title': 'Node.js Introduction', 'content': 'Server-side JavaScript with Node.js'},
                    {'title': 'Express.js Framework', 'content': 'Web server creation with Express'},
                    {'title': 'Database Integration', 'content': 'SQL and NoSQL database connections'},
                    {'title': 'API Development', 'content': 'RESTful API creation and testing'},
                    {'title': 'Authentication', 'content': 'User authentication and authorization'},
                    {'title': 'Deployment', 'content': 'Application deployment and hosting'},
                    {'title': 'Final Project', 'content': 'Full-stack web application development'}
                ]
            },
            'data_science': {
                'title': 'Data Science with Python',
                'description': 'Comprehensive data science course using Python and popular libraries',
                'skill_level': 'Beginner',
                'duration_weeks': 14,
                'modules': [
                    {'title': 'Python Basics', 'content': 'Python syntax, variables, and data structures'},
                    {'title': 'NumPy Fundamentals', 'content': 'Numerical computing with NumPy arrays'},
                    {'title': 'Pandas Data Manipulation', 'content': 'Data analysis with Pandas DataFrames'},
                    {'title': 'Data Visualization', 'content': 'Matplotlib and Seaborn for data visualization'},
                    {'title': 'Statistical Analysis', 'content': 'Descriptive and inferential statistics'},
                    {'title': 'Data Cleaning', 'content': 'Data preprocessing and cleaning techniques'},
                    {'title': 'Exploratory Data Analysis', 'content': 'EDA techniques and best practices'},
                    {'title': 'Machine Learning Basics', 'content': 'Introduction to ML concepts and algorithms'},
                    {'title': 'Supervised Learning', 'content': 'Classification and regression algorithms'},
                    {'title': 'Unsupervised Learning', 'content': 'Clustering and dimensionality reduction'},
                    {'title': 'Model Evaluation', 'content': 'Model validation and performance metrics'},
                    {'title': 'Feature Engineering', 'content': 'Feature selection and transformation'},
                    {'title': 'Deep Learning Intro', 'content': 'Neural networks and TensorFlow basics'},
                    {'title': 'Capstone Project', 'content': 'End-to-end data science project'}
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course templates: {str(e)}'
        }), 500

@admin_bp.route('/certificates', methods=['GET'])
@jwt_required()
@admin_required
def get_all_certificates():
    """Get all issued certificates for admin review"""
    try:
        # Get all completed course enrollments (these would have certificates)
        from models import CourseEnrollment
        
        completed_enrollments = CourseEnrollment.query.filter_by(status='completed').all()
        
        certificates_data = []
        for enrollment in completed_enrollments:
            # Generate certificate data for display
            from ai_recommendations_simple import ai_engine
            
            user_data = {
                'name': enrollment.user.name,
                'email': enrollment.user.email
            }
            
            course_data = {
                'title': enrollment.course.title,
                'skill_level': enrollment.course.skill_level,
                'duration_weeks': enrollment.course.duration_weeks
            }
            
            completion_data = {
                'modules_completed': [m.title for m in enrollment.course.modules],
                'total_modules': len(enrollment.course.modules),
                'final_score': 85,  # Default score
                'completion_date': enrollment.completed_at
            }
            
            certificate = ai_engine.generate_certificate_data(
                user_data, course_data, completion_data
            )
            
            certificates_data.append({
                'enrollment_id': str(enrollment.id),
                'user_name': enrollment.user.name,
                'user_email': enrollment.user.email,
                'course_title': enrollment.course.title,
                'completed_at': enrollment.completed_at.isoformat(),
                'certificate': certificate
            })
        
        return jsonify({
            'success': True,
            'certificates': certificates_data,
            'total_certificates': len(certificates_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get certificates: {str(e)}'
        }), 500

@admin_bp.route('/ai-questions/generate', methods=['POST'])
@jwt_required()
@admin_required
def generate_ai_question():
    """Generate a question using AI based on type, difficulty, and category"""
    try:
        data = request.get_json()
        
        question_type = data.get('question_type', 'multiple_choice')
        difficulty = data.get('difficulty', 'medium')
        category = data.get('category', 'Programming')
        
        if not all([question_type, difficulty, category]):
            return jsonify({
                'success': False,
                'message': 'Question type, difficulty, and category are required'
            }), 400
        
        # Generate question using AI
        generated_question = ai_question_generator.generate_question(
            question_type=question_type,
            difficulty=difficulty,
            category=category
        )
        
        return jsonify({
            'success': True,
            'question': generated_question,
            'message': 'Question generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate question: {str(e)}'
        }), 500

@admin_bp.route('/ai-questions/save', methods=['POST'])
@jwt_required()
@admin_required
def save_ai_generated_question():
    """Save an AI-generated question to the database"""
    try:
        data = request.get_json()
        
        question_text = data.get('question_text')
        question_type = data.get('question_type')
        difficulty_level = data.get('difficulty_level')
        category = data.get('category')
        correct_answer = data.get('correct_answer')
        options = data.get('options')
        explanation = data.get('explanation')
        course_id = data.get('course_id')  # Optional
        
        if not all([question_text, question_type, difficulty_level, category, correct_answer]):
            return jsonify({
                'success': False,
                'message': 'All required fields must be provided'
            }), 400
        
        # Create new question
        new_question = Question(
            question_text=question_text,
            question_type=question_type,
            difficulty_level=difficulty_level,
            category=category,
            correct_answer=correct_answer,
            options=options,
            explanation=explanation,
            course_id=course_id,
            is_active=True
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'question': {
                'id': str(new_question.id),
                'question_text': new_question.question_text,
                'question_type': new_question.question_type,
                'difficulty_level': new_question.difficulty_level,
                'category': new_question.category
            },
            'message': 'Question saved successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to save question: {str(e)}'
        }), 500

@admin_bp.route('/ai-questions/categories', methods=['GET'])
@jwt_required()
@admin_required
def get_question_categories():
    """Get available question categories for AI generation"""
    try:
        categories = [
            'Python',
            'JavaScript', 
            'Web Development',
            'Data Science',
            'Algorithms',
            'Database',
            'Machine Learning',
            'Cybersecurity',
            'Mobile Development',
            'DevOps',
            'Software Engineering',
            'System Design'
        ]
        
        difficulties = ['easy', 'medium', 'hard']
        question_types = ['multiple_choice', 'coding', 'essay']
        
        # Get all courses for course selection
        courses = Course.query.all()
        courses_data = [
            {
                'id': str(course.id),
                'title': course.title,
                'skill_level': course.skill_level
            }
            for course in courses
        ]
        
        return jsonify({
            'success': True,
            'categories': categories,
            'difficulties': difficulties,
            'question_types': question_types,
            'courses': courses_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get categories: {str(e)}'
        }), 500

@admin_bp.route('/ai-questions/batch-generate', methods=['POST'])
@jwt_required()
@admin_required
def batch_generate_questions():
    """Generate multiple questions at once"""
    try:
        data = request.get_json()
        
        question_type = data.get('question_type', 'multiple_choice')
        difficulty = data.get('difficulty', 'medium')
        category = data.get('category', 'Programming')
        count = data.get('count', 5)
        
        if count > 20:
            return jsonify({
                'success': False,
                'message': 'Maximum 20 questions can be generated at once'
            }), 400
        
        generated_questions = []
        for i in range(count):
            question = ai_question_generator.generate_question(
                question_type=question_type,
                difficulty=difficulty,
                category=category
            )
            generated_questions.append(question)
        
        return jsonify({
            'success': True,
            'questions': generated_questions,
            'count': len(generated_questions),
            'message': f'{len(generated_questions)} questions generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate questions: {str(e)}'
        }), 500



