#!/usr/bin/env python3
"""
PostgreSQL连接检查脚本
用于确认是否正确连接到PostgreSQL数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app.config import settings
from sqlalchemy import text
import traceback

def check_postgresql_connection():
    """检查PostgreSQL连接状态"""
    print("🔍 检查PostgreSQL连接状态...")
    print("=" * 50)
    
    # 1. 显示配置信息
    print(f"📊 数据库URL: {settings.database_url}")
    print(f"🔧 数据库类型: {'PostgreSQL' if 'postgresql' in settings.database_url else '其他'}")
    
    try:
        # 2. 测试连接
        print("\n🔗 测试数据库连接...")
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
            
            # 3. 获取数据库版本信息
            print("\n📋 数据库信息:")
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   版本: {version}")
            
            # 4. 检查当前数据库名
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   当前数据库: {db_name}")
            
            # 5. 检查所有表
            print("\n📋 数据库表列表:")
            result = conn.execute(text("""
                SELECT tablename, schemaname 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            if tables:
                for table in tables:
                    print(f"   ✓ {table[0]} (schema: {table[1]})")
            else:
                print("   ⚠️ 没有找到任何表")
            
            # 6. 检查users表详情
            print("\n👥 检查users表:")
            try:
                # 检查表结构
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                if columns:
                    print("   表结构:")
                    for col in columns:
                        print(f"     - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                    
                    # 检查数据
                    result = conn.execute(text("SELECT COUNT(*) FROM users"))
                    count = result.fetchone()[0]
                    print(f"   数据行数: {count}")
                    
                    if count > 0:
                        print("   最近的用户:")
                        result = conn.execute(text("""
                            SELECT id, username, email, created_at 
                            FROM users 
                            ORDER BY created_at DESC 
                            LIMIT 5
                        """))
                        users = result.fetchall()
                        for user in users:
                            print(f"     ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 创建时间: {user[3]}")
                else:
                    print("   ❌ users表不存在")
                    
            except Exception as e:
                print(f"   ❌ 检查users表时出错: {e}")
            
            # 7. 检查连接池状态
            print(f"\n🏊 连接池状态:")
            print(f"   连接池大小: {engine.pool.size()}")
            print(f"   已检出连接: {engine.pool.checkedout()}")
            print(f"   溢出连接: {engine.pool.overflow()}")
            
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n🔍 详细错误信息:")
        traceback.print_exc()
        return False

def test_session():
    """测试Session连接"""
    print("\n🔄 测试Session连接...")
    try:
        db = SessionLocal()
        # 执行简单查询
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.fetchone()[0]
        print(f"✅ Session测试成功，返回值: {test_value}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Session测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PostgreSQL连接诊断工具")
    print("=" * 50)
    
    # 检查环境变量
    print("🔧 环境变量检查:")
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"   DATABASE_URL: {database_url[:50]}...")
    else:
        print("   ⚠️ DATABASE_URL 环境变量未设置")
    
    print("\n" + "=" * 50)
    
    # 检查连接
    connection_ok = check_postgresql_connection()
    session_ok = test_session()
    
    print("\n" + "=" * 50)
    print("📊 诊断结果:")
    print(f"   数据库连接: {'✅ 正常' if connection_ok else '❌ 失败'}")
    print(f"   Session连接: {'✅ 正常' if session_ok else '❌ 失败'}")
    
    if connection_ok and session_ok:
        print("\n🎉 PostgreSQL连接完全正常！")
    else:
        print("\n💥 存在连接问题，请检查配置！")