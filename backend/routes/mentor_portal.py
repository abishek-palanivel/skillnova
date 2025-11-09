from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, User, MentorProfile, ChatRoom, ChatMessage, MentorSession, Mentor

mentor_portal_bp = Blueprint('mentor_portal', __name__)

def mentor_required(f):
    """Decorator to require mentor access"""
    def mentor_decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not (user.is_mentor or user.is_admin):
            return jsonify({
                'success': False,
                'message': 'Mentor access required'
            }), 403
        return f(*args, **kwargs)
    mentor_decorated_function.__name__ = f.__name__
    return mentor_decorated_function

@mentor_portal_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@mentor_required
def mentor_dashboard():
    """Get mentor dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Get mentor profile
        mentor_profile = MentorProfile.query.filter_by(user_id=user_id).first()
        
        # Get mentor record from mentors table
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        # Get mentor sessions statistics
        total_sessions = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_record.id
        ).count()
        
        completed_sessions = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_record.id,
            MentorSession.status == 'completed'
        ).count()
        
        pending_sessions = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_record.id,
            MentorSession.status == 'scheduled'
        ).count()
        
        # Get active chat rooms
        active_chats = ChatRoom.query.filter_by(
            mentor_id=user_id,
            is_active=True
        ).count()
        
        # Get total reviews (sessions with ratings)
        total_reviews = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_record.id,
            MentorSession.rating.isnot(None)
        ).count()
        
        # Calculate average rating from sessions
        rated_sessions = MentorSession.query.filter(
            MentorSession.mentor_id == mentor_record.id,
            MentorSession.rating.isnot(None)
        ).all()
        
        avg_rating = 0.0
        if rated_sessions:
            avg_rating = sum([s.rating for s in rated_sessions]) / len(rated_sessions)
        
        # Get recent messages
        recent_messages = db.session.query(ChatMessage).join(ChatRoom).filter(
            ChatRoom.mentor_id == user_id,
            ChatRoom.is_active == True
        ).order_by(ChatMessage.created_at.desc()).limit(5).all()
        
        dashboard_data = {
            'statistics': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'pending_sessions': pending_sessions,
                'active_chats': active_chats,
                'rating': avg_rating,
                'total_reviews': total_reviews
            },
            'mentor_profile': {
                'bio': mentor_profile.bio if mentor_profile else '',
                'expertise_areas': mentor_profile.expertise_areas if mentor_profile else '',
                'experience_years': mentor_profile.experience_years if mentor_profile else 0,
                'is_verified': mentor_profile.is_verified if mentor_profile else False
            },
            'recent_messages': [
                {
                    'id': str(msg.id),
                    'message_text': msg.message_text,
                    'sender_name': msg.sender.name,
                    'created_at': msg.created_at.isoformat(),
                    'room_id': str(msg.room_id)
                } for msg in recent_messages
            ]
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get mentor dashboard: {str(e)}'
        }), 500

@mentor_portal_bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()
@mentor_required
def mentor_profile():
    """Get or update mentor profile"""
    try:
        user_id = get_jwt_identity()
        
        if request.method == 'GET':
            profile = MentorProfile.query.filter_by(user_id=user_id).first()
            
            if not profile:
                return jsonify({
                    'success': True,
                    'profile': {
                        'bio': '',
                        'expertise_areas': '',
                        'experience_years': 0,
                        'hourly_rate': 0.0,
                        'linkedin_url': '',
                        'github_url': '',
                        'portfolio_url': '',
                        'is_verified': False,
                        'rating': 0.0
                    }
                }), 200
            
            return jsonify({
                'success': True,
                'profile': {
                    'bio': profile.bio,
                    'expertise_areas': profile.expertise_areas,
                    'experience_years': profile.experience_years,
                    'hourly_rate': profile.hourly_rate,
                    'linkedin_url': profile.linkedin_url,
                    'github_url': profile.github_url,
                    'portfolio_url': profile.portfolio_url,
                    'is_verified': profile.is_verified,
                    'rating': profile.rating,
                    'total_sessions': profile.total_sessions
                }
            }), 200
        
        elif request.method == 'POST':
            data = request.get_json()
            
            profile = MentorProfile.query.filter_by(user_id=user_id).first()
            
            if not profile:
                profile = MentorProfile(user_id=user_id)
                db.session.add(profile)
            
            # Update profile fields
            profile.bio = data.get('bio', profile.bio)
            profile.expertise_areas = data.get('expertise_areas', profile.expertise_areas)
            profile.experience_years = data.get('experience_years', profile.experience_years)
            profile.hourly_rate = data.get('hourly_rate', profile.hourly_rate)
            profile.linkedin_url = data.get('linkedin_url', profile.linkedin_url)
            profile.github_url = data.get('github_url', profile.github_url)
            profile.portfolio_url = data.get('portfolio_url', profile.portfolio_url)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to handle mentor profile: {str(e)}'
        }), 500

@mentor_portal_bp.route('/sessions', methods=['GET'])
@jwt_required()
@mentor_required
def get_mentor_sessions():
    """Get mentor's sessions"""
    try:
        user_id = get_jwt_identity()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        sessions = db.session.query(MentorSession).join(User, MentorSession.user_id == User.id).filter(
            MentorSession.mentor_id == mentor_record.id
        ).order_by(MentorSession.scheduled_at.desc()).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'user_name': session.user.name,
                'user_email': session.user.email,
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
            'message': f'Failed to get mentor sessions: {str(e)}'
        }), 500

@mentor_portal_bp.route('/chats', methods=['GET'])
@jwt_required()
@mentor_required
def get_mentor_chats():
    """Get mentor's active chat rooms"""
    try:
        user_id = get_jwt_identity()
        
        chat_rooms = ChatRoom.query.filter_by(
            mentor_id=user_id,
            is_active=True
        ).order_by(ChatRoom.updated_at.desc()).all()
        
        chats_data = []
        for room in chat_rooms:
            # Get last message
            last_message = ChatMessage.query.filter_by(
                room_id=room.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Count unread messages
            unread_count = ChatMessage.query.filter_by(
                room_id=room.id,
                is_read=False
            ).filter(ChatMessage.sender_id != user_id).count()
            
            chats_data.append({
                'id': str(room.id),
                'title': room.title or f"Chat with {room.user.name}",
                'user_name': room.user.name,
                'user_email': room.user.email,
                'last_message': {
                    'text': last_message.message_text if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else '',
                    'sender_name': last_message.sender.name if last_message else ''
                },
                'unread_count': unread_count,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'chats': chats_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get mentor chats: {str(e)}'
        }), 500

@mentor_portal_bp.route('/sessions/<session_id>', methods=['PUT'])
@jwt_required()
@mentor_required
def update_mentor_session(session_id):
    """Update mentor session status"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        session = MentorSession.query.filter_by(
            id=session_id,
            mentor_id=mentor_record.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        # Update session status
        if 'status' in data:
            session.status = data['status']
        
        # Update notes if provided
        if 'notes' in data:
            session.notes = data['notes']
        
        # Update rating if provided
        if 'rating' in data:
            session.rating = data['rating']
        
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update session: {str(e)}'
        }), 500

@mentor_portal_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
@mentor_required
def delete_mentor_session(session_id):
    """Delete mentor session"""
    try:
        user_id = get_jwt_identity()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        session = MentorSession.query.filter_by(
            id=session_id,
            mentor_id=mentor_record.id
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete session: {str(e)}'
        }), 500

@mentor_portal_bp.route('/students', methods=['GET'])
@jwt_required()
@mentor_required
def get_mentor_students():
    """Get list of students who have interacted with this mentor"""
    try:
        user_id = get_jwt_identity()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        # Get students from sessions
        session_students = db.session.query(User).join(MentorSession).filter(
            MentorSession.mentor_id == mentor_record.id
        ).distinct().all()
        
        # Get students from chats
        chat_students = db.session.query(User).join(ChatRoom, ChatRoom.user_id == User.id).filter(
            ChatRoom.mentor_id == user_id
        ).distinct().all()
        
        # Combine and deduplicate
        all_students = {}
        
        for student in session_students:
            all_students[str(student.id)] = {
                'id': str(student.id),
                'name': student.name,
                'email': student.email,
                'interaction_type': 'session',
                'created_at': student.created_at.isoformat()
            }
        
        for student in chat_students:
            if str(student.id) in all_students:
                all_students[str(student.id)]['interaction_type'] = 'both'
            else:
                all_students[str(student.id)] = {
                    'id': str(student.id),
                    'name': student.name,
                    'email': student.email,
                    'interaction_type': 'chat',
                    'created_at': student.created_at.isoformat()
                }
        
        return jsonify({
            'success': True,
            'students': list(all_students.values())
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get mentor students: {str(e)}'
        }), 500

@mentor_portal_bp.route('/sessions', methods=['POST'])
@jwt_required()
@mentor_required
def create_mentor_session():
    """Create a new mentor session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        # Find student by email
        student_email = data.get('user_email')
        student = User.query.filter_by(email=student_email).first()
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404
        
        # Create session
        new_session = MentorSession(
            mentor_id=mentor_record.id,
            user_id=student.id,
            scheduled_at=datetime.fromisoformat(data.get('scheduled_at').replace('T', ' ')),
            duration_minutes=data.get('duration_minutes', 60),
            notes=data.get('notes', ''),
            status='scheduled'
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session scheduled successfully',
            'session_id': str(new_session.id)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create session: {str(e)}'
        }), 500

@mentor_portal_bp.route('/students/<student_id>', methods=['DELETE'])
@jwt_required()
@mentor_required
def delete_mentor_student(student_id):
    """Remove a student from mentor's list"""
    try:
        user_id = get_jwt_identity()
        
        # Get mentor record
        user = User.query.get(user_id)
        mentor_record = Mentor.query.filter_by(email=user.email).first()
        
        if not mentor_record:
            return jsonify({
                'success': False,
                'message': 'Mentor record not found'
            }), 404
        
        # Delete all sessions with this student
        MentorSession.query.filter_by(
            mentor_id=mentor_record.id,
            user_id=student_id
        ).delete()
        
        # Deactivate chat rooms with this student
        ChatRoom.query.filter_by(
            mentor_id=user_id,
            user_id=student_id
        ).update({'is_active': False})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Student removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to remove student: {str(e)}'
        }), 500

@mentor_portal_bp.route('/send-email', methods=['POST'])
@jwt_required()
@mentor_required
def send_mentor_email():
    """Send email to student"""
    try:
        from email_service import send_email
        
        data = request.get_json()
        recipient_email = data.get('recipient_email')
        recipient_name = data.get('recipient_name')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([recipient_email, subject, message]):
            return jsonify({
                'success': False,
                'message': 'Recipient email, subject, and message are required'
            }), 400
        
        # Send email
        success = send_email(
            to_email=recipient_email,
            subject=subject,
            body=message,
            is_html=False
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }), 500

