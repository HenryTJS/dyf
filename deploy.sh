#!/bin/bash
# 德育分管理系统 - PythonAnywhere GitHub部署脚本

echo "🚀 开始部署德育分管理系统..."

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是Git仓库"
    echo "请先初始化Git仓库：git init"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告：检测到未提交的更改"
    echo "请先提交更改：git add . && git commit -m 'Update'"
    read -p "是否继续部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 推送到GitHub
echo "📤 推送代码到GitHub..."
git add .
git commit -m "Deploy to PythonAnywhere - $(date)"
git push origin main

echo "✅ 代码已推送到GitHub"
echo ""
echo "📋 接下来请在PythonAnywhere上执行以下步骤："
echo "1. 克隆仓库："
echo "   cd /home/yourusername"
echo "   git clone https://github.com/yourusername/your-repo-name.git mysite"
echo "   cd mysite"
echo ""
echo "2. 安装依赖："
echo "   pip3.10 install --user -r requirements.txt"
echo ""
echo "3. 初始化数据库："
echo "   python3.10 app.py"
echo ""
echo "4. 在PythonAnywhere控制面板配置Web应用："
echo "   - Source code: /home/yourusername/mysite"
echo "   - WSGI file: /home/yourusername/mysite/wsgi.py"
echo "   - 添加静态文件映射: /static/ -> /home/yourusername/mysite/static/"
echo "   - 添加上传文件映射: /uploads/ -> /home/yourusername/mysite/uploads/"
echo ""
echo "5. 重启Web应用"
echo ""
echo "🎉 部署完成！访问：https://yourusername.pythonanywhere.com/"
