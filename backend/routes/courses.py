from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import func

from models import db, Course, CourseEnrollment, CourseModule, Assessment, CourseRating

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET', 'OPTIONS'])
def get_courses():
    """Get all available courses - Public endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        courses = Course.query.filter_by(is_active=True).all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'modules_count': len(course.modules),
                'cost': float(course.cost) if course.cost else 0.0,
                'is_locked': course.is_locked or False,
                # Keep rating for backward compatibility
                'average_rating': course.average_rating or 0.0,
                'total_ratings': course.total_ratings or 0,
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

@courses_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_course_recommendations():
    """Get personalized course recommendations based on assessment scores"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's latest assessment score
        latest_assessment = Assessment.query.filter_by(
            user_id=user_id,
            assessment_type='initial'
        ).order_by(Assessment.completed_at.desc()).first()
        
        if not latest_assessment:
            return jsonify({
                'success': False,
                'message': 'Please complete the initial assessment first'
            }), 400
        
        score = latest_assessment.score_percentage
        
        # Determine skill level based on score
        if score < 50:
            skill_level = 'Beginner'
        elif score < 80:
            skill_level = 'Intermediate'
        else:
            skill_level = 'Advanced'
        
        # Get recommended courses
        recommended_courses = Course.query.filter_by(
            skill_level=skill_level,
            is_active=True
        ).all()
        
        recommendations = []
        for course in recommended_courses:
            recommendations.append({
                'id': str(course.id),
                'title': course.title,
                'description': course.description,
                'skill_level': course.skill_level,
                'duration_weeks': course.duration_weeks,
                'modules_count': len(course.modules),
                'recommendation_reason': f'Based on your assessment score of {score}%, this {skill_level.lower()} level course is perfect for you.'
            })
        
        return jsonify({
            'success': True,
            'assessment_score': score,
            'recommended_level': skill_level,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get recommendations: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course(course_id):
    """Enroll user in a specific course"""
    try:
        user_id = get_jwt_identity()
        
        # Check if course exists
        course = Course.query.get(course_id)
        if not course or not course.is_active:
            return jsonify({
                'success': False,
                'message': 'Course not found or inactive'
            }), 404
        
        # Check if user is already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({
                'success': False,
                'message': 'You are already enrolled in this course'
            }), 409
        
        # Create enrollment
        enrollment = CourseEnrollment(
            user_id=user_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully enrolled in {course.title}',
            'enrollment': {
                'id': str(enrollment.id),
                'course_title': course.title,
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'status': enrollment.status,
                'progress_percentage': enrollment.progress_percentage
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Enrollment failed: {str(e)}'
        }), 500

@courses_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_course():
    """Enroll user in a course"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('course_id'):
            return jsonify({
                'success': False,
                'message': 'Course ID is required'
            }), 400
        
        course_id = data['course_id']
        
        # Check if course exists
        course = Course.query.get(course_id)
        if not course or not course.is_active:
            return jsonify({
                'success': False,
                'message': 'Course not found or inactive'
            }), 404
        
        # Check if user is already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({
                'success': False,
                'message': 'You are already enrolled in this course'
            }), 409
        
        # Create enrollment
        enrollment = CourseEnrollment(
            user_id=user_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully enrolled in {course.title}',
            'enrollment': {
                'id': str(enrollment.id),
                'course_title': course.title,
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'status': enrollment.status,
                'progress_percentage': enrollment.progress_percentage
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Enrollment failed: {str(e)}'
        }), 500

@courses_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """Get user's enrolled courses"""
    try:
        user_id = get_jwt_identity()
        print(f"🔍 Getting courses for user {user_id}")
        
        enrollments = CourseEnrollment.query.filter_by(user_id=user_id).all()
        print(f"📝 Found {len(enrollments)} enrollments")
        
        my_courses = []
        for enrollment in enrollments:
            course = enrollment.course
            course_data = {
                'enrollment_id': str(enrollment.id),
                'course': {
                    'id': str(course.id),
                    'title': course.title,
                    'description': course.description,
                    'skill_level': course.skill_level,
                    'duration_weeks': course.duration_weeks
                },
                'enrolled_at': enrollment.enrolled_at.isoformat(),
                'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                'progress_percentage': enrollment.progress_percentage,
                'status': enrollment.status
            }
            my_courses.append(course_data)
            print(f"📚 Course: {course.title} (ID: {course.id})")
        
        return jsonify({
            'success': True,
            'my_courses': my_courses,
            'total_enrollments': len(my_courses)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting my courses: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get enrolled courses: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/modules', methods=['GET'])
@jwt_required()
def get_course_modules(course_id):
    """Get modules for a specific course"""
    try:
        user_id = get_jwt_identity()
        print(f"🔍 Getting modules for course {course_id}, user {user_id}")
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        print(f"📝 Enrollment found: {enrollment is not None}")
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 403
        
        # Get course modules
        modules = CourseModule.query.filter_by(
            course_id=course_id,
            is_active=True
        ).order_by(CourseModule.order_index).all()
        
        print(f"📚 Found {len(modules)} modules for course")
        
        modules_data = []
        for module in modules:
            modules_data.append({
                'id': str(module.id),
                'title': module.title,
                'content': module.content,
                'order_index': module.order_index
            })
        
        return jsonify({
            'success': True,
            'course_id': course_id,
            'modules': modules_data,
            'total_modules': len(modules_data)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting modules: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get course modules: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/progress', methods=['PUT'])
@jwt_required()
def update_course_progress(course_id):
    """Update course progress"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'progress_percentage' not in data:
            return jsonify({
                'success': False,
                'message': 'Progress percentage is required'
            }), 400
        
        progress_percentage = data['progress_percentage']
        
        # Validate progress percentage
        if not 0 <= progress_percentage <= 100:
            return jsonify({
                'success': False,
                'message': 'Progress percentage must be between 0 and 100'
            }), 400
        
        # Get enrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'Enrollment not found'
            }), 404
        
        # Update progress
        enrollment.progress_percentage = progress_percentage
        
        # Mark as completed if 100%
        if progress_percentage == 100:
            enrollment.status = 'completed'
            enrollment.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully',
            'enrollment': {
                'progress_percentage': enrollment.progress_percentage,
                'status': enrollment.status,
                'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update progress: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>', methods=['GET'])
def get_course_by_id(course_id):
    """Get specific course details by ID - Public endpoint"""
    try:
        course = Course.query.get(course_id)
        if not course or not course.is_active:
            return jsonify({
                'success': False,
                'message': 'Course not found or inactive'
            }), 404
        
        course_data = {
            'id': str(course.id),
            'title': course.title,
            'description': course.description,
            'skill_level': course.skill_level,
            'duration_weeks': course.duration_weeks,
            'modules_count': len(course.modules),
            'cost': float(course.cost) if course.cost else 0.0,
            'is_locked': course.is_locked or False,
            'created_at': course.created_at.isoformat()
        }
        
        return jsonify({
            'success': True,
            'course': course_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/modules/<module_id>/complete', methods=['POST'])
@jwt_required()
def complete_module(course_id, module_id):
    """Mark a module as completed"""
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
        
        # Verify module exists and belongs to the course
        module = CourseModule.query.filter_by(
            id=module_id,
            course_id=course_id,
            is_active=True
        ).first()
        
        if not module:
            return jsonify({
                'success': False,
                'message': 'Module not found'
            }), 404
        
        # Get all modules for the course to calculate progress
        all_modules = CourseModule.query.filter_by(
            course_id=course_id,
            is_active=True
        ).all()
        
        # For simplicity, we'll track completed modules in the enrollment record
        # In a production system, you'd have a separate ModuleCompletion table
        
        # Calculate new progress (assuming this module is now completed)
        total_modules = len(all_modules)
        # This is a simplified approach - in production, track individual module completions
        current_progress = enrollment.progress_percentage
        progress_per_module = 100.0 / total_modules if total_modules > 0 else 0
        new_progress = min(current_progress + progress_per_module, 100.0)
        
        # Update enrollment progress
        enrollment.progress_percentage = new_progress
        
        # Check if course is now completed
        certificate_data = None
        if new_progress >= 100.0:
            enrollment.status = 'completed'
            enrollment.completed_at = datetime.utcnow()
            
            # Generate AI certificate for course completion
            try:
                from certificate_service import CertificateGenerator
                from models import User, Certificate
                
                user = User.query.get(user_id)
                course = Course.query.get(course_id)
                
                # Check if certificate already exists
                existing_cert = Certificate.query.filter_by(
                    user_id=user_id,
                    course_id=course_id
                ).first()
                
                if not existing_cert:
                    # Generate AI certificate
                    cert_generator = CertificateGenerator()
                    
                    cert_result = cert_generator.generate_certificate(
                        user_name=user.name,
                        course_title=course.title,
                        final_score=85.0,  # Default score for course completion
                        completion_date=datetime.utcnow()
                    )
                    
                    # Save certificate to database
                    certificate = Certificate(
                        user_id=user_id,
                        course_id=course_id,
                        certificate_number=cert_result['certificate_number'],
                        final_score=85.0,
                        certificate_data=cert_result['certificate_data'],
                        pdf_path=cert_result['pdf_path']
                    )
                    db.session.add(certificate)
                    
                    certificate_data = {
                        'certificate_number': cert_result['certificate_number'],
                        'download_url': f'/api/tests/certificates/download/{cert_result["certificate_number"]}',
                        'issued_date': datetime.utcnow().isoformat()
                    }
                    
                    print(f"Certificate generated for course completion: {cert_result['certificate_number']}")
                
            except Exception as cert_error:
                print(f"Certificate generation error: {cert_error}")
                # Don't fail the module completion if certificate generation fails
        
        db.session.commit()
        
        response_data = {
            'success': True,
            'message': f'Module "{module.title}" completed successfully',
            'progress': {
                'percentage': round(new_progress, 1),
                'completed_modules': int(new_progress / progress_per_module) if progress_per_module > 0 else 0,
                'total_modules': total_modules
            }
        }
        
        if certificate_data:
            response_data['certificate'] = certificate_data
            response_data['message'] += '. Congratulations! You have completed the course and earned a certificate!'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to complete module: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/learning-path', methods=['GET'])
@jwt_required()
def get_course_learning_path(course_id):
    """Get AI-generated learning path for a course"""
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
        
        # Add user progress information
        learning_path['user_progress'] = {
            'enrollment_date': enrollment.enrolled_at.isoformat(),
            'progress_percentage': enrollment.progress_percentage,
            'status': enrollment.status,
            'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None
        }
        
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

@courses_bp.route('/<course_id>/certificate', methods=['GET'])
@jwt_required()
def get_course_certificate(course_id):
    """Get certificate for completed course"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user completed the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id,
            status='completed'
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'Course not completed or enrollment not found'
            }), 404
        
        # Generate certificate data
        from ai_recommendations_simple import ai_engine
        from models import User
        
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return jsonify({
                'success': False,
                'message': 'User or course not found'
            }), 404
        
        # Get course modules
        modules = CourseModule.query.filter_by(
            course_id=course_id,
            is_active=True
        ).all()
        
        user_data = {
            'name': user.name,
            'email': user.email
        }
        
        course_data = {
            'title': course.title,
            'skill_level': course.skill_level,
            'duration_weeks': course.duration_weeks
        }
        
        completion_data = {
            'modules_completed': [m.title for m in modules],
            'total_modules': len(modules),
            'final_score': 85,  # In production, calculate from actual assessments
            'completion_date': enrollment.completed_at
        }
        
        certificate_data = ai_engine.generate_certificate_data(
            user_data, course_data, completion_data
        )
        
        return jsonify({
            'success': True,
            'certificate': certificate_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get certificate: {str(e)}'
        }), 500

@courses_bp.route('/ai-recommendations', methods=['GET'])
@jwt_required()
def get_ai_course_recommendations():
    """Get AI-powered course recommendations based on user profile and performance"""
    try:
        user_id = get_jwt_identity()
        
        # Get all available courses (now only Java)
        courses = Course.query.all()
        
        # Get user's enrollments
        enrollments = CourseEnrollment.query.filter_by(user_id=user_id).all()
        enrolled_course_ids = [str(e.course_id) for e in enrollments]
        
        # Create simple recommendations for Java programming
        recommendations = {
            'courses': [],
            'next_steps': [],
            'skill_gaps': []
        }
        
        for course in courses:
            if str(course.id) not in enrolled_course_ids:
                # Recommend unenrolled courses
                recommendations['courses'].append({
                    'id': str(course.id),
                    'title': course.title,
                    'description': course.description,
                    'skill_level': course.skill_level,
                    'duration_weeks': course.duration_weeks,
                    'reason': 'Perfect for mastering Java programming fundamentals',
                    'confidence': 0.95
                })
            else:
                # Suggest next steps for enrolled courses
                enrollment = next(e for e in enrollments if str(e.course_id) == str(course.id))
                if enrollment.progress_percentage < 100:
                    recommendations['next_steps'].append({
                        'course_id': str(course.id),
                        'course_title': course.title,
                        'current_progress': enrollment.progress_percentage,
                        'suggestion': 'Continue with your Java learning journey',
                        'next_module': 'Next available module'
                    })
        
        # Add skill development suggestions
        recommendations['skill_gaps'] = [
            {
                'skill': 'Object-Oriented Programming',
                'importance': 'High',
                'description': 'Master OOP concepts in Java for better code structure'
            },
            {
                'skill': 'Data Structures & Algorithms',
                'importance': 'High', 
                'description': 'Essential for technical interviews and efficient coding'
            },
            {
                'skill': 'Exception Handling',
                'importance': 'Medium',
                'description': 'Learn to handle errors gracefully in Java applications'
            }
        ]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': 'Java programming recommendations generated successfully'
        }), 200
        
    except Exception as e:
        print(f"AI Recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get AI recommendations: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/rate', methods=['POST'])
@jwt_required()
def rate_course(course_id):
    """Rate a course (1-5 stars)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        rating_value = data.get('rating')
        review = data.get('review', '')
        
        # Validate rating
        if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({
                'success': False,
                'message': 'Rating must be between 1 and 5'
            }), 400
        
        # Check if course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Check if user already rated this course
        existing_rating = CourseRating.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            existing_rating.review = review
            existing_rating.updated_at = datetime.utcnow()
        else:
            # Create new rating
            new_rating = CourseRating(
                course_id=course_id,
                user_id=user_id,
                rating=rating_value,
                review=review
            )
            db.session.add(new_rating)
        
        # Recalculate course average rating
        avg_rating = db.session.query(func.avg(CourseRating.rating)).filter_by(course_id=course_id).scalar()
        total_ratings = CourseRating.query.filter_by(course_id=course_id).count()
        
        course.average_rating = float(avg_rating) if avg_rating else 0.0
        course.total_ratings = total_ratings
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully',
            'average_rating': course.average_rating,
            'total_ratings': course.total_ratings,
            'user_rating': rating_value
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit rating: {str(e)}'
        }), 500

@courses_bp.route('/<course_id>/rating', methods=['GET'])
def get_course_rating(course_id):
    """Get course rating information"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Get user's rating if authenticated
        user_rating = 0
        try:
            user_id = get_jwt_identity()
            user_rating_obj = CourseRating.query.filter_by(
                user_id=user_id,
                course_id=course_id
            ).first()
            if user_rating_obj:
                user_rating = user_rating_obj.rating
        except:
            pass  # User not authenticated
        
        return jsonify({
            'success': True,
            'average_rating': course.average_rating or 0.0,
            'total_ratings': course.total_ratings or 0,
            'user_rating': user_rating
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get rating: {str(e)}'
        }), 500
