from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from datetime import datetime, timedelta
import secrets
import os

from models import db, User, PasswordReset

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test', methods=['GET'])
def test_route():
    print("=== TEST ROUTE CALLED ===")
    return jsonify({"message": "Auth route is working"}), 200

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("=== LOGIN ATTEMPT RECEIVED ===")
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_time = user.locked_until - datetime.utcnow()
            hours = int(remaining_time.total_seconds() // 3600)
            minutes = int((remaining_time.total_seconds() % 3600) // 60)
            return jsonify({
                'success': False,
                'message': f'Account locked due to multiple failed login attempts. Try again in {hours}h {minutes}m.',
                'locked_until': user.locked_until.isoformat()
            }), 423
        
        # Simple password check using bcrypt
        import bcrypt
        password_valid = False
        
        if user.password_hash.startswith('$2b$'):
            # bcrypt hash
            password_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
        else:
            # Try werkzeug for other hash types
            try:
                password_valid = check_password_hash(user.password_hash, password)
            except:
                password_valid = False
        
        if not password_valid:
            # Increment failed login attempts
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            
            # Lock account after 3 failed attempts for 24 hours
            if user.failed_login_attempts >= 3:
                user.locked_until = datetime.utcnow() + timedelta(hours=24)
                db.session.commit()
                return jsonify({
                    'success': False,
                    'message': 'Account locked for 24 hours due to 3 failed login attempts. Please try again later or contact support.',
                    'locked_until': user.locked_until.isoformat()
                }), 423
            
            db.session.commit()
            remaining_attempts = 3 - user.failed_login_attempts
            return jsonify({
                'success': False,
                'message': f'Invalid email or password. {remaining_attempts} attempts remaining before account lockout.',
                'remaining_attempts': remaining_attempts
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated. Please contact admin.'
            }), 403
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Login successful! Welcome back to SkillNova.',
            'user': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_mentor': user.is_mentor
            },
            'access_token': access_token
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("Signup attempt received")
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Name, email, and password are required'
            }), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 409
        
        # Create new user with bcrypt password hash
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(new_user.id))
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully! Welcome to SkillNova.',
            'user': {
                'id': str(new_user.id),
                'name': new_user.name,
                'email': new_user.email,
                'is_admin': new_user.is_admin,
                'is_mentor': new_user.is_mentor
            },
            'access_token': access_token
        }), 201
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_mentor': user.is_mentor,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get profile: {str(e)}'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        email = data['email'].strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'No account found with this email address'
            }), 404
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token in database
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        db.session.add(password_reset)
        db.session.commit()
        
        # Get frontend URL for the reset link
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        # Send email using the email service
        try:
            from email_service import email_service
            
            email_sent = email_service.send_password_reset_email(
                user.name, 
                email, 
                reset_link
            )
            
            if email_sent:
                return jsonify({
                    'success': True,
                    'message': 'Password reset instructions sent to your email'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send reset email. Please try again or contact support.'
                }), 500
                
        except Exception as email_error:
            print(f"❌ Email service error: {email_error}")
            return jsonify({
                'success': False,
                'message': 'Email service temporarily unavailable. Please try again later.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset failed: {str(e)}'
        }), 500

@auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Reset token and new password are required'
            }), 400
        
        token = data['token']
        new_password = data['new_password']
        
        # Find valid reset token
        reset_request = PasswordReset.query.filter_by(
            token=token,
            used=False
        ).first()
        
        if not reset_request:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired reset token'
            }), 400
        
        if reset_request.expires_at < datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Reset token has expired. Please request a new one.'
            }), 400
        
        # Update user password
        user = User.query.get(reset_request.user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Mark token as used
        reset_request.used = True
        
        db.session.commit()
        
        # Send confirmation email
        try:
            from email_service import email_service
            email_service.send_email(
                user.email,
                "Password Reset Successful - SkillNova",
                f"""
                <h2>Password Reset Successful</h2>
                <p>Dear {user.name},</p>
                <p>Your password has been successfully reset.</p>
                <p>If you did not make this change, please contact our support team immediately.</p>
                <p>Best regards,<br>SkillNova Team</p>
                """,
                f"Dear {user.name}, your password has been successfully reset. If you did not make this change, please contact support."
            )
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Password reset successful! You can now log in with your new password.'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset failed: {str(e)}'
        }), 500