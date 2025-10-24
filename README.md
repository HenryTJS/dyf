# 德育分管理系统

一个现代化的学生德育分管理平台，支持个人申请、集体申请、审核管理等功能。

## ✨ 主要功能

### 学生端

- 个人德育分申请提交
- 查看德育分记录（按类别分组）
- 查看个人申请和教师端集体申请记录
- 按学年筛选查看德育分
- 德育分数据导出

### 教师端

- 集体德育分申请（批量导入学生名单）
- 查看已提交的集体申请状态
- 管理教师端德育分类别
- Excel/CSV格式学生名单导入

### 管理员端

- 个人申请审核
- 集体申请审核
- 学年管理
- 公告发布与管理
- 数据统计与分析
- 德育分排行榜导出

## 📁 项目结构

```text
├── app.py                     # Flask应用主文件
├── requirements.txt           # Python依赖
├── static/                    # 静态文件
│   ├── css/                   # 样式文件
│   └── js/                    # JavaScript文件
├── templates/                 # HTML模板
│   ├── base.html             # 基础模板
│   ├── login.html            # 登录页面
│   ├── my_scores.html        # 学生德育分查询
│   ├── teacher_scores.html   # 教师端管理
│   └── statistics.html       # 统计页面
├── instance/                  # 数据库文件
│   └── moral_score.db        # SQLite数据库
└── uploads/                   # 上传文件存储
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

应用将在 <http://localhost:5000> 启动

### 3. 默认账户

首次使用时，系统会自动创建默认账户（在代码中配置）

## 🛠️ 技术栈

- **后端框架**：Flask 2.x
- **ORM**：SQLAlchemy
- **数据库**：SQLite
- **前端**：HTML5, CSS3, JavaScript (原生)
- **UI框架**：Bootstrap 4
- **图标库**：Font Awesome
- **文件处理**：pandas, openpyxl

## 📊 数据库模型

- **User** - 用户表（学生、教师、管理员）
- **ScoreCategory** - 德育分类别表
- **ScoreApplication** - 个人申请表
- **GroupApplication** - 集体申请表
- **GroupApplicationMember** - 集体申请成员表
- **ScoreRecord** - 德育分记录表
- **AcademicYear** - 学年管理表
- **Announcement** - 公告表

## ✨ 核心特性

### 德育分计算规则

- 支持多个类别的分数累加
- 各类别设有上限限制
- 任职分取最高项（不叠加）
- 总分限制在0-100分之间

### 文件上传

- 支持PDF格式证明材料上传
- 支持Excel/CSV格式学生名单导入
- 文件大小限制：10MB

### 数据导出

- 个人德育分导出（Excel格式）
- 全校德育分排行榜导出
- 支持按学年、书院、年级筛选

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。
