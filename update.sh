#!/bin/bash
# 德育分管理系统 - PythonAnywhere更新脚本

echo "🔄 开始更新德育分管理系统..."

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是Git仓库"
    exit 1
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p instance
mkdir -p uploads
chmod 755 instance
chmod 755 uploads

# 备份数据库
echo "💾 备份数据库..."
if [ -f "instance/moral_score.db" ]; then
    cp instance/moral_score.db instance/moral_score_backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ 数据库已备份"
else
    echo "⚠️  警告：未找到数据库文件"
fi

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码更新成功"
else
    echo "❌ 代码更新失败"
    exit 1
fi

# 检查是否需要更新依赖
echo "📦 检查依赖..."
pip3.10 install --user -r requirements.txt

echo "✅ 依赖更新完成"

# 重启Web应用
echo "🔄 请手动在PythonAnywhere控制面板重启Web应用"
echo "   或运行：touch /var/www/yourusername_pythonanywhere_com_wsgi.py"

echo ""
echo "🎉 更新完成！"
echo "访问：https://yourusername.pythonanywhere.com/"
