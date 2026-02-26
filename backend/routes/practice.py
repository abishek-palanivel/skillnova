from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Question, CourseEnrollment

practice_bp = Blueprint('practice', __name__)

@practice_bp.route('/module/<module_id>', methods=['GET'])
@jwt_required()
def get_practice_module(module_id):
    """Get practice questions for a specific module"""
    try:
        user_id = get_jwt_identity()
        
        # For now, we'll return general practice questions
        # In a real implementation, you'd link questions to specific modules
        
        difficulty = request.args.get('difficulty', 'medium')
        category = request.args.get('category', 'general')
        limit = int(request.args.get('limit', 10))
        
        # Get practice questions
        questions_query = Question.query.filter_by(
            is_active=True,
            difficulty_level=difficulty
        )
        
        if category != 'general':
            questions_query = questions_query.filter_by(category=category)
        
        questions = questions_query.limit(limit).all()
        
        practice_questions = []
        for question in questions:
            question_data = {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            # Include options for multiple choice questions
            if question.question_type == 'multiple_choice' and question.options:
                question_data['options'] = question.options
            
            practice_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'module_id': module_id,
            'difficulty': difficulty,
            'category': category,
            'questions': practice_questions,
            'total_questions': len(practice_questions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get practice module: {str(e)}'
        }), 500

@practice_bp.route('/questions', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_practice_questions():
    """Get practice questions with filters - prioritize AI-created questions from admin"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get query parameters
        difficulty = request.args.get('difficulty')
        category = request.args.get('category', 'Programming')  # Default category
        question_type = request.args.get('type', 'multiple_choice')
        limit = int(request.args.get('limit', 20))
        
        # Build query - prioritize AI-created questions
        query = Question.query.filter_by(is_active=True)
        
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        if category:
            query = query.filter_by(category=category)
        if question_type:
            query = query.filter_by(question_type=question_type)
        
        # Order by creation date (newest first) to show AI-created questions first
        questions = query.order_by(Question.created_at.desc()).limit(limit).all()
        
        # If no questions found, generate them using AI
        if not questions:
            print(f"No practice questions found. Generating AI questions for category: {category}")
            from ai_question_generator import ai_question_generator
            
            # Generate questions based on requested difficulty or mix
            difficulties_to_generate = []
            if difficulty:
                difficulties_to_generate = [difficulty] * min(10, limit)
            else:
                # Mix of difficulties
                difficulties_to_generate = ['easy'] * 3 + ['medium'] * 4 + ['hard'] * 3
            
            for diff in difficulties_to_generate:
                try:
                    question_data = ai_question_generator.generate_question(
                        question_type, diff, category
                    )
                    
                    new_question = Question(
                        question_text=question_data['question_text'],
                        question_type=question_type,
                        difficulty_level=diff,
                        category=category,
                        correct_answer=question_data.get('correct_answer'),
                        options=question_data.get('options'),
                        explanation=question_data.get('explanation'),
                        is_active=True
                    )
                    db.session.add(new_question)
                except Exception as gen_error:
                    print(f"Error generating practice question: {gen_error}")
                    continue
            
            db.session.commit()
            
            # Reload questions
            query = Question.query.filter_by(is_active=True)
            if difficulty:
                query = query.filter_by(difficulty_level=difficulty)
            if category:
                query = query.filter_by(category=category)
            if question_type:
                query = query.filter_by(question_type=question_type)
            
            questions = query.order_by(Question.created_at.desc()).limit(limit).all()
            
            if not questions:
                return jsonify({
                    'success': True,
                    'questions': [],
                    'message': 'Failed to generate practice questions. Please try again.',
                    'filters': {
                        'difficulty': difficulty,
                        'category': category,
                        'type': question_type,
                        'limit': limit
                    }
                }), 200
        
        questions_data = []
        for question in questions:
            question_data = {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'created_at': question.created_at.isoformat(),
                'is_ai_generated': True  # Assume all questions are AI-generated for now
            }
            
            # Include options for multiple choice questions (but not correct answer)
            if question.question_type == 'multiple_choice' and question.options:
                question_data['options'] = question.options
            
            questions_data.append(question_data)
        
        return jsonify({
            'success': True,
            'questions': questions_data,
            'total_questions': len(questions_data),
            'filters': {
                'difficulty': difficulty,
                'category': category,
                'type': question_type,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get practice questions: {str(e)}'
        }), 500


    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get practice questions: {str(e)}'
        }), 500

@practice_bp.route('/submit-answer', methods=['POST'])
@jwt_required()
def submit_practice_answer():
    """Submit answer for a practice question and get feedback - STRICT EVALUATION"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('question_id') or not data.get('answer'):
            return jsonify({
                'success': False,
                'message': 'Question ID and answer are required'
            }), 400
        
        question_id = data['question_id']
        user_answer = data['answer']
        
        # Get question
        question = Question.query.get(question_id)
        if not question or not question.is_active:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404
        
        # STRICT ANSWER CHECKING - NO MORE "ALWAYS CORRECT"
        is_correct = False
        feedback = ""
        
        if question.question_type == 'multiple_choice':
            # Strict comparison - exact match required
            is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
            if is_correct:
                feedback = "✅ Correct! Well done."
            else:
                feedback = f"❌ Incorrect. The correct answer is: {question.correct_answer}"
        
        elif question.question_type == 'coding':
            # Use AI code evaluator for proper evaluation
            try:
                from ai_code_evaluator import ai_code_evaluator
                
                # Generate test cases if not available
                test_cases = [
                    {'input': '5', 'expected_output': '5'},
                    {'input': '10', 'expected_output': '10'},
                    {'input': '0', 'expected_output': '0'}
                ]
                
                language = data.get('language', 'python')
                evaluation_result = ai_code_evaluator.evaluate_code_submission(
                    user_answer, language, test_cases, question.question_text
                )
                
                if evaluation_result['success']:
                    score = evaluation_result['score']
                    is_correct = score >= 70  # 70% threshold for correctness
                    
                    if is_correct:
                        feedback = f"✅ Code executed successfully! Score: {score}%"
                    else:
                        feedback = f"❌ Code has issues. Score: {score}%. Check your logic and try again."
                        
                    # Add test results details
                    if evaluation_result.get('test_results'):
                        passed_tests = evaluation_result['passed_tests']
                        total_tests = evaluation_result['total_tests']
                        feedback += f" Tests passed: {passed_tests}/{total_tests}"
                else:
                    is_correct = False
                    feedback = f"❌ Code evaluation failed: {evaluation_result.get('error', 'Unknown error')}"
                    
            except Exception as code_error:
                is_correct = False
                feedback = f"❌ Code evaluation error: {str(code_error)}"
        
        elif question.question_type == 'essay':
            # Essay questions require manual review - mark as pending
            is_correct = False  # Don't assume correct
            feedback = "📝 Essay submitted for manual review. You'll receive feedback within 24 hours."
        
        else:
            # For any other question type, strict text comparison
            is_correct = str(user_answer).strip().lower() == str(question.correct_answer).strip().lower()
            if is_correct:
                feedback = "✅ Correct answer!"
            else:
                feedback = f"❌ Incorrect. Expected: {question.correct_answer}"
        
        return jsonify({
            'success': True,
            'question_id': question_id,
            'is_correct': is_correct,
            'feedback': feedback,
            'correct_answer': question.correct_answer if not is_correct and question.question_type == 'multiple_choice' else None,
            'evaluation_strict': True  # Flag to indicate strict evaluation
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit answer: {str(e)}'
        }), 500

@practice_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_practice_categories():
    """Get available practice categories"""
    try:
        # Get distinct categories from questions
        categories = db.session.query(Question.category).filter(
            Question.is_active == True,
            Question.category.isnot(None)
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get categories: {str(e)}'
        }), 500

@practice_bp.route('/quiz', methods=['POST'])
@jwt_required()
def create_practice_quiz():
    """Create a custom practice quiz"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get quiz parameters
        difficulty = data.get('difficulty', 'medium')
        category = data.get('category')
        num_questions = min(int(data.get('num_questions', 10)), 50)  # Max 50 questions
        
        # Build query for quiz questions
        query = Question.query.filter_by(
            is_active=True,
            difficulty_level=difficulty
        )
        
        if category:
            query = query.filter_by(category=category)
        
        # Get random questions
        questions = query.order_by(db.func.random()).limit(num_questions).all()
        
        if not questions:
            return jsonify({
                'success': False,
                'message': 'No questions found matching the criteria'
            }), 404
        
        quiz_questions = []
        for i, question in enumerate(questions, 1):
            question_data = {
                'question_number': i,
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category
            }
            
            # Include options for multiple choice questions
            if question.question_type == 'multiple_choice' and question.options:
                question_data['options'] = question.options
            
            quiz_questions.append(question_data)
        
        return jsonify({
            'success': True,
            'quiz': {
                'difficulty': difficulty,
                'category': category,
                'total_questions': len(quiz_questions),
                'questions': quiz_questions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create quiz: {str(e)}'
        }), 500

@practice_bp.route('/ai-generate-questions', methods=['POST'])
@jwt_required()
def generate_ai_practice_questions():
    """Generate practice questions using AI (admin only)"""
    try:
        from flask_jwt_extended import get_jwt_identity
        from models import User
        
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        data = request.get_json() or {}
        category = data.get('category', 'Python')
        difficulty = data.get('difficulty', 'medium')
        question_type = data.get('question_type', 'multiple_choice')
        count = min(int(data.get('count', 5)), 20)  # Max 20 questions
        
        from ai_question_generator import ai_question_generator
        
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
                'category': category
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