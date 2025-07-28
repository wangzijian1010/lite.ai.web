# 云端部署完整指南

## 当前问题
- 本地可以登录注册，云端部署后无法登录注册
- 前端可以访问，但与后端API通信失败

## 解决步骤

### 1. 后端环境配置
创建生产环境配置文件：

```bash
# backend/.env.production
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-production-secret-key-change-this
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=吉卜力AI
```

### 2. 前端环境配置
确保前端指向正确的后端URL：

```bash
# frontend/.env.production
VITE_API_BASE_URL=http://your-backend-url
```

### 3. 部署前准备
1. 构建前端：`cd frontend && npm run build`
2. 确保后端依赖完整：`cd backend && pip install -r requirements.txt`

### 4. 部署命令
**后端部署**：
```json
{
    "install": ["pip install -r requirements.txt"],
    "start": ["python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
}
```

**前端部署**：
```json
{
    "install": ["npm install", "npm run build", "npm install -g serve"],
    "start": ["npx serve dist -p 5173"]
}
```

### 5. 测试步骤
1. 访问后端API文档：`http://your-backend-url/docs`
2. 测试注册接口：`POST /api/auth/register`
3. 访问前端：`http://your-frontend-url`
4. 尝试注册新用户

## 常见问题
1. **CORS错误**: 检查后端CORS配置是否包含前端域名
2. **数据库错误**: 云端是新数据库，需要重新注册用户
3. **环境变量**: 确保生产环境变量正确设置