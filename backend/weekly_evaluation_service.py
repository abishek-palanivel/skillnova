 #!/usr/bin/env python3
"""
Weekly Evaluation Service
This service handles automated weekly evaluation generation and management
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from models import db, WeeklyEvaluation, WeeklyEvaluationQuestion, WeeklyEvaluationAttempt, WeeklyEvaluationScore, User
from ai_question_generator import ai_question_generator
from ai_code_evaluator import ai_code_evaluator
from email_service import email_service

class WeeklyEvaluationService:
    """Service for managing weekly evaluations"""
    
    def __init__(self):
        self.question_categories = [
            'Python', 'JavaScript', 'Web Development', 'Data Science', 
            'Algorithms', 'Database', 'System Design', 'Software Engineering'
        ]
        self.difficulty_distribution = {
            'easy': 0.4,    # 40% easy questions
            'medium': 0.4,  # 40% medium questions  
            'hard': 0.2     # 20% hard questions
        }
    
    def create_weekly_evaluation(self, scheduled_date: datetime = None, 
                               custom_config: Dict = None) -> Dict[str, Any]:
        """
        Create a new weekly evaluation with AI-generated questions (no default data)
        
        Args:
            scheduled_date: When the evaluation should be scheduled (required)
            custom_config: Custom configuration for the evaluation (required)
            
        Returns:
            Dictionary with creation results
        """
        try:
            # Require scheduled date - no defaults
            if not scheduled_date:
                return {
                    'success': False,
                    'error': 'Scheduled date is required'
                }
            
            # Require custom config - no defaults
            if not custom_config:
                return {
                    'success': False,
                    'error': 'Evaluation configuration is required'
                }
            
            # Validate configuration
            required_fields = ['total_questions', 'coding_questions_count', 'mcq_questions_count', 'duration_minutes']
            for field in required_fields:
                if field not in custom_config:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            total_questions = custom_config['total_questions']
            coding_questions = custom_config['coding_questions_count']
            mcq_questions = custom_config['mcq_questions_count']
            duration_minutes = custom_config['duration_minutes']
            
            # Validate question counts
            if coding_questions + mcq_questions != total_questions:
                return {
                    'success': False,
                    'error': 'Coding questions + MCQ questions must equal total questions'
                }
            
            # Create evaluation record with precise time
            evaluation = WeeklyEvaluation(
                title=f"Weekly Evaluation - {scheduled_date.strftime('%B %d, %Y at %I:%M %p')} (Sunday Evening)",
                description=f"AI-generated weekly evaluation with {coding_questions} coding and {mcq_questions} MCQ questions - Sunday 5:00 PM start, 60 minutes duration",
                scheduled_date=scheduled_date,
                duration_minutes=duration_minutes,
                total_questions=total_questions,
                coding_questions_count=coding_questions,
                mcq_questions_count=mcq_questions,
                auto_generated=True
            )
            
            db.session.add(evaluation)
            db.session.flush()  # Get the evaluation ID
            
            # Generate questions using AI
            questions_created = self._generate_evaluation_questions(
                evaluation.id, coding_questions, mcq_questions
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'evaluation_id': str(evaluation.id),
                'scheduled_date': scheduled_date.isoformat(),
                'questions_created': questions_created,
                'message': f'Weekly evaluation created successfully for {scheduled_date.strftime("%B %d, %Y at %I:%M %p")} with {questions_created} AI-generated questions'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to create weekly evaluation: {str(e)}'
            }
    
    def _generate_evaluation_questions(self, evaluation_id: str, 
                                     coding_count: int, mcq_count: int) -> int:
        """Generate questions for the evaluation"""
        questions_created = 0
        order_index = 1
        
        # Generate coding questions
        for i in range(coding_count):
            category = random.choice(self.question_categories)
            difficulty = self._get_random_difficulty()
            
            # Generate coding question
            question_data = ai_question_generator.generate_question(
                'coding', difficulty, category
            )
            
            # Generate test cases for coding questions
            test_cases = self._generate_test_cases(question_data, category, difficulty)
            
            question = WeeklyEvaluationQuestion(
                evaluation_id=evaluation_id,
                question_text=question_data['question_text'],
                question_type='coding',
                difficulty_level=difficulty,
                category=category,
                correct_answer=question_data['correct_answer'],
                test_cases=test_cases,
                explanation=question_data.get('explanation', ''),
                points=15 if difficulty == 'hard' else 12 if difficulty == 'medium' else 10,
                order_index=order_index
            )
            
            db.session.add(question)
            questions_created += 1
            order_index += 1
        
        # Generate multiple choice questions
        for i in range(mcq_count):
            category = random.choice(self.question_categories)
            difficulty = self._get_random_difficulty()
            
            question_data = ai_question_generator.generate_question(
                'multiple_choice', difficulty, category
            )
            
            question = WeeklyEvaluationQuestion(
                evaluation_id=evaluation_id,
                question_text=question_data['question_text'],
                question_type='multiple_choice',
                difficulty_level=difficulty,
                category=category,
                correct_answer=question_data['correct_answer'],
                options=question_data.get('options', {}),
                explanation=question_data.get('explanation', ''),
                points=10 if difficulty == 'hard' else 8 if difficulty == 'medium' else 5,
                order_index=order_index
            )
            
            db.session.add(question)
            questions_created += 1
            order_index += 1
        
        return questions_created
    
    def _get_random_difficulty(self) -> str:
        """Get random difficulty based on distribution"""
        rand = random.random()
        if rand < self.difficulty_distribution['easy']:
            return 'easy'
        elif rand < self.difficulty_distribution['easy'] + self.difficulty_distribution['medium']:
            return 'medium'
        else:
            return 'hard'
    
    def _generate_test_cases(self, question_data: Dict, category: str, difficulty: str) -> List[Dict]:
        """Generate test cases for coding questions"""
        test_cases = []
        
        # Generate test cases based on category and difficulty
        if category.lower() == 'python':
            if 'sort' in question_data['question_text'].lower():
                test_cases = [
                    {'input': '[3, 1, 4, 1, 5]', 'expected_output': '[1, 1, 3, 4, 5]'},
                    {'input': '[9, 2, 7, 8]', 'expected_output': '[2, 7, 8, 9]'},
                    {'input': '[]', 'expected_output': '[]'}
                ]
            elif 'fibonacci' in question_data['question_text'].lower():
                test_cases = [
                    {'input': '5', 'expected_output': '5'},
                    {'input': '10', 'expected_output': '55'},
                    {'input': '0', 'expected_output': '0'}
                ]
            else:
                # Generic test cases
                test_cases = [
                    {'input': '5', 'expected_output': '5'},
                    {'input': '10', 'expected_output': '10'},
                    {'input': '0', 'expected_output': '0'}
                ]
        
        elif category.lower() == 'algorithms':
            if difficulty == 'easy':
                test_cases = [
                    {'input': '[1, 2, 3, 4, 5]\n3', 'expected_output': '2'},
                    {'input': '[10, 20, 30]\n20', 'expected_output': '1'},
                    {'input': '[5]\n5', 'expected_output': '0'}
                ]
            else:
                test_cases = [
                    {'input': '[1, 3, 5, 7, 9]\n5', 'expected_output': '2'},
                    {'input': '[2, 4, 6, 8]\n6', 'expected_output': '2'},
                    {'input': '[1]\n2', 'expected_output': '-1'}
                ]
        
        else:
            # Default test cases
            test_cases = [
                {'input': 'test input 1', 'expected_output': 'expected output 1'},
                {'input': 'test input 2', 'expected_output': 'expected output 2'},
                {'input': 'test input 3', 'expected_output': 'expected output 3'}
            ]
        
        return test_cases
    
    def get_next_evaluation(self) -> Optional[Dict[str, Any]]:
        """Get the next scheduled evaluation"""
        try:
            now = datetime.utcnow()
            next_evaluation = WeeklyEvaluation.query.filter(
                WeeklyEvaluation.scheduled_date > now,
                WeeklyEvaluation.is_active == True
            ).order_by(WeeklyEvaluation.scheduled_date.asc()).first()
            
            if next_evaluation:
                return {
                    'id': str(next_evaluation.id),
                    'title': next_evaluation.title,
                    'scheduled_date': next_evaluation.scheduled_date.isoformat(),
                    'duration_minutes': next_evaluation.duration_minutes,
                    'total_questions': next_evaluation.total_questions,
                    'status': 'scheduled'
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting next evaluation: {e}")
            return None
    
    def start_evaluation_for_user(self, user_id: str, evaluation_id: str) -> Dict[str, Any]:
        """Start an evaluation for a specific user"""
        try:
            # Check if user already has an attempt
            existing_attempt = WeeklyEvaluationAttempt.query.filter_by(
                user_id=user_id,
                evaluation_id=evaluation_id
            ).first()
            
            if existing_attempt:
                if existing_attempt.status == 'completed':
                    return {
                        'success': False,
                        'message': 'You have already completed this evaluation'
                    }
                else:
                    # Return existing attempt
                    return {
                        'success': True,
                        'attempt_id': str(existing_attempt.id),
                        'message': 'Resuming existing evaluation attempt'
                    }
            
            # Create new attempt
            attempt = WeeklyEvaluationAttempt(
                evaluation_id=evaluation_id,
                user_id=user_id,
                status='in_progress'
            )
            
            db.session.add(attempt)
            db.session.commit()
            
            return {
                'success': True,
                'attempt_id': str(attempt.id),
                'message': 'Evaluation started successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to start evaluation: {str(e)}'
            }
    
    def submit_evaluation_answer(self, attempt_id: str, question_id: str, 
                               answer: Any, language: str = None) -> Dict[str, Any]:
        """Submit an answer for a specific question"""
        try:
            attempt = WeeklyEvaluationAttempt.query.get(attempt_id)
            if not attempt:
                return {'success': False, 'error': 'Attempt not found'}
            
            if attempt.status != 'in_progress':
                return {'success': False, 'error': 'Evaluation is not in progress'}
            
            # Get current answers
            answers = attempt.answers or {}
            
            # Store the answer
            answers[question_id] = {
                'answer': answer,
                'language': language,
                'submitted_at': datetime.utcnow().isoformat()
            }
            
            attempt.answers = answers
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Answer submitted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to submit answer: {str(e)}'
            }
    
    def complete_evaluation(self, attempt_id: str) -> Dict[str, Any]:
        """Complete and evaluate the submission"""
        try:
            attempt = WeeklyEvaluationAttempt.query.get(attempt_id)
            if not attempt:
                return {'success': False, 'error': 'Attempt not found'}
            
            if attempt.status != 'in_progress':
                return {'success': False, 'error': 'Evaluation is not in progress'}
            
            # Get evaluation questions
            questions = WeeklyEvaluationQuestion.query.filter_by(
                evaluation_id=attempt.evaluation_id
            ).order_by(WeeklyEvaluationQuestion.order_index).all()
            
            # Evaluate answers
            evaluation_results = self._evaluate_submission(attempt, questions)
            
            # Update attempt
            attempt.status = 'completed'
            attempt.completed_at = datetime.utcnow()
            attempt.score_percentage = evaluation_results['score_percentage']
            attempt.total_points = evaluation_results['total_points']
            attempt.earned_points = evaluation_results['earned_points']
            attempt.ai_evaluation_results = evaluation_results['detailed_results']
            
            # Calculate time taken
            time_taken = (attempt.completed_at - attempt.started_at).total_seconds() / 60
            attempt.time_taken_minutes = int(time_taken)
            
            # Create score record
            score_record = WeeklyEvaluationScore(
                user_id=attempt.user_id,
                evaluation_id=attempt.evaluation_id,
                attempt_id=attempt.id,
                score_percentage=evaluation_results['score_percentage'],
                grade=self._calculate_grade(evaluation_results['score_percentage']),
                coding_score=evaluation_results.get('coding_score', 0),
                mcq_score=evaluation_results.get('mcq_score', 0),
                admin_decision='pending'
            )
            
            db.session.add(score_record)
            db.session.commit()
            
            return {
                'success': True,
                'score_percentage': evaluation_results['score_percentage'],
                'grade': score_record.grade,
                'coding_score': evaluation_results.get('coding_score', 0),
                'mcq_score': evaluation_results.get('mcq_score', 0),
                'total_points': evaluation_results['total_points'],
                'earned_points': evaluation_results['earned_points'],
                'detailed_results': evaluation_results['detailed_results'],
                'completion_time': datetime.utcnow().isoformat(),
                'message': 'Evaluation completed successfully - Score available instantly!'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to complete evaluation: {str(e)}'
            }
    
    def _evaluate_submission(self, attempt: WeeklyEvaluationAttempt, 
                           questions: List[WeeklyEvaluationQuestion]) -> Dict[str, Any]:
        """Evaluate the complete submission"""
        total_points = 0
        earned_points = 0
        coding_points = 0
        coding_earned = 0
        mcq_points = 0
        mcq_earned = 0
        detailed_results = {}
        
        answers = attempt.answers or {}
        
        for question in questions:
            question_id = str(question.id)
            total_points += question.points
            
            if question.question_type == 'coding':
                coding_points += question.points
            else:
                mcq_points += question.points
            
            if question_id in answers:
                user_answer = answers[question_id]
                
                if question.question_type == 'multiple_choice':
                    # Evaluate MCQ
                    is_correct = user_answer['answer'] == question.correct_answer
                    points_earned = question.points if is_correct else 0
                    
                    detailed_results[question_id] = {
                        'question_type': 'multiple_choice',
                        'correct': is_correct,
                        'points_earned': points_earned,
                        'max_points': question.points,
                        'user_answer': user_answer['answer'],
                        'correct_answer': question.correct_answer
                    }
                    
                    earned_points += points_earned
                    mcq_earned += points_earned
                
                elif question.question_type == 'coding':
                    # Evaluate coding question
                    code = user_answer['answer']
                    language = user_answer.get('language', 'python')
                    test_cases = question.test_cases or []
                    
                    evaluation_result = ai_code_evaluator.evaluate_code_submission(
                        code, language, test_cases, question.question_text
                    )
                    
                    # Calculate points based on test cases passed and code quality
                    test_score = evaluation_result.get('score', 0) / 100
                    quality_score = evaluation_result.get('code_quality', {}).get('overall_score', 50) / 100
                    
                    # Weighted scoring: 70% test cases, 30% code quality
                    final_score = (test_score * 0.7) + (quality_score * 0.3)
                    points_earned = int(question.points * final_score)
                    
                    detailed_results[question_id] = {
                        'question_type': 'coding',
                        'points_earned': points_earned,
                        'max_points': question.points,
                        'test_results': evaluation_result.get('test_results', []),
                        'code_quality': evaluation_result.get('code_quality', {}),
                        'compilation_success': evaluation_result.get('success', False),
                        'language': language
                    }
                    
                    earned_points += points_earned
                    coding_earned += points_earned
            else:
                # No answer provided
                detailed_results[question_id] = {
                    'question_type': question.question_type,
                    'points_earned': 0,
                    'max_points': question.points,
                    'no_answer': True
                }
        
        score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        coding_score = (coding_earned / coding_points * 100) if coding_points > 0 else 0
        mcq_score = (mcq_earned / mcq_points * 100) if mcq_points > 0 else 0
        
        return {
            'score_percentage': round(score_percentage, 2),
            'total_points': total_points,
            'earned_points': earned_points,
            'coding_score': round(coding_score, 2),
            'mcq_score': round(mcq_score, 2),
            'detailed_results': detailed_results
        }
    
    def _calculate_grade(self, score_percentage: float) -> str:
        """Calculate letter grade based on score percentage"""
        if score_percentage >= 97:
            return 'A+'
        elif score_percentage >= 93:
            return 'A'
        elif score_percentage >= 90:
            return 'A-'
        elif score_percentage >= 87:
            return 'B+'
        elif score_percentage >= 83:
            return 'B'
        elif score_percentage >= 80:
            return 'B-'
        elif score_percentage >= 77:
            return 'C+'
        elif score_percentage >= 73:
            return 'C'
        elif score_percentage >= 70:
            return 'C-'
        elif score_percentage >= 67:
            return 'D+'
        elif score_percentage >= 65:
            return 'D'
        else:
            return 'F'
    
    def auto_generate_weekly_evaluations(self, weeks_ahead: int = 4) -> Dict[str, Any]:
        """Auto-generate weekly evaluations for the next few weeks - SUNDAYS 5:00 PM"""
        try:
            created_evaluations = []
            
            for week in range(1, weeks_ahead + 1):
                # Calculate next SUNDAY at 5:00 PM
                today = datetime.now()
                days_ahead = (6 - today.weekday() + 7 * week) % 7  # Sunday is 6
                if days_ahead == 0:  # If today is Sunday, schedule for next Sunday
                    days_ahead = 7
                scheduled_date = (today + timedelta(days=days_ahead)).replace(
                    hour=17, minute=0, second=0, microsecond=0  # 5:00 PM sharp
                )
                
                # Check if evaluation already exists for this date
                existing = WeeklyEvaluation.query.filter(
                    WeeklyEvaluation.scheduled_date.between(
                        scheduled_date.replace(hour=0),
                        scheduled_date.replace(hour=23, minute=59)
                    )
                ).first()
                
                if not existing:
                    # Create with strict 60-minute duration
                    custom_config = {
                        'total_questions': 10,
                        'coding_questions_count': 3,
                        'mcq_questions_count': 7,
                        'duration_minutes': 60  # STRICT 60 minutes
                    }
                    result = self.create_weekly_evaluation(scheduled_date, custom_config)
                    if result['success']:
                        created_evaluations.append({
                            'date': scheduled_date.strftime('%Y-%m-%d %H:%M'),
                            'evaluation_id': result['evaluation_id'],
                            'scheduled_time': '5:00 PM Sunday (60 minutes)'
                        })
            
            return {
                'success': True,
                'created_evaluations': created_evaluations,
                'message': f'Created {len(created_evaluations)} weekly evaluations'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to auto-generate evaluations: {str(e)}'
            }

# Global instance
weekly_evaluation_service = WeeklyEvaluationService()