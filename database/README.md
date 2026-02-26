# Database Documentation

## Overview
This folder contains the database schema and migration scripts for the SkillNova platform.

## Files

### schema.sql
Complete database schema for PostgreSQL. Use this for fresh installations.

**To create a new database:**
```bash
# Create database
createdb skillnova

# Apply schema
psql -U your_username -d skillnova -f database/schema.sql
```

### migrations/
Contains incremental database migration scripts for updating existing databases.

**Migration files:**
- `001_add_mentor_fields.sql` - Adds missing fields to mentors table (Dec 2025)

**To apply migrations:**

Option 1 - Using Python runner (Recommended):
```bash
python database/run_migrations.py
```

Option 2 - Using psql:
```bash
# Apply a specific migration
psql -U your_username -d skillnova -f database/migrations/001_add_mentor_fields.sql
```

## Database Structure

### Core Tables
- **users** - User accounts (students, mentors, admins)
- **bio_data** - User profile information
- **password_resets** - Password reset tokens

### Course Management
- **courses** - Course catalog
- **course_modules** - Course content modules
- **course_enrollments** - Student course enrollments

### Mentorship
- **mentors** - Mentor profiles
- **mentor_sessions** - Scheduled mentor sessions
- **mentor_profiles** - Extended mentor information

### Assessments
- **questions** - Question bank
- **assessments** - Assessment records
- **module_tests** - Module-level tests
- **course_tests** - Course-level tests
- **user_test_attempts** - Test attempt tracking
- **test_results** - Test results

### Weekly Evaluations
- **weekly_evaluations** - Scheduled evaluations
- **weekly_evaluation_questions** - Evaluation questions
- **weekly_evaluation_attempts** - User attempts
- **weekly_evaluation_scores** - Evaluation scores and admin decisions

### Communication
- **chat_rooms** - Chat room management
- **chat_messages** - Chat messages
- **video_calls** - Video call sessions

### Certificates
- **certificates** - Course completion certificates

## Indexes
All tables have appropriate indexes for optimal query performance. See schema.sql for details.

## Triggers
- `update_updated_at_column()` - Automatically updates `updated_at` timestamps

## Notes
- All primary keys use UUID v4
- Timestamps use UTC
- Foreign keys have appropriate CASCADE rules
- Check constraints ensure data integrity
