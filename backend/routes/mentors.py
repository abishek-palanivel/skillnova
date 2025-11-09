from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from models import db, Mentor, MentorSession

mentors_bp = Blueprint('mentors', __name__)

@mentors_bp.route('/', methods=['GET', 'OPTIONS'])
def get_mentors():
    """Get all available mentors - Public endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        mentors = Mentor.query.filter_by(is_available=True).all()
        
        mentors_data = []
        for mentor in mentors:
            mentors_data.append({
                'id': str(mentor.id),
                'name': mentor.name,
                'email': mentor.email,
                'expertise': mentor.expertise,
                'experience_years': mentor.experience_years,
                'rating': mentor.rating,
                'total_sessions': len(mentor.sessions),
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

@mentors_bp.route('/<mentor_id>/book-session', methods=['POST'])
@jwt_required()
def book_mentor_session(mentor_id):
    """Book a session with a specific mentor"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Check if mentor exists and is available
        mentor = Mentor.query.get(mentor_id)
        if not mentor or not mentor.is_available:
            return jsonify({
                'success': False,
                'message': 'Mentor not found or unavailable'
            }), 404
        
        # For demo purposes, create a session with default scheduling
        from datetime import datetime, timedelta
        scheduled_at = datetime.utcnow() + timedelta(days=7)  # Schedule for next week
        duration_minutes = data.get('duration_minutes', 60)
        
        # Create mentor session
        session = MentorSession(
            user_id=user_id,
            mentor_id=mentor_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Session booking request sent to {mentor.name}',
            'session': {
                'id': str(session.id),
                'mentor_name': mentor.name,
                'scheduled_at': session.scheduled_at.isoformat(),
                'duration_minutes': session.duration_minutes,
                'status': session.status,
                'created_at': session.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to book session: {str(e)}'
        }), 500

@mentors_bp.route('/book', methods=['POST'])
@jwt_required()
def book_mentor_session_legacy():
    """Book a session with a mentor"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('mentor_id') or not data.get('scheduled_at'):
            return jsonify({
                'success': False,
                'message': 'Mentor ID and scheduled time are required'
            }), 400
        
        mentor_id = data['mentor_id']
        scheduled_at_str = data['scheduled_at']
        duration_minutes = data.get('duration_minutes', 60)
        
        # Parse scheduled time
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid date format. Use ISO format.'
            }), 400
        
        # Check if mentor exists and is available
        mentor = Mentor.query.get(mentor_id)
        if not mentor or not mentor.is_available:
            return jsonify({
                'success': False,
                'message': 'Mentor not found or unavailable'
            }), 404
        
        # Check if scheduled time is in the future
        if scheduled_at <= datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Session must be scheduled for a future time'
            }), 400
        
        # Check for conflicting sessions (simple check - same mentor, overlapping time)
        session_end = scheduled_at + timedelta(minutes=duration_minutes)
        conflicting_sessions = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_id,
            MentorSession.status == 'scheduled',
            MentorSession.scheduled_at < session_end,
            MentorSession.scheduled_at + timedelta(minutes=MentorSession.duration_minutes) > scheduled_at
        ).first()
        
        if conflicting_sessions:
            return jsonify({
                'success': False,
                'message': 'Mentor is not available at the requested time'
            }), 409
        
        # Create mentor session
        session = MentorSession(
            user_id=user_id,
            mentor_id=mentor_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Session booked successfully with {mentor.name}',
            'session': {
                'id': str(session.id),
                'mentor_name': mentor.name,
                'scheduled_at': session.scheduled_at.isoformat(),
                'duration_minutes': session.duration_minutes,
                'status': session.status,
                'created_at': session.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to book session: {str(e)}'
        }), 500

@mentors_bp.route('/my-sessions', methods=['GET'])
@jwt_required()
def get_my_sessions():
    """Get user's mentor sessions"""
    try:
        user_id = get_jwt_identity()
        
        sessions = MentorSession.query.filter_by(user_id=user_id).order_by(
            MentorSession.scheduled_at.desc()
        ).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'mentor': {
                    'id': str(session.mentor.id),
                    'name': session.mentor.name,
                    'expertise': session.mentor.expertise
                },
                'scheduled_at': session.scheduled_at.isoformat(),
                'duration_minutes': session.duration_minutes,
                'status': session.status,
                'notes': session.notes,
                'rating': session.rating,
                'created_at': session.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get sessions: {str(e)}'
        }), 500

@mentors_bp.route('/sessions/<session_id>/complete', methods=['PUT'])
@jwt_required()
def complete_session(session_id):
    """Mark session as completed and add notes/rating"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get session
        session = MentorSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        if session.status != 'scheduled':
            return jsonify({
                'success': False,
                'message': 'Session is not in scheduled status'
            }), 400
        
        # Update session
        session.status = 'completed'
        session.notes = data.get('notes', '')
        session.rating = data.get('rating')
        
        # Validate rating
        if session.rating and not 1 <= session.rating <= 5:
            return jsonify({
                'success': False,
                'message': 'Rating must be between 1 and 5'
            }), 400
        
        db.session.commit()
        
        # Update mentor's average rating
        if session.rating:
            mentor = session.mentor
            completed_sessions = MentorSession.query.filter_by(
                mentor_id=mentor.id,
                status='completed'
            ).filter(MentorSession.rating.isnot(None)).all()
            
            if completed_sessions:
                total_rating = sum([s.rating for s in completed_sessions])
                mentor.rating = total_rating / len(completed_sessions)
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session completed successfully',
            'session': {
                'id': str(session.id),
                'status': session.status,
                'notes': session.notes,
                'rating': session.rating
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to complete session: {str(e)}'
        }), 500

@mentors_bp.route('/sessions/<session_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_session(session_id):
    """Cancel a scheduled session"""
    try:
        user_id = get_jwt_identity()
        
        # Get session
        session = MentorSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        if session.status != 'scheduled':
            return jsonify({
                'success': False,
                'message': 'Only scheduled sessions can be cancelled'
            }), 400
        
        # Check if session is at least 24 hours away
        time_until_session = session.scheduled_at - datetime.utcnow()
        if time_until_session < timedelta(hours=24):
            return jsonify({
                'success': False,
                'message': 'Sessions can only be cancelled at least 24 hours in advance'
            }), 400
        
        # Cancel session
        session.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to cancel session: {str(e)}'
        }), 500