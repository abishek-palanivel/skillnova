from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, BioData, Question, Course, Assessment, TestResult
from ai_recommendations_simple import ai_engine
import random

user_bp = Blueprint('user', __name__)

@user_bp.route('/biodata', methods=['POST'])
@jwt_required()
def submit_biodata():
    """Submit or update user bio data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Bio data is required'
            }), 400
        
        # Check if bio data already exists
        existing_biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if existing_biodata:
            # Update existing bio data
            existing_biodata.education = data.get('education', existing_biodata.education)
            existing_biodata.skills = data.get('skills', existing_biodata.skills)
            existing_biodata.goals = data.get('goals', existing_biodata.goals)
            existing_biodata.interests = data.get('interests', existing_biodata.interests)
            existing_biodata.linkedin_url = data.get('linkedin_url', existing_biodata.linkedin_url)
            existing_biodata.experience_level = data.get('experience_level', existing_biodata.experience_level)
            existing_biodata.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Bio data updated successfully',
                'biodata': {
                    'id': str(existing_biodata.id),
                    'education': existing_biodata.education,
                    'skills': existing_biodata.skills,
                    'goals': existing_biodata.goals,
                    'interests': existing_biodata.interests,
                    'linkedin_url': existing_biodata.linkedin_url,
                    'experience_level': existing_biodata.experience_level,
                    'updated_at': existing_biodata.updated_at.isoformat()
                }
            }), 200
        else:
            # Create new bio data
            new_biodata = BioData(
                user_id=user_id,
                education=data.get('education'),
                skills=data.get('skills'),
                goals=data.get('goals'),
                interests=data.get('interests'),
                linkedin_url=data.get('linkedin_url'),
                experience_level=data.get('experience_level')
            )
            
            db.session.add(new_biodata)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Bio data submitted successfully',
                'biodata': {
                    'id': str(new_biodata.id),
                    'education': new_biodata.education,
                    'skills': new_biodata.skills,
                    'goals': new_biodata.goals,
                    'interests': new_biodata.interests,
                    'linkedin_url': new_biodata.linkedin_url,
                    'experience_level': new_biodata.experience_level,
                    'created_at': new_biodata.created_at.isoformat()
                }
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit bio data: {str(e)}'
        }), 500

@user_bp.route('/biodata', methods=['GET'])
@jwt_required()
def get_biodata():
    """Get user bio data"""
    try:
        user_id = get_jwt_identity()
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            return jsonify({
                'success': False,
                'message': 'Bio data not found'
            }), 404
        
        return jsonify({
            'success': True,
            'biodata': {
                'id': str(biodata.id),
                'education': biodata.education,
                'skills': biodata.skills,
                'goals': biodata.goals,
                'interests': biodata.interests,
                'linkedin_url': biodata.linkedin_url,
                'experience_level': biodata.experience_level,
                'created_at': biodata.created_at.isoformat(),
                'updated_at': biodata.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get bio data: {str(e)}'
        }), 500

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get user dashboard data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user's progress data
        biodata = BioData.query.filter_by(user_id=user_id).first()
        enrollments = user.enrollments
        assessments = user.assessments

        
        # Calculate progress statistics
        total_courses = len(enrollments)
        completed_courses = len([e for e in enrollments if e.status == 'completed'])
        total_assessments = len(assessments)
        avg_score = sum([a.score_percentage for a in assessments]) / total_assessments if total_assessments > 0 else 0
        
        dashboard_data = {
            'user': {
                'name': user.name,
                'email': user.email,
                'member_since': user.created_at.isoformat()
            },
            'progress': {
                'bio_data_completed': biodata is not None,
                'total_courses': total_courses,
                'completed_courses': completed_courses,
                'total_assessments': total_assessments,
                'average_score': round(avg_score, 2),
                'has_outcome': False
            },
            'recent_activities': []
        }
        
        # Add recent activities - get all activities and sort by date
        activities = []
        
        # Add assessments
        for assessment in assessments:
            activities.append({
                'type': 'assessment',
                'description': f'Completed {assessment.assessment_type} assessment with {assessment.score_percentage}% score',
                'score': assessment.score_percentage,
                'date': assessment.completed_at,
                'date_iso': assessment.completed_at.isoformat()
            })
        
        # Add enrollments
        for enrollment in enrollments:
            activities.append({
                'type': 'enrollment',
                'description': f'Enrolled in {enrollment.course.title}',
                'progress': enrollment.progress_percentage,
                'date': enrollment.enrolled_at,
                'date_iso': enrollment.enrolled_at.isoformat()
            })
        
        # Add test results
        from models import TestResult
        test_results = TestResult.query.filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).limit(5).all()
        for test in test_results:
            activities.append({
                'type': 'test',
                'description': f'Completed test with {test.score_percentage}% score',
                'score': test.score_percentage,
                'date': test.completed_at,
                'date_iso': test.completed_at.isoformat()
            })
        
        # Add mentor sessions
        from models import MentorSession
        sessions = MentorSession.query.filter_by(user_id=user_id).order_by(MentorSession.created_at.desc()).limit(5).all()
        for session in sessions:
            activities.append({
                'type': 'session',
                'description': f'Booked session with mentor',
                'status': session.status,
                'date': session.created_at,
                'date_iso': session.created_at.isoformat()
            })
        
        # Sort by date and get latest 10
        activities.sort(key=lambda x: x['date'], reverse=True)
        dashboard_data['recent_activities'] = [
            {
                'description': activity['description'],
                'date': activity['date_iso'],
                'type': activity['type']
            }
            for activity in activities[:10]
        ]
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get dashboard: {str(e)}'
        }), 500

@user_bp.route('/recommendations/courses', methods=['GET', 'OPTIONS'])
def get_course_recommendations():
    """Get AI-powered course recommendations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Apply JWT validation for non-OPTIONS requests
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()
    
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            # Provide default recommendations for users without bio data
            default_profile = {
                'interests': ['web_development'],
                'skill_level': 'beginner',
                'profile_completeness': 0
            }
            recommendations = ai_engine.recommend_courses(default_profile, limit=6)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'message': 'Complete your bio data for personalized recommendations',
                'user_profile': default_profile
            }), 200
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores if available
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
        
        # Analyze user profile
        user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        
        # Get course recommendations
        recommendations = ai_engine.recommend_courses(user_profile, limit=8)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course recommendations: {str(e)}'
        }), 500

@user_bp.route('/recommendations/mentors', methods=['GET', 'OPTIONS'])
def get_mentor_recommendations():
    """Get AI-powered mentor recommendations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Apply JWT validation for non-OPTIONS requests
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()
    
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            # Provide default recommendations for users without bio data
            default_profile = {
                'interests': ['web_development'],
                'skill_level': 'beginner',
                'profile_completeness': 0
            }
            recommendations = ai_engine.recommend_mentors(default_profile, limit=6)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'message': 'Complete your bio data for personalized recommendations',
                'user_profile': default_profile
            }), 200
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores if available
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
        
        # Analyze user profile
        user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        
        # Get mentor recommendations
        recommendations = ai_engine.recommend_mentors(user_profile, limit=6)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get mentor recommendations: {str(e)}'
        }), 500

@user_bp.route('/recommendations/practice', methods=['GET', 'OPTIONS'])
def get_practice_recommendations():
    """Get AI-powered practice exercise recommendations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Apply JWT validation for non-OPTIONS requests
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()
    
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            # Provide default recommendations for users without bio data
            default_profile = {
                'interests': ['web_development'],
                'skill_level': 'beginner',
                'profile_completeness': 0
            }
            recommendations = ai_engine.recommend_practice_exercises(default_profile, limit=6)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'message': 'Complete your bio data for personalized recommendations',
                'user_profile': default_profile
            }), 200
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores if available
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
        
        # Analyze user profile
        user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        
        # Get practice recommendations
        recommendations = ai_engine.recommend_practice_exercises(user_profile, limit=6)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get practice recommendations: {str(e)}'
        }), 500

@user_bp.route('/assessments', methods=['GET'])
@jwt_required()
def get_user_assessments():
    """Get user's assessment history"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        assessments = []
        for assessment in user.assessments:
            assessments.append({
                'id': str(assessment.id),
                'assessment_type': assessment.assessment_type,
                'score_percentage': assessment.score_percentage,
                'total_questions': assessment.total_questions,
                'correct_answers': assessment.correct_answers,
                'time_taken_minutes': assessment.time_taken_minutes,
                'completed_at': assessment.completed_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'assessments': assessments
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get assessments: {str(e)}'
        }), 500

@user_bp.route('/recommendations/tests', methods=['GET', 'OPTIONS'])
def get_test_recommendations():
    """Get AI-powered test recommendations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # Apply JWT validation for non-OPTIONS requests
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
        biodata = BioData.query.filter_by(user_id=user_id).first()
    except Exception as auth_error:
        return jsonify({
            'success': False,
            'message': f'Authentication error: {str(auth_error)}'
        }), 401
    
    try:
        
        if not biodata:
            # Provide default recommendations for users without bio data
            default_profile = {
                'interests': ['Web Development'],  # Use proper format
                'skill_level': 'Beginner',  # Use proper capitalization
                'profile_completeness': 0
            }
            recommendations = ai_engine.recommend_tests(default_profile, limit=6)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'message': 'Complete your bio data for personalized recommendations',
                'user_profile': default_profile
            }), 200
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores if available
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
        
        # Analyze user profile
        try:
            user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        except Exception as e:
            print(f"Error analyzing user profile: {e}")
            # Fallback profile
            user_profile = {
                'interests': ['Web Development'],
                'skill_level': 'Beginner'
            }
        
        # Get test recommendations
        recommendations = ai_engine.recommend_tests(user_profile, limit=6)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get test recommendations: {str(e)}'
        }), 500



@user_bp.route('/recommendations/learning-path', methods=['GET'])
@jwt_required()
def get_learning_path():
    """Get AI-generated personalized learning path"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            return jsonify({
                'success': False,
                'message': 'Please complete your bio data first to get your learning path'
            }), 400
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores if available
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else None
        
        # Analyze user profile
        user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        
        # Generate learning path
        learning_path = ai_engine.generate_learning_path(user_profile)
        
        return jsonify({
            'success': True,
            'learning_path': learning_path,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate learning path: {str(e)}'
        }), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile with bio data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        profile_data = {
            'name': user.name,
            'email': user.email,
            'bio_data': {
                'education': biodata.education if biodata else '',
                'skills': biodata.skills if biodata else '',
                'goals': biodata.goals if biodata else '',
                'interests': biodata.interests if biodata else '',
                'linkedin_url': biodata.linkedin_url if biodata else '',
                'experience_level': biodata.experience_level if biodata else 'Beginner'
            }
        }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get profile: {str(e)}'
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update user basic info
        if 'name' in data:
            user.name = data['name']
        
        # Update or create bio data
        biodata = BioData.query.filter_by(user_id=user_id).first()
        bio_data_info = data.get('bio_data', {})
        
        if biodata:
            # Update existing bio data
            biodata.education = bio_data_info.get('education', biodata.education)
            biodata.skills = bio_data_info.get('skills', biodata.skills)
            biodata.goals = bio_data_info.get('goals', biodata.goals)
            biodata.interests = bio_data_info.get('interests', biodata.interests)
            biodata.linkedin_url = bio_data_info.get('linkedin_url', biodata.linkedin_url)
            biodata.experience_level = bio_data_info.get('experience_level', biodata.experience_level)
            biodata.updated_at = datetime.utcnow()
        else:
            # Create new bio data
            biodata = BioData(
                user_id=user_id,
                education=bio_data_info.get('education'),
                skills=bio_data_info.get('skills'),
                goals=bio_data_info.get('goals'),
                interests=bio_data_info.get('interests'),
                linkedin_url=bio_data_info.get('linkedin_url'),
                experience_level=bio_data_info.get('experience_level', 'Beginner')
            )
            db.session.add(biodata)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'name': user.name,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update profile: {str(e)}'
        }), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Calculate statistics
        enrollments = user.enrollments
        assessments = user.assessments
        
        courses_enrolled = len(enrollments)
        courses_completed = len([e for e in enrollments if e.status == 'completed'])
        assessments_taken = len(assessments)
        average_score = sum([a.score_percentage for a in assessments]) / assessments_taken if assessments_taken > 0 else 0
        
        stats = {
            'courses_enrolled': courses_enrolled,
            'courses_completed': courses_completed,
            'assessments_taken': assessments_taken,
            'average_score': round(average_score, 1)
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user stats: {str(e)}'
        }), 500

@user_bp.route('/career-predictions', methods=['GET'])
@jwt_required()
def get_career_predictions():
    """Get AI career predictions for user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            return jsonify({
                'success': False,
                'message': 'Please complete your bio data first to get career predictions'
            }), 400
        
        # Prepare user profile for AI analysis
        bio_dict = {
            'skills': biodata.skills,
            'goals': biodata.goals,
            'interests': biodata.interests,
            'education': biodata.education,
            'experience_level': biodata.experience_level
        }
        
        # Get assessment scores and course progress
        assessment_scores = [a.score_percentage for a in user.assessments] if user.assessments else []
        course_progress = sum([e.progress_percentage for e in user.enrollments]) / len(user.enrollments) if user.enrollments else 0
        
        # Analyze user profile
        user_profile = ai_engine.analyze_user_profile(bio_dict, assessment_scores)
        
        # Get learning recommendations
        predictions = ai_engine.get_learning_recommendations(user_profile, course_progress, assessment_scores)
        
        return jsonify({
            'success': True,
            'predictions': predictions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get career predictions: {str(e)}'
        }), 500

@user_bp.route('/questions/practice', methods=['GET'])
@jwt_required()
def get_practice_questions():
    """Get practice questions for users"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        category = request.args.get('category', '')
        difficulty = request.args.get('difficulty', '')
        question_type = request.args.get('type', '')
        limit = request.args.get('limit', 10, type=int)
        
        # Build query
        query = Question.query.filter_by(is_active=True)
        
        if category:
            query = query.filter(Question.category.ilike(f'%{category}%'))
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty.lower())
        if question_type:
            query = query.filter_by(question_type=question_type.lower())
        
        # Get questions and randomize
        questions = query.all()
        if len(questions) > limit:
            questions = random.sample(questions, limit)
        
        questions_data = []
        for question in questions:
            questions_data.append({
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'options': question.options,
                'explanation': question.explanation,
                'created_at': question.created_at.isoformat() if question.created_at else None
            })
        
        return jsonify({
            'success': True,
            'questions': questions_data,
            'count': len(questions_data),
            'filters': {
                'category': category,
                'difficulty': difficulty,
                'type': question_type
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get practice questions: {str(e)}'
        }), 500

@user_bp.route('/questions/categories', methods=['GET'])
@jwt_required()
def get_question_categories_user():
    """Get available question categories for users"""
    try:
        # Get unique categories from existing questions
        categories = db.session.query(Question.category).filter_by(is_active=True).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # Get unique difficulties
        difficulties = db.session.query(Question.difficulty_level).filter_by(is_active=True).distinct().all()
        difficulties = [diff[0] for diff in difficulties if diff[0]]
        
        # Get unique question types
        question_types = db.session.query(Question.question_type).filter_by(is_active=True).distinct().all()
        question_types = [qtype[0] for qtype in question_types if qtype[0]]
        
        return jsonify({
            'success': True,
            'categories': sorted(categories),
            'difficulties': sorted(difficulties),
            'question_types': sorted(question_types)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get categories: {str(e)}'
        }), 500

@user_bp.route('/questions/<question_id>/answer', methods=['POST'])
@jwt_required()
def submit_question_answer():
    """Submit answer for a practice question"""
    try:
        user_id = get_jwt_identity()
        question_id = request.view_args['question_id']
        data = request.get_json()
        
        user_answer = data.get('answer')
        if not user_answer:
            return jsonify({
                'success': False,
                'message': 'Answer is required'
            }), 400
        
        # Get the question
        question = Question.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
        
        # Check if answer is correct
        is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
        
        # For multiple choice, also check exact match
        if question.question_type == 'multiple_choice':
            is_correct = str(user_answer).strip().upper() == str(question.correct_answer).strip().upper()
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'user_answer': user_answer
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit answer: {str(e)}'
        }), 500

@user_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by name or email"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': True,
                'users': []
            }), 200
        
        # Search users by name or email (exclude current user and admins)
        users = User.query.filter(
            User.id != current_user_id,
            User.is_active == True,
            db.or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'is_mentor': user.is_mentor,
                'is_admin': user.is_admin
            })
        
        return jsonify({
            'success': True,
            'users': users_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to search users: {str(e)}'
        }), 500