#!/usr/bin/env python3
"""
检查当前环境变量和数据库配置
"""

import os
import sys

def check_environment():
    print("🔍 环境变量检查")
    print("=" * 40)
    
    # 检查.env文件
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ 找到.env文件: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'DATABASE_URL=' in content:
                for line in content.split('\n'):
                    if line.startswith('DATABASE_URL='):
                        db_url = line.split('=', 1)[1]
                        print(f"📊 .env中的DATABASE_URL: {db_url}")
                        if db_url.startswith('postgresql://'):
                            print("✅ 配置为PostgreSQL")
                        elif db_url.startswith('sqlite:'):
                            print("⚠️ 配置为SQLite")
                        else:
                            print("❓ 未知数据库类型")
                        break
            else:
                print("❌ .env文件中没有DATABASE_URL")
    else:
        print(f"❌ 未找到.env文件: {env_file}")
    
    # 检查环境变量
    print("\n🔧 系统环境变量:")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"📊 系统DATABASE_URL: {database_url[:50]}...")
    else:
        print("❌ 系统中没有DATABASE_URL环境变量")
    
    # 检查应用配置
    print("\n⚙️ 应用配置:")
    try:
        sys.path.insert(0, '.')
        from app.config import settings
        print(f"📊 应用使用的DATABASE_URL: {settings.database_url}")
        if 'postgresql' in settings.database_url:
            print("✅ 应用配置为PostgreSQL")
        else:
            print("⚠️ 应用配置为其他数据库")
    except Exception as e:
        print(f"❌ 无法加载应用配置: {e}")

if __name__ == "__main__":
    check_environment()