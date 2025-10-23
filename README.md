# 德育分管理系统

一个现代化的学生德育分管理平台，支持个人申请、集体申请、审核管理等功能。

## ✨ 主要功能

- **学生端**：个人德育分申请、查看德育分记录
- **教师端**：集体德育分申请、学生德育分管理
- **管理员端**：申请审核、学年管理、公告发布、数据统计

## 🚀 快速部署

### GitHub部署（推荐）

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. **使用部署脚本**
```bash
chmod +x deploy.sh
./deploy.sh
```

3. **在PythonAnywhere上配置Web应用**
   - Source code: `/home/yourusername/mysite`
   - WSGI file: `/home/yourusername/mysite/wsgi.py`
   - 静态文件映射: `/static/` → `/home/yourusername/mysite/static/`
   - 上传文件映射: `/uploads/` → `/home/yourusername/mysite/uploads/`

## 📁 项目结构

```
├── wsgi.py                    # PythonAnywhere入口点
├── app.py                     # Flask应用主文件
├── index.html                 # 静态主页
├── deploy.sh                  # 本地部署脚本
├── update.sh                  # 服务器更新脚本
├── requirements.txt           # Python依赖
├── static/                    # 静态文件
├── templates/                 # HTML模板
├── instance/                  # 数据库文件
└── uploads/                   # 上传文件
```

## 🔄 更新应用

在PythonAnywhere服务器上运行：
```bash
cd /home/yourusername/mysite
chmod +x update.sh
./update.sh
```

## 📖 详细文档

请查看 [PythonAnywhere部署说明.md](PythonAnywhere部署说明.md) 获取完整的部署指南。

## 🛠️ 技术栈

- **后端**：Flask, SQLAlchemy
- **前端**：HTML, CSS, JavaScript
- **数据库**：SQLite
- **部署**：PythonAnywhere

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看：
1. 部署说明文档
2. PythonAnywhere官方文档
3. GitHub Issues页面