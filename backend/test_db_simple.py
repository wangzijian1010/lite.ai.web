#!/usr/bin/env python3
"""
Simple database connection test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_connection():
    print("🔍 Testing basic database connection...")
    
    try:
        from app.config import settings
        print(f"✅ Config loaded successfully")
        print(f"📊 Database URL: {settings.database_url[:30]}...")
        
        from app.database import engine, check_db_connection
        print(f"✅ Database module imported")
        
        # Test connection
        if check_db_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_connection()