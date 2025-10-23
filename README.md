# 德育分后台管理系统

一个使用Flask作为后端的德育分管理系统，包含学生申请、管理员审核、数据统计等功能。

## 🚀 技术栈

### 后端

- **Python 3.8+**
- **Flask 2.3.3** - Web框架
- **Flask-SQLAlchemy** - 数据库ORM
- **Flask-CORS** - 跨域支持
- **PyJWT** - JWT身份验证
- **pandas** - Excel文件处理
- **SQLite** - 数据库

### 前端

- **HTML5 + Bootstrap 5** - 响应式界面
- **JavaScript** - 交互功能
- **CSS3** - 样式设计

## 📋 功能特性

### 学生功能

- ✅ **个人申请加分**：填写申请信息，上传证明材料
- ✅ **申请记录查询**：查看申请历史和审核状态
- ✅ **德育分查询**：查看个人德育分统计和记录
- ✅ **公告查看**：查看最新通知和公告

### 管理员功能

- ✅ **申请审核**：审核学生申请，通过/拒绝并填写意见
- ✅ **统一导入加分**：Excel批量导入德育分数据
- ✅ **数据汇总**：统计图表、排行榜、数据分析
- ✅ **公告管理**：发布、编辑、删除系统公告

## 🛠️ 安装和运行

### 环境要求

- **Python 3.8+** （推荐Python 3.9或更高版本）

### 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载并安装最新版本的Python
3. 安装时勾选"Add Python to PATH"

### 快速启动

#### 方法1：直接启动

```bash
python app.py
```

#### 方法2：先创建演示数据

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 创建演示数据（可选）
python demo_data.py

# 3. 启动系统
python app.py
```

### 访问系统

- **系统地址**：http://localhost:5000

## 👤 默认账户

### 管理员账户

- 用户名：`admin`
- 密码：`admin123`

### 演示学生账户

- 用户名：`student001` 密码：`123456` 姓名：张三
- 用户名：`student002` 密码：`123456` 姓名：李四
- 用户名：`student003` 密码：`123456` 姓名：王五
- 用户名：`student004` 密码：`123456` 姓名：赵六
- 用户名：`student005` 密码：`123456` 姓名：钱七

## 📋 功能使用

### 学生功能

#### 1. 申请德育分

1. 登录后点击"申请德育分"
2. 选择德育分类别（思想品德、学习表现等）
3. 填写申请标题和详细描述
4. 输入申请分数（1-100分）
5. 上传证明材料（可选）
6. 点击"提交申请"

#### 2. 查看申请记录

1. 点击"我的申请"
2. 查看所有申请记录
3. 查看申请状态：待审核/已通过/已拒绝
4. 点击"查看详情"了解审核结果

#### 3. 查询德育分

1. 点击"德育分查询"
2. 查看个人德育分总分
3. 查看各类别分数统计
4. 查看详细获得记录

#### 4. 查看公告

1. 点击"公告栏"
2. 查看最新公告和通知
3. 重要公告会有特殊标识

### 管理员功能

#### 1. 审核申请

1. 登录管理员账户
2. 点击"审核申请"
3. 查看待审核申请列表
4. 点击"审核"查看详细信息
5. 选择通过/拒绝并填写审核意见
6. 提交审核结果

#### 2. 批量导入德育分

1. 点击"批量导入德育分"
2. 下载Excel模板
3. 按模板格式填写数据：
   - 学号（必填）
   - 类别名称（必填）
   - 分数（必填）
   - 描述（可选）
   - 学期（可选）
4. 上传Excel文件
5. 查看导入结果

#### 3. 数据统计

1. 点击"数据统计"
2. 查看系统整体数据
3. 查看各类别统计图表
4. 查看学生德育分排行榜

#### 4. 公告管理

1. 点击"公告管理"
2. 发布新公告
3. 编辑或删除已有公告
4. 设置重要公告标识

## 🎯 德育分类别

系统预设了以下德育分类别：

- **思想品德**：思想政治表现、道德品质等，最高100分
- **学习表现**：学习态度、成绩表现等，最高100分
- **社会实践**：志愿服务、社会实践等，最高100分
- **文体活动**：文艺、体育等活动参与，最高100分
- **创新实践**：科技创新、创业实践等，最高100分

## 📊 Excel导入格式

批量导入德育分需要按照以下格式填写Excel文件：

| 字段名 | 说明 | 必填 | 示例 |
|--------|------|------|------|
| student_id | 学生学号 | 是 | 2024001 |
| category_name | 德育分类别名称 | 是 | 思想品德 |
| score | 德育分分数 | 是 | 10 |
| description | 描述说明 | 否 | 参与志愿服务活动 |
| semester | 学期 | 否 | 2024-1 |

## 📁 项目结构

```
德育分管理系统/
├── 📄 app.py                    # Flask主应用
├── 📄 requirements.txt          # Python依赖
├── 📄 demo_data.py              # 演示数据脚本
├── 📄 README.md                 # 系统说明
├── 📁 templates/                # Flask模板
│   ├── 📄 base.html            # 基础模板
│   ├── 📄 login.html           # 登录页面
│   └── 📄 dashboard.html       # 首页
├── 📁 static/                   # 静态文件
│   ├── 📁 css/
│   │   └── 📄 style.css        # 样式文件
│   ├── 📁 js/
│   │   └── 📄 main.js          # JavaScript文件
│   └── 📁 images/              # 图片资源
├── 📁 uploads/                  # 文件上传目录
└── 📁 instance/                 # 数据库文件
    └── 📄 moral_score.db       # SQLite数据库
```

## 🔧 API接口

### 认证相关

- `POST /api/login` - 用户登录
- `GET /api/user/profile` - 获取用户信息

### 申请管理

- `POST /api/applications` - 提交申请
- `GET /api/applications/my` - 获取个人申请
- `GET /api/applications` - 获取所有申请（管理员）
- `PUT /api/applications/<id>/review` - 审核申请

### 德育分管理

- `GET /api/scores/my` - 获取个人德育分
- `GET /api/scores/all` - 获取所有德育分（管理员）
- `POST /api/import/scores` - 批量导入德育分

### 统计和公告

- `GET /api/statistics` - 获取统计数据
- `GET /api/announcements` - 获取公告列表
- `POST /api/announcements` - 发布公告
- `PUT /api/announcements/<id>` - 更新公告
- `DELETE /api/announcements/<id>` - 删除公告

## 🔧 常见问题

### Q: Python安装后无法识别命令？

A: 需要将Python添加到系统PATH环境变量中，或重新安装Python并勾选"Add Python to PATH"。

### Q: pip install失败怎么办？

A: 尝试使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q: 端口被占用怎么办？

A: 修改 `app.py` 文件中的端口号：

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为5001端口
```

### Q: 忘记管理员密码怎么办？

A: 删除数据库文件 `instance/moral_score.db`，重新启动系统会自动创建默认管理员账户。

### Q: 如何备份数据？

A: 直接复制 `instance/moral_score.db` 文件即可完成数据备份。

### Q: 系统运行缓慢怎么办？

A: 检查数据库文件大小，如果过大可以清理历史数据，或考虑升级到MySQL等专业数据库。

## 🛠️ 开发说明

### 修改配置

- 修改 `app.py` 中的配置参数
- 调整 `requirements.txt` 中的依赖版本
- 修改前端模板调整界面样式

### 添加新功能

1. 在 `app.py` 中添加新的路由和视图函数
2. 如需新的数据模型，在 `app.py` 中定义新的Model类
3. 在 `templates/` 中创建新页面模板
4. 更新静态文件（CSS/JS）

## 📞 技术支持

如遇到问题，请检查：

1. Python版本是否为3.8以上
2. 是否已安装所有依赖：`pip install -r requirements.txt`
3. 端口5000是否被占用
4. 数据库文件是否存在且可读写
5. 防火墙是否阻止了服务运行

## 📄 许可证

MIT License
