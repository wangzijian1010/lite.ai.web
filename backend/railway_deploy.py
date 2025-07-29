#!/usr/bin/env python3
"""
Railway deployment helper
This script helps deploy your app to Railway where it can access the internal PostgreSQL
"""

def create_railway_config():
    """Create Railway-specific configuration"""
    
    # Railway deployment configuration
    railway_env = """# Railway Production Environment
DATABASE_URL=postgresql://postgres:OvcVYcoCeeGOSIfioTFYirbMuDfaEIxv@postgres.railway.internal:5432/railway
SECRET_KEY=ghibli-ai-production-secret-key-2024-change-this-in-real-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Configuration
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=吉卜力AI

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
"""
    
    with open('.env.railway', 'w') as f:
        f.write(railway_env)
    
    print("✅ Created .env.railway for Railway deployment")
    print("📋 This uses the internal DATABASE_URL which works on Railway")
    
    # Create a simple deployment script
    deploy_script = """#!/bin/bash
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
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    import os
    os.chmod('deploy.sh', 0o755)
    
    print("✅ Created deploy.sh script")
    print("\n📋 To deploy to Railway:")
    print("1. Push your code to GitHub")
    print("2. Connect Railway to your GitHub repo")
    print("3. Railway will automatically deploy")
    print("4. The internal DATABASE_URL will work on Railway")

if __name__ == "__main__":
    create_railway_config()