#!/usr/bin/env python3
"""
简单的数据库连接测试
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    try:
        from app.config import settings
        from app.database import engine
        from sqlalchemy import text
        
        print("🔍 数据库连接测试")
        print("=" * 40)
        
        # 显示配置
        print(f"📊 DATABASE_URL: {settings.database_url}")
        print(f"🔧 数据库类型: {'PostgreSQL' if 'postgresql' in settings.database_url else '其他'}")
        
        # 测试连接
        print("\n🔗 测试连接...")
        with engine.connect() as conn:
            print("✅ 连接成功!")
            
            # 获取基本信息
            if 'postgresql' in settings.database_url:
                # PostgreSQL查询
                result = conn.execute(text("SELECT current_database(), version()"))
                row = result.fetchone()
                print(f"📋 数据库名: {row[0]}")
                print(f"📋 版本: {row[1].split(',')[0]}")
                
                # 检查表
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' 
                    ORDER BY tablename
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"📋 表列表: {tables}")
                
                # 检查users表
                if 'users' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM users"))
                    count = result.fetchone()[0]
                    print(f"👥 users表记录数: {count}")
                    
                    if count > 0:
                        result = conn.execute(text("""
                            SELECT id, username, email, created_at 
                            FROM users 
                            ORDER BY created_at DESC 
                            LIMIT 3
                        """))
                        users = result.fetchall()
                        print("👥 最近用户:")
                        for user in users:
                            print(f"   - ID:{user[0]}, 用户名:{user[1]}, 邮箱:{user[2]}")
                else:
                    print("⚠️ users表不存在")
            else:
                # SQLite查询
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                print(f"📋 表列表: {tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    print("\n" + "=" * 40)
    if success:
        print("🎉 数据库连接测试成功!")
    else:
        print("💥 数据库连接测试失败!")