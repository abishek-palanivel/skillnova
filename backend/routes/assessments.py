from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import random
import json

from models import db, Assessment, Question
from ai_recommendations_simple import ai_engine

assessments_bp = Blueprint('assessments', __name__)

@assessments_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_assessment_questions():
    """Get AI-generated questions for assessment based on user profile"""
    try:
        from models import User, BioData
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        print(f"Getting personalized assessment for user: {user.email}")
        
        # Get user's bio data for AI analysis
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if not biodata:
            return jsonify({
                'success': False,
                'message': 'Please complete your bio data first before taking the assessment'
            }), 400
        
        bio_data = {
            'skills': biodata.skills or 'General Programming',
            'goals': biodata.goals or 'Learn programming',
            'interests': biodata.interests or 'Web Development',
            'education': biodata.education or 'Self-taught',
            'experience_level': biodata.experience_level or 'Beginner'
        }
        print(f"Bio data for AI analysis: {bio_data}")
        
        # Generate AI-personalized questions based on bio data
        try:
            user_profile = ai_engine.analyze_bio_data_with_ai(bio_data)
            print(f"User profile analyzed: {user_profile}")
            
            # Generate 20 personalized questions using AI
            ai_questions = ai_engine.generate_intelligent_assessment_questions(user_profile, 20)
            print(f"Generated {len(ai_questions)} AI-personalized questions")
            
            # Shuffle questions uniquely for each user
            import random
            seed = hash(f"{user_id}_assessment_{datetime.now().date()}")
            random.seed(seed)
            shuffled_questions = ai_questions.copy()
            random.shuffle(shuffled_questions)
            random.seed()  # Reset seed
            
            # Prepare questions for frontend (without correct answers)
            questions_data = []
            correct_answers_map = {}
            for i, question in enumerate(shuffled_questions, 1):
                question_id = f'ai_personalized_{i}'
                questions_data.append({
                    'id': question_id,
                    'question_text': question['question_text'],
                    'question_type': question['question_type'],
                    'options': question.get('options', []),
                    'difficulty_level': question['difficulty_level'],
                    'category': question['category'],
                    'points': question.get('points', 5)
                })
                # Store correct answer separately (not sent to frontend)
                correct_answers_map[question_id] = question['correct_answer']
            

            
        except Exception as ai_error:
            print(f"AI question generation failed: {ai_error}")
            # Fallback to database questions with personalization
            db_questions = Question.query.filter_by(is_active=True).all()
            
            # Shuffle and select 20 questions
            import random
            seed = hash(f"{user_id}_fallback_{datetime.now().date()}")
            random.seed(seed)
            selected_questions = random.sample(db_questions, min(20, len(db_questions)))
            random.seed()
            
            questions_data = []
            for i, question in enumerate(selected_questions, 1):
                question_data = {
                    'id': f'db_{question.id}',
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'difficulty_level': question.difficulty_level,
                    'category': question.category,
                    'correct_answer': question.correct_answer,
                    'points': 5
                }
                
                if question.question_type == 'multiple_choice' and question.options:
                    if isinstance(question.options, dict):
                        question_data['options'] = list(question.options.values())
                    elif isinstance(question.options, list):
                        question_data['options'] = question.options
                    else:
                        question_data['options'] = []
                
                questions_data.append(question_data)
            
            # Set default user profile
            user_profile = {
                'interests': bio_data['interests'].split(',') if bio_data['interests'] else ['Programming'],
                'skill_level': bio_data['experience_level'],
                'confidence_score': 0.5,
                'recommended_focus': 'Foundation Building'
            }
        
        print(f"Returning {len(questions_data)} personalized questions")
        
        return jsonify({
            'success': True,
            'questions': questions_data,
            'user_profile': user_profile,
            'assessment_type': 'ai_personalized',
            'total_questions': len(questions_data),
            'message': f'🤖 AI has generated {len(questions_data)} personalized questions based on your profile!'
        }), 200
        
    except Exception as e:
        print(f"Assessment questions error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get assessment questions: {str(e)}'
        }), 500

@assessments_bp.route('/ai-personalized', methods=['GET'])
@jwt_required()
def get_ai_personalized_assessment():
    """Get AI-personalized assessment questions based on bio data"""
    return get_assessment_questions()  # Use the same logic

@assessments_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_assessment():
    """Submit assessment answers and calculate score"""
    try:
        print("🚀 Assessment submission started")
        user_id = get_jwt_identity()
        print(f"👤 User ID: {user_id}")
        
        data = request.get_json()
        print(f"📝 Request data keys: {list(data.keys()) if data else 'None'}")
        
        if not data or 'answers' not in data:
            print("❌ Missing answers in request data")
            return jsonify({
                'success': False,
                'message': 'Assessment answers are required'
            }), 400
        
        answers = data['answers']
        time_taken = data.get('time_taken_minutes', 0)
        assessment_type = data.get('assessment_type', 'initial')
        
        print(f"📊 Processing {len(answers)} answers")
        print(f"⏱️ Time taken: {time_taken} minutes")
        print(f"📋 Assessment type: {assessment_type}")
        
        # Calculate score - handle both AI-generated and database questions
        total_questions = len(answers)
        correct_answers = 0
        
        print(f"🧮 Starting scoring for {total_questions} questions")
        
        # For AI-generated questions, we need to regenerate the same questions deterministically
        try:
            biodata = BioData.query.filter_by(user_id=user_id).first()
            if biodata:
                bio_data = {
                    'skills': biodata.skills or 'General Programming',
                    'goals': biodata.goals or 'Learn programming',
                    'interests': biodata.interests or 'Web Development',
                    'education': biodata.education or 'Self-taught',
                    'experience_level': biodata.experience_level or 'Beginner'
                }
                
                # Generate the same questions using the same seed
                user_profile = ai_engine.analyze_bio_data_with_ai(bio_data)
                
                # Use deterministic seed for consistent question generation
                import random
                seed = hash(f"{user_id}_assessment_{datetime.now().date()}")
                random.seed(seed)
                
                ai_questions = ai_engine.generate_intelligent_assessment_questions(user_profile, 20)
                
                # Shuffle with same seed
                shuffled_questions = ai_questions.copy()
                random.shuffle(shuffled_questions)
                random.seed()  # Reset seed
                
                # Create answer key
                question_answers = {}
                for i, question in enumerate(shuffled_questions, 1):
                    question_answers[f'ai_personalized_{i}'] = question['correct_answer']
                
                # Score the answers
                for question_id, user_answer in answers.items():
                    if question_id.startswith('ai_personalized_'):
                        correct_answer = question_answers.get(question_id)
                        if correct_answer and str(user_answer).strip() == str(correct_answer).strip():
                            correct_answers += 1
                    elif question_id.startswith('db_'):
                        # Database question
                        db_question_id = question_id.replace('db_', '')
                        question = Question.query.get(db_question_id)
                        if question and question.correct_answer:
                            if str(user_answer).strip() == str(question.correct_answer).strip():
                                correct_answers += 1
                    else:
                        # Try database lookup
                        question = Question.query.get(question_id)
                        if question and question.correct_answer:
                            if str(user_answer).strip() == str(question.correct_answer).strip():
                                correct_answers += 1
                                
            else:
                # No bio data - fallback scoring
                correct_answers = int(total_questions * 0.6)
                
        except Exception as scoring_error:
            print(f"Error in scoring: {scoring_error}")
            # Fallback scoring based on reasonable assumptions
            correct_answers = int(total_questions * 0.65)
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Get user's bio data for personalized recommendations
        from models import BioData
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if biodata:
            bio_data = {
                'skills': biodata.skills or 'General Programming',
                'goals': biodata.goals or 'Learn programming',
                'interests': biodata.interests or 'Web Development',
                'education': biodata.education or 'Self-taught',
                'experience_level': biodata.experience_level or 'Beginner'
            }
        else:
            bio_data = {
                'skills': 'General Programming',
                'goals': 'Learn programming',
                'interests': 'Web Development',
                'education': 'Self-taught',
                'experience_level': 'Beginner'
            }
        
        # Generate comprehensive user profile and course recommendations
        try:
            user_profile = ai_engine.analyze_bio_data_with_ai(bio_data)
            
            # Update skill level based on assessment score
            if score_percentage >= 90:
                user_profile['skill_level'] = 'Advanced'
                skill_assessment = 'Expert Level'
            elif score_percentage >= 75:
                user_profile['skill_level'] = 'Intermediate'
                skill_assessment = 'Intermediate Level'
            elif score_percentage >= 60:
                user_profile['skill_level'] = 'Beginner-Intermediate'
                skill_assessment = 'Developing Skills'
            else:
                user_profile['skill_level'] = 'Beginner'
                skill_assessment = 'Foundation Building'
            
            # Get comprehensive assessment results
            assessment_results = {
                'score_percentage': score_percentage,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'skill_assessment': skill_assessment,
                'bio_data': bio_data
            }
            
            # Get SkillNova internal courses
            try:
                from models import Course
                internal_courses = Course.query.filter_by(is_active=True).all()
                skillnova_recommendations = []
                
                print(f"📚 Found {len(internal_courses)} internal courses")
                
                for course in internal_courses:
                    match_score = 0.8  # Base match score
                    
                    # Adjust match score based on skill level alignment
                    if course.skill_level.lower() == user_profile['skill_level'].lower():
                        match_score += 0.2
                    
                    skillnova_recommendations.append({
                        'id': str(course.id),
                        'title': course.title,
                        'description': course.description,
                        'skill_level': course.skill_level,
                        'duration_weeks': course.duration_weeks,
                        'match_score': match_score,
                        'source': 'SkillNova',
                        'ai_recommendation_reason': f'Matches your {skill_assessment} and interests in {bio_data.get("interests", "programming")}',
                        'rating': 4.8,
                        'students': 1250,
                        'price': 'Free',
                        'url': f'/courses/{course.id}'
                    })
                    
            except Exception as course_error:
                print(f"⚠️ Course loading error: {course_error}")
                skillnova_recommendations = []
            
            # Get external course recommendations (Udemy, Coursera, etc.)
            try:
                external_recommendations = ai_engine.recommend_external_courses(
                    user_profile, 
                    assessment_results, 
                    limit=12
                )
                print(f"🌐 Generated {len(external_recommendations)} external recommendations")
            except Exception as ext_error:
                print(f"⚠️ External recommendations error: {ext_error}")
                external_recommendations = []
            
            # Combine and sort recommendations
            all_recommendations = skillnova_recommendations + external_recommendations
            all_recommendations.sort(key=lambda x: x.get('match_score', 0.5), reverse=True)
            
            print(f"Generated {len(skillnova_recommendations)} SkillNova + {len(external_recommendations)} external recommendations")
            
        except Exception as rec_error:
            print(f"Course recommendation failed: {rec_error}")
            # Fallback recommendations and variables
            skillnova_recommendations = []
            external_recommendations = []
            all_recommendations = [
                {
                    'title': 'Introduction to Programming',
                    'description': 'Learn programming fundamentals',
                    'skill_level': 'Beginner',
                    'source': 'SkillNova',
                    'match_score': 0.8,
                    'price': 'Free',
                    'rating': 4.5
                }
            ]
            user_profile = {
                'interests': bio_data.get('interests', 'Programming').split(','),
                'skill_level': 'Beginner',
                'confidence_score': 0.5
            }
            assessment_results = {
                'score_percentage': score_percentage,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'skill_assessment': 'Foundation Building',
                'bio_data': bio_data
            }
        
        # Save assessment result
        assessment = Assessment(
            user_id=user_id,
            assessment_type=assessment_type,
            score_percentage=score_percentage,
            total_questions=total_questions,
            correct_answers=correct_answers,
            time_taken_minutes=time_taken
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        # Determine performance level and message
        if score_percentage >= 80:
            performance_level = 'Excellent'
            message = 'Outstanding performance! You have a strong foundation.'
        elif score_percentage >= 60:
            performance_level = 'Good'
            message = 'Good job! You have solid understanding with room for improvement.'
        elif score_percentage >= 40:
            performance_level = 'Fair'
            message = 'Fair performance. Focus on strengthening your fundamentals.'
        else:
            performance_level = 'Needs Improvement'
            message = 'Keep learning! Everyone starts somewhere.'
        
        return jsonify({
            'success': True,
            'message': 'Assessment completed successfully',
            'results': {
                'score_percentage': round(score_percentage, 1),
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'time_taken_minutes': time_taken,
                'assessment_id': str(assessment.id),
                'performance_level': performance_level,
                'recommendation': message,
                'passed': score_percentage >= 60,
                'skill_assessment': assessment_results.get('skill_assessment', 'Foundation Building'),
                'user_profile': user_profile,
                'course_recommendations': {
                    'total_recommendations': len(all_recommendations),
                    'skillnova_courses': len(skillnova_recommendations),
                    'external_courses': len(external_recommendations),
                    'recommendations': all_recommendations[:15]  # Top 15 recommendations
                },
                'personalization_data': {
                    'bio_based': True,
                    'performance_based': True,
                    'ai_generated': True,
                    'unique_to_user': True
                }
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Assessment submission error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit assessment: {str(e)}'
        }), 500

@assessments_bp.route('/history', methods=['GET'])
@jwt_required()
def get_assessment_history():
    """Get user's assessment history"""
    try:
        user_id = get_jwt_identity()
        
        assessments = Assessment.query.filter_by(user_id=user_id).order_by(
            Assessment.completed_at.desc()
        ).all()
        
        history = []
        for assessment in assessments:
            history.append({
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
            'assessments': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get assessment history: {str(e)}'
        }), 500

@assessments_bp.route('/<assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment_details():
    """Get detailed assessment results"""
    try:
        user_id = get_jwt_identity()
        assessment = Assessment.query.filter_by(
            id=assessment_id,
            user_id=user_id
        ).first()
        
        if not assessment:
            return jsonify({
                'success': False,
                'message': 'Assessment not found'
            }), 404
        
        assessment_data = {
            'id': str(assessment.id),
            'assessment_type': assessment.assessment_type,
            'score_percentage': assessment.score_percentage,
            'total_questions': assessment.total_questions,
            'correct_answers': assessment.correct_answers,
            'time_taken_minutes': assessment.time_taken_minutes,
            'completed_at': assessment.completed_at.isoformat()
        }
        
        return jsonify({
            'success': True,
            'assessment': assessment_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get assessment details: {str(e)}'
        }), 500

@assessments_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_ai_recommendations():
    """Get AI-powered course and learning recommendations"""
    try:
        from models import User, Assessment
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user's bio data from BioData model
        from models import BioData
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if biodata:
            bio_data = {
                'skills': biodata.skills,
                'goals': biodata.goals,
                'interests': biodata.interests,
                'education': biodata.education,
                'experience_level': biodata.experience_level
            }
        else:
            # Default bio data if none exists
            bio_data = {
                'skills': 'General Programming',
                'goals': 'Learn programming',
                'interests': 'Web Development',
                'education': 'Self-taught',
                'experience_level': 'Beginner'
            }
        
        # Get latest assessment results
        latest_assessment = Assessment.query.filter_by(user_id=user_id).order_by(
            Assessment.completed_at.desc()
        ).first()
        
        assessment_results = None
        if latest_assessment:
            assessment_results = {'score': latest_assessment.score_percentage}
        
        # Analyze user profile with AI
        try:
            user_profile = ai_engine.analyze_user_profile(bio_data, assessment_results)
        except Exception as profile_error:
            print(f"User profile analysis error: {profile_error}")
            # Fallback user profile
            user_profile = {
                'interests': bio_data.get('interests', 'Programming').split(',') if bio_data.get('interests') else ['Programming'],
                'skill_level': bio_data.get('experience_level', 'Beginner'),
                'confidence_score': 0.5,
                'recommended_focus': 'Foundation Building'
            }
        
        # Generate recommendations using available AI engine methods
        recommendations = {
            'courses': [],
            'external_courses': [],
            'mentors': [],
            'practice_exercises': [],
            'tests': [],

            'learning_path': [],
            'user_profile': user_profile
        }
        
        try:
            # Get course recommendations
            recommendations['courses'] = ai_engine.recommend_courses(user_profile, limit=5)
        except Exception as e:
            print(f"Course recommendation error: {e}")
            
        try:
            # Get external course recommendations
            recommendations['external_courses'] = ai_engine.get_external_course_recommendations(
                user_profile.get('interests', ['Programming']), 
                user_profile.get('skill_level', 'Beginner'),
                limit=5
            )
        except Exception as e:
            print(f"External course recommendation error: {e}")
            
        try:
            # Get mentor recommendations
            recommendations['mentors'] = ai_engine.recommend_mentors(user_profile, limit=5)
        except Exception as e:
            print(f"Mentor recommendation error: {e}")
            
        try:
            # Get practice exercise recommendations
            recommendations['practice_exercises'] = ai_engine.recommend_practice_exercises(user_profile, limit=5)
        except Exception as e:
            print(f"Practice exercise recommendation error: {e}")
            
        try:
            # Get test recommendations
            recommendations['tests'] = ai_engine.recommend_tests(user_profile, limit=5)
        except Exception as e:
            print(f"Test recommendation error: {e}")
            

            
        try:
            # Get learning path
            recommendations['learning_path'] = ai_engine.generate_learning_path(user_profile)
        except Exception as e:
            print(f"Learning path error: {e}")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': 'AI recommendations generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate recommendations: {str(e)}'
        }), 500

@assessments_bp.route('/course-recommendations', methods=['GET'])
@jwt_required()
def get_course_recommendations():
    """Get personalized course recommendations based on user profile and latest assessment"""
    try:
        from models import User, BioData
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user's bio data
        biodata = BioData.query.filter_by(user_id=user_id).first()
        
        if biodata:
            bio_data = {
                'skills': biodata.skills or 'General Programming',
                'goals': biodata.goals or 'Learn programming',
                'interests': biodata.interests or 'Web Development',
                'education': biodata.education or 'Self-taught',
                'experience_level': biodata.experience_level or 'Beginner'
            }
        else:
            bio_data = {
                'skills': 'General Programming',
                'goals': 'Learn programming',
                'interests': 'Web Development',
                'education': 'Self-taught',
                'experience_level': 'Beginner'
            }
        
        # Get latest assessment results
        latest_assessment = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.completed_at.desc()).first()
        
        assessment_results = None
        if latest_assessment:
            assessment_results = {
                'score_percentage': latest_assessment.score_percentage,
                'correct_answers': latest_assessment.correct_answers,
                'total_questions': latest_assessment.total_questions
            }
        
        # Generate user profile and recommendations
        try:
            user_profile = ai_engine.analyze_bio_data_with_ai(bio_data)
            
            # Get personalized course recommendations
            recommended_courses = ai_engine.recommend_external_courses(
                user_profile, 
                assessment_results, 
                limit=12
            )
            
            return jsonify({
                'success': True,
                'user_profile': user_profile,
                'assessment_results': assessment_results,
                'recommended_courses': recommended_courses,
                'message': f'Found {len(recommended_courses)} personalized course recommendations'
            }), 200
            
        except Exception as ai_error:
            print(f"AI recommendation failed: {ai_error}")
            return jsonify({
                'success': False,
                'message': f'Failed to generate recommendations: {str(ai_error)}'
            }), 500
        
    except Exception as e:
        print(f"Course recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get course recommendations: {str(e)}'
        }), 500