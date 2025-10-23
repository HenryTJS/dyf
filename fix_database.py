#!/usr/bin/env python3
"""
修复数据库路径问题的脚本
适用于PythonAnywhere部署
"""

import os
import sys

def fix_database_path():
    print("🔧 开始修复数据库路径问题...")
    
    # 获取当前目录
    current_dir = os.path.abspath(os.path.dirname(__file__))
    print(f"当前目录: {current_dir}")
    
    # 创建必要的目录
    instance_dir = os.path.join(current_dir, 'instance')
    uploads_dir = os.path.join(current_dir, 'uploads')
    
    print(f"创建目录: {instance_dir}")
    os.makedirs(instance_dir, exist_ok=True)
    
    print(f"创建目录: {uploads_dir}")
    os.makedirs(uploads_dir, exist_ok=True)
    
    # 设置权限
    try:
        os.chmod(instance_dir, 0o755)
        os.chmod(uploads_dir, 0o755)
        print("✅ 目录权限设置成功")
    except Exception as e:
        print(f"⚠️ 权限设置警告: {e}")
    
    # 检查数据库文件
    db_path = os.path.join(instance_dir, 'moral_score.db')
    print(f"数据库路径: {db_path}")
    
    if os.path.exists(db_path):
        print("✅ 数据库文件已存在")
        # 设置数据库文件权限
        try:
            os.chmod(db_path, 0o664)
            print("✅ 数据库文件权限设置成功")
        except Exception as e:
            print(f"⚠️ 数据库权限设置警告: {e}")
    else:
        print("ℹ️ 数据库文件不存在，将在首次运行时创建")
    
    # 测试数据库连接
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()
        print("✅ 数据库连接测试成功")
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False
    
    print("🎉 数据库路径修复完成！")
    return True

if __name__ == '__main__':
    success = fix_database_path()
    if success:
        print("\n📋 接下来请运行:")
        print("python3.10 app.py")
    else:
        print("\n❌ 修复失败，请检查错误信息")
        sys.exit(1)
