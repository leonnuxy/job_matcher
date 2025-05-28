#!/bin/bash

echo "Setting up Gemini API key for job_matcher..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
fi

# Check if GEMINI_API_KEY is already set
if grep -q "GEMINI_API_KEY" .env; then
    echo "GEMINI_API_KEY already exists in .env file"
    source .env
    if [ -n "$GEMINI_API_KEY" ]; then
        echo "✅ GEMINI_API_KEY is set"
    else
        echo "⚠️  GEMINI_API_KEY exists but is empty"
    fi
else
    echo "GEMINI_API_KEY not found in .env"
    echo ""
    echo "To get a Gemini API key:"
    echo "1. Go to https://makersuite.google.com/app/apikey"
    echo "2. Create a new API key"
    echo "3. Copy the key"
    echo ""
    read -p "Enter your Gemini API key (or press Enter to skip): " gemini_key
    
    if [ -n "$gemini_key" ]; then
        echo "GEMINI_API_KEY=$gemini_key" >> .env
        echo "✅ GEMINI_API_KEY added to .env file"
        export GEMINI_API_KEY=$gemini_key
    else
        echo "⚠️  Skipped API key setup"
    fi
fi

echo ""
echo "Current environment variables:"
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:+[SET]} ${GEMINI_API_KEY:-[NOT SET]}"

echo ""
echo "To load environment variables in future sessions, run:"
echo "source .env"

echo ""
echo "Environment setup complete!"
