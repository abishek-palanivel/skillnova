#!/usr/bin/env python3
"""
Weekly Evaluations Routes
User-facing routes for weekly evaluations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (db, User, WeeklyEvaluation, WeeklyEvaluationQuestion, 
                   WeeklyEvaluationAttempt, WeeklyEvaluationScore)
from weekly_evaluation_service import weekly_evaluation_service

weekly_evaluations_bp = Blueprint('weekly_evaluations', __name__)

@weekly_evaluations_bp.route('/next', methods=['GET'])
@jwt_required()
def get_next_evaluation():
    """Get the next scheduled weekly evaluation"""
    try:
        user_id = get_jwt_identity()
        
        # Get next evaluation
        next_evaluation = weekly_evaluation_service.get_next_evaluation()
        
        if not next_evaluation:
            return jsonify({
                'success': True,
                'next_evaluation': None,
                'message': 'No upcoming evaluations scheduled'
            }), 200
        
        # Check if user has already attempted this evaluation
        existing_attempt = WeeklyEvaluationAttempt.query.filter_by(
            user_id=user_id,
            evaluation_id=next_evaluation['id']
        ).first()
        
        if existing_attempt:
            next_evaluation['user_status'] = existing_attempt.status
            next_evaluation['attempt_id'] = str(existing_attempt.id)
            if existing_attempt.status == 'completed':
                next_evaluation['score'] = existing_attempt.score_percentage
        else:
            next_evaluation['user_status'] = 'not_started'
        
        return jsonify({
            'success': True,
            'next_evaluation': next_evaluation
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get next evaluation: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_evaluation():
    """Get current active evaluation if available"""
    try:
        user_id = get_jwt_identity()
        now = datetime.utcnow()
        
        # Find evaluation that is currently active (STRICT 5:00 PM - 7:00 PM Sunday window)
        current_evaluation = WeeklyEvaluation.query.filter(
            WeeklyEvaluation.scheduled_date <= now,
            WeeklyEvaluation.scheduled_date >= now - timedelta(hours=2),  # 2-hour window (5 PM - 7 PM)
            WeeklyEvaluation.is_active == True
        ).first()
        
        if not current_evaluation:
            return jsonify({
                'success': True,
                'current_evaluation': None,
                'message': 'No active evaluation at this time'
            }), 200
        
        # Check user's attempt status
        user_attempt = WeeklyEvaluationAttempt.query.filter_by(
            user_id=user_id,
            evaluation_id=current_evaluation.id
        ).first()
        
        evaluation_data = {
            'id': str(current_evaluation.id),
            'title': current_evaluation.title,
            'description': current_evaluation.description,
            'scheduled_date': current_evaluation.scheduled_date.isoformat(),
            'duration_minutes': current_evaluation.duration_minutes,
            'total_questions': current_evaluation.total_questions,
            'coding_questions_count': current_evaluation.coding_questions_count,
            'mcq_questions_count': current_evaluation.mcq_questions_count
        }
        
        if user_attempt:
            evaluation_data['user_status'] = user_attempt.status
            evaluation_data['attempt_id'] = str(user_attempt.id)
            evaluation_data['started_at'] = user_attempt.started_at.isoformat()
            if user_attempt.status == 'completed':
                evaluation_data['completed_at'] = user_attempt.completed_at.isoformat()
                evaluation_data['score'] = user_attempt.score_percentage
        else:
            evaluation_data['user_status'] = 'not_started'
        
        return jsonify({
            'success': True,
            'current_evaluation': evaluation_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get current evaluation: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/<evaluation_id>/start', methods=['POST'])
@jwt_required()
def start_evaluation(evaluation_id):
    """Start a weekly evaluation"""
    try:
        user_id = get_jwt_identity()
        
        # Check if evaluation exists and is available
        evaluation = WeeklyEvaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({
                'success': False,
                'message': 'Evaluation not found'
            }), 404
        
        if not evaluation.is_active:
            return jsonify({
                'success': False,
                'message': 'Evaluation is not active'
            }), 400
        
        # Check if evaluation is available (STRICT 5:00 PM - 7:00 PM Sunday window)
        now = datetime.utcnow()
        evaluation_start = evaluation.scheduled_date
        evaluation_end = evaluation.scheduled_date + timedelta(hours=2)  # 2-hour window (5 PM - 7 PM)
        
        if now < evaluation_start:
            return jsonify({
                'success': False,
                'message': f'Evaluation starts at {evaluation_start.strftime("%I:%M %p on %A, %B %d")}. Please wait.',
                'start_time': evaluation_start.isoformat(),
                'current_time': now.isoformat()
            }), 400
        
        # Check if evaluation window has expired (7:00 PM Sunday)
        if now > evaluation_end:
            return jsonify({
                'success': False,
                'message': f'Evaluation window closed at {evaluation_end.strftime("%I:%M %p on %A, %B %d")}. Next evaluation will be announced.',
                'end_time': evaluation_end.isoformat()
            }), 400
        
        # Start evaluation for user
        result = weekly_evaluation_service.start_evaluation_for_user(user_id, evaluation_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to start evaluation: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/attempts/<attempt_id>/questions', methods=['GET'])
@jwt_required()
def get_evaluation_questions(attempt_id):
    """Get questions for an evaluation attempt"""
    try:
        user_id = get_jwt_identity()
        
        # Verify attempt belongs to user
        attempt = WeeklyEvaluationAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id
        ).first()
        
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Attempt not found or access denied'
            }), 404
        
        if attempt.status not in ['in_progress']:
            return jsonify({
                'success': False,
                'message': 'Evaluation is not in progress'
            }), 400
        
        # Get questions
        questions = WeeklyEvaluationQuestion.query.filter_by(
            evaluation_id=attempt.evaluation_id
        ).order_by(WeeklyEvaluationQuestion.order_index).all()
        
        questions_data = []
        for question in questions:
            question_data = {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'category': question.category,
                'points': question.points,
                'order_index': question.order_index
            }
            
            # Add options for multiple choice questions
            if question.question_type == 'multiple_choice':
                question_data['options'] = question.options
            
            # Add test cases info for coding questions (without revealing expected outputs)
            elif question.question_type == 'coding':
                if question.test_cases:
                    question_data['test_cases_count'] = len(question.test_cases)
                    # Only show input examples, not expected outputs
                    question_data['sample_inputs'] = [
                        tc.get('input', '') for tc in question.test_cases[:2]  # First 2 as examples
                    ]
            
            questions_data.append(question_data)
        
        # Get evaluation info
        evaluation = attempt.evaluation
        
        return jsonify({
            'success': True,
            'evaluation': {
                'id': str(evaluation.id),
                'title': evaluation.title,
                'duration_minutes': evaluation.duration_minutes,
                'total_questions': evaluation.total_questions
            },
            'attempt': {
                'id': str(attempt.id),
                'started_at': attempt.started_at.isoformat(),
                'status': attempt.status
            },
            'questions': questions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get questions: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/attempts/<attempt_id>/submit-answer', methods=['POST'])
@jwt_required()
def submit_answer(attempt_id):
    """Submit an answer for a specific question"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'question_id' not in data or 'answer' not in data:
            return jsonify({
                'success': False,
                'message': 'Question ID and answer are required'
            }), 400
        
        # Verify attempt belongs to user
        attempt = WeeklyEvaluationAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id
        ).first()
        
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Attempt not found or access denied'
            }), 404
        
        # Submit answer
        result = weekly_evaluation_service.submit_evaluation_answer(
            attempt_id=attempt_id,
            question_id=data['question_id'],
            answer=data['answer'],
            language=data.get('language', 'python')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit answer: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/attempts/<attempt_id>/complete', methods=['POST'])
@jwt_required()
def complete_evaluation(attempt_id):
    """Complete and submit the evaluation"""
    try:
        user_id = get_jwt_identity()
        
        # Verify attempt belongs to user
        attempt = WeeklyEvaluationAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id
        ).first()
        
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Attempt not found or access denied'
            }), 404
        
        # Complete evaluation
        result = weekly_evaluation_service.complete_evaluation(attempt_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to complete evaluation: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/my-scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    """Get user's evaluation scores and results"""
    try:
        user_id = get_jwt_identity()
        
        # Get user's scores
        scores = WeeklyEvaluationScore.query.filter_by(
            user_id=user_id
        ).order_by(WeeklyEvaluationScore.created_at.desc()).all()
        
        scores_data = []
        for score in scores:
            evaluation = score.evaluation
            scores_data.append({
                'id': str(score.id),
                'evaluation': {
                    'id': str(evaluation.id),
                    'title': evaluation.title,
                    'scheduled_date': evaluation.scheduled_date.isoformat()
                },
                'score_percentage': score.score_percentage,
                'grade': score.grade,
                'coding_score': score.coding_score,
                'mcq_score': score.mcq_score,
                'admin_decision': score.admin_decision,
                'admin_feedback': score.admin_feedback,
                'decision_date': score.decision_date.isoformat() if score.decision_date else None,
                'created_at': score.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'scores': scores_data,
            'total_evaluations': len(scores_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get scores: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/scores/<score_id>/details', methods=['GET'])
@jwt_required()
def get_score_details(score_id):
    """Get detailed results for a specific evaluation score"""
    try:
        user_id = get_jwt_identity()
        
        # Verify score belongs to user
        score = WeeklyEvaluationScore.query.filter_by(
            id=score_id,
            user_id=user_id
        ).first()
        
        if not score:
            return jsonify({
                'success': False,
                'message': 'Score not found or access denied'
            }), 404
        
        # Get attempt details
        attempt = score.attempt
        evaluation = score.evaluation
        
        # Get questions for context
        questions = WeeklyEvaluationQuestion.query.filter_by(
            evaluation_id=evaluation.id
        ).order_by(WeeklyEvaluationQuestion.order_index).all()
        
        questions_map = {str(q.id): q for q in questions}
        
        # Prepare detailed results
        detailed_results = []
        ai_results = attempt.ai_evaluation_results or {}
        
        for question in questions:
            question_id = str(question.id)
            result_data = {
                'question': {
                    'id': question_id,
                    'text': question.question_text,
                    'type': question.question_type,
                    'difficulty': question.difficulty_level,
                    'category': question.category,
                    'points': question.points
                },
                'result': ai_results.get(question_id, {})
            }
            
            # Add question-specific details
            if question.question_type == 'multiple_choice':
                result_data['question']['options'] = question.options
                result_data['question']['correct_answer'] = question.correct_answer
                result_data['question']['explanation'] = question.explanation
            
            detailed_results.append(result_data)
        
        return jsonify({
            'success': True,
            'score': {
                'id': str(score.id),
                'score_percentage': score.score_percentage,
                'grade': score.grade,
                'coding_score': score.coding_score,
                'mcq_score': score.mcq_score,
                'admin_decision': score.admin_decision,
                'admin_feedback': score.admin_feedback
            },
            'evaluation': {
                'id': str(evaluation.id),
                'title': evaluation.title,
                'scheduled_date': evaluation.scheduled_date.isoformat()
            },
            'attempt': {
                'id': str(attempt.id),
                'time_taken_minutes': attempt.time_taken_minutes,
                'completed_at': attempt.completed_at.isoformat()
            },
            'detailed_results': detailed_results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get score details: {str(e)}'
        }), 500

@weekly_evaluations_bp.route('/history', methods=['GET'])
@jwt_required()
def get_evaluation_history():
    """Get user's complete evaluation history"""
    try:
        user_id = get_jwt_identity()
        
        # Get all user attempts
        attempts = WeeklyEvaluationAttempt.query.filter_by(
            user_id=user_id
        ).order_by(WeeklyEvaluationAttempt.started_at.desc()).all()
        
        history_data = []
        for attempt in attempts:
            evaluation = attempt.evaluation
            
            # Get score if available
            score = WeeklyEvaluationScore.query.filter_by(
                attempt_id=attempt.id
            ).first()
            
            history_item = {
                'attempt_id': str(attempt.id),
                'evaluation': {
                    'id': str(evaluation.id),
                    'title': evaluation.title,
                    'scheduled_date': evaluation.scheduled_date.isoformat()
                },
                'status': attempt.status,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'time_taken_minutes': attempt.time_taken_minutes,
                'score_percentage': attempt.score_percentage
            }
            
            if score:
                history_item['score_details'] = {
                    'grade': score.grade,
                    'admin_decision': score.admin_decision,
                    'has_feedback': bool(score.admin_feedback)
                }
            
            history_data.append(history_item)
        
        return jsonify({
            'success': True,
            'history': history_data,
            'total_attempts': len(history_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get evaluation history: {str(e)}'
        }), 500