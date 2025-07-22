"""
用户积分管理模块
"""

from sqlalchemy.orm import Session
from app.models.models import User

def check_user_credits(user: User, required_credits: int = 10) -> bool:
    """检查用户积分是否足够"""
    return user.credits >= required_credits

def deduct_user_credits(db: Session, user: User, credits_to_deduct: int = 10) -> bool:
    """扣除用户积分"""
    if user.credits < credits_to_deduct:
        return False
    
    user.credits -= credits_to_deduct
    db.commit()
    db.refresh(user)
    return True
