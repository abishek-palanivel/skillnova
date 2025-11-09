from flask_sqlalchemy import SQLAlchemy

# This will be initialized in app.py
db = SQLAlchemy()
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_mentor = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bio_data = db.relationship('BioData', backref='user', uselist=False, cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', backref='user', cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='user', cascade='all, delete-orphan')
    mentor_sessions = db.relationship('MentorSession', backref='user', cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', backref='user', cascade='all, delete-orphan')


class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BioData(db.Model):
    __tablename__ = 'bio_data'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    goals = db.Column(db.Text)
    interests = db.Column(db.Text)
    linkedin_url = db.Column(db.String(255))
    experience_level = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    skill_level = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Advanced
    duration_weeks = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('CourseEnrollment', backref='course', cascade='all, delete-orphan')
    modules = db.relationship('CourseModule', backref='course', cascade='all, delete-orphan')

class CourseModule(db.Model):
    __tablename__ = 'course_modules'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    progress_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='active')  # active, completed, dropped

class Mentor(db.Model):
    __tablename__ = 'mentors'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    expertise = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)  # years of experience
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    linkedin = db.Column(db.String(255))
    github = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    total_sessions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='mentor_record')
    sessions = db.relationship('MentorSession', backref='mentor', cascade='all, delete-orphan')

class MentorSession(db.Model):
    __tablename__ = 'mentor_sessions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mentors.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # initial, module, final
    score_percentage = db.Column(db.Float)
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    time_taken_minutes = db.Column(db.Integer)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, coding, essay
    difficulty_level = db.Column(db.String(50), nullable=False)  # easy, medium, hard
    category = db.Column(db.String(100))
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('courses.id'), nullable=True)
    module_id = db.Column(UUID(as_uuid=True), db.ForeignKey('course_modules.id'), nullable=True)
    correct_answer = db.Column(db.Text)
    options = db.Column(db.JSON)  # For multiple choice questions
    explanation = db.Column(db.Text)  # Explanation for the correct answer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModuleTest(db.Model):
    __tablename__ = 'module_tests'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = db.Column(UUID(as_uuid=True), db.ForeignKey('course_modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)
    passing_score = db.Column(db.Float, default=70.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    module = db.relationship('CourseModule', backref='tests')

class CourseTest(db.Model):
    __tablename__ = 'course_tests'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=60)
    passing_score = db.Column(db.Float, default=70.0)
    is_final_test = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', backref='tests')

class UserTestAttempt(db.Model):
    __tablename__ = 'user_test_attempts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(UUID(as_uuid=True), nullable=True)  # Can reference either module_tests or course_tests
    test_type = db.Column(db.String(50), nullable=False)  # module, final
    questions_order = db.Column(db.JSON)  # Store shuffled question order for this attempt
    answers = db.Column(db.JSON)  # Store user answers
    score_percentage = db.Column(db.Float)
    time_taken_minutes = db.Column(db.Integer)
    status = db.Column(db.String(50), default='in_progress')  # in_progress, completed, abandoned
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class TestResult(db.Model):
    __tablename__ = 'test_results'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    score_percentage = db.Column(db.Float, nullable=False)
    answers = db.Column(db.JSON)  # Store user answers
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)



class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('courses.id'), nullable=False)
    certificate_number = db.Column(db.String(100), unique=True, nullable=False)
    final_score = db.Column(db.Float, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_data = db.Column(db.JSON)  # Store certificate details for AI generation
    pdf_path = db.Column(db.String(500))  # Path to generated PDF certificate
    is_valid = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='certificates')
    course = db.relationship('Course', backref='certificates')

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_type = db.Column(db.String(50), nullable=False)  # user_mentor, user_admin
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)  # For user-mentor chats
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)  # For user-admin chats
    title = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Integer)  # 1-5 star rating
    feedback = db.Column(db.Text)  # Optional feedback text
    rated_at = db.Column(db.DateTime)  # When the rating was given
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_chat_rooms')
    mentor = db.relationship('User', foreign_keys=[mentor_id], backref='mentor_chat_rooms')
    admin = db.relationship('User', foreign_keys=[admin_id], backref='admin_chat_rooms')
    messages = db.relationship('ChatMessage', backref='chat_room', cascade='all, delete-orphan')

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), default='text')  # text, file, image
    file_url = db.Column(db.String(500))  # For file attachments
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')

class MentorProfile(db.Model):
    __tablename__ = 'mentor_profiles'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)
    expertise_areas = db.Column(db.Text)  # JSON string of expertise areas
    experience_years = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float)
    availability_schedule = db.Column(db.JSON)  # Weekly schedule
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_sessions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='mentor_profile')

class WeeklyEvaluation(db.Model):
    __tablename__ = 'weekly_evaluations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    is_active = db.Column(db.Boolean, default=True)
    auto_generated = db.Column(db.Boolean, default=True)
    total_questions = db.Column(db.Integer, default=10)
    coding_questions_count = db.Column(db.Integer, default=3)
    mcq_questions_count = db.Column(db.Integer, default=7)
    passing_score = db.Column(db.Float, default=70.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('WeeklyEvaluationQuestion', backref='evaluation', cascade='all, delete-orphan')
    attempts = db.relationship('WeeklyEvaluationAttempt', backref='evaluation', cascade='all, delete-orphan')

class WeeklyEvaluationQuestion(db.Model):
    __tablename__ = 'weekly_evaluation_questions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('weekly_evaluations.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, coding
    difficulty_level = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100))
    correct_answer = db.Column(db.Text)
    options = db.Column(db.JSON)  # For multiple choice questions
    test_cases = db.Column(db.JSON)  # For coding questions
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=10)
    order_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeeklyEvaluationAttempt(db.Model):
    __tablename__ = 'weekly_evaluation_attempts'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('weekly_evaluations.id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON)  # Store user answers
    score_percentage = db.Column(db.Float)
    total_points = db.Column(db.Integer)
    earned_points = db.Column(db.Integer)
    time_taken_minutes = db.Column(db.Integer)
    status = db.Column(db.String(50), default='in_progress')  # in_progress, completed, auto_submitted
    ai_evaluation_results = db.Column(db.JSON)  # Store AI evaluation details
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='weekly_evaluation_attempts')

class WeeklyEvaluationScore(db.Model):
    __tablename__ = 'weekly_evaluation_scores'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    evaluation_id = db.Column(UUID(as_uuid=True), db.ForeignKey('weekly_evaluations.id'), nullable=False)
    attempt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('weekly_evaluation_attempts.id'), nullable=False)
    score_percentage = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10))  # A+, A, B+, B, C+, C, D, F
    coding_score = db.Column(db.Float)
    mcq_score = db.Column(db.Float)
    admin_feedback = db.Column(db.Text)
    admin_decision = db.Column(db.String(50))  # selected, rejected, pending, internship_offered, scholarship_offered
    decision_date = db.Column(db.DateTime)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='weekly_evaluation_scores')
    evaluation = db.relationship('WeeklyEvaluation', backref='scores')
    attempt = db.relationship('WeeklyEvaluationAttempt', backref='score')

class VideoCall(db.Model):
    __tablename__ = 'video_calls'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = db.Column(db.String(100), unique=True, nullable=False)
    initiator_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)  # Who started the call
    participant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)  # Who joined
    call_type = db.Column(db.String(50), nullable=False)  # mentor_user, admin_user, admin_mentor
    status = db.Column(db.String(50), default='waiting')  # waiting, active, ended, cancelled
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    call_notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 rating
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    initiator = db.relationship('User', foreign_keys=[initiator_id], backref='initiated_calls')
    participant = db.relationship('User', foreign_keys=[participant_id], backref='participated_calls')


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'video_call', 'message', 'system'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Additional data like call_id, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')