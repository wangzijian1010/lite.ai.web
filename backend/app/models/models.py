from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)  # 邮箱是否已验证
    credits = Column(Integer, default=50)  # 用户积分，新用户默认50积分
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    code = Column(String)
    attempts = Column(Integer, default=0)  # 验证尝试次数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    used = Column(Boolean, default=False)  # 是否已使用

class EmailSendLog(Base):
    __tablename__ = "email_send_logs"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)  # 发送者IP（可选）