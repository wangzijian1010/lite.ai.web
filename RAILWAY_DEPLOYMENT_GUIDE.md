# 🚀 Railway 部署完整教程

## 第一步：准备工作

### 1.1 注册Railway账号
1. 打开浏览器，访问：https://railway.app/
2. 点击右上角 "Login" 按钮
3. 选择 "Continue with GitHub"（推荐，因为需要连接代码仓库）
4. 授权Railway访问你的GitHub账号
5. 注册成功后，你会获得 $5 的免费使用额度

### 1.2 安装Railway CLI（命令行工具）
打开命令行工具（Windows用PowerShell，Mac用Terminal），执行：

```bash
# 方法1：使用npm安装（推荐）
npm install -g @railway/cli

# 方法2：Windows用户也可以直接下载
# 访问 https://github.com/railwayapp/cli/releases
# 下载 railway-windows-amd64.exe
```

安装完成后，验证安装：
```bash
railway --version
```

## 第二步：准备你的代码

### 2.1 创建GitHub仓库
1. 登录 GitHub.com
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`ghibli-ai-app`
4. 设置为 Public（免费用户）
5. 点击 "Create repository"

### 2.2 上传代码到GitHub
在你的项目根目录（f:/lite.ai.web）执行：

```bash
# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: Ghibli AI app"

# 连接到你的GitHub仓库（替换成你的用户名）
git remote add origin https://github.com/你的用户名/ghibli-ai-app.git

# 推送代码
git push -u origin main
```

## 第三步：部署后端到Railway

### 3.1 登录Railway CLI
```bash
railway login
```
这会打开浏览器，点击授权即可。

### 3.2 创建后端项目
```bash
# 进入后端目录
cd backend

# 初始化Railway项目
railway init

# 选择 "Empty Project"
# 项目名称输入：ghibli-ai-backend
```

### 3.3 连接GitHub仓库
1. 访问 https://railway.app/dashboard
2. 找到你刚创建的 `ghibli-ai-backend` 项目
3. 点击项目进入
4. 点击 "Connect Repo"
5. 选择你的 `ghibli-ai-app` 仓库
6. Root Directory 设置为：`backend`
7. 点击 "Connect"

### 3.4 配置环境变量
在Railway项目页面：
1. 点击 "Variables" 标签
2. 添加以下环境变量：

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=ghibli-ai-production-secret-key-2024-railway
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp
PORT=8000
```

### 3.5 部署后端
```bash
# 在backend目录下
railway up
```

等待部署完成，你会得到一个后端URL，类似：
`https://ghibli-ai-backend-production.up.railway.app`

## 第四步：部署前端到Railway

### 4.1 创建前端项目
```bash
# 回到项目根目录
cd ..

# 进入前端目录
cd frontend

# 创建新的Railway项目
railway init

# 选择 "Empty Project"
# 项目名称输入：ghibli-ai-frontend
```

### 4.2 连接GitHub仓库
1. 访问 https://railway.app/dashboard
2. 找到 `ghibli-ai-frontend` 项目
3. 点击 "Connect Repo"
4. 选择你的 `ghibli-ai-app` 仓库
5. Root Directory 设置为：`frontend`
6. 点击 "Connect"

### 4.3 配置前端环境变量
在Railway前端项目页面添加：
```
VITE_API_BASE_URL=https://你的后端URL
```

### 4.4 部署前端
```bash
# 在frontend目录下
railway up
```

## 第五步：配置域名和HTTPS

### 5.1 获取部署URL
部署完成后，在Railway dashboard中：
1. 后端项目 → Settings → Domains → 复制URL
2. 前端项目 → Settings → Domains → 复制URL

### 5.2 更新前端配置
更新前端的环境变量，将后端URL设置为Railway提供的URL。

## 第六步：测试部署

### 6.1 测试后端
访问你的后端URL + `/docs`，例如：
`https://ghibli-ai-backend-production.up.railway.app/docs`

应该能看到FastAPI的文档页面。

### 6.2 测试前端
访问你的前端URL，测试：
1. 页面是否正常加载
2. 用户注册/登录功能
3. 图片上传和处理功能

## 第七步：监控和维护

### 7.1 查看日志
```bash
# 查看后端日志
railway logs

# 实时查看日志
railway logs --follow
```

### 7.2 查看使用情况
在Railway dashboard中可以查看：
- CPU使用率
- 内存使用率
- 网络流量
- 费用使用情况

## 常见问题解决

### Q1: 部署失败怎么办？
```bash
# 查看详细日志
railway logs

# 重新部署
railway up --detach
```

### Q2: 环境变量没生效？
1. 检查Railway dashboard中的Variables设置
2. 重新部署：`railway up`

### Q3: 前端无法连接后端？
1. 检查CORS设置
2. 确认前端环境变量中的后端URL正确
3. 检查后端是否正常运行

### Q4: 数据库问题？
Railway会自动处理SQLite文件，但重新部署时数据会丢失。
生产环境建议使用Railway提供的PostgreSQL数据库。

## 费用说明

- 免费额度：$5/月
- 超出后按使用量计费
- 一般小项目免费额度够用

## 下一步优化

1. **数据库升级**：使用Railway PostgreSQL
2. **文件存储**：使用云存储服务（如AWS S3）
3. **域名绑定**：绑定自定义域名
4. **监控告警**：设置性能监控

---

按照这个教程一步步操作，你就能成功将项目部署到Railway上了！有任何问题随时问我。