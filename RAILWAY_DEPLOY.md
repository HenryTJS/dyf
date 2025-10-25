# Railway 部署指南

## 🚀 3步完成部署

### 步骤1: 注册账号
1. 访问 https://railway.app
2. 使用 GitHub 账号登录

### 步骤2: 创建项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 授权并选择您的仓库

### 步骤3: 添加数据库
1. 项目页面点击 **"+ New"**
2. 选择 **"Database"** → **"Add PostgreSQL"**
3. 自动创建并连接数据库

## ✅ 完成！

Railway 会自动：
- ✅ 检测 Python 应用
- ✅ 运行 `pip install -r requirements.txt`
- ✅ 启动应用（使用 Procfile）
- ✅ 配置数据库连接
- ✅ 生成 URL（如：your-app.up.railway.app）

## 🔧 环境变量（自动配置）

Railway 会自动设置：
- `DATABASE_URL` - PostgreSQL 连接字符串
- `PORT` - 应用端口
- `RAILWAY_ENVIRONMENT` - 环境标识

## 📝 注意事项

### 修改 app.py 数据库配置

在 `app.py` 开头添加：

```python
import os

# Railway 数据库配置
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Railway 环境
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

## 💰 费用

- **免费额度**: $5/月
- **足够**: 一个小型应用运行
- **超出**: 按使用量计费

## 🎯 一键部署

1. 推送到 GitHub
2. 在 Railway 点击部署
3. 完成！

就是这么简单！🎉
