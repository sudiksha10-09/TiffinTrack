#!/bin/bash

# Fix Plan Description Column Length
# This script updates the database to allow longer plan descriptions

echo "🔧 TiffinTrack - Fix Plan Description Column"
echo "=============================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run this script from the TiffinTrack directory."
    exit 1
fi

# Extract database URL
DATABASE_URL=$(grep DATABASE_URL .env | cut -d '=' -f2- | tr -d '"' | tr -d "'")

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not found in .env file!"
    exit 1
fi

echo "✅ Found database connection"
echo ""

# Run the SQL command
echo "📝 Updating description column to TEXT type..."
echo ""

psql "$DATABASE_URL" -c "ALTER TABLE plans ALTER COLUMN description TYPE TEXT;" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database updated successfully!"
    echo ""
    
    # Verify the change
    echo "🔍 Verifying the change..."
    psql "$DATABASE_URL" -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'plans' AND column_name = 'description';"
    
    echo ""
    echo "✅ Fix completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Restart the application: sudo systemctl restart tiffintrack"
    echo "2. Try adding your plan again"
    echo ""
else
    echo ""
    echo "❌ Error updating database!"
    echo ""
    echo "Manual fix:"
    echo "1. Connect to database: psql \"$DATABASE_URL\""
    echo "2. Run: ALTER TABLE plans ALTER COLUMN description TYPE TEXT;"
    echo "3. Exit: \\q"
    echo ""
fi
