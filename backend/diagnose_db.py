#!/usr/bin/env python3
"""
数据库连接诊断工具
用于排查吉卜力AI后端系统的PostgreSQL连接问题
"""

import os
import sys
import logging
from urllib.parse import urlparse
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    env_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'DATABASE_PUBLIC_URL': os.getenv('DATABASE_PUBLIC_URL'),
        'DB_POOL_SIZE': os.getenv('DB_POOL_SIZE', '10'),
        'DB_MAX_OVERFLOW': os.getenv('DB_MAX_OVERFLOW', '20'),
        'DB_POOL_TIMEOUT': os.getenv('DB_POOL_TIMEOUT', '30'),
        'DB_POOL_RECYCLE': os.getenv('DB_POOL_RECYCLE', '3600'),
    }
    
    for key, value in env_vars.items():
        if value:
            if 'URL' in key:
                # 隐藏密码部分
                parsed = urlparse(value)
                masked_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
                print(f"✅ {key}: {masked_url}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: 未设置")
    
    return env_vars

def parse_database_url(database_url):
    """解析数据库连接字符串"""
    if not database_url:
        return None
    
    try:
        parsed = urlparse(database_url)
        return {
            'scheme': parsed.scheme,
            'username': parsed.username,
            'password': parsed.password,
            'hostname': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/') if parsed.path else 'postgres'
        }
    except Exception as e:
        logger.error(f"解析数据库URL失败: {e}")
        return None

def test_raw_connection(db_config):
    """使用psycopg2直接测试数据库连接"""
    print("\n🔧 测试原始数据库连接...")
    
    if not db_config:
        print("❌ 数据库配置无效")
        return False
    
    try:
        # 构建连接字符串
        conn_str = f"host={db_config['hostname']} port={db_config['port']} dbname={db_config['database']} user={db_config['username']} password={db_config['password']}"
        
        print(f"📡 连接到: {db_config['hostname']}:{db_config['port']}")
        print(f"📊 数据库: {db_config['database']}")
        print(f"👤 用户: {db_config['username']}")
        
        # 尝试连接
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        
        # 执行测试查询
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # 获取数据库版本信息
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ 原始连接成功!")
        print(f"📋 查询结果: {result}")
        print(f"🗄️ 数据库版本: {version}")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 连接失败 (OperationalError): {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_sqlalchemy_connection(database_url):
    """测试SQLAlchemy连接"""
    print("\n⚙️ 测试SQLAlchemy连接...")
    
    if not database_url:
        print("❌ DATABASE_URL未设置")
        return False
    
    try:
        # 创建引擎
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=True  # 显示SQL语句
        )
        
        # 测试连接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            
            # 获取当前数据库信息
            db_info = connection.execute(text("SELECT current_database(), current_user, inet_server_addr(), inet_server_port()"))
            info = db_info.fetchone()
            
        print(f"✅ SQLAlchemy连接成功!")
        print(f"📋 查询结果: {row}")
        print(f"🗄️ 当前数据库: {info[0]}")
        print(f"👤 当前用户: {info[1]}")
        print(f"🌐 服务器地址: {info[2]}:{info[3]}")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_application_connection():
    """测试应用程序连接配置"""
    print("\n🚀 测试应用程序连接配置...")
    
    try:
        # 导入应用配置
        sys.path.append('/Users/wangzijian/Desktop/lite.ai.web/backend')
        from app.config import settings
        from app.database import check_db_connection, engine
        
        print(f"📊 配置的数据库URL: {settings.database_url[:50]}...")
        print(f"🔧 连接池大小: {settings.db_pool_size}")
        print(f"📈 最大溢出: {settings.db_max_overflow}")
        print(f"⏱️ 连接超时: {settings.db_pool_timeout}秒")
        print(f"♻️ 连接回收: {settings.db_pool_recycle}秒")
        
        # 测试应用的连接检查函数
        if check_db_connection():
            print("✅ 应用程序连接检查成功!")
            
            # 测试引擎信息
            print(f"🔧 引擎类型: {type(engine).__name__}")
            print(f"🔗 引擎URL: {engine.url}")
            
            return True
        else:
            print("❌ 应用程序连接检查失败!")
            return False
            
    except ImportError as e:
        print(f"❌ 导入应用模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 应用连接测试失败: {e}")
        return False

def check_network_connectivity(hostname, port):
    """检查网络连通性"""
    print(f"\n🌐 检查网络连通性 {hostname}:{port}...")
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ 网络连接正常")
            return True
        else:
            print(f"❌ 网络连接失败，错误代码: {result}")
            return False
    except Exception as e:
        print(f"❌ 网络检查失败: {e}")
        return False

def main():
    """主诊断流程"""
    print("🏥 吉卜力AI数据库连接诊断工具")
    print("=" * 50)
    
    # 1. 检查环境变量
    env_vars = check_environment_variables()
    
    # 2. 解析数据库URL
    database_url = env_vars.get('DATABASE_URL')
    db_config = parse_database_url(database_url)
    
    if not db_config:
        print("\n❌ 无法解析数据库连接字符串，请检查DATABASE_URL格式")
        return
    
    # 3. 检查网络连通性
    network_ok = check_network_connectivity(db_config['hostname'], db_config['port'])
    
    # 4. 测试原始连接
    raw_connection_ok = test_raw_connection(db_config)
    
    # 5. 测试SQLAlchemy连接
    sqlalchemy_ok = test_sqlalchemy_connection(database_url)
    
    # 6. 测试应用程序连接
    app_connection_ok = test_application_connection()
    
    # 7. 生成诊断报告
    print("\n📋 诊断报告")
    print("=" * 30)
    print(f"🌐 网络连通性: {'✅ 正常' if network_ok else '❌ 失败'}")
    print(f"🔧 原始连接: {'✅ 正常' if raw_connection_ok else '❌ 失败'}")
    print(f"⚙️ SQLAlchemy连接: {'✅ 正常' if sqlalchemy_ok else '❌ 失败'}")
    print(f"🚀 应用程序连接: {'✅ 正常' if app_connection_ok else '❌ 失败'}")
    
    if all([network_ok, raw_connection_ok, sqlalchemy_ok, app_connection_ok]):
        print("\n🎉 所有连接测试通过！数据库配置正常。")
    else:
        print("\n⚠️ 发现连接问题，请根据上述错误信息进行修复。")
        
        # 提供修复建议
        print("\n🔧 修复建议:")
        if not network_ok:
            print("- 检查网络连接和防火墙设置")
            print("- 确认数据库服务器地址和端口正确")
        if not raw_connection_ok:
            print("- 检查数据库用户名和密码")
            print("- 确认数据库服务正在运行")
            print("- 检查数据库访问权限")
        if not sqlalchemy_ok:
            print("- 检查SQLAlchemy版本兼容性")
            print("- 确认psycopg2驱动已正确安装")
        if not app_connection_ok:
            print("- 检查应用程序配置文件")
            print("- 确认环境变量在应用中正确加载")

if __name__ == "__main__":
    main()