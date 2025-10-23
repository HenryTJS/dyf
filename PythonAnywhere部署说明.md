# 德育分管理系统 - PythonAnywhere 部署指南

## 🚀 快速开始（GitHub部署）

如果您已经将项目同步到GitHub，推荐使用以下快速部署方法：

### 方法一：使用部署脚本（推荐）

在本地项目目录运行：
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 方法二：手动部署

```bash
# 1. 克隆GitHub仓库
cd /home/yourusername
git clone https://github.com/yourusername/your-repo-name.git mysite
cd mysite

# 2. 安装依赖
pip3.10 install --user -r requirements.txt

# 3. 初始化数据库
python3.10 app.py

# 4. 在PythonAnywhere控制面板配置Web应用
# - Source code: /home/yourusername/mysite
# - WSGI file: /home/yourusername/mysite/wsgi.py
# - 添加静态文件映射: /static/ -> /home/yourusername/mysite/static/
# - 添加上传文件映射: /uploads/ -> /home/yourusername/mysite/uploads/

# 5. 重启Web应用
```

## 项目结构说明

本项目已按照PythonAnywhere的推荐结构进行了调整：

```
项目根目录/
├── wsgi.py              # WSGI入口文件
├── app.py               # Flask应用主文件
├── index.html           # 静态主页
├── requirements.txt     # Python依赖
├── static/             # 静态文件目录
│   ├── css/
│   └── js/
├── templates/          # 模板文件目录
├── instance/           # 数据库文件目录
├── uploads/            # 上传文件目录
└── PythonAnywhere部署说明.md
```

## 部署方法

### 方法一：从GitHub直接部署（推荐）

#### 1. 克隆GitHub仓库

在PythonAnywhere的Bash控制台中运行：
```bash
cd /home/yourusername
git clone https://github.com/yourusername/your-repo-name.git mysite
cd mysite
```

#### 2. 安装依赖

```bash
pip3.10 install --user -r requirements.txt
```

#### 3. 配置Web应用

1. 登录PythonAnywhere控制面板
2. 进入 "Web" 标签页
3. 点击 "Add a new web app"
4. 选择 "Manual configuration"
5. 选择Python版本（推荐3.10）
6. 在 "Source code" 中填入：`/home/yourusername/mysite`
7. 在 "WSGI configuration file" 中填入：`/home/yourusername/mysite/wsgi.py`

#### 4. 修改WSGI配置

编辑 `/home/yourusername/mysite/wsgi.py` 文件，将 `yourusername` 替换为您的实际用户名：

```python
project_home = '/home/yourusername/mysite'  # 替换为实际路径
```

#### 5. 配置静态文件映射

在Web应用配置页面中，添加以下静态文件映射：

| URL | Directory |
|-----|-----------|
| /static/ | /home/yourusername/mysite/static/ |
| /uploads/ | /home/yourusername/mysite/uploads/ |

#### 6. 初始化数据库

```bash
cd /home/yourusername/mysite
python3.10 app.py
```

#### 7. 重启Web应用

在Web应用配置页面点击 "Reload" 按钮重启应用。

### 方法二：手动上传文件

#### 1. 上传项目文件

将整个项目文件夹上传到PythonAnywhere的以下路径：
```
/home/yourusername/mysite/
```

### 2. 安装依赖

在PythonAnywhere的Bash控制台中运行：
```bash
cd /home/yourusername/mysite
pip3.10 install --user -r requirements.txt
```

### 3. 配置Web应用

1. 登录PythonAnywhere控制面板
2. 进入 "Web" 标签页
3. 点击 "Add a new web app"
4. 选择 "Manual configuration"
5. 选择Python版本（推荐3.10）
6. 在 "Source code" 中填入：`/home/yourusername/mysite`
7. 在 "WSGI configuration file" 中填入：`/home/yourusername/mysite/wsgi.py`

### 4. 修改WSGI配置

编辑 `/home/yourusername/mysite/wsgi.py` 文件，将 `yourusername` 替换为您的实际用户名：

```python
project_home = '/home/yourusername/mysite'  # 替换为实际路径
```

### 5. 配置静态文件映射

在Web应用配置页面中，添加以下静态文件映射：

| URL | Directory |
|-----|-----------|
| /static/ | /home/yourusername/mysite/static/ |
| /uploads/ | /home/yourusername/mysite/uploads/ |

### 6. 初始化数据库

在PythonAnywhere的Bash控制台中运行：
```bash
cd /home/yourusername/mysite
python3.10 app.py
```

这将自动创建数据库和必要的表结构。

### 7. 重启Web应用

在Web应用配置页面点击 "Reload" 按钮重启应用。

## GitHub部署的优势

### 🔄 自动更新
```bash
# 更新代码到最新版本
cd /home/yourusername/mysite
git pull origin main
# 重启Web应用
```

### 📦 版本控制
- 可以轻松回滚到之前的版本
- 跟踪所有代码变更
- 团队协作开发

### 🚀 快速部署
- 无需手动上传文件
- 一键克隆整个项目
- 自动同步最新代码

## 更新应用

### 方法一：使用更新脚本（推荐）

在PythonAnywhere的Bash控制台中运行：
```bash
cd /home/yourusername/mysite
chmod +x update.sh
./update.sh
```

### 方法二：手动更新

```bash
# 从GitHub更新代码
cd /home/yourusername/mysite
git pull origin main

# 更新依赖（如果需要）
pip3.10 install --user -r requirements.txt

# 重启Web应用
# 在PythonAnywhere控制面板的Web应用页面点击 "Reload" 按钮
```

## 访问应用

部署完成后，您可以通过以下URL访问应用：
- 主页：`https://yourusername.pythonanywhere.com/`
- 登录页：`https://yourusername.pythonanywhere.com/login`

## 功能说明

### 用户角色
- **学生**：可以申请个人德育分、查看自己的德育分记录
- **教师**：可以提交集体德育分申请、管理学生德育分
- **管理员**：可以审核申请、管理学年、发布公告、查看统计

### 主要功能
1. **个人申请**：学生可以申请各类德育分
2. **集体申请**：教师可以为多个学生批量申请德育分
3. **审核管理**：管理员可以审核所有申请
4. **德育分统计**：按学年、书院、年级等维度统计德育分
5. **学年管理**：管理员可以管理学年信息
6. **公告管理**：发布和管理系统公告

## 注意事项

1. **数据库文件**：数据库文件位于 `instance/moral_score.db`
2. **上传文件**：上传的文件存储在 `uploads/` 目录
3. **静态文件**：CSS和JS文件在 `static/` 目录
4. **模板文件**：HTML模板在 `templates/` 目录

## 故障排除

### 常见问题

1. **500错误**：检查wsgi.py文件中的路径是否正确
2. **静态文件不加载**：确认静态文件映射配置正确
3. **数据库错误**：确保instance目录有写入权限
4. **上传失败**：确保uploads目录存在且有写入权限

### 日志查看

在PythonAnywhere的Web应用配置页面可以查看错误日志，帮助诊断问题。

## 安全建议

1. 修改默认的SECRET_KEY
2. 定期备份数据库文件
3. 设置强密码策略
4. 定期更新依赖包

## GitHub部署常见问题

### Q: 如何更新已部署的应用？
A: 使用以下命令更新：
```bash
cd /home/yourusername/mysite
git pull origin main
# 然后在PythonAnywhere控制面板重启Web应用
```

### Q: 如何回滚到之前的版本？
A: 使用Git回滚：
```bash
cd /home/yourusername/mysite
git log --oneline  # 查看提交历史
git reset --hard <commit-hash>  # 回滚到指定版本
# 重启Web应用
```

### Q: 如何添加新的依赖包？
A: 更新requirements.txt后：
```bash
cd /home/yourusername/mysite
git pull origin main  # 获取最新的requirements.txt
pip3.10 install --user -r requirements.txt
# 重启Web应用
```

### Q: 如何备份数据库？
A: 数据库文件位于 `instance/moral_score.db`，可以定期备份：
```bash
cp /home/yourusername/mysite/instance/moral_score.db /home/yourusername/backup_$(date +%Y%m%d).db
```

## 部署脚本说明

### deploy.sh - 本地部署脚本
- 自动提交代码到GitHub
- 提供详细的部署步骤指导
- 适用于本地开发环境

### update.sh - 服务器更新脚本
- 自动备份数据库
- 拉取最新代码
- 更新依赖包
- 适用于PythonAnywhere服务器

### 使用方法
```bash
# 本地部署
chmod +x deploy.sh
./deploy.sh

# 服务器更新
chmod +x update.sh
./update.sh
```

## 联系支持

如果遇到部署问题，请检查：
1. PythonAnywhere官方文档
2. Flask部署指南
3. 项目错误日志
4. GitHub仓库的Issues页面
