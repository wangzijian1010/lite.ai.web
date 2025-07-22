#!/usr/bin/env python3
"""
数据库迁移脚本：为用户表添加积分字段
"""

import sqlite3
import os
from pathlib import Path

def add_credits_field():
    """为用户表添加积分字段"""
    # 数据库文件路径
    db_path = Path(__file__).parent / "app.db"
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        print("请先运行应用创建数据库，或者检查数据库路径是否正确")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查credits字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'credits' in column_names:
            print("积分字段已存在，无需添加")
            return True
        
        # 添加credits字段，默认值为50
        cursor.execute("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 50")
        
        # 为现有用户设置积分为50
        cursor.execute("UPDATE users SET credits = 50 WHERE credits IS NULL")
        
        # 提交更改
        conn.commit()
        
        print("成功为用户表添加积分字段")
        print("现有用户的积分已设置为50")
        
        # 验证字段添加成功
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n当前用户表结构:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"数据库操作错误: {e}")
        return False
    except Exception as e:
        print(f"未知错误: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始添加积分字段到用户表...")
    success = add_credits_field()
    if success:
        print("迁移完成！")
    else:
        print("迁移失败！")
