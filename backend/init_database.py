#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建所有必要的数据库表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, check_db_connection
from app.models import models  # 导入所有模型
from app.config import settings

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 显示当前配置
    print(f"📊 数据库URL: {settings.database_url[:50]}...")
    
    # 检查连接
    if not check_db_connection():
        print("❌ 数据库连接失败！请检查配置")
        return False
    
    print("✅ 数据库连接成功")
    
    try:
        # 创建所有表
        print("🔧 正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建完成")
        
        # 验证表是否创建成功
        from sqlalchemy import text
        with engine.connect() as conn:
            # 检查users表是否存在
            if settings.database_url.startswith('postgresql'):
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            else:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            
            tables = [row[0] for row in result]
            print(f"📋 已创建的表: {tables}")
            
            if 'users' in tables:
                print("✅ users表创建成功")
            else:
                print("⚠️ users表未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("🎉 数据库初始化完成！")
    else:
        print("💥 数据库初始化失败！")
        sys.exit(1)