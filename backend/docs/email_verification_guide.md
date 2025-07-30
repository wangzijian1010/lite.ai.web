# 邮箱认证配置指南

## 📧 邮箱验证功能已激活

您的 AI 图像处理平台现在已启用真实的邮箱验证功能。用户必须通过邮箱验证码才能完成注册。

## 🔧 SMTP 邮箱配置

### 1. 创建环境配置文件

在 `backend` 目录下创建 `.env` 文件：

```bash
cp .env.example .env
```

### 2. 配置邮箱服务

编辑 `.env` 文件，配置以下邮箱参数：

```env
# 邮箱SMTP配置 (必填项，用于邮箱验证)
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your_email@qq.com
SMTP_PASSWORD=your_authorization_code
SMTP_FROM_EMAIL=your_email@qq.com
SMTP_FROM_NAME=吉卜力AI
```

## 🎯 支持的邮箱服务商

### QQ邮箱（推荐）
```env
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your_qq_email@qq.com
SMTP_PASSWORD=your_qq_auth_code
```

**获取QQ邮箱授权码步骤：**
1. 登录QQ邮箱
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启"POP3/SMTP服务"
4. 生成授权码（不是QQ密码）

### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Gmail需要使用应用专用密码：**
1. 开启两步验证
2. 生成应用专用密码
3. 使用应用专用密码作为SMTP_PASSWORD

### 163邮箱
```env
SMTP_HOST=smtp.163.com
SMTP_PORT=587
SMTP_USERNAME=your_email@163.com
SMTP_PASSWORD=your_auth_code
```

### 企业邮箱
```env
SMTP_HOST=your_company_smtp.com
SMTP_PORT=587
SMTP_USERNAME=your_email@company.com
SMTP_PASSWORD=your_password
```

## ⚙️ 验证码配置

```env
# 验证码配置
VERIFICATION_CODE_EXPIRE_MINUTES=5    # 验证码5分钟过期
VERIFICATION_CODE_LENGTH=6            # 6位验证码
MAX_VERIFICATION_ATTEMPTS=3           # 最大验证次数
EMAIL_SEND_COOLDOWN_SECONDS=60        # 邮箱发送冷却时间（防刷）
```

## 🚀 启动服务

配置完成后启动后端服务：

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 测试邮箱功能

1. **开发环境测试**：
   - 如果未配置邮箱，验证码会打印在控制台
   - 方便开发和调试

2. **生产环境**：
   - 必须配置真实邮箱
   - 验证码通过邮件发送

## 📝 注册流程

1. 用户输入邮箱、用户名、密码
2. 点击"发送验证码"
3. 系统发送6位验证码到用户邮箱
4. 用户输入验证码
5. 提交注册表单
6. 验证成功后创建账户并自动登录

## 🔍 故障排除

### 邮件发送失败
1. 检查SMTP配置是否正确
2. 确认授权码/应用密码是否有效
3. 检查网络连接
4. 查看控制台错误日志

### 验证码收不到
1. 检查垃圾邮件文件夹
2. 确认邮箱地址输入正确
3. 等待网络延迟（通常1-2分钟内到达）

### 验证码错误
1. 确认验证码输入正确（6位数字）
2. 检查验证码是否过期（5分钟有效期）
3. 最多尝试3次，失败后需重新获取

## 🛡️ 安全特性

- ✅ 邮箱验证防止虚假注册
- ✅ 验证码有效期限制
- ✅ 发送频率限制（60秒冷却）
- ✅ 验证尝试次数限制
- ✅ 防重复注册检查

## 📱 邮件模板

系统会发送HTML格式的验证邮件，包含：
- 品牌化的邮件头部
- 清晰的验证码显示
- 有效期和安全提示
- 专业的邮件格式

现在您的平台具备了完整的邮箱验证功能！🎉