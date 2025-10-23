#!/usr/bin/env python3
"""
德育分管理系统启动脚本
适用于PythonAnywhere部署
"""

import os
import sys
from app import app, init_db

if __name__ == '__main__':
    # 初始化数据库
    print("正在初始化数据库...")
    init_db()
    
    # 启动应用
    print("德育分管理系统启动中...")
    print("访问地址: http://localhost:5000")
    
    # 在PythonAnywhere上运行时，通常不需要指定host和port
    # 因为WSGI服务器会处理这些
    app.run(debug=False)
