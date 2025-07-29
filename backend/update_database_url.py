#!/usr/bin/env python3
"""
更新数据库URL配置
"""

import os
import sys

def update_database_url(new_url):
    """更新.env文件中的DATABASE_URL"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"❌ 未找到{env_file}文件")
        return False
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新DATABASE_URL
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f'DATABASE_URL={new_url}\n'
            updated = True
            print(f"✅ 已更新DATABASE_URL")
            break
    
    if not updated:
        lines.append(f'DATABASE_URL={new_url}\n')
        print(f"✅ 已添加DATABASE_URL")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ 配置已保存到{env_file}")
    
    # 验证配置
    print("\n🔍 验证新配置...")
    os.environ['DATABASE_URL'] = new_url
    
    try:
        sys.path.insert(0, '.')
        from app.config import settings
        from app.database import engine
        from sqlalchemy import text
        
        print(f"📊 新的DATABASE_URL: {settings.database_url[:50]}...")
        
        # 测试连接
        with engine.connect() as conn:
            if 'postgresql' in new_url:
                result = conn.execute(text("SELECT current_database(), version()"))
                row = result.fetchone()
                print(f"✅ PostgreSQL连接成功!")
                print(f"📋 数据库名: {row[0]}")
                print(f"📋 版本: {row[1].split(',')[0]}")
            else:
                result = conn.execute(text("SELECT 1"))
                print(f"✅ 数据库连接成功!")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 update_database_url.py <DATABASE_URL>")
        sys.exit(1)
    
    new_url = sys.argv[1]
    success = update_database_url(new_url)
    
    if success:
        print("\n🎉 数据库配置更新完成!")
        print("请重启你的FastAPI应用以使用新的PostgreSQL连接。")
    else:
        print("\n💥 配置更新失败!")