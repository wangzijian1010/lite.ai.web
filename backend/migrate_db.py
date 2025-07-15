"""
数据库迁移脚本 - 添加邮箱验证功能所需的字段和表
"""
import sqlite3
import os
from datetime import datetime

def migrate_database():
    db_path = "./app.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，将自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("开始数据库迁移...")
        
        # 检查 users 表是否存在 email_verified 字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'email_verified' not in columns:
            print("添加 email_verified 字段到 users 表...")
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE")
        
        # 创建 email_verifications 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR NOT NULL,
                code VARCHAR NOT NULL,
                attempts INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 创建 email_send_logs 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR
            )
        """)
        
        # 为邮箱字段创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_verifications_email ON email_verifications(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_send_logs_email ON email_send_logs(email)")
        
        conn.commit()
        print("数据库迁移完成！")
        
    except Exception as e:
        print(f"迁移过程中出现错误: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()