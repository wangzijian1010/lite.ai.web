#!/usr/bin/env python3
"""
简化的数据库环境变量检查工具
专门用于检查Railway PostgreSQL连接配置
"""

import os
from urllib.parse import urlparse

def main():
    print("🔍 检查数据库环境变量配置")
    print("=" * 40)
    
    # 检查关键环境变量
    env_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'DATABASE_PUBLIC_URL': os.getenv('DATABASE_PUBLIC_URL'),
        'DB_POOL_SIZE': os.getenv('DB_POOL_SIZE', '10'),
        'DB_MAX_OVERFLOW': os.getenv('DB_MAX_OVERFLOW', '20'),
        'DB_POOL_TIMEOUT': os.getenv('DB_POOL_TIMEOUT', '30'),
        'DB_POOL_RECYCLE': os.getenv('DB_POOL_RECYCLE', '3600'),
    }
    
    print("\n📋 环境变量状态:")
    for key, value in env_vars.items():
        if value:
            if 'URL' in key:
                # 解析并显示URL信息（隐藏密码）
                try:
                    parsed = urlparse(value)
                    masked_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
                    print(f"✅ {key}: {masked_url}")
                    
                    # 详细分析DATABASE_URL
                    if key == 'DATABASE_URL':
                        print(f"   📊 协议: {parsed.scheme}")
                        print(f"   👤 用户名: {parsed.username}")
                        print(f"   🌐 主机: {parsed.hostname}")
                        print(f"   🔌 端口: {parsed.port}")
                        print(f"   🗄️ 数据库: {parsed.path.lstrip('/')}")
                        
                        # 检查是否为Railway内部地址
                        if 'railway.internal' in parsed.hostname:
                            print(f"   ✅ 检测到Railway内部地址")
                        else:
                            print(f"   ⚠️ 非Railway内部地址，可能需要使用DATABASE_PUBLIC_URL")
                            
                except Exception as e:
                    print(f"❌ {key}: URL解析失败 - {e}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: 未设置")
    
    # 检查应用配置
    print("\n🚀 检查应用配置:")
    try:
        from app.config import settings
        print(f"✅ 配置加载成功")
        print(f"📊 数据库URL前缀: {settings.database_url[:30]}...")
        print(f"🔧 连接池大小: {settings.db_pool_size}")
        print(f"📈 最大溢出: {settings.db_max_overflow}")
        print(f"⏱️ 连接超时: {settings.db_pool_timeout}秒")
        print(f"♻️ 连接回收: {settings.db_pool_recycle}秒")
        
        # 检查是否为PostgreSQL
        if settings.database_url.startswith('postgresql'):
            print("✅ 检测到PostgreSQL配置")
        else:
            print("⚠️ 未检测到PostgreSQL配置，当前使用SQLite")
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
    
    # 提供修复建议
    print("\n🔧 常见问题和解决方案:")
    print("1. 如果DATABASE_URL未设置:")
    print("   - 在Railway控制台的Variables标签页添加DATABASE_URL")
    print("   - 格式: postgresql://user:password@host:port/database")
    
    print("\n2. 如果连接超时:")
    print("   - 检查是否使用了正确的内部地址(.railway.internal)")
    print("   - 确认PostgreSQL服务正在运行")
    
    print("\n3. 如果认证失败:")
    print("   - 检查用户名和密码是否正确")
    print("   - 确认数据库用户有足够权限")
    
    print("\n4. Railway特定建议:")
    print("   - 使用DATABASE_URL而不是DATABASE_PUBLIC_URL（内部通信）")
    print("   - 确保PostgreSQL服务和应用服务在同一个项目中")
    print("   - 检查Railway服务状态和日志")

if __name__ == "__main__":
    main()