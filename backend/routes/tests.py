from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os

from models import db, Assessment, TestResult, Question, User, UserTestAttempt, Certificate, Course
tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/initial-assessment', methods=['GET'])
@jwt_required()
def get_initial_assessment():
    """Get initial assessment questions"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user has already taken initial assessment
        existing_assessment = Assessment.query.filter_by(
            user_id=user_id,
            assessment_type='initial'
        ).first()
        
        if existing_assessment:
            return jsonify({
                'success': False,
                'message': 'You have already completed the initial assessment',
                'existing_score': existing_assessment.score_percentage
            }), 409
        
        # Get assessment questions (mix of difficulties)
        easy_questions = Question.query.filter_by(
            is_active=True,
            difficulty_level='easy'
        ).limit(5).all()
        
        medium_questions = Question.query.filter_by(
            is_active=True,
            difficulty_level='medium'
        ).limit(10).all()
        
        hard_questions = Question.query.filter_by(
            is_active=True,
            difficulty_level='hard'
        ).limit(5).all()
        
        all_questions = easy_questions + medium_questions + hard_questions
        
        # If no questions found, get any available questions
        if not all_questions:
            all_questions = Question.query.filter_by(is_active=True).limit(20).all()
        
        assessment_questions = []
        for i, question in enumerate(all_questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                # Convert options from dict format to array format for frontend
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            assessment_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'assessment': {
                'type': 'initial',
                'total_questions': len(assessment_questions),
                'time_limit_minutes': 60,
                'questions': assessment_questions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get initial assessment: {str(e)}'
        }), 500

@tests_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_test():
    """Submit test answers and calculate score"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('test_type') or not data.get('answers'):
            return jsonify({
                'success': False,
                'message': 'Test type and answers are required'
            }), 400
        
        test_type = data['test_type']
        answers = data['answers']  # List of {question_id, answer}
        time_taken = data.get('time_taken_minutes', 0)
        
        # Calculate score
        total_questions = len(answers)
        correct_answers = 0
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            user_answer = answer_data.get('answer', '').strip()
            
            question = Question.query.get(question_id)
            if question and question.correct_answer:
                if question.question_type == 'multiple_choice':
                    if user_answer.lower() == question.correct_answer.strip().lower():
                        correct_answers += 1
                # For other question types, we'd need more sophisticated evaluation
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Save assessment result
        if test_type in ['initial', 'module', 'final']:
            assessment = Assessment(
                user_id=user_id,
                assessment_type=test_type,
                score_percentage=score_percentage,
                total_questions=total_questions,
                correct_answers=correct_answers,
                time_taken_minutes=time_taken
            )
            db.session.add(assessment)
        
        # Save detailed test result
        test_result = TestResult(
            user_id=user_id,
            test_type=test_type,
            score_percentage=score_percentage,
            answers=answers
        )
        db.session.add(test_result)
        
        # Generate AI recommendations based on assessment results
        try:
            from ai_recommendations_simple import ai_engine
            from models import BioData
            
            # Get user's bio data for AI analysis
            biodata = BioData.query.filter_by(user_id=user_id).first()
            
            if biodata:
                bio_data = {
                    'skills': biodata.skills,
                    'goals': biodata.goals,
                    'interests': biodata.interests,
                    'education': biodata.education,
                    'experience_level': biodata.experience_level
                }
                
                # Analyze user profile with assessment results
                user_profile = ai_engine.analyze_bio_data_with_ai(bio_data)
                
                # Get AI course recommendations based on performance
                ai_recommendations = ai_engine.recommend_courses_ai(user_profile, score_percentage, limit=5)
                
            else:
                ai_recommendations = []
                
        except Exception as e:
            print(f"AI recommendation error: {e}")
            ai_recommendations = []
        
        # Handle certificate generation - 60% PASS RATE FOR FINAL TESTS
        certificate_data = None
        if test_type in ['course_final', 'final'] and score_percentage >= 60:
            try:
                from certificate_service import CertificateGenerator
                from models import User, Course, Certificate, CourseEnrollment
                
                user = User.query.get(user_id)
                course = Course.query.get(course_id) if course_id else None
                
                if user and course:
                    # Check if user has completed all modules
                    enrollment = CourseEnrollment.query.filter_by(
                        user_id=user_id,
                        course_id=course_id
                    ).first()
                    
                    # Generate certificate if: 60%+ score (relaxed requirement)
                    can_generate_certificate = score_percentage >= 60
                    
                    if can_generate_certificate:
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
                                final_score=score_percentage,
                                completion_date=datetime.utcnow()
                            )
                            
                            # Save certificate to database
                            certificate = Certificate(
                                user_id=user_id,
                                course_id=course_id,
                                certificate_number=cert_result['certificate_number'],
                                final_score=score_percentage,
                                certificate_data=cert_result['certificate_data'],
                                pdf_path=cert_result['pdf_path']
                            )
                            db.session.add(certificate)
                            
                            # Mark course as completed if enrollment exists
                            if enrollment:
                                enrollment.status = 'completed'
                                enrollment.completed_at = datetime.utcnow()
                                enrollment.progress_percentage = 100
                            
                            certificate_data = {
                                'certificate_number': cert_result['certificate_number'],
                                'download_url': f'/api/tests/certificates/download/{cert_result["certificate_number"]}',
                                'issued_date': datetime.utcnow().isoformat(),
                                'course_title': course.title,
                                'final_score': score_percentage
                            }
                            
                            print(f"🎓 Certificate generated for course completion: {cert_result['certificate_number']}")
                        else:
                            certificate_data = {
                                'certificate_number': existing_cert.certificate_number,
                                'download_url': f'/api/tests/certificates/download/{existing_cert.certificate_number}',
                                'issued_date': existing_cert.issued_at.isoformat(),
                                'course_title': course.title,
                                'final_score': existing_cert.final_score,
                                'already_issued': True
                            }
                
            except Exception as cert_error:
                print(f"Certificate generation error: {cert_error}")
                # Don't fail the test submission if certificate generation fails
        
        db.session.commit()
        
        # Update course progress for module tests - only if passed with 60%+
        if test_type == 'module' and data.get('module_id') and score_percentage >= 60:
            try:
                from models import CourseModule, CourseEnrollment
                module = CourseModule.query.get(data['module_id'])
                if module:
                    enrollment = CourseEnrollment.query.filter_by(
                        user_id=user_id,
                        course_id=module.course_id
                    ).first()
                    
                    if enrollment:
                        # Mark module as completed and update progress
                        total_modules = CourseModule.query.filter_by(course_id=module.course_id).count()
                        progress_increment = 100 / total_modules if total_modules > 0 else 0
                        new_progress = min(100, enrollment.progress_percentage + progress_increment)
                        enrollment.progress_percentage = new_progress
                        
                        # If all modules completed, mark course as ready for final test
                        if new_progress >= 100:
                            enrollment.status = 'ready_for_final'
                        
                        print(f"📈 Module {module.title} completed! Course progress: {new_progress}%")
                        
            except Exception as e:
                print(f"Error updating course progress: {e}")
        
        # Determine performance level and recommendations (60% pass requirement)
        passed = score_percentage >= 60
        
        if score_percentage >= 90:
            performance_level = "Excellent"
            recommendation = "Outstanding! You're ready for advanced courses and career opportunities!"
        elif score_percentage >= 80:
            performance_level = "Very Good"
            recommendation = "Great job! You're well-prepared for advanced learning and specialization."
        elif score_percentage >= 70:
            performance_level = "Good"
            recommendation = "Good performance! Consider intermediate to advanced courses."
        elif score_percentage >= 60:
            performance_level = "Pass"
            recommendation = "You passed! Focus on strengthening your skills with recommended courses."
        else:
            performance_level = "Needs Improvement"
            recommendation = "Below passing score. Start with beginner courses to build your foundation."
        
        response_data = {
            'success': True,
            'message': 'Test submitted successfully',
            'results': {
                'test_type': test_type,
                'score_percentage': round(score_percentage, 2),
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'time_taken_minutes': time_taken,
                'performance_level': performance_level,
                'recommendation': recommendation,
                'passed': passed,
                'pass_threshold': 60,
                'completed_at': datetime.utcnow().isoformat(),
                'ai_course_recommendations': ai_recommendations
            }
        }
        
        # Add certificate data if generated
        if certificate_data:
            response_data['certificate'] = certificate_data
            if not certificate_data.get('already_issued'):
                response_data['message'] = '🎉 Congratulations! You passed the course and earned a certificate!'
            else:
                response_data['message'] = 'Test completed! Your certificate is already available for download.'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit test: {str(e)}'
        }), 500

@tests_bp.route('/certificates/download/<certificate_number>', methods=['GET'])
@jwt_required()
def download_certificate(certificate_number):
    """Download certificate PDF"""
    try:
        user_id = get_jwt_identity()
        
        # Find certificate
        certificate = Certificate.query.filter_by(
            certificate_number=certificate_number,
            user_id=user_id
        ).first()
        
        if not certificate:
            return jsonify({
                'success': False,
                'message': 'Certificate not found or access denied'
            }), 404
        
        # Check if PDF file exists
        if not certificate.pdf_path or not os.path.exists(certificate.pdf_path):
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

@tests_bp.route('/certificates', methods=['GET'])
@jwt_required()
def get_user_certificates():
    """Get all certificates for the current user"""
    try:
        user_id = get_jwt_identity()
        
        certificates = Certificate.query.filter_by(user_id=user_id).all()
        
        certificates_data = []
        for cert in certificates:
            certificates_data.append({
                'id': str(cert.id),
                'certificate_number': cert.certificate_number,
                'course_title': cert.course.title if cert.course else 'Unknown Course',
                'final_score': cert.final_score,
                'issued_at': cert.issued_at.isoformat(),
                'download_url': f'/api/tests/certificates/download/{cert.certificate_number}'
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

@tests_bp.route('/module-test/<module_id>', methods=['GET'])
@jwt_required()
def get_module_test(module_id):
    """Get 5 shuffled test questions for a specific module with MCQ auto-progression"""
    try:
        user_id = get_jwt_identity()
        
        # Get the module and its course to find relevant questions
        from models import CourseModule
        module = CourseModule.query.get(module_id)
        
        if not module:
            return jsonify({
                'success': False,
                'message': 'Module not found'
            }), 404
        
        # Get questions specific to this course first, then general questions
        course_questions = Question.query.filter_by(
            course_id=module.course_id,
            is_active=True
        ).all()
        
        # If no course-specific questions, get general questions
        if not course_questions:
            course_questions = Question.query.filter_by(is_active=True).all()
        
        if not course_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for this module'
            }), 404
        
        # Shuffle questions uniquely for each user - 5 questions for module test
        import random
        seed = hash(f"{user_id}_{module_id}_{datetime.utcnow().date()}")
        random.seed(seed)
        shuffled_questions = random.sample(course_questions, min(5, len(course_questions)))
        random.seed()  # Reset seed
        
        test_questions = []
        for i, question in enumerate(shuffled_questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                # Convert options from dict format to array format for frontend
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            test_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'test': {
                'test_title': f'{module.course.title} - {module.title} Assessment',
                'type': 'module',
                'module_id': module_id,
                'course_id': str(module.course_id),
                'course_title': module.course.title,
                'total_questions': len(test_questions),
                'duration_minutes': 30,
                'questions': test_questions,
                'attempt_id': f'module_{module_id}_{user_id}_{int(datetime.utcnow().timestamp())}',
                'mcq_auto_progression': True,  # Enable MCQ auto-progression
                'pass_threshold': 60,
                'note': '📝 MCQ: Select option to auto-advance to next question'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get module test: {str(e)}'
        }), 500

@tests_bp.route('/course-assessment/<course_id>', methods=['GET'])
@jwt_required()
def get_course_assessment(course_id):
    """Get comprehensive assessment for a specific course"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is enrolled in the course
        from models import CourseEnrollment
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
        
        # Get course-specific questions
        course_questions = Question.query.filter_by(
            course_id=course_id,
            is_active=True
        ).all()
        
        # If no course-specific questions, get questions by category matching course title
        if not course_questions:
            course_questions = Question.query.filter(
                Question.category.ilike(f'%{course.title}%'),
                Question.is_active == True
            ).all()
        
        # If still no questions, get general questions
        if not course_questions:
            course_questions = Question.query.filter_by(is_active=True).limit(15).all()
        
        if not course_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for this course assessment'
            }), 404
        
        # Select questions with balanced difficulty
        import random
        easy_questions = [q for q in course_questions if q.difficulty_level == 'easy']
        medium_questions = [q for q in course_questions if q.difficulty_level == 'medium']
        hard_questions = [q for q in course_questions if q.difficulty_level == 'hard']
        
        # Aim for 5 easy, 7 medium, 3 hard (15 total)
        selected_questions = []
        selected_questions.extend(random.sample(easy_questions, min(5, len(easy_questions))))
        selected_questions.extend(random.sample(medium_questions, min(7, len(medium_questions))))
        selected_questions.extend(random.sample(hard_questions, min(3, len(hard_questions))))
        
        # If we don't have enough, fill with remaining questions
        remaining_needed = 15 - len(selected_questions)
        if remaining_needed > 0:
            remaining_questions = [q for q in course_questions if q not in selected_questions]
            selected_questions.extend(random.sample(remaining_questions, min(remaining_needed, len(remaining_questions))))
        
        # Shuffle the final selection
        random.shuffle(selected_questions)
        
        test_questions = []
        for i, question in enumerate(selected_questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            test_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'assessment': {
                'title': f'{course.title} - Comprehensive Assessment',
                'type': 'course_final',
                'course_id': course_id,
                'course_title': course.title,
                'total_questions': len(test_questions),
                'duration_minutes': 90,
                'passing_score': 75,
                'questions': test_questions,
                'attempt_id': f'course_{course_id}_{user_id}_{int(datetime.utcnow().timestamp())}',
                'certificate_eligible': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course assessment: {str(e)}'
        }), 500

@tests_bp.route('/final-assessment', methods=['GET'])
@jwt_required()
def get_final_assessment():
    """Get final comprehensive assessment with 15 shuffled questions"""
    try:
        user_id = get_jwt_identity()
        
        # Check if user has completed courses
        user = User.query.get(user_id)
        completed_courses = [e for e in user.enrollments if e.status == 'completed']
        
        if not completed_courses:
            return jsonify({
                'success': False,
                'message': 'Please complete at least one course before taking the final assessment'
            }), 400
        
        # Get comprehensive questions from all difficulty levels
        all_questions = Question.query.filter_by(is_active=True).all()
        
        if not all_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for final assessment'
            }), 404
        
        # Shuffle questions uniquely for each user - 15 questions for final assessment
        import random
        seed = hash(f"{user_id}_final_assessment_{datetime.utcnow().date()}")
        random.seed(seed)
        shuffled_questions = random.sample(all_questions, min(15, len(all_questions)))
        random.seed()  # Reset seed
        
        assessment_questions = []
        for i, question in enumerate(shuffled_questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                # Convert options from dict format to array format for frontend
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            assessment_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'assessment': {
                'test_title': 'Final Assessment',
                'type': 'final',
                'total_questions': len(assessment_questions),
                'duration_minutes': 90,
                'questions': assessment_questions,
                'attempt_id': f'final_assessment_{user_id}_{int(datetime.utcnow().timestamp())}',
                'note': 'This is your final comprehensive assessment. Achieve 100% for an AI-generated certificate!'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get final assessment: {str(e)}'
        }), 500

@tests_bp.route('/history', methods=['GET'])
@jwt_required()
def get_test_history():
    """Get user's test history"""
    try:
        user_id = get_jwt_identity()
        
        # Get assessments
        assessments = Assessment.query.filter_by(user_id=user_id).order_by(
            Assessment.completed_at.desc()
        ).all()
        
        # Get test results
        test_results = TestResult.query.filter_by(user_id=user_id).order_by(
            TestResult.completed_at.desc()
        ).all()
        
        history = []
        
        # Add assessments to history
        for assessment in assessments:
            history.append({
                'type': 'assessment',
                'assessment_type': assessment.assessment_type,
                'score_percentage': assessment.score_percentage,
                'correct_answers': assessment.correct_answers,
                'total_questions': assessment.total_questions,
                'time_taken_minutes': assessment.time_taken_minutes,
                'completed_at': assessment.completed_at.isoformat()
            })
        
        # Add other test results to history
        for result in test_results:
            if result.test_type not in ['initial', 'module', 'final']:
                history.append({
                    'type': 'test',
                    'test_type': result.test_type,
                    'score_percentage': result.score_percentage,
                    'completed_at': result.completed_at.isoformat()
                })
        
        # Sort by completion date
        history.sort(key=lambda x: x['completed_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'test_history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get test history: {str(e)}'
        }), 500

# New Test Management Endpoints

@tests_bp.route('/module/start', methods=['POST'])
@jwt_required()
def start_module_test():
    """Start a new module test with 5 shuffled questions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        module_id = data.get('module_id')
        
        print(f"Starting module test: user_id={user_id}, module_id={module_id}")
        
        if not module_id:
            return jsonify({
                'success': False,
                'message': 'Module ID is required'
            }), 400
        
        # Get available questions for the test
        all_questions = Question.query.filter_by(is_active=True).all()
        
        if not all_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for this module'
            }), 404
        
        # Shuffle questions uniquely for each user
        import random
        seed = hash(f"{user_id}_{module_id}_{datetime.utcnow().date()}")
        random.seed(seed)
        shuffled_questions = random.sample(all_questions, min(5, len(all_questions)))
        random.seed()  # Reset seed
        
        # Prepare questions for frontend
        question_data = []
        for i, question in enumerate(shuffled_questions, 1):
            q_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                if isinstance(question.options, dict):
                    q_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    q_data['options'] = question.options
                else:
                    q_data['options'] = []
            
            question_data.append(q_data)
        
        # Create test attempt record
        attempt = UserTestAttempt(
            user_id=user_id,
            test_id=module_id,
            test_type='module',
            questions_order=[str(q.id) for q in shuffled_questions],
            status='in_progress'
        )
        db.session.add(attempt)
        db.session.commit()
        
        test_response = {
            'attempt_id': str(attempt.id),
            'test_title': f'Module Test - {module_id}',
            'duration_minutes': 30,
            'total_questions': len(question_data),
            'questions': question_data,
            'status': 'started'
        }
        
        return jsonify({
            'success': True,
            'test': test_response
        }), 200
        
    except Exception as e:
        print(f"Module test start error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to start module test: {str(e)}'
        }), 400

@tests_bp.route('/final/start', methods=['POST'])
@jwt_required()
def start_final_test():
    """Start a new final test with 15 shuffled questions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({
                'success': False,
                'message': 'Course ID is required'
            }), 400
        
        # Get available questions for the final test
        all_questions = Question.query.filter_by(is_active=True).all()
        
        if not all_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for final test'
            }), 404
        
        # Shuffle questions uniquely for each user - 15 questions for final test
        import random
        seed = hash(f"{user_id}_final_{course_id}_{datetime.utcnow().date()}")
        random.seed(seed)
        shuffled_questions = random.sample(all_questions, min(15, len(all_questions)))
        random.seed()  # Reset seed
        
        # Prepare questions for frontend
        question_data = []
        for i, question in enumerate(shuffled_questions, 1):
            q_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                if isinstance(question.options, dict):
                    q_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    q_data['options'] = question.options
                else:
                    q_data['options'] = []
            
            question_data.append(q_data)
        
        # Create test attempt record
        attempt = UserTestAttempt(
            user_id=user_id,
            test_id=course_id,
            test_type='final',
            questions_order=[str(q.id) for q in shuffled_questions],
            status='in_progress'
        )
        db.session.add(attempt)
        db.session.commit()
        
        test_response = {
            'attempt_id': str(attempt.id),
            'test_title': f'Final Test - Course {course_id}',
            'duration_minutes': 90,
            'total_questions': len(question_data),
            'questions': question_data,
            'status': 'started'
        }
        
        return jsonify({
            'success': True,
            'test': test_response
        }), 200
        
    except Exception as e:
        print(f"Final test start error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to start final test: {str(e)}'
        }), 500

@tests_bp.route('/answer', methods=['POST'])
@jwt_required()
def submit_answer():
    """Submit an answer for a specific question"""
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        print(f"Submitting answer: attempt_id={attempt_id}, question_id={question_id}, answer={answer}")
        
        if not attempt_id or not question_id or answer is None:
            return jsonify({
                'success': False,
                'message': 'Attempt ID, Question ID, and Answer are required'
            }), 400
        
        # For now, just acknowledge the answer submission
        # In a real implementation, you'd store this in database
        return jsonify({
            'success': True,
            'message': 'Answer submitted successfully'
        }), 200
        
    except Exception as e:
        print(f"Answer submission error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to submit answer: {str(e)}'
        }), 500

@tests_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_test():
    """Complete test and calculate final score with certificate generation for perfect scores"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        answers = data.get('answers', {})
        test_type = data.get('test_type', 'module')
        module_id = data.get('module_id')
        course_id = data.get('course_id')
        time_taken_minutes = data.get('time_taken_minutes', 30)
        
        print(f"Completing test: attempt_id={attempt_id}, answers_count={len(answers)}, test_type={test_type}")
        
        if not attempt_id:
            return jsonify({
                'success': False,
                'message': 'Attempt ID is required'
            }), 400
        
        # Get the test attempt
        attempt = UserTestAttempt.query.filter_by(id=attempt_id, user_id=user_id).first()
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Test attempt not found'
            }), 404
        
        # Validate that all questions are answered
        if not answers or len(answers) == 0:
            return jsonify({
                'success': False,
                'message': 'No answers provided. Please answer all questions before submitting.'
            }), 400
        
        # Get expected number of questions based on test type
        expected_questions = 5 if test_type == 'module' else 15
        if len(answers) < expected_questions:
            return jsonify({
                'success': False,
                'message': f'Incomplete test. Please answer all {expected_questions} questions before submitting.'
            }), 400
        
        # STRICT EVALUATION - Calculate score based on submitted answers
        total_questions = len(answers)
        correct_answers = 0
        
        if answers:
            for question_id, user_answer in answers.items():
                question = Question.query.get(question_id)
                if question and question.correct_answer:
                    # STRICT comparison - exact match required
                    if str(user_answer).strip().lower() == str(question.correct_answer).strip().lower():
                        correct_answers += 1
        
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        passed = score_percentage >= 60.0  # Strict 60% passing requirement
        
        # Update test attempt
        attempt.answers = answers
        attempt.score_percentage = score_percentage
        attempt.time_taken_minutes = time_taken_minutes
        attempt.status = 'completed'
        attempt.completed_at = datetime.utcnow()
        
        # Save test result
        test_result = TestResult(
            user_id=user_id,
            test_type=test_type,
            score_percentage=score_percentage,
            answers=answers
        )
        db.session.add(test_result)
        
        certificate_generated = False
        certificate_data = None
        
        # Generate certificate for final tests with 60%+ score
        if test_type in ['course_final', 'final'] and score_percentage >= 60.0 and course_id:
            try:
                user = User.query.get(user_id)
                course = Course.query.get(course_id)
                
                if user and course:
                    # Check if certificate already exists for this course
                    existing_cert = Certificate.query.filter_by(
                        user_id=user_id,
                        course_id=course_id
                    ).first()
                    
                    if not existing_cert:
                        # Generate AI certificate
                        from certificate_service import CertificateGenerator
                        cert_generator = CertificateGenerator()
                        
                        cert_result = cert_generator.generate_certificate(
                            user_name=user.name,
                            course_title=course.title,
                            final_score=score_percentage,
                            completion_date=datetime.utcnow()
                        )
                        
                        # Save certificate to database
                        certificate = Certificate(
                            user_id=user_id,
                            course_id=course_id,
                            certificate_number=cert_result['certificate_number'],
                            final_score=score_percentage,
                            certificate_data=cert_result['certificate_data'],
                            pdf_path=cert_result['pdf_path']
                        )
                        db.session.add(certificate)
                        
                        # Mark course as completed
                        from models import CourseEnrollment
                        enrollment = CourseEnrollment.query.filter_by(
                            user_id=user_id,
                            course_id=course_id
                        ).first()
                        if enrollment:
                            enrollment.status = 'completed'
                            enrollment.completed_at = datetime.utcnow()
                            enrollment.progress_percentage = 100
                        
                        certificate_generated = True
                        certificate_data = {
                            'certificate_number': cert_result['certificate_number'],
                            'download_url': f'/api/tests/certificates/download/{cert_result["certificate_number"]}',
                            'issued_date': datetime.utcnow().isoformat(),
                            'course_title': course.title,
                            'final_score': score_percentage
                        }
                        
                        print(f"🎓 Certificate generated for {user.name}: {cert_result['certificate_number']} (Score: {score_percentage}%)")
                    else:
                        # Certificate already exists
                        certificate_generated = True
                        certificate_data = {
                            'certificate_number': existing_cert.certificate_number,
                            'download_url': f'/api/tests/certificates/download/{existing_cert.certificate_number}',
                            'issued_date': existing_cert.issued_at.isoformat(),
                            'course_title': course.title,
                            'final_score': existing_cert.final_score,
                            'already_issued': True
                        }
                        print(f"Certificate already exists for user {user.name}")
                    
            except Exception as cert_error:
                print(f"Certificate generation error: {cert_error}")
                # Don't fail the test completion if certificate generation fails
        
        db.session.commit()
        
        results = {
            'attempt_id': attempt_id,
            'score_percentage': round(score_percentage, 1),
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'time_taken_minutes': time_taken_minutes,
            'completion_date': datetime.utcnow().isoformat(),
            'status': 'completed',
            'passed': passed,
            'test_type': test_type,
            'pass_threshold': 60.0,
            'certificate_generated': certificate_generated,
            'certificate_data': certificate_data,
            'message': f'Test completed. Score: {round(score_percentage, 1)}%. {"PASSED" if passed else "FAILED - Need 60% to pass"}'
        }
        
        return jsonify({
            'success': True,
            'message': 'Test completed successfully',
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Test completion error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to complete test: {str(e)}'
        }), 500

# Test attempts functionality can be implemented later if needed

# Certificate routes moved to certificates.py to avoid duplication

# Duplicate download_certificate function removed - using certificates.py instead

@tests_bp.route('/certificates/verify/<certificate_number>', methods=['GET'])
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
                'issued_date': certificate.issued_at.isoformat()
            },
            'message': 'Certificate is valid and authentic'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to verify certificate: {str(e)}'
        }), 500

@tests_bp.route('/debug/questions', methods=['GET'])
@jwt_required()
def debug_questions():
    """Debug endpoint to check questions"""
    try:
        questions = Question.query.filter_by(is_active=True).limit(5).all()
        
        question_data = []
        for q in questions:
            q_data = {
                'id': str(q.id),
                'question_text': q.question_text,
                'question_type': q.question_type,
                'difficulty_level': q.difficulty_level,
                'category': q.category,
                'options_raw': q.options,
                'options_processed': list(q.options.values()) if isinstance(q.options, dict) else q.options
            }
            question_data.append(q_data)
        
        return jsonify({
            'success': True,
            'total_questions': Question.query.count(),
            'sample_questions': question_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Debug failed: {str(e)}'
        }), 500

@tests_bp.route('/course/<course_id>/final-test', methods=['GET'])
@jwt_required()
def get_course_final_test(course_id):
    """Get final test for a specific course with certificate eligibility"""
    try:
        user_id = get_jwt_identity()
        
        # Verify user is enrolled in the course
        from models import CourseEnrollment
        enrollment = CourseEnrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 403
        
        # Check if user has completed all modules (100% progress required)
        if enrollment.progress_percentage < 100:
            return jsonify({
                'success': False,
                'message': f'Complete all modules first. Current progress: {enrollment.progress_percentage}%'
            }), 400
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404
        
        # Get course-specific questions or general questions
        course_questions = Question.query.filter_by(
            course_id=course_id,
            is_active=True
        ).all()
        
        if not course_questions:
            # Get general questions if no course-specific ones
            course_questions = Question.query.filter_by(is_active=True).limit(15).all()
        
        if not course_questions:
            return jsonify({
                'success': False,
                'message': 'No questions available for this course'
            }), 404
        
        # Select balanced questions (5 easy, 7 medium, 3 hard)
        import random
        easy_questions = [q for q in course_questions if q.difficulty_level == 'easy']
        medium_questions = [q for q in course_questions if q.difficulty_level == 'medium']
        hard_questions = [q for q in course_questions if q.difficulty_level == 'hard']
        
        selected_questions = []
        selected_questions.extend(random.sample(easy_questions, min(5, len(easy_questions))))
        selected_questions.extend(random.sample(medium_questions, min(7, len(medium_questions))))
        selected_questions.extend(random.sample(hard_questions, min(3, len(hard_questions))))
        
        # Fill remaining slots if needed
        remaining_needed = 15 - len(selected_questions)
        if remaining_needed > 0:
            remaining_questions = [q for q in course_questions if q not in selected_questions]
            selected_questions.extend(random.sample(remaining_questions, min(remaining_needed, len(remaining_questions))))
        
        random.shuffle(selected_questions)
        
        test_questions = []
        for i, question in enumerate(selected_questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            test_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'test': {
                'test_title': f'{course.title} - Final Assessment',
                'test_type': 'course_final',
                'course_id': course_id,
                'course_title': course.title,
                'duration_minutes': 90,
                'questions': test_questions,
                'attempt_id': f'course_final_{course_id}_{user_id}_{int(datetime.utcnow().timestamp())}',
                'certificate_eligible': True,
                'pass_threshold': 60,
                'note': '🎓 Pass with 60%+ to earn your AI-generated certificate!'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get course final test: {str(e)}'
        }), 500

@tests_bp.route('/simple-test', methods=['GET'])
@jwt_required()
def get_simple_test():
    """Get a simple test with available questions"""
    try:
        user_id = get_jwt_identity()
        
        # Get any available questions
        questions = Question.query.filter_by(is_active=True).limit(10).all()
        
        if not questions:
            return jsonify({
                'success': False,
                'message': 'No questions available'
            }), 404
        
        test_questions = []
        for i, question in enumerate(questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            if question.question_type == 'multiple_choice' and question.options:
                # Convert options from dict format to array format for frontend
                if isinstance(question.options, dict):
                    question_data['options'] = list(question.options.values())
                elif isinstance(question.options, list):
                    question_data['options'] = question.options
                else:
                    question_data['options'] = []
            
            test_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'test': {
                'test_title': 'Practice Test',
                'duration_minutes': 30,
                'questions': test_questions,
                'attempt_id': f'simple_test_{user_id}_{int(datetime.utcnow().timestamp())}'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get simple test: {str(e)}'
        }), 500

@tests_bp.route('/supported-languages', methods=['GET'])
def get_supported_languages():
    """Get list of supported programming languages for code editor"""
    try:
        from ai_code_evaluator import ai_code_evaluator
        
        languages_info = ai_code_evaluator.get_supported_languages()
        
        return jsonify({
            'success': True,
            'supported_languages': languages_info['languages'],
            'total_languages': languages_info['total_languages'],
            'message': 'Code editor supports multiple programming languages with proper evaluation'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get supported languages: {str(e)}'
        }), 500