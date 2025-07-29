#!/bin/bash
# Railway Deployment Script

echo "🚀 Deploying to Railway..."

# Copy Railway environment
cp .env.railway .env

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 init_database.py

# Start the application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
