from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from models import db, User, ChatRoom, ChatMessage, MentorProfile

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/test', methods=['GET'])
def test_chat_route():
    """Test route to verify chat blueprint is working"""
    return jsonify({
        'success': True,
        'message': 'Chat routes are working!'
    }), 200

@chat_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_user_chat_rooms():
    """Get user's chat rooms"""
    try:
        user_id = get_jwt_identity()
        
        # Convert string ID to UUID if needed
        try:
            import uuid
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
        except ValueError as ve:
            return jsonify({
                'success': False,
                'message': 'Invalid user ID format'
            }), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get all chat rooms where user is a participant
        chat_rooms = ChatRoom.query.filter(
            ChatRoom.is_active == True,
            db.or_(
                ChatRoom.user_id == user_id,
                ChatRoom.mentor_id == user_id,
                ChatRoom.admin_id == user_id
            )
        ).order_by(ChatRoom.updated_at.desc()).all()
        

        
        rooms_data = []
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
            
            # Determine other participant
            other_participant = None
            if room.room_type == 'user_mentor':
                if str(user_id) == str(room.user_id):
                    other_participant = room.mentor
                else:
                    other_participant = room.user
            elif room.room_type == 'user_admin':
                if str(user_id) == str(room.user_id):
                    other_participant = room.admin if room.admin_id else None
                elif str(user_id) == str(room.admin_id) if room.admin_id else False:
                    other_participant = room.user
                else:
                    # Handle peer-to-peer case or other scenarios
                    other_participant = room.user if str(user_id) != str(room.user_id) else None
            
            rooms_data.append({
                'id': str(room.id),
                'room_type': room.room_type,
                'title': room.title or f"Chat with {other_participant.name if other_participant else 'Unknown'}",
                'other_participant': {
                    'id': str(other_participant.id) if other_participant else '',
                    'name': other_participant.name if other_participant else 'Unknown',
                    'email': other_participant.email if other_participant else '',
                    'role': 'mentor' if other_participant and other_participant.is_mentor else 'admin' if other_participant and other_participant.is_admin else 'user'
                } if other_participant else None,
                'last_message': {
                    'text': last_message.message_text if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else '',
                    'sender_name': last_message.sender.name if last_message and last_message.sender else '',
                    'is_own': str(last_message.sender_id) == str(user_id) if last_message else False
                } if last_message else None,
                'unread_count': unread_count,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'rooms': rooms_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get chat rooms: {str(e)}'
        }), 500

@chat_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_chat_room():
    """Create a new chat room - supports all user types communicating with each other"""
    print("=== CHAT ROOM CREATION ATTEMPT ===")
    try:
        user_id = get_jwt_identity()
        print(f"Current user ID: {user_id}")
        
        # Handle both JSON and form data, or empty body
        try:
            data = request.get_json(force=True) or {}
        except:
            data = {}
        
        print(f"Request data: {data}")
        
        if not data:
            print("❌ No request data")
            return jsonify({
                'success': False,
                'message': 'Request data is required'
            }), 400
        
        target_user_id = data.get('target_user_id')
        title = data.get('title', '')
        
        print(f"Target user ID: {target_user_id}")
        
        if not target_user_id:
            print("❌ No target user ID")
            return jsonify({
                'success': False,
                'message': 'Target user ID is required'
            }), 400
        
        # Convert string IDs to UUID if needed
        try:
            import uuid
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            if isinstance(target_user_id, str):
                target_user_id = uuid.UUID(target_user_id)
        except ValueError as ve:
            return jsonify({
                'success': False,
                'message': f'Invalid ID format: {str(ve)}'
            }), 400
        
        # Validate users
        current_user = User.query.get(user_id)
        target_user = User.query.get(target_user_id)
        
        print(f"Current user found: {current_user is not None}")
        print(f"Target user found: {target_user is not None}")
        
        if not current_user or not target_user:
            print(f"❌ User not found - current: {current_user}, target: {target_user}")
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        if user_id == target_user_id:
            return jsonify({
                'success': False,
                'message': 'Cannot create chat room with yourself'
            }), 400
        
        # Determine room type and participants based on user roles
        room_type = None
        room_data = {
            'title': title or f"Chat with {target_user.name}",
            'is_active': True
        }
        
        # Check for existing room between these two users (regardless of who initiated)
        existing_room = None
        
        # Check all possible room configurations
        if current_user.is_admin or target_user.is_admin:
            # Admin involved - use user_admin type
            room_type = 'user_admin'
            
            # Find existing admin room
            existing_room = ChatRoom.query.filter(
                ChatRoom.room_type == 'user_admin',
                ChatRoom.is_active == True,
                db.or_(
                    db.and_(ChatRoom.user_id == user_id, ChatRoom.admin_id == target_user_id),
                    db.and_(ChatRoom.user_id == target_user_id, ChatRoom.admin_id == user_id)
                )
            ).first()
            
            if not existing_room:
                # Create new admin room
                if current_user.is_admin:
                    room_data['user_id'] = target_user_id
                    room_data['admin_id'] = user_id
                else:
                    room_data['user_id'] = user_id
                    room_data['admin_id'] = target_user_id
                    
        elif current_user.is_mentor or target_user.is_mentor:
            # Mentor involved - use user_mentor type
            room_type = 'user_mentor'
            
            # Find existing mentor room
            existing_room = ChatRoom.query.filter(
                ChatRoom.room_type == 'user_mentor',
                ChatRoom.is_active == True,
                db.or_(
                    db.and_(ChatRoom.user_id == user_id, ChatRoom.mentor_id == target_user_id),
                    db.and_(ChatRoom.user_id == target_user_id, ChatRoom.mentor_id == user_id)
                )
            ).first()
            
            if not existing_room:
                # Create new mentor room
                if current_user.is_mentor:
                    room_data['user_id'] = target_user_id
                    room_data['mentor_id'] = user_id
                else:
                    room_data['user_id'] = user_id
                    room_data['mentor_id'] = target_user_id
        else:
            # Both regular users - use user_admin type with admin as null (peer-to-peer)
            room_type = 'user_admin'
            
            # Find existing user room
            existing_room = ChatRoom.query.filter(
                ChatRoom.room_type == 'user_admin',
                ChatRoom.is_active == True,
                ChatRoom.admin_id.is_(None),
                db.or_(
                    ChatRoom.user_id == user_id,
                    ChatRoom.user_id == target_user_id
                )
            ).first()
            
            if not existing_room:
                # Create peer-to-peer room
                room_data['user_id'] = user_id
                room_data['admin_id'] = None
        
        if existing_room:
            return jsonify({
                'success': True,
                'room': {
                    'id': str(existing_room.id),
                    'message': 'Chat room already exists'
                }
            }), 200
        
        # Create new room
        room_data['room_type'] = room_type
        new_room = ChatRoom(**room_data)
        db.session.add(new_room)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'room': {
                'id': str(new_room.id),
                'message': 'Chat room created successfully'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Chat room creation error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({
            'success': False,
            'message': f'Failed to create chat room: {str(e)}'
        }), 500

@chat_bp.route('/rooms/<room_id>/messages', methods=['GET'])
@jwt_required()
def get_chat_messages(room_id):
    """Get messages from a chat room"""
    try:
        user_id = get_jwt_identity()
        
        # Convert string IDs to UUID if needed
        try:
            import uuid
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            if isinstance(room_id, str):
                room_id = uuid.UUID(room_id)
        except ValueError as ve:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        # Verify user has access to this room
        room = ChatRoom.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Chat room not found'
            }), 404
        
        # Check if user is participant in this room
        is_participant = (
            str(room.user_id) == str(user_id) or 
            str(room.mentor_id) == str(user_id) or 
            str(room.admin_id) == str(user_id)
        )
        
        if not is_participant:
            return jsonify({
                'success': False,
                'message': 'Access denied to this chat room'
            }), 403
        
        # Get messages
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        messages = ChatMessage.query.filter_by(
            room_id=room_id
        ).order_by(ChatMessage.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        messages_data = []
        for message in messages.items:
            # Ensure sender exists
            if not message.sender:
                continue
                
            messages_data.append({
                'id': str(message.id),
                'sender': {
                    'id': str(message.sender.id),
                    'name': message.sender.name,
                    'role': 'mentor' if message.sender.is_mentor else 'admin' if message.sender.is_admin else 'user'
                },
                'message_text': message.message_text,
                'message_type': message.message_type,
                'file_url': message.file_url,
                'is_read': message.is_read,
                'is_own': str(message.sender_id) == str(user_id),
                'created_at': message.created_at.isoformat()
            })
        
        # Mark messages as read for this user
        try:
            ChatMessage.query.filter_by(
                room_id=room_id,
                is_read=False
            ).filter(ChatMessage.sender_id != user_id).update({'is_read': True})
            db.session.commit()
        except Exception as mark_error:
            # Don't fail the request if marking as read fails
            print(f"Warning: Failed to mark messages as read: {mark_error}")
        
        # Reverse to show oldest first
        messages_data.reverse()
        
        return jsonify({
            'success': True,
            'messages': messages_data,
            'pagination': {
                'page': messages.page,
                'pages': messages.pages,
                'per_page': messages.per_page,
                'total': messages.total,
                'has_next': messages.has_next,
                'has_prev': messages.has_prev
            }
        }), 200
        
    except Exception as e:

        return jsonify({
            'success': False,
            'message': f'Failed to get chat messages: {str(e)}'
        }), 500

@chat_bp.route('/rooms/<room_id>/messages', methods=['POST'])
@jwt_required()
def send_chat_message(room_id):
    """Send a message to a chat room"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Convert string IDs to UUID if needed
        try:
            import uuid
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            if isinstance(room_id, str):
                room_id = uuid.UUID(room_id)
        except ValueError as ve:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        message_text = data.get('message_text', '').strip()
        message_type = data.get('message_type', 'text')
        
        if not message_text:
            return jsonify({
                'success': False,
                'message': 'Message text is required'
            }), 400
        
        # Verify user has access to this room
        room = ChatRoom.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Chat room not found'
            }), 404
        
        # Check if user is participant in this room
        is_participant = (
            str(room.user_id) == str(user_id) or 
            str(room.mentor_id) == str(user_id) or 
            str(room.admin_id) == str(user_id)
        )
        
        if not is_participant:
            return jsonify({
                'success': False,
                'message': 'Access denied to this chat room'
            }), 403
        
        # Create message
        new_message = ChatMessage(
            room_id=room_id,
            sender_id=user_id,
            message_text=message_text,
            message_type=message_type
        )
        
        db.session.add(new_message)
        
        # Update room's updated_at timestamp
        room.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Return the created message
        sender = User.query.get(user_id)
        if not sender:
            return jsonify({
                'success': False,
                'message': 'Sender not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': {
                'id': str(new_message.id),
                'sender': {
                    'id': str(sender.id),
                    'name': sender.name,
                    'role': 'mentor' if sender.is_mentor else 'admin' if sender.is_admin else 'user'
                },
                'message_text': new_message.message_text,
                'message_type': new_message.message_type,
                'is_own': True,
                'created_at': new_message.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()

        return jsonify({
            'success': False,
            'message': f'Failed to send message: {str(e)}'
        }), 500

@chat_bp.route('/mentors', methods=['GET'])
@jwt_required()
def get_available_mentors():
    """Get list of available mentors for chat"""
    try:
        mentors = User.query.filter_by(
            is_mentor=True,
            is_active=True
        ).all()
        
        mentors_data = []
        for mentor in mentors:
            profile = MentorProfile.query.filter_by(user_id=mentor.id).first()
            
            mentors_data.append({
                'id': str(mentor.id),
                'name': mentor.name,
                'email': mentor.email,
                'bio': profile.bio if profile else '',
                'expertise_areas': profile.expertise_areas if profile else '',
                'experience_years': profile.experience_years if profile else 0,
                'rating': profile.rating if profile else 0.0,
                'total_sessions': profile.total_sessions if profile else 0,
                'is_verified': profile.is_verified if profile else False
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

@chat_bp.route('/admins', methods=['GET'])
@jwt_required()
def get_available_admins():
    """Get list of available admins for chat"""
    try:
        current_user_id = get_jwt_identity()
        
        admins = User.query.filter(
            User.is_admin == True,
            User.is_active == True,
            User.id != current_user_id  # Exclude current user
        ).all()
        
        admins_data = []
        for admin in admins:
            admins_data.append({
                'id': str(admin.id),
                'name': admin.name,
                'email': admin.email,
                'role': 'Administrator'
            })
        
        return jsonify({
            'success': True,
            'admins': admins_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get admins: {str(e)}'
        }), 500

@chat_bp.route('/users', methods=['GET'])
@jwt_required()
def get_available_users():
    """Get list of available users for chat (for admins and mentors)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Current user not found'
            }), 404
        
        # Only admins and mentors can see all users
        if not (current_user.is_admin or current_user.is_mentor):
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Get all active users except current user
        users = User.query.filter(
            User.is_active == True,
            User.id != current_user_id
        ).all()
        
        users_data = []
        for user in users:
            role = 'Administrator' if user.is_admin else 'Mentor' if user.is_mentor else 'Student'
            users_data.append({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': role,
                'is_admin': user.is_admin,
                'is_mentor': user.is_mentor
            })
        
        return jsonify({
            'success': True,
            'users': users_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get users: {str(e)}'
        }), 500

@chat_bp.route('/messages/<message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a specific message"""
    try:
        user_id = get_jwt_identity()
        
        # Convert string ID to UUID if needed
        try:
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            if isinstance(message_id, str):
                message_id = uuid.UUID(message_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        # Find the message
        message = ChatMessage.query.get(message_id)
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        # Check if user is the sender or has admin privileges
        user = User.query.get(user_id)
        can_delete = (
            str(message.sender_id) == str(user_id) or  # Message sender
            (user and user.is_admin)  # Admin can delete any message
        )
        
        if not can_delete:
            return jsonify({
                'success': False,
                'message': 'You can only delete your own messages'
            }), 403
        
        # Delete the message
        db.session.delete(message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete message: {str(e)}'
        }), 500

@chat_bp.route('/rooms/<room_id>', methods=['DELETE'])
@jwt_required()
def delete_chat_room(room_id):
    """Delete an entire chat room and all its messages"""
    try:
        user_id = get_jwt_identity()
        
        # Convert string IDs to UUID if needed
        try:
            if isinstance(user_id, str):
                user_id = uuid.UUID(user_id)
            if isinstance(room_id, str):
                room_id = uuid.UUID(room_id)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid ID format'
            }), 400
        
        # Find the room
        room = ChatRoom.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Chat room not found'
            }), 404
        
        # Check if user is a participant or admin
        user = User.query.get(user_id)
        is_participant = (
            str(room.user_id) == str(user_id) or 
            str(room.mentor_id) == str(user_id) or 
            str(room.admin_id) == str(user_id)
        )
        
        can_delete = is_participant or (user and user.is_admin)
        
        if not can_delete:
            return jsonify({
                'success': False,
                'message': 'Access denied to delete this chat room'
            }), 403
        
        # Delete all messages in the room first
        ChatMessage.query.filter_by(room_id=room_id).delete()
        
        # Delete the room
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chat room deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete chat room: {str(e)}'
        }), 500

@chat_bp.route('/rooms/<room_id>/rate', methods=['POST'])
@jwt_required()
def rate_chat_session(room_id):
    """Rate a chat session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        rating = data.get('rating')
        feedback = data.get('feedback', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'message': 'Rating must be between 1 and 5'
            }), 400
        
        # Verify user has access to this room
        room = ChatRoom.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Chat room not found'
            }), 404
        
        # Check if user is participant in this room
        is_participant = (
            room.user_id == user_id or 
            room.mentor_id == user_id or 
            room.admin_id == user_id
        )
        
        if not is_participant:
            return jsonify({
                'success': False,
                'message': 'Access denied to this chat room'
            }), 403
        
        # Update room rating
        room.rating = rating
        room.feedback = feedback
        room.rated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to submit rating: {str(e)}'
        }), 500