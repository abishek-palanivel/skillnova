from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os
import uuid
import secrets
import string

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User, VideoCall

video_calls_bp = Blueprint('video_calls', __name__)

def generate_room_id():
    """Generate a unique room ID for video calls"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

@video_calls_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_video_call():
    """Initiate a video call with real-time notification"""
    print("=" * 50)
    print("🎥 VIDEO CALL INITIATION")
    print("=" * 50)
    try:
        from notification_service import notification_service
        
        current_user_id = get_jwt_identity()
        print(f"Current user ID: {current_user_id}")
        
        # Convert to UUID if string
        if isinstance(current_user_id, str):
            current_user_id = uuid.UUID(current_user_id)
        
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            print(f"❌ Current user not found: {current_user_id}")
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        print(f"Current user: {current_user.name} (Admin: {current_user.is_admin}, Mentor: {current_user.is_mentor})")
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        participant_id = data.get('participant_id')
        participant_email = data.get('participant_email')
        
        # Find participant by ID or email
        participant = None
        if participant_id:
            # Convert to UUID if string
            if isinstance(participant_id, str):
                participant_id = uuid.UUID(participant_id)
            participant = User.query.get(participant_id)
        elif participant_email:
            participant = User.query.filter_by(email=participant_email.lower().strip()).first()
        
        if not participant:
            print(f"❌ Participant not found: {participant_id or participant_email}")
            return jsonify({
                'success': False,
                'message': 'Participant not found'
            }), 404
        
        print(f"Participant: {participant.name} (Admin: {participant.is_admin}, Mentor: {participant.is_mentor})")
        
        # Determine call type
        if current_user.is_admin and participant.is_mentor:
            call_type = 'admin_mentor'
        elif current_user.is_admin and not participant.is_mentor and not participant.is_admin:
            call_type = 'admin_user'
        elif current_user.is_mentor and not participant.is_mentor and not participant.is_admin:
            call_type = 'mentor_user'
        elif not current_user.is_mentor and not current_user.is_admin and participant.is_mentor:
            call_type = 'mentor_user'
        elif not current_user.is_mentor and not current_user.is_admin and participant.is_admin:
            call_type = 'admin_user'
        elif current_user.is_mentor and participant.is_admin:
            call_type = 'admin_mentor'
        else:
            print(f"❌ Invalid call type - Current: Admin={current_user.is_admin}, Mentor={current_user.is_mentor} | Participant: Admin={participant.is_admin}, Mentor={participant.is_mentor}")
            return jsonify({
                'success': False,
                'message': 'Invalid call type'
            }), 400
        
        print(f"Call type determined: {call_type}")
        
        # Check if there's already an active call between these users
        # Convert both IDs to UUID for proper comparison
        current_user_uuid = current_user_id if isinstance(current_user_id, uuid.UUID) else uuid.UUID(str(current_user_id))
        participant_uuid = participant.id if isinstance(participant.id, uuid.UUID) else uuid.UUID(str(participant.id))
        
        existing_call = VideoCall.query.filter(
            db.or_(
                db.and_(
                    VideoCall.initiator_id == current_user_uuid,
                    VideoCall.participant_id == participant_uuid
                ),
                db.and_(
                    VideoCall.initiator_id == participant_uuid,
                    VideoCall.participant_id == current_user_uuid
                )
            ),
            VideoCall.status.in_(['waiting', 'active'])
        ).first()
        
        if existing_call:
            print(f"⚠️ Existing active call found: {existing_call.id} - Status: {existing_call.status}")
            return jsonify({
                'success': False,
                'message': 'There is already an active call between these users',
                'existing_call': {
                    'id': str(existing_call.id),
                    'room_id': existing_call.room_id,
                    'status': existing_call.status
                }
            }), 409
        
        # Create new video call
        room_id = generate_room_id()
        
        video_call = VideoCall(
            room_id=room_id,
            initiator_id=current_user_id,
            participant_id=participant.id,
            call_type=call_type,
            status='waiting'
        )
        
        db.session.add(video_call)
        db.session.flush()  # Get the call ID
        
        print(f"✅ Video call created: {video_call.id}")
        
        # Create notification for participant (the person being called)
        participant_notification = notification_service.create_video_call_notification(
            user_id=str(participant.id),
            caller_name=current_user.name,
            call_id=str(video_call.id),
            room_id=room_id
        )
        
        print(f"📧 Participant notification created: {participant_notification['success']}")
        
        # Create notification for initiator (confirmation that call was initiated)
        initiator_notification = notification_service.create_notification(
            user_id=str(current_user.id),
            notification_type='video_call',
            title='Video Call Initiated',
            message=f'Calling {participant.name}... Waiting for response',
            data={
                'call_id': str(video_call.id),
                'room_id': room_id,
                'participant_name': participant.name,
                'type': 'outgoing_call'
            }
        )
        
        print(f"📧 Initiator notification created: {initiator_notification['success']}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video call initiated successfully and notifications sent',
            'call': {
                'id': str(video_call.id),
                'room_id': room_id,
                'call_type': call_type,
                'status': 'waiting',
                'initiator': {
                    'id': str(current_user.id),
                    'name': current_user.name,
                    'is_admin': current_user.is_admin,
                    'is_mentor': current_user.is_mentor
                },
                'participant': {
                    'id': str(participant.id),
                    'name': participant.name,
                    'is_admin': participant.is_admin,
                    'is_mentor': participant.is_mentor
                },
                'created_at': video_call.created_at.isoformat()
            },
            'notifications_sent': {
                'participant': participant_notification['success'],
                'initiator': initiator_notification['success']
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Video call initiation error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({
            'success': False,
            'message': f'Failed to initiate video call: {str(e)}'
        }), 500

@video_calls_bp.route('/join/<room_id>', methods=['POST'])
@jwt_required()
def join_video_call(room_id):
    """Join a video call"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        video_call = VideoCall.query.filter_by(room_id=room_id).first()
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user is authorized to join this call
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to join this call'
            }), 403
        
        if video_call.status == 'ended':
            return jsonify({
                'success': False,
                'message': 'This call has already ended'
            }), 400
        
        # Update call status to active
        video_call.status = 'active'
        if not video_call.started_at:
            video_call.started_at = datetime.utcnow()
        
        db.session.commit()
        
        # Get other participant info
        other_user_id = video_call.participant_id if video_call.initiator_id == current_user_id else video_call.initiator_id
        other_user = User.query.get(other_user_id)
        
        return jsonify({
            'success': True,
            'message': 'Joined video call successfully',
            'call': {
                'id': str(video_call.id),
                'room_id': room_id,
                'status': 'active',
                'call_type': video_call.call_type,
                'other_participant': {
                    'id': str(other_user.id),
                    'name': other_user.name,
                    'is_admin': other_user.is_admin,
                    'is_mentor': other_user.is_mentor
                } if other_user else None,
                'started_at': video_call.started_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to join video call: {str(e)}'
        }), 500

@video_calls_bp.route('/end/<room_id>', methods=['POST'])
@jwt_required()
def end_video_call(room_id):
    """End a video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.filter_by(room_id=room_id).first()
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user is authorized to end this call
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to end this call'
            }), 403
        
        if video_call.status == 'ended':
            return jsonify({
                'success': False,
                'message': 'This call has already ended'
            }), 400
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration_minutes = 0
        
        if video_call.started_at:
            duration = end_time - video_call.started_at
            duration_minutes = int(duration.total_seconds() / 60)
        
        # Update call status
        video_call.status = 'ended'
        video_call.ended_at = end_time
        video_call.duration_minutes = duration_minutes
        
        # Add call notes if provided
        data = request.get_json() or {}
        if data.get('notes'):
            video_call.call_notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video call ended successfully',
            'call': {
                'id': str(video_call.id),
                'room_id': room_id,
                'status': 'ended',
                'duration_minutes': duration_minutes,
                'ended_at': end_time.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to end video call: {str(e)}'
        }), 500

@video_calls_bp.route('/my-calls', methods=['GET'])
@jwt_required()
def get_my_calls():
    """Get user's video call history"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Get calls where user is either initiator or participant
        calls = VideoCall.query.filter(
            (VideoCall.initiator_id == current_user_id) | 
            (VideoCall.participant_id == current_user_id)
        ).order_by(VideoCall.created_at.desc()).all()
        
        calls_data = []
        for call in calls:
            # Get other participant info
            other_user_id = call.participant_id if call.initiator_id == current_user_id else call.initiator_id
            other_user = User.query.get(other_user_id) if other_user_id else None
            
            calls_data.append({
                'id': str(call.id),
                'room_id': call.room_id,
                'call_type': call.call_type,
                'status': call.status,
                'is_initiator': call.initiator_id == current_user_id,
                'other_participant': {
                    'id': str(other_user.id),
                    'name': other_user.name,
                    'is_admin': other_user.is_admin,
                    'is_mentor': other_user.is_mentor
                } if other_user else None,
                'duration_minutes': call.duration_minutes,
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'created_at': call.created_at.isoformat(),
                'call_notes': call.call_notes,
                'rating': call.rating
            })
        
        return jsonify({
            'success': True,
            'calls': calls_data,
            'user_info': {
                'id': str(current_user.id),
                'name': current_user.name,
                'is_admin': current_user.is_admin,
                'is_mentor': current_user.is_mentor
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get call history: {str(e)}'
        }), 500

@video_calls_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_calls():
    """Get active video calls for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get active calls where user is either initiator or participant
        active_calls = VideoCall.query.filter(
            ((VideoCall.initiator_id == current_user_id) | 
             (VideoCall.participant_id == current_user_id)),
            VideoCall.status.in_(['waiting', 'active'])
        ).all()
        
        calls_data = []
        for call in active_calls:
            # Get other participant info
            other_user_id = call.participant_id if call.initiator_id == current_user_id else call.initiator_id
            other_user = User.query.get(other_user_id) if other_user_id else None
            
            calls_data.append({
                'id': str(call.id),
                'room_id': call.room_id,
                'call_type': call.call_type,
                'status': call.status,
                'is_initiator': call.initiator_id == current_user_id,
                'other_participant': {
                    'id': str(other_user.id),
                    'name': other_user.name,
                    'is_admin': other_user.is_admin,
                    'is_mentor': other_user.is_mentor
                } if other_user else None,
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'created_at': call.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'active_calls': calls_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get active calls: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>/rate', methods=['POST'])
@jwt_required()
def rate_video_call(call_id):
    """Rate a completed video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user participated in this call
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to rate this call'
            }), 403
        
        if video_call.status != 'ended':
            return jsonify({
                'success': False,
                'message': 'Can only rate completed calls'
            }), 400
        
        data = request.get_json()
        rating = data.get('rating')
        feedback = data.get('feedback', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'message': 'Rating must be between 1 and 5'
            }), 400
        
        video_call.rating = rating
        video_call.feedback = feedback
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Call rated successfully',
            'rating': rating,
            'feedback': feedback
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to rate call: {str(e)}'
        }), 500

@video_calls_bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_calls_admin():
    """Get all video calls for admin monitoring"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        # Get all calls with pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        calls_query = VideoCall.query.order_by(VideoCall.created_at.desc())
        calls_pagination = calls_query.paginate(page=page, per_page=per_page, error_out=False)
        
        calls_data = []
        for call in calls_pagination.items:
            initiator = User.query.get(call.initiator_id)
            participant = User.query.get(call.participant_id) if call.participant_id else None
            
            calls_data.append({
                'id': str(call.id),
                'room_id': call.room_id,
                'call_type': call.call_type,
                'status': call.status,
                'initiator': {
                    'id': str(initiator.id),
                    'name': initiator.name,
                    'email': initiator.email,
                    'is_admin': initiator.is_admin,
                    'is_mentor': initiator.is_mentor
                } if initiator else None,
                'participant': {
                    'id': str(participant.id),
                    'name': participant.name,
                    'email': participant.email,
                    'is_admin': participant.is_admin,
                    'is_mentor': participant.is_mentor
                } if participant else None,
                'duration_minutes': call.duration_minutes,
                'rating': call.rating,
                'feedback': call.feedback,
                'started_at': call.started_at.isoformat() if call.started_at else None,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'created_at': call.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'calls': calls_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': calls_pagination.total,
                'pages': calls_pagination.pages,
                'has_next': calls_pagination.has_next,
                'has_prev': calls_pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get all calls: {str(e)}'
        }), 500

@video_calls_bp.route('/incoming', methods=['GET'])
@jwt_required()
def get_incoming_calls():
    """Get incoming video calls for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get calls where current user is the participant and status is waiting
        incoming_calls = VideoCall.query.filter(
            VideoCall.participant_id == current_user_id,
            VideoCall.status == 'waiting'
        ).order_by(VideoCall.created_at.desc()).all()
        
        calls_data = []
        for call in incoming_calls:
            initiator = User.query.get(call.initiator_id)
            
            calls_data.append({
                'id': str(call.id),
                'room_id': call.room_id,
                'title': f'Video Call from {initiator.name}' if initiator else 'Video Call',
                'description': f'Incoming video call from {initiator.name}',
                'mentor_name': initiator.name if initiator else 'Unknown',
                'call_type': call.call_type,
                'status': call.status,
                'created_at': call.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'calls': calls_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get incoming calls: {str(e)}'
        }), 500

@video_calls_bp.route('/scheduled', methods=['GET'])
@jwt_required()
def get_scheduled_calls():
    """Get scheduled video calls for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # For now, return empty array as we don't have scheduled calls implemented
        # This can be extended later to support scheduled calls
        
        return jsonify({
            'success': True,
            'calls': []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get scheduled calls: {str(e)}'
        }), 500

@video_calls_bp.route('/history', methods=['GET'])
@jwt_required()
def get_call_history():
    """Get video call history for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get completed calls where user participated
        history_calls = VideoCall.query.filter(
            ((VideoCall.initiator_id == current_user_id) | 
             (VideoCall.participant_id == current_user_id)),
            VideoCall.status == 'ended'
        ).order_by(VideoCall.ended_at.desc()).all()
        
        calls_data = []
        for call in history_calls:
            # Get other participant info
            other_user_id = call.participant_id if call.initiator_id == current_user_id else call.initiator_id
            other_user = User.query.get(other_user_id) if other_user_id else None
            
            # Determine status based on call completion
            status = 'completed' if call.duration_minutes and call.duration_minutes > 0 else 'missed'
            
            calls_data.append({
                'id': str(call.id),
                'title': f'Video Call with {other_user.name}' if other_user else 'Video Call',
                'mentor_name': other_user.name if other_user else 'Unknown',
                'status': status,
                'duration': call.duration_minutes,
                'notes': call.call_notes,
                'rating': call.rating,
                'created_at': call.created_at.isoformat(),
                'ended_at': call.ended_at.isoformat() if call.ended_at else None
            })
        
        return jsonify({
            'success': True,
            'calls': calls_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get call history: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>/accept', methods=['POST'])
@jwt_required()
def accept_call(call_id):
    """Accept an incoming video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if current user is the participant
        if str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to accept this call'
            }), 403
        
        if video_call.status != 'waiting':
            return jsonify({
                'success': False,
                'message': 'Call is no longer available'
            }), 400
        
        # Update call status to active
        video_call.status = 'active'
        video_call.started_at = datetime.utcnow()
        
        # Get initiator info
        initiator = User.query.get(video_call.initiator_id)
        current_user = User.query.get(current_user_id)
        
        # Notify initiator that call was accepted
        if initiator:
            from notification_service import notification_service
            notification_service.create_notification(
                user_id=str(initiator.id),
                notification_type='video_call',
                title='Call Accepted',
                message=f'{current_user.name if current_user else "User"} accepted your call',
                data={
                    'call_id': str(video_call.id),
                    'room_id': video_call.room_id,
                    'type': 'call_accepted'
                }
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Call accepted successfully',
            'room_id': video_call.room_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to accept call: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>/reject', methods=['POST'])
@jwt_required()
def reject_call(call_id):
    """Reject an incoming video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if current user is the participant
        if str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to reject this call'
            }), 403
        
        if video_call.status != 'waiting':
            return jsonify({
                'success': False,
                'message': 'Call is no longer available'
            }), 400
        
        # Update call status to rejected
        video_call.status = 'rejected'
        video_call.ended_at = datetime.utcnow()
        
        # Get initiator info
        initiator = User.query.get(video_call.initiator_id)
        current_user = User.query.get(current_user_id)
        
        # Notify initiator that call was rejected
        if initiator:
            from notification_service import notification_service
            notification_service.create_notification(
                user_id=str(initiator.id),
                notification_type='video_call',
                title='Call Declined',
                message=f'{current_user.name if current_user else "User"} declined your call',
                data={
                    'call_id': str(video_call.id),
                    'type': 'call_rejected'
                }
            )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Call rejected successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to reject call: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>/join', methods=['POST'])
@jwt_required()
def join_scheduled_call(call_id):
    """Join a scheduled video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user is authorized to join
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to join this call'
            }), 403
        
        # Update call status if needed
        if video_call.status == 'scheduled':
            video_call.status = 'active'
            video_call.started_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Joined call successfully',
            'room_id': video_call.room_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to join call: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>', methods=['GET'])
@jwt_required()
def get_call_details(call_id):
    """Get video call details"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user is authorized to view this call
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to view this call'
            }), 403
        
        # Get participant info
        initiator = User.query.get(video_call.initiator_id)
        participant = User.query.get(video_call.participant_id) if video_call.participant_id else None
        
        # Determine mentor name based on who is the mentor
        mentor_name = None
        if initiator and initiator.is_mentor:
            mentor_name = initiator.name
        elif participant and participant.is_mentor:
            mentor_name = participant.name
        
        call_data = {
            'id': str(video_call.id),
            'room_id': video_call.room_id,
            'title': f'Video Call with {mentor_name}' if mentor_name else 'Video Call',
            'mentor_name': mentor_name,
            'call_type': video_call.call_type,
            'status': video_call.status,
            'initiator': {
                'id': str(initiator.id),
                'name': initiator.name,
                'is_mentor': initiator.is_mentor
            } if initiator else None,
            'participant': {
                'id': str(participant.id),
                'name': participant.name,
                'is_mentor': participant.is_mentor
            } if participant else None,
            'started_at': video_call.started_at.isoformat() if video_call.started_at else None,
            'created_at': video_call.created_at.isoformat()
        }
        
        return jsonify({
            'success': True,
            'call': call_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get call details: {str(e)}'
        }), 500

@video_calls_bp.route('/<call_id>/end', methods=['POST'])
@jwt_required()
def end_call(call_id):
    """End a video call"""
    try:
        current_user_id = get_jwt_identity()
        
        video_call = VideoCall.query.get(call_id)
        if not video_call:
            return jsonify({
                'success': False,
                'message': 'Video call not found'
            }), 404
        
        # Check if user is authorized to end this call
        if str(video_call.initiator_id) != str(current_user_id) and str(video_call.participant_id) != str(current_user_id):
            return jsonify({
                'success': False,
                'message': 'You are not authorized to end this call'
            }), 403
        
        if video_call.status == 'ended':
            return jsonify({
                'success': False,
                'message': 'Call has already ended'
            }), 400
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration_minutes = 0
        
        if video_call.started_at:
            duration = end_time - video_call.started_at
            duration_minutes = int(duration.total_seconds() / 60)
        
        # Update call status
        video_call.status = 'ended'
        video_call.ended_at = end_time
        video_call.duration_minutes = duration_minutes
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Call ended successfully',
            'duration_minutes': duration_minutes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to end call: {str(e)}'
        }), 500