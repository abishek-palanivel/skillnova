-- Migration: Add missing fields to mentors table
-- Date: 2025-12-01
-- Description: Adds hourly_rate and other missing fields to mentors table

-- Add missing columns if they don't exist
DO $$ 
BEGIN
    -- Add hourly_rate column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'hourly_rate'
    ) THEN
        ALTER TABLE mentors ADD COLUMN hourly_rate FLOAT DEFAULT 0.0;
        RAISE NOTICE 'Added hourly_rate column to mentors table';
    END IF;

    -- Add user_id column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE mentors ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added user_id column to mentors table';
    END IF;

    -- Add bio column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'bio'
    ) THEN
        ALTER TABLE mentors ADD COLUMN bio TEXT;
        RAISE NOTICE 'Added bio column to mentors table';
    END IF;

    -- Add phone column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'phone'
    ) THEN
        ALTER TABLE mentors ADD COLUMN phone VARCHAR(20);
        RAISE NOTICE 'Added phone column to mentors table';
    END IF;

    -- Add linkedin column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'linkedin'
    ) THEN
        ALTER TABLE mentors ADD COLUMN linkedin VARCHAR(255);
        RAISE NOTICE 'Added linkedin column to mentors table';
    END IF;

    -- Add github column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'github'
    ) THEN
        ALTER TABLE mentors ADD COLUMN github VARCHAR(255);
        RAISE NOTICE 'Added github column to mentors table';
    END IF;

    -- Add total_sessions column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'total_sessions'
    ) THEN
        ALTER TABLE mentors ADD COLUMN total_sessions INTEGER DEFAULT 0;
        RAISE NOTICE 'Added total_sessions column to mentors table';
    END IF;

    -- Add updated_at column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mentors' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE mentors ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column to mentors table';
    END IF;

    -- Update experience_years default
    ALTER TABLE mentors ALTER COLUMN experience_years SET DEFAULT 0;
    
    RAISE NOTICE 'Migration completed successfully';
END $$;
