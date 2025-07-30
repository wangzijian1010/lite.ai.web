#!/usr/bin/env python3
"""
邮箱验证功能测试脚本
运行此脚本可以测试邮箱发送功能是否正常
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.email import send_verification_email, generate_verification_code
from app.config import settings

async def test_email_functionality():
    """测试邮箱功能"""
    print("🧪 开始测试邮箱验证功能...")
    print(f"📧 SMTP配置:")
    print(f"   服务器: {settings.smtp_host}:{settings.smtp_port}")
    print(f"   用户名: {settings.smtp_username}")
    print(f"   发件人: {settings.smtp_from_email}")
    print(f"   显示名: {settings.smtp_from_name}")
    print()
    
    # 检查配置
    if not all([settings.smtp_username, settings.smtp_password, settings.smtp_from_email]):
        print("⚠️ 邮箱配置不完整，将使用开发模式")
        print("   请在 .env 文件中配置以下参数：")
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD") 
        print("   - SMTP_FROM_EMAIL")
        print()
    
    # 获取测试邮箱
    test_email = input("请输入测试邮箱地址: ").strip()
    if not test_email:
        print("❌ 请输入有效的邮箱地址")
        return
    
    # 生成验证码
    code = generate_verification_code(settings.verification_code_length)
    print(f"🔢 生成的验证码: {code}")
    print()
    
    # 发送邮件
    print("📤 正在发送测试邮件...")
    try:
        success = await send_verification_email(test_email, code)
        if success:
            print("✅ 邮件发送成功！")
            print(f"📬 请检查邮箱 {test_email} 是否收到验证码")
            print(f"🔍 如果没有收到，请检查垃圾邮件文件夹")
        else:
            print("❌ 邮件发送失败")
            print("🔍 请检查SMTP配置和网络连接")
    except Exception as e:
        print(f"💥 发送邮件时出错: {e}")
    
    print()
    print("🎯 测试完成！")

def main():
    """主函数"""
    print("=" * 50)
    print("📧 吉卜力AI - 邮箱验证功能测试")
    print("=" * 50)
    
    try:
        asyncio.run(test_email_functionality())
    except KeyboardInterrupt:
        print("\n👋 测试已取消")
    except Exception as e:
        print(f"💥 测试过程中出错: {e}")

if __name__ == "__main__":
    main()