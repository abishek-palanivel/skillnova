-- Migration: Add course ratings functionality
-- Created: 2024-12-01
-- PostgreSQL compatible

-- Create course_ratings table
CREATE TABLE IF NOT EXISTS course_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    user_id UUID NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_course_ratings_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_course_ratings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_user_course_rating UNIQUE (user_id, course_id)
);

-- Add rating columns to courses table (if they don't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='average_rating') THEN
        ALTER TABLE courses ADD COLUMN average_rating DECIMAL(3,2) DEFAULT 0.00;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='total_ratings') THEN
        ALTER TABLE courses ADD COLUMN total_ratings INT DEFAULT 0;
    END IF;
END $$;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_course_ratings_course_id ON course_ratings(course_id);
CREATE INDEX IF NOT EXISTS idx_course_ratings_user_id ON course_ratings(user_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_course_ratings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_course_ratings_updated_at ON course_ratings;
CREATE TRIGGER trigger_update_course_ratings_updated_at
    BEFORE UPDATE ON course_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_course_ratings_updated_at();
