# 德育分管理系统

一个现代化的学生德育分管理平台，支持个人申请、集体申请、审核管理、数据统计等完整功能。

## ✨ 主要功能

### 👨‍🎓 学生端

- **个人申请**：提交思想政治理论分、学术科研分、社会服务分、奖励分等申请
- **我的德育分**：查看个人德育分记录，按类别分组展示，支持按学年筛选
- **我的申请**：查看个人提交的申请记录和审核状态
- **集体申请记录**：查看教师端提交的集体申请（涉及本人的记录）
- **数据导出**：导出个人德育分明细（Excel格式）
- **公告查看**：查看系统公告和通知

### 👨‍🏫 教师端

- **集体申请**：批量提交德育分申请（支持Excel/CSV格式学生名单导入）
- **申请管理**：查看和管理已提交的集体申请状态
- **类别管理**：管理教师端可用的德育分类别（集体活动分、文体竞赛分、任职分等）
- **批量操作**：一次性为多名学生添加德育分记录

### 👨‍💼 管理员端

- **统一审核**：在同一页面审核学生个人申请和教师集体申请（支持批准/拒绝/批量操作）
- **系统管理**：
  - 学年管理（创建、激活学年）
  - 公告管理（发布、编辑、删除公告）
- **数据统计**：
  - 全校德育分排行榜（支持按学年、书院、年级、班级筛选）
  - 德育分分布统计和可视化
  - 批量导出排行榜数据
- **修改密码**：管理员密码修改

## 📁 项目结构

```text
├── app.py                              # Flask应用主文件（2179行）
├── requirements.txt                    # Python依赖
├── static/                             # 静态文件
│   ├── css/
│   │   └── style.css                   # 全局样式
│   └── js/                             # JavaScript文件
├── templates/                          # HTML模板
│   ├── base.html                       # 基础模板（含导航）
│   ├── login.html                      # 登录页面
│   ├── announcements.html              # 公告查看
│   ├── change_password.html            # 修改密码
│   ├── application_form.html           # 个人申请表单
│   ├── category_application_form.html  # 类别管理页面
│   ├── my_applications.html            # 我的申请记录
│   ├── category_my_applications.html   # 我的类别申请
│   ├── my_scores.html                  # 学生德育分查询
│   ├── group_application.html          # 教师集体申请
│   ├── my_group_applications.html      # 我的集体申请记录
│   ├── unified_review.html             # 统一审核页面（学生+教师申请）
│   ├── system_manage.html              # 系统管理页面（学年+公告）
│   ├── teacher_scores.html             # 教师端管理
│   └── statistics.html                 # 统计和排行榜
├── instance/                           # 实例数据
│   └── moral_score.db                  # SQLite数据库
└── uploads/                            # 上传文件存储
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- pip

### 1. 克隆项目

```bash
git clone <repository-url>
cd dyf
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

### 4. 默认账户

首次启动时，系统会自动初始化数据库并创建默认账户（在 `init_db()` 函数中配置）

**建议**：首次登录后立即修改默认密码

## 🛠️ 技术栈

- **后端框架**：Flask 2.x
- **ORM**：SQLAlchemy
- **数据库**：SQLite
- **前端**：HTML5, CSS3, JavaScript (原生)
- **UI框架**：Bootstrap 4
- **图标库**：Font Awesome 5
- **数据处理**：pandas, openpyxl
- **文件上传**：Werkzeug

## 📊 数据库模型

| 模型 | 说明 |
|------|------|
| **User** | 用户表（学生、教师、管理员三种角色） |
| **ScoreCategory** | 德育分类别表（主类别+子类别） |
| **ScoreApplication** | 个人申请表（学生端提交） |
| **GroupApplication** | 集体申请表（教师端提交） |
| **GroupApplicationMember** | 集体申请成员关联表 |
| **ScoreRecord** | 德育分记录表（审核通过后生成） |
| **AcademicYear** | 学年管理表 |
| **Announcement** | 公告表 |

## ✨ 核心特性

### 🎯 德育分类别体系

#### 学生端可申请类别

| 主类别 | 子类别 | 上限 |
|--------|--------|------|
| **思想政治理论分** | 思想政治理论 | 3分 |
| **学术科研分** | 专利、专著、论文 | 10分 |
| **社会服务分** | 工时、挂职锻炼、政府见习 | 4分 |
| **奖励分** | 市级奖励、省级奖励、国家级奖励 | 5分 |

#### 教师端可管理类别

| 主类别 | 子类别 | 上限 |
|--------|--------|------|
| **集体活动分** | 集体活动分 | 3分 |
| **学术科研分** | 竞赛 | 10分 |
| **文体竞赛分** | 文艺竞赛、体育竞赛 | 6分 |
| **任职分** | 学生组织、社团、班级 | 4分（仅取最高项） |
| **奖励分** | 院级奖励、校级奖励 | 5分 |
| **社会服务分** | 社会实践 | 4分 |
| **扣分** | 扣分 | 无上限 |

### 📐 德育分计算规则

1. **主类别上限**：每个主类别有分数上限（如学术科研分最高10分）
2. **子类别上限**：特定子类别有独立上限（如**工时最多加1分**）
3. **任职分特殊规则**：只取最高的1项，不累加
4. **其他类别**：在各自子类别上限内累加，但不超过主类别上限
5. **总分范围**：最终德育分在0-100分之间

**计算顺序**：
```
单项分数 → 应用子类别上限 → 按主类别分组 → 应用主类别上限 → 汇总总分
```

### 🔐 权限控制

- **学生**：只能查看和申请个人德育分，查看涉及自己的集体申请
- **教师**：可以批量提交集体申请，管理教师端类别
- **管理员**：拥有所有权限，包括审核、统计、系统管理

### 📤 文件上传

- **证明材料**：支持 PDF 格式（个人申请时上传）
- **学生名单**：支持 Excel (.xlsx, .xls) 和 CSV 格式
- **文件大小限制**：10MB
- **存储路径**：`uploads/` 目录

### 📊 数据导出

- **个人德育分**：导出个人所有德育分记录（Excel格式）
- **排行榜导出**：按条件筛选后导出全校排行榜
- **筛选条件**：支持按学年、书院、年级、班级筛选

## 🔄 最近优化

### v1.0 - 核心功能
- ✅ 基础的申请、审核、统计功能
- ✅ 学生、教师、管理员三端分离

### v1.1 - 代码重构
- ✅ 移除已弃用的学期逻辑，统一使用学年
- ✅ 中心化类别定义和常量（`TEACHER_MAIN_CATEGORIES`, `STUDENT_MAIN_CATEGORIES` 等）
- ✅ 抽取通用工具函数（`is_teacher_category`, `calculate_category_score_with_subcategory`）
- ✅ 消除重复的类别初始化代码

### v1.2 - UI/UX改进
- ✅ 统一审核页面：合并学生个人申请和教师集体申请的审核界面
- ✅ 统一系统管理：合并学年管理和公告管理为单一标签页面
- ✅ 删除冗余的旧页面和路由

### v1.3 - 业务逻辑优化
- ✅ 实现工时子类别1分上限
- ✅ 完善排行榜的班级筛选功能
- ✅ 优化分数计算逻辑（先应用子类别限制，再应用主类别限制）

### v1.4 - 代码清理
- ✅ 移除 PythonAnywhere 部署配置
- ✅ 清理不必要的静态文件夹配置

## 🏗️ 架构设计

### 后端架构

```
app.py
├── 常量定义区（类别、限制）
├── 模型定义区（User, ScoreCategory, ScoreApplication, etc.）
├── 工具函数区（is_teacher_category, calculate_category_score_with_subcategory）
├── 路由处理区
│   ├── 认证路由（登录、登出）
│   ├── 学生端路由
│   ├── 教师端路由
│   ├── 管理员路由
│   └── API路由
└── 数据库初始化（init_db）
```

### 前端架构

- **基础模板**：`base.html` 提供统一导航和样式
- **角色分离**：不同角色看到不同的导航菜单
- **响应式设计**：使用 Bootstrap 实现移动端适配
- **标签页UI**：审核页面和管理页面使用标签切换，提升用户体验

## 🧪 开发建议

### 添加新的德育分类别

1. 在 `app.py` 中更新相应的常量列表：
   - `TEACHER_MAIN_CATEGORIES` 或 `STUDENT_MAIN_CATEGORIES`
   - `TEACHER_ALLOWED_CHILDREN` 或 `STUDENT_ALLOWED_CHILDREN`
2. 在 `CATEGORY_MAX_LIMITS` 中设置主类别上限
3. （可选）在 `SUBCATEGORY_MAX_LIMITS` 中设置子类别上限
4. 重启应用，系统会自动初始化新类别

### 修改分数计算规则

编辑 `calculate_category_score_with_subcategory` 函数，该函数处理：
- 子类别分数累加
- 子类别上限应用
- 主类别上限应用
- 特殊规则（如任职分只取最高项）

### 数据库迁移

SQLite 不支持某些 ALTER TABLE 操作，建议：
1. 在 `init_db()` 函数中添加迁移逻辑
2. 使用表重建策略（创建新表 → 复制数据 → 删除旧表 → 重命名新表）

## 📝 API 端点示例

### 获取个人德育分
```
GET /api/scores/my?academic_year_id=1
```

### 提交个人申请
```
POST /api/applications
Content-Type: multipart/form-data
```

### 获取排行榜
```
GET /api/scores/all?academic_year_id=1&college=XX书院&grade=2023&class_name=1班
```

### 审核申请
```
POST /api/applications/{id}/review
Body: {"action": "approve", "admin_notes": "审核通过"}
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎贡献代码、提出建议或报告问题！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issues
- 发送邮件（待补充）

---

**注意**：本系统为教育管理系统，请在生产环境中注意数据安全和隐私保护。建议：
- 使用 HTTPS 协议
- 定期备份数据库
- 设置强密码策略
- 限制文件上传类型和大小
- 在生产环境中关闭 Flask 的 DEBUG 模式
