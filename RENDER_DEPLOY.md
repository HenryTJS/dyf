# Render 部署指南

## 🚀 免费部署方案

### 步骤1: 注册账号
1. 访问 https://render.com
2. 使用 GitHub 账号登录

### 步骤2: 创建 Web Service
1. 点击 **"New +"** → **"Web Service"**
2. 连接您的 GitHub 仓库
3. 配置：
   - **Name**: 您的应用名称
   - **Region**: Singapore（离中国最近）
   - **Branch**: main
   - **Root Directory**: (留空)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### 步骤3: 创建数据库
1. 点击 **"New +"** → **"PostgreSQL"**
2. 配置：
   - **Name**: moral_score_db
   - **Database**: moral_score
   - **User**: (自动生成)
   - **Region**: Singapore
   - **Plan**: Free

### 步骤4: 连接数据库
1. 在 Web Service 中点击 **"Environment"**
2. 添加变量：
   - `DATABASE_URL`: 从 PostgreSQL 服务复制 Internal Database URL

### 步骤5: 部署
1. 点击 **"Manual Deploy"** → **"Deploy latest commit"**
2. 等待部署完成
3. 获得免费URL（如：your-app.onrender.com）

## ✅ 完成！

## 💡 优点
- ✅ 完全免费
- ✅ PostgreSQL 免费
- ✅ 自动部署
- ✅ HTTPS 自动配置

## ⚠️ 注意事项

### 修改 app.py 支持 Render
在数据库配置部分添加：

```python
# 支持 Render 数据库 URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render 环境
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # 本地环境（保持原有配置）
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    # ... 原有代码
```

### 休眠说明
- Free Plan 应用在 15 分钟无活动后会休眠
- 首次访问需要等待几秒唤醒
- 如有需要，可升级到 Starter Plan ($7/月)
