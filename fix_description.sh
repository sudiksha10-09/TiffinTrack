#!/bin/bash

# Fix Plan Description Column Length
# This script updates the database to allow longer plan descriptions

echo "🔧 TiffinTrack - Fix Plan Description Column"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f app.py ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the TiffinTrack directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please make sure .env exists in the TiffinTrack directory."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not found in .env file!"
    exit 1
fi

echo "✅ Found database connection"
echo ""

# Use Python to fix the database
echo "📝 Running database fix using Python..."
echo ""

python3 fix_db_description.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All done! Now restart the application:"
    echo "   sudo systemctl restart tiffintrack"
    echo ""
else
    echo ""
    echo "❌ Fix failed. Check the error messages above."
    echo ""
fi
