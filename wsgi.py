#!/usr/bin/python3.10

import sys
import os

# 添加项目根目录到Python路径
project_home = '/home/yourusername/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'

# 导入Flask应用
from app import app as application

if __name__ == "__main__":
    application.run()
