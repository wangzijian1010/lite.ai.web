#!/usr/bin/env python3
"""
修复Railway PostgreSQL连接
帮助获取正确的公网连接字符串
"""

def fix_railway_connection():
    print("🔧 Railway PostgreSQL连接修复")
    print("=" * 50)
    
    print("❌ 当前问题:")
    print("   你正在使用内网地址: postgres.railway.internal")
    print("   这个地址只能在Railway内部网络访问")
    print()
    
    print("✅ 解决方案:")
    print("   需要使用Railway的公网连接地址")
    print()
    
    print("📋 获取正确连接字符串的步骤:")
    print("1. 登录Railway控制台")
    print("2. 进入你的项目")
    print("3. 点击PostgreSQL服务")
    print("4. 进入'Connect'标签页")
    print("5. 找到'Public Network'部分")
    print("6. 复制'Database URL'")
    print()
    
    print("🔍 正确的URL格式应该是:")
    print("   postgresql://postgres:password@containers-us-west-xxx.railway.app:port/railway")
    print("   或")
    print("   postgresql://postgres:password@viaduct.proxy.rlwy.net:port/railway")
    print()
    
    print("⚠️ 注意:")
    print("   - 不要使用包含'.railway.internal'的内网地址")
    print("   - 使用包含'.railway.app'或'rlwy.net'的公网地址")
    print()
    
    # 获取用户输入
    print("请粘贴Railway的公网DATABASE_URL:")
    new_url = input().strip()
    
    if not new_url:
        print("❌ URL不能为空")
        return False
    
    if 'railway.internal' in new_url:
        print("❌ 这仍然是内网地址，请使用公网地址")
        return False
    
    if not new_url.startswith('postgresql://'):
        print("❌ URL格式不正确")
        return False
    
    # 更新.env文件
    import os
    env_file = ".env"
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新DATABASE_URL
        for i, line in enumerate(lines):
            if line.startswith('DATABASE_URL='):
                lines[i] = f'DATABASE_URL={new_url}\n'
                break
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ 已更新{env_file}")
        
        # 测试连接
        print("\n🔍 测试新连接...")
        os.environ['DATABASE_URL'] = new_url
        
        try:
            import sys
            sys.path.insert(0, '.')
            from app.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT current_database(), version()"))
                row = result.fetchone()
                print(f"✅ 连接成功!")
                print(f"📋 数据库: {row[0]}")
                print(f"📋 版本: {row[1].split(',')[0]}")
                
            return True
            
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False
    
    else:
        print(f"❌ 未找到{env_file}文件")
        return False

if __name__ == "__main__":
    success = fix_railway_connection()
    if success:
        print("\n🎉 连接修复成功!")
        print("现在可以运行: python3 init_database.py")
    else:
        print("\n💥 连接修复失败!")