#!/usr/bin/env python3
"""
Test different Railway URL formats to find the working one
"""

import sys
sys.path.insert(0, '.')

def test_url_format(base_url, password="OvcVYcoCeeGOSIfioTFYirbMuDfaEIxv"):
    """Test a specific URL format"""
    from sqlalchemy import create_engine, text
    
    try:
        print(f"🔍 Testing: {base_url[:50]}...")
        engine = create_engine(base_url, connect_args={"connect_timeout": 5})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ SUCCESS: {base_url[:50]}...")
            return True
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:100]}...")
        return False

def find_working_url():
    """Try different URL formats to find the working one"""
    print("🔍 Testing different Railway URL formats...")
    print("=" * 60)
    
    password = "OvcVYcoCeeGOSIfioTFYirbMuDfaEIxv"
    
    # Common Railway URL patterns
    url_patterns = [
        # Current internal (won't work)
        f"postgresql://postgres:{password}@postgres.railway.internal:5432/railway",
        
        # Common external patterns
        f"postgresql://postgres:{password}@viaduct.proxy.rlwy.net:5432/railway",
        f"postgresql://postgres:{password}@containers-us-west-1.railway.app:5432/railway",
        f"postgresql://postgres:{password}@containers-us-west-2.railway.app:5432/railway",
        f"postgresql://postgres:{password}@containers-us-east-1.railway.app:5432/railway",
        
        # Different ports
        f"postgresql://postgres:{password}@viaduct.proxy.rlwy.net:6543/railway",
        f"postgresql://postgres:{password}@viaduct.proxy.rlwy.net:7432/railway",
    ]
    
    working_urls = []
    
    for url in url_patterns:
        if test_url_format(url):
            working_urls.append(url)
    
    print("\n" + "=" * 60)
    if working_urls:
        print("🎉 Found working URL(s):")
        for url in working_urls:
            print(f"✅ {url}")
        return working_urls[0]
    else:
        print("❌ No working URLs found")
        print("You need to get the correct public URL from Railway Console")
        return None

if __name__ == "__main__":
    working_url = find_working_url()
    
    if working_url:
        print(f"\n🔧 To update your .env file, run:")
        print(f"DATABASE_URL={working_url}")
    else:
        print(f"\n📋 Please check Railway Console for the correct public URL")