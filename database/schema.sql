-- SkillNova Database Schema
-- PostgreSQL Database Setup Script

-- Create database (run this as postgres superuser)
-- CREATE DATABASE skillnova;
-- \c skillnova;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_mentor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password reset tokens
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bio data table
CREATE TABLE bio_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    education TEXT,
    skills TEXT,
    goals TEXT,
    interests TEXT,
    linkedin_url VARCHAR(255),
    experience_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Courses table
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    skill_level VARCHAR(50) NOT NULL CHECK (skill_level IN ('Beginner', 'Intermediate', 'Advanced')),
    duration_weeks INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Course modules
CREATE TABLE course_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    order_index INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Course enrollments
CREATE TABLE course_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    progress_percentage FLOAT DEFAULT 0.0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
    UNIQUE(user_id, course_id)
);

-- Mentors table
CREATE TABLE mentors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    expertise TEXT,
    experience_years INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    rating FLOAT DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mentor sessions
CREATE TABLE mentor_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentor_id UUID NOT NULL REFERENCES mentors(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessments table
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL CHECK (assessment_type IN ('initial', 'module', 'final')),
    score_percentage FLOAT CHECK (score_percentage >= 0 AND score_percentage <= 100),
    total_questions INTEGER,
    correct_answers INTEGER,
    time_taken_minutes INTEGER,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('multiple_choice', 'coding', 'essay')),
    difficulty_level VARCHAR(50) NOT NULL CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    category VARCHAR(100),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    module_id UUID REFERENCES course_modules(id) ON DELETE CASCADE,
    correct_answer TEXT,
    options JSONB, -- For multiple choice questions
    explanation TEXT, -- Explanation for the correct answer
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module tests table
CREATE TABLE module_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    duration_minutes INTEGER DEFAULT 30,
    passing_score FLOAT DEFAULT 70.0 CHECK (passing_score >= 0 AND passing_score <= 100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Final course tests table
CREATE TABLE course_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    duration_minutes INTEGER DEFAULT 60,
    passing_score FLOAT DEFAULT 70.0 CHECK (passing_score >= 0 AND passing_score <= 100),
    is_final_test BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User test attempts table
CREATE TABLE user_test_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_id UUID, -- Can reference either module_tests or course_tests
    test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('module', 'final')),
    questions_order JSONB, -- Store shuffled question order for this attempt
    answers JSONB, -- Store user answers
    score_percentage FLOAT,
    time_taken_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Test results table
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_type VARCHAR(50) NOT NULL,
    score_percentage FLOAT NOT NULL CHECK (score_percentage >= 0 AND score_percentage <= 100),
    answers JSONB, -- Store user answers
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Certificates table
CREATE TABLE certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    certificate_number VARCHAR(100) UNIQUE NOT NULL,
    final_score FLOAT NOT NULL CHECK (final_score >= 0 AND final_score <= 100),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    certificate_data JSONB, -- Store certificate details for AI generation
    pdf_path VARCHAR(500), -- Path to generated PDF certificate
    is_valid BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, course_id)
);

-- Chat rooms table
CREATE TABLE chat_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_type VARCHAR(50) NOT NULL CHECK (room_type IN ('user_mentor', 'user_admin')),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mentor_id UUID REFERENCES users(id) ON DELETE CASCADE, -- For user-mentor chats
    admin_id UUID REFERENCES users(id) ON DELETE CASCADE, -- For user-admin chats
    title VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- 1-5 star rating
    feedback TEXT, -- Optional feedback text
    rated_at TIMESTAMP, -- When the rating was given
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id UUID NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'file', 'image')),
    file_url VARCHAR(500), -- For file attachments
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mentor profiles table
CREATE TABLE mentor_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    expertise_areas TEXT, -- JSON string of expertise areas
    experience_years INTEGER,
    hourly_rate FLOAT,
    availability_schedule JSONB, -- Weekly schedule
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    rating FLOAT DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5),
    total_sessions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_admin ON users(is_admin);
CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_user_id ON password_resets(user_id);
CREATE INDEX idx_bio_data_user_id ON bio_data(user_id);
CREATE INDEX idx_courses_skill_level ON courses(skill_level);
CREATE INDEX idx_courses_is_active ON courses(is_active);
CREATE INDEX idx_course_modules_course_id ON course_modules(course_id);
CREATE INDEX idx_course_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX idx_course_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX idx_mentors_is_available ON mentors(is_available);
CREATE INDEX idx_mentor_sessions_user_id ON mentor_sessions(user_id);
CREATE INDEX idx_mentor_sessions_mentor_id ON mentor_sessions(mentor_id);
CREATE INDEX idx_mentor_sessions_scheduled_at ON mentor_sessions(scheduled_at);
CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
CREATE INDEX idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX idx_questions_category ON questions(category);
CREATE INDEX idx_questions_course_id ON questions(course_id);
CREATE INDEX idx_questions_module_id ON questions(module_id);
CREATE INDEX idx_questions_is_active ON questions(is_active);
CREATE INDEX idx_module_tests_module_id ON module_tests(module_id);
CREATE INDEX idx_course_tests_course_id ON course_tests(course_id);
CREATE INDEX idx_user_test_attempts_user_id ON user_test_attempts(user_id);
CREATE INDEX idx_user_test_attempts_test_id ON user_test_attempts(test_id);
CREATE INDEX idx_test_results_user_id ON test_results(user_id);

CREATE INDEX idx_certificates_user_id ON certificates(user_id);
CREATE INDEX idx_certificates_course_id ON certificates(course_id);
CREATE INDEX idx_certificates_number ON certificates(certificate_number);
CREATE INDEX idx_chat_rooms_user_id ON chat_rooms(user_id);
CREATE INDEX idx_chat_rooms_mentor_id ON chat_rooms(mentor_id);
CREATE INDEX idx_chat_rooms_admin_id ON chat_rooms(admin_id);
CREATE INDEX idx_chat_rooms_room_type ON chat_rooms(room_type);
CREATE INDEX idx_chat_rooms_is_active ON chat_rooms(is_active);
CREATE INDEX idx_chat_messages_room_id ON chat_messages(room_id);
CREATE INDEX idx_chat_messages_sender_id ON chat_messages(sender_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_mentor_profiles_user_id ON mentor_profiles(user_id);
CREATE INDEX idx_mentor_profiles_is_verified ON mentor_profiles(is_verified);

-- Weekly evaluations table
CREATE TABLE weekly_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    auto_generated BOOLEAN DEFAULT TRUE,
    total_questions INTEGER DEFAULT 10,
    coding_questions_count INTEGER DEFAULT 3,
    mcq_questions_count INTEGER DEFAULT 7,
    passing_score FLOAT DEFAULT 70.0 CHECK (passing_score >= 0 AND passing_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly evaluation questions table
CREATE TABLE weekly_evaluation_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES weekly_evaluations(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('multiple_choice', 'coding')),
    difficulty_level VARCHAR(50) NOT NULL CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    category VARCHAR(100),
    correct_answer TEXT,
    options JSONB, -- For multiple choice questions
    test_cases JSONB, -- For coding questions
    explanation TEXT,
    points INTEGER DEFAULT 10,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly evaluation attempts table
CREATE TABLE weekly_evaluation_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL REFERENCES weekly_evaluations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    answers JSONB, -- Store user answers
    score_percentage FLOAT CHECK (score_percentage >= 0 AND score_percentage <= 100),
    total_points INTEGER,
    earned_points INTEGER,
    time_taken_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'auto_submitted')),
    ai_evaluation_results JSONB, -- Store AI evaluation details
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(evaluation_id, user_id) -- One attempt per user per evaluation
);

-- Weekly evaluation scores table
CREATE TABLE weekly_evaluation_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    evaluation_id UUID NOT NULL REFERENCES weekly_evaluations(id) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES weekly_evaluation_attempts(id) ON DELETE CASCADE,
    score_percentage FLOAT NOT NULL CHECK (score_percentage >= 0 AND score_percentage <= 100),
    grade VARCHAR(10),
    coding_score FLOAT,
    mcq_score FLOAT,
    admin_feedback TEXT,
    admin_decision VARCHAR(50) CHECK (admin_decision IN ('selected', 'rejected', 'pending', 'internship_offered', 'scholarship_offered')),
    decision_date TIMESTAMP,
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, evaluation_id) -- One score per user per evaluation
);

-- Create indexes for weekly evaluations
CREATE INDEX idx_weekly_evaluations_scheduled_date ON weekly_evaluations(scheduled_date);
CREATE INDEX idx_weekly_evaluations_is_active ON weekly_evaluations(is_active);
CREATE INDEX idx_weekly_evaluation_questions_evaluation_id ON weekly_evaluation_questions(evaluation_id);
CREATE INDEX idx_weekly_evaluation_questions_order_index ON weekly_evaluation_questions(order_index);
CREATE INDEX idx_weekly_evaluation_attempts_evaluation_id ON weekly_evaluation_attempts(evaluation_id);
CREATE INDEX idx_weekly_evaluation_attempts_user_id ON weekly_evaluation_attempts(user_id);
CREATE INDEX idx_weekly_evaluation_attempts_status ON weekly_evaluation_attempts(status);
CREATE INDEX idx_weekly_evaluation_scores_user_id ON weekly_evaluation_scores(user_id);
CREATE INDEX idx_weekly_evaluation_scores_evaluation_id ON weekly_evaluation_scores(evaluation_id);
CREATE INDEX idx_weekly_evaluation_scores_admin_decision ON weekly_evaluation_scores(admin_decision);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bio_data_updated_at BEFORE UPDATE ON bio_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_rooms_updated_at BEFORE UPDATE ON chat_rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mentor_profiles_updated_at BEFORE UPDATE ON mentor_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Video calls table
CREATE TABLE video_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id VARCHAR(100) UNIQUE NOT NULL,
    initiator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_type VARCHAR(50) NOT NULL CHECK (call_type IN ('mentor_user', 'admin_user', 'admin_mentor')),
    status VARCHAR(50) DEFAULT 'waiting' CHECK (status IN ('waiting', 'active', 'ended', 'cancelled')),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    call_notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for video calls
CREATE INDEX idx_video_calls_room_id ON video_calls(room_id);
CREATE INDEX idx_video_calls_initiator_id ON video_calls(initiator_id);
CREATE INDEX idx_video_calls_participant_id ON video_calls(participant_id);
CREATE INDEX idx_video_calls_status ON video_calls(status);
CREATE INDEX idx_video_calls_call_type ON video_calls(call_type);
CREATE INDEX idx_video_calls_created_at ON video_calls(created_at);