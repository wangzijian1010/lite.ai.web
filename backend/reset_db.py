"""
重置数据库脚本 - 删除并重新创建所有表
注意：这将删除所有现有数据！
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.models import Base

def reset_database():
    """删除并重新创建所有数据库表"""
    print("警告：这将删除所有现有数据！")
    confirm = input("确定要继续吗？(输入 'yes' 确认): ")
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    try:
        print("删除所有表...")
        Base.metadata.drop_all(bind=engine)
        
        print("重新创建所有表...")
        Base.metadata.create_all(bind=engine)
        
        print("数据库重置完成！")
        
    except Exception as e:
        print(f"重置过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    reset_database()