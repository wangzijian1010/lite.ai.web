#!/usr/bin/env python3
"""
Simple connection test for Railway PostgreSQL
"""

import os
import sys

def test_connection():
    try:
        # Set up path
        sys.path.insert(0, '.')
        
        # Import after path setup
        from app.config import settings
        from sqlalchemy import create_engine, text
        
        print("🔍 Testing Railway PostgreSQL Connection")
        print("=" * 50)
        
        # Show current config
        db_url = settings.database_url
        print(f"📊 DATABASE_URL: {db_url[:50]}...")
        
        # Check URL type
        if 'railway.internal' in db_url:
            print("❌ Using INTERNAL URL - this won't work from local machine")
            print("   You need the PUBLIC URL from Railway Console")
            return False
        elif 'railway.app' in db_url or 'rlwy.net' in db_url:
            print("✅ Using PUBLIC URL - this should work")
        else:
            print("⚠️ Unknown URL format")
        
        # Test connection
        print("\n🔗 Testing connection...")
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), version()"))
            row = result.fetchone()
            
            print("✅ Connection successful!")
            print(f"📋 Database: {row[0]}")
            print(f"📋 PostgreSQL: {row[1].split(',')[0]}")
            
            # Test table creation
            print("\n🔧 Testing table operations...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                INSERT INTO test_connection (message) 
                VALUES ('Connection test successful')
            """))
            
            result = conn.execute(text("SELECT COUNT(*) FROM test_connection"))
            count = result.fetchone()[0]
            print(f"✅ Test table operations successful (records: {count})")
            
            # Clean up
            conn.execute(text("DROP TABLE test_connection"))
            conn.commit()
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Railway PostgreSQL connection is working!")
        print("You can now run: python3 init_database.py")
    else:
        print("💥 Connection failed - check your DATABASE_URL")
        print("Make sure you're using the PUBLIC URL from Railway")