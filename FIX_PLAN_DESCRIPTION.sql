-- Fix Plan Description Column Length Issue
-- This script changes the description column from VARCHAR(255) to TEXT
-- to allow longer descriptions for meal plans

-- Run this on your AWS PostgreSQL database

-- Change the description column type
ALTER TABLE plans 
ALTER COLUMN description TYPE TEXT;

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'plans' AND column_name = 'description';

-- Expected output:
-- column_name | data_type | character_maximum_length
-- description | text      | NULL (unlimited)
