#!/usr/bin/env python3
"""
PostgreSQL设置助手
帮助用户正确配置PostgreSQL连接
"""

import os
import sys

def setup_postgresql():
    print("🔧 PostgreSQL设置助手")
    print("=" * 50)
    
    print("请按照以下步骤设置PostgreSQL连接：")
    print()
    print("1. 在Railway中获取数据库连接信息：")
    print("   - 进入你的Railway项目")
    print("   - 点击PostgreSQL服务")
    print("   - 进入'Connect'标签页")
    print("   - 复制'Database URL'")
    print()
    
    # 获取用户输入的DATABASE_URL
    database_url = input("请粘贴你的PostgreSQL DATABASE_URL: ").strip()
    
    if not database_url:
        print("❌ DATABASE_URL不能为空")
        return False
    
    if not database_url.startswith('postgresql://'):
        print("❌ DATABASE_URL应该以'postgresql://'开头")
        return False
    
    # 读取现有的.env文件或创建新的
    env_file = ".env"
    env_content = []
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.readlines()
    
    # 更新或添加DATABASE_URL
    database_url_found = False
    for i, line in enumerate(env_content):
        if line.startswith('DATABASE_URL='):
            env_content[i] = f'DATABASE_URL={database_url}\n'
            database_url_found = True
            break
    
    if not database_url_found:
        env_content.append(f'DATABASE_URL={database_url}\n')
    
    # 写入.env文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(env_content)
    
    print(f"✅ DATABASE_URL已保存到{env_file}")
    
    # 测试连接
    print("\n🔍 测试数据库连接...")
    
    # 设置环境变量
    os.environ['DATABASE_URL'] = database_url
    
    try:
        # 重新导入配置
        sys.path.insert(0, '.')
        from app.config import settings
        from app.database import engine
        from sqlalchemy import text
        
        print(f"📊 配置的DATABASE_URL: {settings.database_url[:50]}...")
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), version()"))
            row = result.fetchone()
            print(f"✅ 连接成功!")
            print(f"📋 数据库名: {row[0]}")
            print(f"📋 PostgreSQL版本: {row[1].split(',')[0]}")
            
        print("\n🎉 PostgreSQL设置完成!")
        print("现在你可以重启应用，它将连接到PostgreSQL数据库。")
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        print("请检查DATABASE_URL是否正确")
        return False

if __name__ == "__main__":
    setup_postgresql()