#!/usr/bin/env python3
"""
Quick database connection test
"""

def test_url(url):
    try:
        from sqlalchemy import create_engine, text
        print(f"Testing: {url[:60]}...")
        
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connection successful!")
            return True
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        test_url(url)
    else:
        print("Usage: python3 quick_test.py 'your-database-url'")