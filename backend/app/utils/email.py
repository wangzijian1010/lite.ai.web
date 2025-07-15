import random
import string
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings

def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))

def create_verification_email(email: str, code: str) -> MIMEMultipart:
    """创建验证邮件"""
    msg = MIMEMultipart()
    msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg['To'] = email
    msg['Subject'] = f"【{settings.smtp_from_name}】邮箱验证码"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">🎨 {settings.smtp_from_name}</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">AI 图片处理服务</p>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #333; margin-top: 0;">邮箱验证码</h2>
                <p>您好！</p>
                <p>您正在注册 {settings.smtp_from_name} 账户，请使用以下验证码完成注册：</p>
                
                <div style="background: white; border: 2px dashed #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                    <span style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px;">{code}</span>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    • 验证码有效期为 {settings.verification_code_expire_minutes} 分钟<br>
                    • 请勿泄露验证码给他人<br>
                    • 如非本人操作，请忽略此邮件
                </p>
            </div>
            
            <div style="text-align: center; color: #888; font-size: 12px;">
                <p>此邮件由系统自动发送，请勿回复</p>
                <p>© 2024 {settings.smtp_from_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    return msg

async def send_verification_email(email: str, code: str) -> bool:
    """发送验证邮件"""
    if not all([settings.smtp_username, settings.smtp_password, settings.smtp_from_email]):
        # 开发环境下，如果没有配置邮箱，直接打印验证码
        print(f"[开发模式] 验证码发送到 {email}: {code}")
        return True
    
    try:
        msg = create_verification_email(email, code)
        
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_username,
            password=settings.smtp_password,
        )
        
        print(f"验证邮件已发送到: {email}")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        # 开发环境下，邮件发送失败时打印验证码
        print(f"[开发模式] 验证码: {code}")
        return False