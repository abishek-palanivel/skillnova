from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
import sys

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abi%401234@localhost:5432/skillnova'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'skillnova-jwt-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
from models import db
db.init_app(app)
jwt = JWTManager(app)

# Configure CORS - Allow all origins for development
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
     supports_credentials=True,
     expose_headers=["Content-Type", "Authorization"],
     send_wildcard=False,
     vary_header=True)

# Import models after db initialization will be done in routes

def create_admin_user():
    """Create or update admin and mentor users with consistent passwords"""
    try:
        from models import User
        import bcrypt
        
        # Use a fixed salt for consistent password hashing
        fixed_salt = b'$2b$12$SkillNovaAdminSalt123456'
        password_hash = bcrypt.hashpw("abi@1234".encode('utf-8'), fixed_salt).decode('utf-8')
        
        # Create/Update Admin User (Pure Admin - no mentor privileges)
        admin = User.query.filter_by(email='abishekopennova@gmail.com').first()
        if not admin:
            print("Creating admin user...")
            admin_user = User(
                name="Abishek (Admin)",
                email="abishekopennova@gmail.com",
                password_hash=password_hash,
                is_admin=True,
                is_mentor=False,  # Pure admin
                is_active=True
            )
            db.session.add(admin_user)
            print("✅ Admin user created successfully!")
        else:
            # Update existing admin user
            admin.password_hash = password_hash
            admin.is_admin = True
            admin.is_mentor = False  # Ensure pure admin
            admin.is_active = True
            admin.name = "Abishek (Admin)"
            print("✅ Admin user updated!")
        
        # Create/Update Mentor User (Pure Mentor - no admin privileges)
        mentor = User.query.filter_by(email='abishekpopennova@gmail.com').first()
        if not mentor:
            print("Creating mentor user...")
            mentor_user = User(
                name="Abishek P (Mentor)",
                email="abishekpopennova@gmail.com",
                password_hash=password_hash,
                is_admin=False,  # Pure mentor
                is_mentor=True,
                is_active=True
            )
            db.session.add(mentor_user)
            print("✅ Mentor user created successfully!")
        else:
            # Update existing mentor user
            mentor.password_hash = password_hash
            mentor.is_admin = False  # Ensure pure mentor
            mentor.is_mentor = True
            mentor.is_active = True
            mentor.name = "Abishek P (Mentor)"
            print("✅ Mentor user updated!")
        
        # Create/Update Regular User
        regular_user = User.query.filter_by(email='abishekpalanivel212@gmail.com').first()
        if not regular_user:
            print("Creating regular user...")
            user = User(
                name="Abishek Palanivel",
                email="abishekpalanivel212@gmail.com",
                password_hash=password_hash,
                is_admin=False,
                is_mentor=False,
                is_active=True
            )
            db.session.add(user)
            print("✅ Regular user created successfully!")
        else:
            # Update existing regular user
            regular_user.password_hash = password_hash
            regular_user.is_admin = False
            regular_user.is_mentor = False
            regular_user.is_active = True
            regular_user.name = "Abishek Palanivel"
            print("✅ Regular user updated!")
        
        db.session.commit()
        print("✅ All users synchronized successfully!")
            
    except Exception as e:
        print(f"❌ User setup error: {e}")
        # Fallback to werkzeug if bcrypt fails
        try:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash("abi@1234")
            
            # Update admin
            admin = User.query.filter_by(email='abishekopennova@gmail.com').first()
            if admin:
                admin.password_hash = password_hash
                admin.is_admin = True
                admin.is_mentor = False
            
            # Update mentor
            mentor = User.query.filter_by(email='abishekpopennova@gmail.com').first()
            if mentor:
                mentor.password_hash = password_hash
                mentor.is_admin = False
                mentor.is_mentor = True
            
            db.session.commit()
            print("✅ Users updated with fallback method!")
        except Exception as fallback_error:
            print(f"❌ Fallback user setup also failed: {fallback_error}")

# Import and register blueprints after app context is ready
def register_blueprints():
    try:
        print("📦 Registering blueprints...")
        
        from routes.auth import auth_bp
        print("✓ Auth blueprint imported")
        
        from routes.user import user_bp
        print("✓ User blueprint imported")
        
        from routes.admin import admin_bp
        print("✓ Admin blueprint imported")
        
        from routes.courses import courses_bp
        print("✓ Courses blueprint imported")
        
        from routes.mentors import mentors_bp
        print("✓ Mentors blueprint imported")
        
        from routes.practice import practice_bp
        print("✓ Practice blueprint imported")
        
        from routes.tests import tests_bp
        print("✓ Tests blueprint imported")

        from routes.assessments import assessments_bp
        print("✓ Assessments blueprint imported")
        
        from routes.certificates import certificates_bp
        print("✓ Certificates blueprint imported")
        
        from routes.mentor_portal import mentor_portal_bp
        print("✓ Mentor portal blueprint imported")
        
        from routes.chat import chat_bp
        print("✓ Chat blueprint imported")
        
        from routes.weekly_evaluations import weekly_evaluations_bp
        print("✓ Weekly evaluations blueprint imported")
        
        from routes.video_calls import video_calls_bp
        print("✓ Video calls blueprint imported")
        
        from routes.notifications import notifications_bp
        print("✓ Notifications blueprint imported")
        
        from routes.final_projects import final_projects_bp
        print("✓ Final projects blueprint imported")
        
        # Register all blueprints
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("✓ Auth routes registered at /api/auth")
        
        app.register_blueprint(user_bp, url_prefix='/api/user')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(courses_bp, url_prefix='/api/courses')
        app.register_blueprint(mentors_bp, url_prefix='/api/mentors')
        app.register_blueprint(practice_bp, url_prefix='/api/practice')
        app.register_blueprint(tests_bp, url_prefix='/api/tests')
        app.register_blueprint(assessments_bp, url_prefix='/api/assessments')
        app.register_blueprint(certificates_bp, url_prefix='/api/certificates')
        app.register_blueprint(mentor_portal_bp, url_prefix='/api/mentor-portal')
        app.register_blueprint(chat_bp, url_prefix='/api/chat')
        app.register_blueprint(weekly_evaluations_bp, url_prefix='/api/weekly-evaluations')
        app.register_blueprint(video_calls_bp, url_prefix='/api/video-calls')
        app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
        app.register_blueprint(final_projects_bp, url_prefix='/api/final-projects')
        
        print("✅ All blueprints registered successfully!")
        
    except Exception as e:
        print(f"❌ Error registering blueprints: {e}")
        import traceback
        traceback.print_exc()

# Register blueprints immediately after app creation
with app.app_context():
    try:
        # Import models here to avoid circular imports
        from models import User, PasswordReset
        
        # Create tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        create_admin_user()
        
        # Register blueprints
        register_blueprints()
        
    except Exception as e:
        print(f"❌ Application initialization error: {e}")
        # Don't exit here as it might be imported

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to SkillNova API",
        "tagline": "Shine with Skills. Grow with Guidance.",
        "version": "1.0.0",
        "developer": "Abishek",
        "linkedin": "https://www.linkedin.com/in/abishek-p-9ab80a326"
    })

@app.route('/api/health')
def health_check():
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = True
    except:
        db_status = False
    
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "cors_enabled": True,
        "database_connected": db_status
    })

# Add explicit OPTIONS handler for preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With,Accept,Origin")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# CORS is now handled entirely by Flask-CORS extension

if __name__ == '__main__':
    try:
        with app.app_context():
            # Test database connection first
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                print("✅ Database connection successful!")
            except Exception as db_error:
                print(f"❌ Database connection failed: {db_error}")
                print("Please ensure PostgreSQL is running and database 'skillnova' exists.")
                exit(1)
            
            print("✅ Database tables created successfully!")
            
    except Exception as e:
        print(f"❌ Application initialization error: {e}")
        exit(1)
    
    print("\n🚀 Starting SkillNova Backend Server...")
    print("=" * 50)
    print("Backend API: http://localhost:5000")
    print("Health Check: http://localhost:5000/api/health")
    print("Admin Portal: abishekopennova@gmail.com / abi@1234")
    print("Mentor Portal: abishekpopennova@gmail.com / abi@1234")
    print("Student Portal: abishekpalanivel212@gmail.com / abi@1234")
    print("CORS enabled for localhost:3000 and localhost:3001")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        exit(1)