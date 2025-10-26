from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime, timedelta
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'moral_score_secret_key_2024'

# SQLite数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
# 使用Flask标准的instance文件夹存储数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'moral_score.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化扩展
db = SQLAlchemy(app)

# ==================== 类别相关常量定义 ====================
# 教师端可管理的主类别
TEACHER_MAIN_CATEGORIES = ['集体活动分', '学术科研分', '文体竞赛分', '任职分', '奖励分', '社会服务分', '扣分']

# 学生端可申请的主类别
STUDENT_MAIN_CATEGORIES = ['思想政治理论分', '学术科研分', '社会服务分', '奖励分']

# 教师端可管理的子类别（按主类别分组）
TEACHER_ALLOWED_CHILDREN = {
    '集体活动分': ['集体活动分'],
    '学术科研分': ['竞赛'],
    '文体竞赛分': ['文艺竞赛', '体育竞赛'],
    '任职分': ['学生组织', '社团', '班级'],
    '奖励分': ['院级奖励', '校级奖励'],
    '社会服务分': ['社会实践'],
    '扣分': ['扣分']
}

# 学生端可申请的子类别（按主类别分组）
STUDENT_ALLOWED_CHILDREN = {
    '思想政治理论分': ['思想政治理论'],
    '学术科研分': ['专利', '专著', '论文'],
    '社会服务分': ['工时', '挂职锻炼', '政府见习'],
    '奖励分': ['市级奖励', '省级奖励', '国家级奖励']
}

# 纯教师端主类别（所有子类别都是教师端管理）
PURE_TEACHER_CATEGORIES = ['集体活动分', '文体竞赛分', '任职分', '扣分']

# 教师端子类别（混合主类别中的教师端子类别）
TEACHER_SUBCATEGORIES = {
    '社会服务分': ['社会实践'],
    '学术科研分': ['竞赛'],
    '奖励分': ['院级奖励', '校级奖励']
}

# 所有主类别列表
ALL_MAIN_CATEGORIES = ['思想政治理论分', '社会服务分', '集体活动分', '学术科研分', '文体竞赛分', '奖励分', '任职分', '扣分']

# 主类别分数上限
CATEGORY_MAX_LIMITS = {
    '思想政治理论分': 3,
    '社会服务分': 4,
    '集体活动分': 3,
    '学术科研分': 10,
    '文体竞赛分': 6,
    '奖励分': 5,
    '任职分': 4,
    '扣分': 0
}

# 子类别分数上限（单个子类别的最高分）
SUBCATEGORY_MAX_LIMITS = {
    '工时': 1,  # 工时最多加1分
    # 可以继续添加其他有特殊限制的子类别
}

# 特殊处理的类别
SPECIAL_CATEGORY_ZHIREN = '任职分'  # 任职分只能取最高1项，不能叠加

# ==================== 工具函数 ====================
def is_teacher_category(main_category_name, sub_category_name=None):
    """判断类别是否为教师端管理"""
    if main_category_name in PURE_TEACHER_CATEGORIES:
        return True
    if sub_category_name and main_category_name in TEACHER_SUBCATEGORIES:
        return sub_category_name in TEACHER_SUBCATEGORIES[main_category_name]
    return False

def calculate_category_score(main_category, scores):
    """计算主类别最终分数（应用上限和特殊规则）
    注意：这个函数接收的是简单分数列表，不包含子类别信息
    如果需要应用子类别限制，请使用 calculate_category_score_with_subcategory
    """
    max_limit = CATEGORY_MAX_LIMITS.get(main_category, 100)
    
    if main_category == SPECIAL_CATEGORY_ZHIREN:
        # 任职分：只能取最高1项
        max_score = max(scores) if scores else 0
        return min(max_score, max_limit)
    else:
        # 其他类别：累加但不超过主类别最高分
        total_score = sum(scores)
        return min(total_score, max_limit)

def calculate_category_score_with_subcategory(main_category, records):
    """计算主类别最终分数（应用子类别和主类别上限）
    
    Args:
        main_category: 主类别名称
        records: 记录列表，每条记录需包含 'score' 和 'category_name' 字段
    
    Returns:
        最终分数
    """
    # 按子类别分组
    subcategory_scores = {}
    for record in records:
        sub_name = record.get('category_name', '')
        if sub_name not in subcategory_scores:
            subcategory_scores[sub_name] = []
        subcategory_scores[sub_name].append(record['score'])
    
    # 计算每个子类别的分数（应用子类别上限）
    total_score = 0
    for sub_name, scores in subcategory_scores.items():
        sub_total = sum(scores)
        # 应用子类别上限（如工时最多1分）
        if sub_name in SUBCATEGORY_MAX_LIMITS:
            sub_total = min(sub_total, SUBCATEGORY_MAX_LIMITS[sub_name])
        total_score += sub_total
    
    # 应用主类别上限和特殊规则
    max_limit = CATEGORY_MAX_LIMITS.get(main_category, 100)
    
    if main_category == SPECIAL_CATEGORY_ZHIREN:
        # 任职分：只能取最高1项
        all_scores = [r['score'] for r in records]
        max_score = max(all_scores) if all_scores else 0
        return min(max_score, max_limit)
    else:
        # 其他类别：累加但不超过主类别最高分
        return min(total_score, max_limit)

# ==================== 数据库模型 ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    # 学生字段
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    class_name = db.Column(db.String(50), nullable=True)
    college = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(20), nullable=True)
    # 教师/审核端字段
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    teacher_college = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'student_id': self.student_id,
            'class_name': self.class_name,
            'college': self.college,
            'grade': self.grade,
            'role': self.role
        }

class ScoreCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    max_score = db.Column(db.Integer, default=100)
    parent_id = db.Column(db.Integer, db.ForeignKey('score_category.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    parent = db.relationship('ScoreCategory', remote_side=[id], backref='children')

class ScoreApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('score_category.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    evidence = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_comment = db.Column(db.Text)
    academic_year = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    # 关系
    user = db.relationship('User', foreign_keys=[user_id])
    category = db.relationship('ScoreCategory')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

class AcademicYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_name = db.Column(db.String(20), unique=True, nullable=False)  # 如 "2025-2026"
    is_current = db.Column(db.Boolean, default=False)  # 是否为当前学年
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AcademicYear {self.year_name}>'

class ScoreRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('score_category.id'), nullable=True)  # 允许为空，用于初始德育分
    score = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    academic_year = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 追溯来源，可空
    application_id = db.Column(db.Integer, nullable=True)
    group_application_id = db.Column(db.Integer, nullable=True)

    # 关系
    user = db.relationship('User')
    category = db.relationship('ScoreCategory')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_important = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    author = db.relationship('User')

# 集体申请相关模型
class GroupApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('score_category.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_comment = db.Column(db.Text)
    academic_year = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    teacher = db.relationship('User', foreign_keys=[teacher_user_id])
    category = db.relationship('ScoreCategory')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])

class GroupApplicationMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_application_id = db.Column(db.Integer, db.ForeignKey('group_application.id'), nullable=False)
    student_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    
    # 添加唯一性约束，防止同一申请中重复添加同一学生
    __table_args__ = (db.UniqueConstraint('group_application_id', 'student_user_id', name='unique_group_student'),)

    group_application = db.relationship('GroupApplication', backref='members')
    student = db.relationship('User')


# 路由定义


@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    # 获取用户角色
    user_role = session.get('user', {}).get('role', 'student')

    # 角色下的主类别与允许的子类别
    if user_role == 'teacher':
        main_names = TEACHER_MAIN_CATEGORIES
        allowed_children = TEACHER_ALLOWED_CHILDREN
    else:
        main_names = STUDENT_MAIN_CATEGORIES
        allowed_children = STUDENT_ALLOWED_CHILDREN

    # 获取主类别
    main_categories = ScoreCategory.query.filter(
        ScoreCategory.name.in_(main_names),
        ScoreCategory.parent_id == None
    ).all()

    result = []
    for main_cat in main_categories:
        category_data = {
            'id': main_cat.id,
            'name': main_cat.name,
            'description': main_cat.description,
            'max_score': main_cat.max_score,
            'parent_id': main_cat.parent_id,
            'children': []
        }

        # 获取并按角色过滤子类别
        subcategories = ScoreCategory.query.filter_by(parent_id=main_cat.id).all()
        for sub_cat in subcategories:
            if main_cat.name in allowed_children:
                if sub_cat.name not in allowed_children[main_cat.name]:
                    continue
            category_data['children'].append({
                'id': sub_cat.id,
                'name': sub_cat.name,
                'description': sub_cat.description,
                'max_score': sub_cat.max_score,
                'parent_id': sub_cat.parent_id
            })

        result.append(category_data)

    return jsonify(result)

@app.route('/api/categories/all', methods=['GET'])
def api_get_all_categories():
    """获取所有类别（包括教师端管理的类别），用于学生端显示"""
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 获取所有主类别
    main_categories = ScoreCategory.query.filter(ScoreCategory.parent_id == None).all()
    
    result = []
    for main_cat in main_categories:
        # 判断主类别来源类型
        source_type = '教师端' if main_cat.name in PURE_TEACHER_CATEGORIES else '学生端'
        
        category_data = {
            'id': main_cat.id,
            'name': main_cat.name,
            'description': main_cat.description,
            'max_score': main_cat.max_score,
            'parent_id': main_cat.parent_id,
            'source_type': source_type,
            'children': []
        }

        # 获取子类别并判断每个子类别的来源类型
        subcategories = ScoreCategory.query.filter_by(parent_id=main_cat.id).all()
        for sub_cat in subcategories:
            # 判断子类别是否为教师端管理
            sub_source_type = '教师端' if is_teacher_category(main_cat.name, sub_cat.name) else '学生端'
            
            category_data['children'].append({
                'id': sub_cat.id,
                'name': sub_cat.name,
                'description': sub_cat.description,
                'max_score': sub_cat.max_score,
                'parent_id': sub_cat.parent_id,
                'source_type': sub_source_type
            })

        result.append(category_data)

    return jsonify(result)

@app.route('/api/categories/teacher', methods=['GET'])
def api_get_teacher_categories():
    """获取教师端管理的类别"""
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 获取教师端管理的主类别
    main_categories = ScoreCategory.query.filter(
        ScoreCategory.parent_id == None,
        ScoreCategory.name.in_(TEACHER_MAIN_CATEGORIES)
    ).all()
    
    result = []
    for main_cat in main_categories:
        category_data = {
            'id': main_cat.id,
            'name': main_cat.name,
            'description': main_cat.description,
            'max_score': main_cat.max_score,
            'parent_id': main_cat.parent_id,
            'source_type': '教师端',
            'children': []
        }

        # 获取子类别，并根据规则设置权限
        subcategories = ScoreCategory.query.filter_by(parent_id=main_cat.id).all()
        for sub_cat in subcategories:
            # 只添加教师端管理的子类别
            if is_teacher_category(main_cat.name, sub_cat.name):
                category_data['children'].append({
                    'id': sub_cat.id,
                    'name': sub_cat.name,
                    'description': sub_cat.description,
                    'max_score': sub_cat.max_score,
                    'parent_id': sub_cat.parent_id,
                    'source_type': '教师端'
                })

        # 只添加有教师端子类别的主类别
        if category_data['children']:
            result.append(category_data)

    return jsonify(result)

@app.route('/api/teacher/group-applications', methods=['GET'])
def api_get_teacher_group_applications():
    """获取教师的集体申请记录"""
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': '需要教师权限'}), 403
    
    teacher_id = session['user']['id']
    applications = GroupApplication.query.filter_by(teacher_user_id=teacher_id).order_by(GroupApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        result.append({
            'id': app.id,
            'title': app.title,
            'description': app.description,
            'evidence': app.evidence,
            'status': app.status,
            'review_comment': app.review_comment,
            'created_at': app.created_at.isoformat(),
            'reviewed_at': app.reviewed_at.isoformat() if app.reviewed_at else None,
            'academic_year': app.academic_year
        })
    
    return jsonify(result)

@app.route('/api/applications', methods=['POST'])
def api_create_application():
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    
    current_user_id = session['user']['id']
    print(f"学生申请提交，用户ID: {current_user_id}")
    
    # 处理文件上传
    evidence_filename = ''
    if 'evidence' in request.files:
        file = request.files['evidence']
        print(f"上传的文件: {file.filename if file else 'None'}")
        if file and file.filename:
            # 检查原始文件扩展名
            original_filename = file.filename
            print(f"原始文件名: {original_filename}")
            
            # 检查是否为PDF文件（基于原始文件名）
            if not original_filename.lower().endswith('.pdf'):
                print(f"原始文件不是PDF格式: {original_filename}")
                return jsonify({'message': '请上传PDF格式的文件'}), 400
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            print(f"处理后的文件名: {filename}")
            
            # 如果secure_filename过滤掉了扩展名，手动添加
            if not filename.lower().endswith('.pdf'):
                filename = filename + '.pdf'
                print(f"重新添加PDF扩展名: {filename}")
            
            # 添加时间戳避免重名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            # 保存文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            evidence_filename = filename
            print(f"文件保存成功: {evidence_filename}")
    else:
        print("未检测到文件上传")
    
    # 获取表单数据（全部必填）
    category_id = request.form.get('category_id')
    description = request.form.get('description')
    score = request.form.get('score')
    
    print(f"表单数据 - category_id: {category_id}, description: {description[:50] if description else None}, score: {score}")
    
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    current_academic_year = current_year.year_name if current_year else None
    
    academic_year = request.form.get('academic_year', current_academic_year)
    print(f"学年: {academic_year}")
    
    if not category_id or not description or not score:
        print("参数不完整，返回400错误")
        missing_fields = []
        if not category_id: missing_fields.append('申请类别')
        if not description: missing_fields.append('申请描述')
        if not score: missing_fields.append('申请分数')
        return jsonify({'message': f'请填写所有必填字段: {", ".join(missing_fields)}'}), 400
    # 学生端：证据必填
    if not evidence_filename:
        print("缺少证据文件，返回400错误")
        return jsonify({'message': '请上传PDF证明材料'}), 400
    
    application = ScoreApplication(
        user_id=current_user_id,
        category_id=category_id,
        title=description,  # 使用description作为title
        description=description,
        score=score,
        evidence=evidence_filename,
        academic_year=academic_year
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'message': '申请提交成功', 'id': application.id})

@app.route('/api/applications/<int:app_id>', methods=['PUT'])
def api_update_application(app_id):
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    current_user_id = session['user']['id']
    application = ScoreApplication.query.get_or_404(app_id)
    if application.user_id != current_user_id:
        return jsonify({'message': '无权修改他人申请'}), 403
    if application.status == 'approved':
        return jsonify({'message': '审核通过后不可修改'}), 400
    # 仅允许在待审或已驳回时修改
    description = request.form.get('description')
    score = request.form.get('score')
    category_id = request.form.get('category_id')
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    academic_year = request.form.get('academic_year', current_year.year_name if current_year else None)
    if 'evidence' in request.files:
        file = request.files['evidence']
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            application.evidence = filename
    if description:
        application.description = description
        application.title = description  # 使用description作为title
    if score is not None:
        application.score = score
    if category_id is not None:
        application.category_id = category_id
    if academic_year:
        application.academic_year = academic_year
    db.session.commit()
    return jsonify({'message': '申请已更新'})

@app.route('/api/applications/<int:app_id>/withdraw', methods=['POST'])
def api_withdraw_application(app_id):
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    current_user_id = session['user']['id']
    application = ScoreApplication.query.get_or_404(app_id)
    if application.user_id != current_user_id:
        return jsonify({'message': '无权撤回他人申请'}), 403
    if application.status == 'approved':
        return jsonify({'message': '审核通过后不可撤回'}), 400
    application.status = 'withdrawn'
    db.session.commit()
    return jsonify({'message': '申请已撤回'})

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载上传的文件"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': '文件不存在'}), 404

@app.route('/api/applications/my', methods=['GET'])
def api_get_my_applications():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    if session['user']['role'] != 'student':
        return jsonify({'error': '仅学生可访问'}), 403
    
    user_id = session['user']['id']
    category_id = request.args.get('category_id', type=int)
    
    query = db.session.query(ScoreApplication, ScoreCategory).join(
        ScoreCategory, ScoreApplication.category_id == ScoreCategory.id
    ).filter(ScoreApplication.user_id == user_id)
    
    if category_id:
        query = query.filter(ScoreApplication.category_id == category_id)
    
    applications = query.order_by(ScoreApplication.created_at.desc()).all()
    
    result = []
    for app, category in applications:
        result.append({
            'id': app.id,
            'category_id': app.category_id,
            'title': app.title,
            'description': app.description,
            'score': app.score,
            'evidence': app.evidence,
            'status': app.status,
            'review_comment': app.review_comment,
            'created_at': app.created_at.isoformat(),
            'reviewed_at': app.reviewed_at.isoformat() if app.reviewed_at else None,
            'category_name': category.name,
            'academic_year': app.academic_year
        })
    
    return jsonify(result)

@app.route('/api/applications', methods=['GET'])
def api_get_all_applications():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    applications = db.session.query(ScoreApplication, ScoreCategory, User).join(
        ScoreCategory, ScoreApplication.category_id == ScoreCategory.id
    ).join(User, ScoreApplication.user_id == User.id).order_by(
        ScoreApplication.created_at.desc()
    ).all()
    
    result = []
    for app, category, user in applications:
        result.append({
            'id': app.id,
            'title': app.title,
            'description': app.description,
            'score': app.score,
            'evidence': app.evidence,
            'status': app.status,
            'review_comment': app.review_comment,
            'created_at': app.created_at.isoformat(),
            'reviewed_at': app.reviewed_at.isoformat() if app.reviewed_at else None,
            'category_name': category.name,
            'user_name': user.name,
            'student_id': user.student_id,
            'class_name': user.class_name
        })
    
    return jsonify(result)

@app.route('/api/applications/<int:app_id>/review', methods=['PUT'])
def api_review_application(app_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': '请求数据为空'}), 400
        
        application = ScoreApplication.query.get_or_404(app_id)
        application.status = data['status']
        application.review_comment = data['review_comment']
        application.reviewer_id = session['user']['id']
        application.reviewed_at = datetime.utcnow()
        
        # 如果审核通过，添加到德育分记录，先进行去重校验：同一学生、类别、学年不可重复
        if data['status'] == 'approved':
            if not application.academic_year:
                return jsonify({'message': '申请缺少学年，无法通过'}), 400
            existing = ScoreRecord.query.filter_by(
                user_id=application.user_id,
                category_id=application.category_id,
                academic_year=application.academic_year
            ).first()
            if existing:
                db.session.rollback()
                return jsonify({'message': '同一学生在同一类别和学年已有记录，不能重复通过'}), 400
            record = ScoreRecord(
                user_id=application.user_id,
                category_id=application.category_id,
                score=application.score,
                source='个人申请',
                description=application.title,
                academic_year=application.academic_year,
                application_id=application.id
            )
            db.session.add(record)
        
        db.session.commit()
        return jsonify({'message': '审核完成'})
    
    except Exception as e:
        db.session.rollback()
        print(f"审核错误: {e}")
        return jsonify({'message': f'审核失败: {str(e)}'}), 500

@app.route('/api/group-applications', methods=['POST'])
def api_create_group_application():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'message': '需要教师权限'}), 403
    teacher_user_id = session['user']['id']
    
    print(f"开始处理团体申请，教师ID: {teacher_user_id}")
    
    # 防重复提交：检查最近1分钟内是否有相同教师的申请（更宽松的限制）
    recent_apps = GroupApplication.query.filter(
        GroupApplication.teacher_user_id == teacher_user_id,
        GroupApplication.created_at >= datetime.utcnow() - timedelta(minutes=1)
    ).count()
    if recent_apps > 0:
        print(f"检测到重复提交，最近1分钟内有 {recent_apps} 个申请")
        return jsonify({'message': '请勿重复提交，请等待1分钟后再试'}), 400

    # 处理证据文件
    evidence_filename = ''
    if 'evidence' in request.files:
        file = request.files['evidence']
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            evidence_filename = filename

    category_id = request.form.get('category_id')
    description = request.form.get('description')
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    academic_year = request.form.get('academic_year', current_year.year_name if current_year else None)

    print(f"请求参数 - category_id: {category_id}, description: {description[:50] if description else None}, evidence_filename: {evidence_filename}")

    if not category_id or not description:
        print("参数不完整，返回400错误")
        return jsonify({'message': '参数不完整'}), 400
    
    # 教师端集体申请：证明材料必填
    if not evidence_filename:
        print("缺少证明材料，返回400错误")
        return jsonify({'message': '请上传证明材料'}), 400

    group_app = GroupApplication(
        teacher_user_id=teacher_user_id,
        category_id=category_id,
        title=description,
        description=description,
        evidence=evidence_filename,
        academic_year=academic_year
    )
    db.session.add(group_app)
    db.session.flush()

    # 读取成员Excel/CSV：字段 学号, 姓名, 班级, 分值
    if 'members' not in request.files:
        db.session.rollback()
        return jsonify({'message': '缺少成员名单文件'}), 400
    members_file = request.files['members']
    file_extension = os.path.splitext(members_file.filename)[1].lower()
    try:
        if file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(members_file)
        elif file_extension == '.csv':
            df = pd.read_csv(members_file)
        else:
            db.session.rollback()
            return jsonify({'message': '不支持的成员名单文件格式，请上传Excel或CSV文件'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'成员名单解析失败: {str(e)}'}), 400

    required_cols = ['学号', '姓名', '分值']
    
    # 检查必需列
    for col in required_cols:
        if col not in df.columns:
            db.session.rollback()
            return jsonify({'message': f'成员名单缺少必需列: {col}'}), 400

    # 检查Excel文件中是否有重复的学号
    student_ids = df['学号'].astype(str).str.strip()
    duplicates_in_file = student_ids[student_ids.duplicated()].tolist()
    if duplicates_in_file:
        # 只显示前3个重复的学号，避免错误信息过长
        duplicate_sample = duplicates_in_file[:3]
        return jsonify({'message': f'Excel文件中存在重复学号: {duplicate_sample}，请检查并删除重复行后重新提交'}), 400
    
    errors = []
    added = 0
    
    for _, row in df.iterrows():
        try:
            student_id = str(row['学号']).strip()
            score_val = int(row['分值'])
            
            user = User.query.filter_by(student_id=student_id, role='student').first()
            if not user:
                errors.append(f'学号不存在: {student_id}')
                continue
            member = GroupApplicationMember(
                group_application_id=group_app.id,
                student_user_id=user.id,
                score=score_val
            )
            db.session.add(member)
            added += 1
        except Exception as ie:
            if 'UNIQUE constraint failed' in str(ie):
                errors.append(f'学号 {student_id} 已存在于此申请中')
            else:
                errors.append(f'处理学号 {student_id} 时出错: {str(ie)}')

    if added == 0:
        db.session.rollback()
        return jsonify({'message': '成员名单为空或无有效成员', 'errors': errors}), 400

    db.session.commit()
    return jsonify({'message': '集体申请提交成功', 'id': group_app.id, 'errors': errors})

@app.route('/api/group-applications', methods=['GET'])
def api_get_all_group_applications():
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    
    role = session['user']['role']
    user_id = session['user']['id']
    
    if role == 'admin':
        # 管理员端：返回所有集体申请
        apps = GroupApplication.query.order_by(GroupApplication.created_at.desc()).all()
    elif role == 'teacher':
        # 教师端：只返回自己提交的集体申请
        apps = GroupApplication.query.filter_by(teacher_user_id=user_id).order_by(GroupApplication.created_at.desc()).all()
    else:
        # 学生端：返回自己参与的集体申请
        member_records = GroupApplicationMember.query.filter_by(student_user_id=user_id).all()
        app_ids = [m.group_application_id for m in member_records]
        apps = GroupApplication.query.filter(GroupApplication.id.in_(app_ids)).order_by(GroupApplication.created_at.desc()).all() if app_ids else []
    
    result = []
    for ga in apps:
        # 如果是学生查看，返回该学生在此申请中的分数
        student_score = None
        if role == 'student':
            member = GroupApplicationMember.query.filter_by(
                group_application_id=ga.id,
                student_user_id=user_id
            ).first()
            if member:
                student_score = member.score
        
        result.append({
            'id': ga.id,
            'title': ga.title,
            'description': ga.description,
            'academic_year': ga.academic_year,
            'status': ga.status,
            'created_at': ga.created_at.isoformat(),
            'member_count': len(ga.members),
            'teacher_name': ga.teacher.name if ga.teacher else '未知教师',
            'category_name': ga.category.name if ga.category else '未知类别',
            'student_score': student_score,
            'evidence': ga.evidence,
            'review_comment': ga.review_comment,
            'reviewed_at': ga.reviewed_at.isoformat() if ga.reviewed_at else None
        })
    return jsonify(result)

@app.route('/api/group-applications/my', methods=['GET'])
def api_get_my_group_applications():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'message': '需要教师权限'}), 403
    teacher_user_id = session['user']['id']
    apps = GroupApplication.query.filter_by(teacher_user_id=teacher_user_id).order_by(GroupApplication.created_at.desc()).all()
    result = []
    for ga in apps:
        result.append({
            'id': ga.id,
            'title': ga.title,
            'description': ga.description,
            'academic_year': ga.academic_year,
            'status': ga.status,
            'created_at': ga.created_at.isoformat(),
            'member_count': len(ga.members)
        })
    return jsonify(result)

@app.route('/api/group-applications/<int:gid>', methods=['GET'])
def api_get_group_application_detail(gid):
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    
    role = session['user']['role']
    user_id = session['user']['id']
    
    ga = GroupApplication.query.get_or_404(gid)
    
    # 权限检查：管理员可以查看所有申请，教师只能查看自己的申请
    if role == 'admin' or (role == 'teacher' and ga.teacher_user_id == user_id):
        # 获取成员详情
        members = []
        for member in ga.members:
            student = User.query.get(member.student_user_id)
            members.append({
                'student_id': student.student_id if student else '',
                'student_name': student.name if student else '',
                'class_name': student.class_name if student else '',
                'score': member.score
            })
        
        return jsonify({
            'id': ga.id,
            'title': ga.title,
            'description': ga.description,
            'academic_year': ga.academic_year,
            'status': ga.status,
            'created_at': ga.created_at.isoformat(),
            'teacher_name': ga.teacher.name if ga.teacher else '未知教师',
            'category_name': ga.category.name if ga.category else '未知类别',
            'evidence': ga.evidence,
            'review_comment': ga.review_comment,
            'members': members
        })
    else:
        return jsonify({'message': '无权访问'}), 403

@app.route('/api/group-applications/<int:gid>', methods=['PUT'])
def api_update_group_application(gid):
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'message': '需要教师权限'}), 403
    teacher_user_id = session['user']['id']
    ga = GroupApplication.query.get_or_404(gid)
    if ga.teacher_user_id != teacher_user_id:
        return jsonify({'message': '无权修改他人申请'}), 403
    if ga.status == 'approved':
        return jsonify({'message': '审核通过后不可修改'}), 400
    title = request.form.get('title')
    description = request.form.get('description')
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    academic_year = request.form.get('academic_year', current_year.year_name if current_year else None)
    category_id = request.form.get('category_id')
    if 'evidence' in request.files:
        file = request.files['evidence']
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            ga.evidence = filename
    if title:
        ga.title = title
    if description:
        ga.description = description
    if academic_year:
        ga.academic_year = academic_year
    if category_id is not None:
        ga.category_id = category_id

    # 可选：若上传了新成员名单，覆盖原有明细
    if 'members' in request.files:
        members_file = request.files['members']
        try:
            df = pd.read_excel(members_file)
        except Exception as e:
            return jsonify({'message': f'成员名单解析失败: {str(e)}'}), 400
        required_cols = ['学号', '姓名', '分值']
        
        # 检查必需列
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'message': f'成员名单缺少必需列: {col}'}), 400
        # 清空旧明细
        GroupApplicationMember.query.filter_by(group_application_id=ga.id).delete()
        added = 0
        for _, row in df.iterrows():
            try:
                student_id = str(row['学号']).strip()
                score_val = int(row['分值'])
                user = User.query.filter_by(student_id=student_id, role='student').first()
                if not user:
                    continue
                member = GroupApplicationMember(
                    group_application_id=ga.id,
                    student_user_id=user.id,
                    score=score_val
                )
                db.session.add(member)
                added += 1
            except Exception:
                continue
        if added == 0:
            return jsonify({'message': '成员名单为空或无有效成员'}), 400

    db.session.commit()
    return jsonify({'message': '集体申请已更新'})

@app.route('/api/group-applications/<int:gid>/withdraw', methods=['POST'])
def api_withdraw_group_application(gid):
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'message': '需要教师权限'}), 403
    teacher_user_id = session['user']['id']
    ga = GroupApplication.query.get_or_404(gid)
    if ga.teacher_user_id != teacher_user_id:
        return jsonify({'message': '无权撤回他人申请'}), 403
    if ga.status == 'approved':
        return jsonify({'message': '审核通过后不可撤回'}), 400
    ga.status = 'withdrawn'
    db.session.commit()
    return jsonify({'message': '集体申请已撤回'})

@app.route('/api/group-applications/<int:gid>/review', methods=['PUT'])
def api_review_group_application(gid):
    try:
        print(f"审核集体申请 {gid}，用户: {session.get('user', {}).get('name', '未知')}")
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        data = request.get_json()
        print(f"请求数据: {data}")
        if not data:
            return jsonify({'message': '请求数据为空'}), 400
        status = data.get('status')
        review_comment = data.get('review_comment')
        if status not in ['approved', 'rejected']:
            return jsonify({'message': '无效的审核状态'}), 400
        if status == 'rejected' and not review_comment:
            return jsonify({'message': '驳回需填写原因'}), 400
        ga = GroupApplication.query.get_or_404(gid)
        ga.status = status
        ga.review_comment = review_comment
        ga.reviewer_id = session['user']['id']
        ga.reviewed_at = datetime.utcnow()

        if status == 'approved':
            # 去重校验：任一成员存在相同user、category、academic_year记录则整单拒绝
            conflicts = []
            for m in ga.members:
                exist = ScoreRecord.query.filter_by(
                    user_id=m.student_user_id,
                    category_id=ga.category_id,
                    academic_year=ga.academic_year
                ).first()
                if exist:
                    student = User.query.get(m.student_user_id)
                    conflicts.append({'student_id': student.student_id, 'name': student.name})
            if conflicts:
                db.session.rollback()
                return jsonify({'message': '存在重复记录，无法通过', 'conflicts': conflicts}), 400
            # 批量落库
            for m in ga.members:
                rec = ScoreRecord(
                    user_id=m.student_user_id,
                    category_id=ga.category_id,
                    score=m.score,
                    source='集体申请',
                    description=ga.title,
                    academic_year=ga.academic_year,
                    group_application_id=ga.id
                )
                db.session.add(rec)

        db.session.commit()
        print(f"集体申请 {gid} 审核成功，状态: {status}")
        return jsonify({'message': '审核完成'})
    except Exception as e:
        db.session.rollback()
        print(f"审核集体申请 {gid} 失败: {str(e)}")
        return jsonify({'message': f'审核失败: {str(e)}'}), 500

@app.route('/api/statistics', methods=['GET'])
def api_get_statistics():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    default_academic_year = current_year.year_name if current_year else None
    
    # 统计个人申请
    total_individual_applications = ScoreApplication.query.count()
    pending_individual_applications = ScoreApplication.query.filter_by(status='pending').count()
    
    # 统计集体申请
    total_group_applications = GroupApplication.query.count()
    pending_group_applications = GroupApplication.query.filter_by(status='pending').count()
    
    # 总申请数 = 个人申请 + 集体申请
    total_applications = total_individual_applications + total_group_applications
    pending_applications = pending_individual_applications + pending_group_applications
    
    stats = {
        'totalUsers': User.query.filter_by(role='student').count(),
        'totalApplications': total_applications,
        'pendingApplications': pending_applications,
        'totalIndividualApplications': total_individual_applications,
        'totalGroupApplications': total_group_applications,
        'pendingIndividualApplications': pending_individual_applications,
        'pendingGroupApplications': pending_group_applications,
        'totalScores': db.session.query(db.func.sum(ScoreRecord.score)).scalar() or 0,
        'defaultAcademicYear': default_academic_year
    }
    
    return jsonify(stats)

@app.route('/api/scores/my', methods=['GET'])
def api_get_my_scores():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    if session['user']['role'] != 'student':
        return jsonify({'error': '仅学生可访问'}), 403
    
    user_id = session['user']['id']
    # 过滤参数：academic_year，如 2027-2028
    academic_year = request.args.get('academic_year')

    # 获取所有德育分记录，包括学生端和教师端可申请的类别
    query = db.session.query(ScoreRecord, ScoreCategory).join(
        ScoreCategory, ScoreRecord.category_id == ScoreCategory.id
    ).filter(ScoreRecord.user_id == user_id)

    if academic_year:
        query = query.filter(ScoreRecord.academic_year == academic_year)

    scores = query.order_by(
        ScoreRecord.created_at.desc()
    ).all()
    
    result = []
    total_score = 0
    
    # 使用定义的类别常量
    teacher_categories = TEACHER_MAIN_CATEGORIES
    student_categories = STUDENT_MAIN_CATEGORIES
    
    # 按主类别分组统计，应用分数上限限制
    category_scores = {}
    
    for record, category in scores:
        # 获取主类别
        if category.parent_id:
            parent_category = ScoreCategory.query.get(category.parent_id)
            main_category_name = parent_category.name
        else:
            main_category_name = category.name
        
        if main_category_name not in category_scores:
            category_scores[main_category_name] = []
        
        category_scores[main_category_name].append({
            'id': record.id,
            'score': record.score,
            'source': record.source,
            'description': record.description,
            'academic_year': record.academic_year,
            'created_at': record.created_at.isoformat(),
            'category_name': category.name,
            'category_id': category.id,
            'group_application_id': record.group_application_id
        })
    
    # 应用特殊规则计算最终分数（项目类别层面限制）
    final_scores = {}
    result = []
    total_score = 0
    
    for main_category, records in category_scores.items():
        # 计算该主类别的原始总分
        total_category_score = sum([r['score'] for r in records])
        
        # 使用新函数计算最终分数（应用子类别限制，如工时最多1分）
        final_score = calculate_category_score_with_subcategory(main_category, records)
        
        final_scores[main_category] = final_score
        total_score += final_score
        
        # 获取上限
        max_limit = CATEGORY_MAX_LIMITS.get(main_category, 100)
        
        # 为每个记录添加计算后的分数和主类别信息
        for record in records:
            # 判断类别来源
            source_type = '学生端' if record['category_name'] in student_categories else '教师端'
            
            result.append({
                'id': record['id'],
                'score': record['score'],
                'source': record['source'],
                'source_type': source_type,
                'description': record['description'],
                'academic_year': record['academic_year'],
                'created_at': record['created_at'],
                'category_name': record['category_name'],
                'category_id': record.get('category_id'),
                'group_application_id': record.get('group_application_id'),
                'main_category': main_category,
                'main_category_final_score': final_score,  # 主类别最终分数
                'main_category_original_score': total_category_score,  # 主类别原始分数
                'is_limited': total_category_score > max_limit  # 是否达到上限
            })
    
    # 设置总分最大值(100)和最小值(0)
    total_score = max(0, min(100, total_score))
    
    return jsonify({'scores': result, 'totalScore': total_score, 'categoryScores': final_scores})

@app.route('/api/scores/my/export', methods=['GET'])
def api_export_my_scores():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    user_id = session['user']['id']
    academic_year = request.args.get('academic_year')

    query = db.session.query(ScoreRecord, ScoreCategory).join(
        ScoreCategory, ScoreRecord.category_id == ScoreCategory.id
    ).filter(ScoreRecord.user_id == user_id)

    if academic_year:
        query = query.filter(ScoreRecord.academic_year == academic_year)

    rows = query.order_by(ScoreRecord.created_at.desc()).all()
    data = []
    for r, cat in rows:
        data.append({
            '类别': cat.name,
            '分值': r.score,
            '来源': r.source,
            '说明': r.description,
            '学年': r.academic_year,
            '创建时间': r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    df = pd.DataFrame(data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='我的德育分')
    buf.seek(0)
    filename = '我的德育分.xlsx' if not academic_year else f'我的德育分_{academic_year}.xlsx'
    return send_file(buf, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/api/scores/all', methods=['GET'])
def api_get_all_scores():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    # 过滤参数
    # 从数据库获取当前学年作为默认值
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    academic_year = request.args.get('academic_year', current_year.year_name if current_year else None)
    college = request.args.get('college')  # 书院筛选
    grade = request.args.get('grade')      # 年级筛选
    class_name = request.args.get('class_name')  # 班级筛选

    # 查询所有学生的德育分记录，需要应用项目类别上限
    base = db.session.query(
        User.id,
        User.name,
        User.student_id,
        User.class_name,
        User.college,
        User.grade,
        ScoreRecord.score,
        ScoreRecord.academic_year,
        ScoreCategory.name.label('category_name'),
        ScoreCategory.parent_id
    ).outerjoin(ScoreRecord, User.id == ScoreRecord.user_id).outerjoin(
        ScoreCategory, ScoreRecord.category_id == ScoreCategory.id
    ).filter(
        User.role == 'student'
    )

    # 按学年筛选
    if academic_year:
        base = base.filter(ScoreRecord.academic_year == academic_year)
    
    # 按书院筛选
    if college:
        base = base.filter(User.college == college)
    
    # 按年级筛选
    if grade:
        base = base.filter(User.grade == grade)
    
    # 按班级筛选
    if class_name:
        base = base.filter(User.class_name == class_name)

    # 获取所有记录
    records = base.all()
    
    # 按学生分组，应用项目类别上限计算总分
    student_scores = {}
    
    for record in records:
        user_id = record.id
        if user_id not in student_scores:
            student_scores[user_id] = {
                'name': record.name,
                'student_id': record.student_id,
                'class_name': record.class_name,
                'college': record.college,
                'grade': record.grade,
                'category_scores': {},
                'total_score': 0,
                'record_count': 0
            }
        
        if record.score is not None:
            student_scores[user_id]['record_count'] += 1
            
            # 获取主类别
            if record.parent_id:
                parent_category = ScoreCategory.query.get(record.parent_id)
                main_category_name = parent_category.name
            else:
                main_category_name = record.category_name
            
            if main_category_name not in student_scores[user_id]['category_scores']:
                student_scores[user_id]['category_scores'][main_category_name] = []
            
            # 存储包含子类别信息的记录
            student_scores[user_id]['category_scores'][main_category_name].append({
                'score': record.score,
                'category_name': record.category_name
            })
    
    # 应用项目类别上限计算最终分数
    result = []
    for user_id, data in student_scores.items():
        total_score = 0
        
        for main_category, records in data['category_scores'].items():
            # 使用新函数计算最终分数（应用子类别限制，如工时最多1分）
            final_score = calculate_category_score_with_subcategory(main_category, records)
            total_score += final_score
        
        # 设置总分最大值(100)和最小值(0)
        total_score = max(0, min(100, total_score))
        
        result.append({
            'name': data['name'],
            'student_id': data['student_id'],
            'class_name': data['class_name'],
            'college': data['college'],
            'grade': data['grade'],
            'total_score': total_score,
            'record_count': data['record_count']
        })
    
    # 按总分排序
    result.sort(key=lambda x: x['total_score'], reverse=True)
    
    return jsonify(result)

@app.route('/api/academic-years', methods=['GET'])
def api_get_academic_years():
    """获取学年信息"""
    # 从数据库获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    current_academic_year = current_year.year_name if current_year else None
    
    # 获取所有可用学年
    all_years = AcademicYear.query.order_by(AcademicYear.year_name.desc()).all()
    available_years = [year.year_name for year in all_years]
    
    return jsonify({
        'currentAcademicYear': current_academic_year,
        'availableYears': available_years,
        'academicYears': [{'year_name': year, 'is_current': year == current_academic_year} for year in available_years]
    })

@app.route('/api/admin/academic-years', methods=['GET'])
def api_admin_get_academic_years():
    """管理员获取所有学年信息"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    years = AcademicYear.query.order_by(AcademicYear.year_name.desc()).all()
    result = []
    for year in years:
        result.append({
            'id': year.id,
            'year_name': year.year_name,
            'is_current': year.is_current,
            'created_at': year.created_at.isoformat() if year.created_at else None
        })
    
    return jsonify(result)

@app.route('/api/admin/academic-years', methods=['POST'])
def api_admin_add_academic_year():
    """管理员添加新学年"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    data = request.get_json()
    year_name = data.get('year_name')
    
    if not year_name:
        return jsonify({'message': '学年名称不能为空'}), 400
    
    # 检查学年是否已存在
    existing_year = AcademicYear.query.filter_by(year_name=year_name).first()
    if existing_year:
        return jsonify({'message': '该学年已存在'}), 400
    
    # 创建新学年
    new_year = AcademicYear(year_name=year_name)
    db.session.add(new_year)
    db.session.commit()
    
    return jsonify({'message': '学年添加成功', 'id': new_year.id})

@app.route('/api/admin/academic-years/<int:year_id>/set-current', methods=['POST'])
def api_admin_set_current_year(year_id):
    """管理员设置当前学年"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    # 先取消所有学年的当前状态
    AcademicYear.query.update({'is_current': False})
    
    # 设置指定学年为当前学年
    year = AcademicYear.query.get(year_id)
    if not year:
        return jsonify({'message': '学年不存在'}), 404
    
    year.is_current = True
    db.session.commit()
    
    return jsonify({'message': '当前学年设置成功'})

@app.route('/api/admin/academic-years/<int:year_id>', methods=['DELETE'])
def api_admin_delete_academic_year(year_id):
    """管理员删除学年"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    year = AcademicYear.query.get(year_id)
    if not year:
        return jsonify({'message': '学年不存在'}), 404
    
    # 检查是否有申请或记录使用该学年
    has_applications = ScoreApplication.query.filter_by(academic_year=year.year_name).first()
    has_records = ScoreRecord.query.filter_by(academic_year=year.year_name).first()
    
    if has_applications or has_records:
        return jsonify({'message': '该学年已有相关数据，无法删除'}), 400
    
    db.session.delete(year)
    db.session.commit()
    
    return jsonify({'message': '学年删除成功'})

@app.route('/api/statistics/filters', methods=['GET'])
def api_get_statistics_filters():
    """获取统计筛选选项"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    # 获取所有书院
    colleges = db.session.query(User.college).filter(
        User.role == 'student',
        User.college.isnot(None),
        User.college != ''
    ).distinct().all()
    
    # 获取所有年级
    grades = db.session.query(User.grade).filter(
        User.role == 'student',
        User.grade.isnot(None),
        User.grade != ''
    ).distinct().all()
    
    # 获取所有班级
    classes = db.session.query(User.class_name).filter(
        User.role == 'student',
        User.class_name.isnot(None),
        User.class_name != ''
    ).distinct().all()
    
    # 从学年管理表获取所有学年
    academic_years = AcademicYear.query.order_by(AcademicYear.year_name.desc()).all()
    academic_year_list = [year.year_name for year in academic_years]
    
    # 获取当前学年
    current_year = AcademicYear.query.filter_by(is_current=True).first()
    default_academic_year = current_year.year_name if current_year else None
    
    return jsonify({
        'colleges': [c[0] for c in colleges],
        'grades': [g[0] for g in grades],
        'classes': [c[0] for c in classes],
        'academicYears': academic_year_list,
        'defaultAcademicYear': default_academic_year
    })

@app.route('/api/scores/export', methods=['GET'])
def api_export_all_scores():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403

    academic_year = request.args.get('academic_year')
    college = request.args.get('college')
    grade = request.args.get('grade')
    class_name = request.args.get('class_name')

    # 使用与排行榜相同的逻辑，应用项目类别上限
    base = db.session.query(
        User.id,
        User.name,
        User.student_id,
        User.class_name,
        User.college,
        User.grade,
        ScoreRecord.score,
        ScoreRecord.academic_year,
        ScoreCategory.name.label('category_name'),
        ScoreCategory.parent_id
    ).outerjoin(ScoreRecord, User.id == ScoreRecord.user_id).outerjoin(
        ScoreCategory, ScoreRecord.category_id == ScoreCategory.id
    ).filter(
        User.role == 'student'
    )

    if academic_year:
        base = base.filter(ScoreRecord.academic_year == academic_year)
    
    if college:
        base = base.filter(User.college == college)
    
    if grade:
        base = base.filter(User.grade == grade)
    
    if class_name:
        base = base.filter(User.class_name == class_name)

    records = base.all()
    
    # 按学生分组，应用项目类别上限计算总分
    student_scores = {}
    
    for record in records:
        user_id = record.id
        if user_id not in student_scores:
            student_scores[user_id] = {
                'name': record.name,
                'student_id': record.student_id,
                'class_name': record.class_name,
                'college': record.college or '',
                'grade': record.grade or '',
                'category_scores': {},
                'total_score': 0,
                'record_count': 0
            }
        
        if record.score is not None:
            student_scores[user_id]['record_count'] += 1
            
            # 获取主类别
            if record.parent_id:
                parent_category = ScoreCategory.query.get(record.parent_id)
                main_category_name = parent_category.name
            else:
                main_category_name = record.category_name
            
            if main_category_name not in student_scores[user_id]['category_scores']:
                student_scores[user_id]['category_scores'][main_category_name] = []
            
            # 存储包含子类别信息的记录
            student_scores[user_id]['category_scores'][main_category_name].append({
                'score': record.score,
                'category_name': record.category_name
            })
    
    # 使用定义的所有类别常量
    all_categories = ALL_MAIN_CATEGORIES
    
    # 应用项目类别上限计算最终分数
    data = []
    for user_id, data_item in student_scores.items():
        category_scores = {}
        total_score = 0
        
        for main_category, records in data_item['category_scores'].items():
            # 使用新函数计算最终分数（应用子类别限制，如工时最多1分）
            final_score = calculate_category_score_with_subcategory(main_category, records)
            category_scores[main_category] = final_score
            total_score += final_score
        
        # 设置总分最大值(100)和最小值(0)
        total_score = max(0, min(100, total_score))
        
        # 为每个类别设置默认值0（如果没有记录）
        for category in all_categories:
            if category not in category_scores:
                category_scores[category] = 0
        
        data.append({
            '排名': 0,  # 稍后计算
            '姓名': data_item['name'],
            '学号': data_item['student_id'],
            '班级': data_item['class_name'],
            '书院': data_item['college'],
            '年级': data_item['grade'],
            '基准分': 70,
            '思想政治理论分': category_scores.get('思想政治理论分', 0),
            '社会服务分': category_scores.get('社会服务分', 0),
            '集体活动分': category_scores.get('集体活动分', 0),
            '学术科研分': category_scores.get('学术科研分', 0),
            '文体竞赛分': category_scores.get('文体竞赛分', 0),
            '奖励分': category_scores.get('奖励分', 0),
            '任职分': category_scores.get('任职分', 0),
            '扣分': category_scores.get('扣分', 0),
            '总分': total_score
        })
    
    # 按总分排序并计算排名
    data.sort(key=lambda x: x['总分'], reverse=True)
    for i, item in enumerate(data):
        item['排名'] = i + 1
    
    df = pd.DataFrame(data)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='集体德育分汇总')
    buf.seek(0)
    filename = '集体德育分汇总.xlsx' if not academic_year else f'集体德育分汇总_{academic_year}.xlsx'
    return send_file(buf, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/api/announcements', methods=['GET'])
def api_get_announcements():
    announcements = db.session.query(Announcement, User).join(
        User, Announcement.author_id == User.id
    ).order_by(Announcement.created_at.desc()).all()
    
    result = []
    for announcement, author in announcements:
        result.append({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'created_at': announcement.created_at.isoformat(),
            'author_name': author.name
        })
    
    return jsonify(result)

@app.route('/api/announcements', methods=['POST'])
def api_create_announcement():
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': '请求数据为空'}), 400
        
        if not data.get('title') or not data.get('content'):
            return jsonify({'message': '标题和内容不能为空'}), 400
        
        announcement = Announcement(
            title=data['title'],
            content=data['content'],
            author_id=session['user']['id']
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({'message': '公告发布成功', 'id': announcement.id})
    
    except Exception as e:
        db.session.rollback()
        print(f"创建公告错误: {e}")
        return jsonify({'message': f'创建公告失败: {str(e)}'}), 500

@app.route('/api/announcements/<int:announcement_id>', methods=['PUT'])
def api_update_announcement(announcement_id):
    try:
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({'message': '需要管理员权限'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': '请求数据为空'}), 400
        
        if not data.get('title') or not data.get('content'):
            return jsonify({'message': '标题和内容不能为空'}), 400
        
        announcement = Announcement.query.get_or_404(announcement_id)
        announcement.title = data['title']
        announcement.content = data['content']
        
        db.session.commit()
        return jsonify({'message': '公告更新成功'})
    
    except Exception as e:
        db.session.rollback()
        print(f"更新公告错误: {e}")
        return jsonify({'message': f'更新公告失败: {str(e)}'}), 500

@app.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
def api_delete_announcement(announcement_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'message': '需要管理员权限'}), 403
    
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    
    return jsonify({'message': '公告删除成功'})

@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    """修改密码"""
    if 'user' not in session:
        return jsonify({'message': '未登录'}), 401
    
    data = request.get_json()
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not current_password or not new_password:
        return jsonify({'message': '密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': '新密码长度至少6位'}), 400
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    # 验证当前密码
    if not user.check_password(current_password):
        return jsonify({'message': '当前密码错误'}), 400
    
    # 设置新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})

@app.route('/change-password')
def change_password():
    """修改密码页面"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('change_password.html')

# 初始化数据库
def init_db():
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("✅ SQLite数据库初始化完成")
        except Exception as e:
            print(f"❌ 数据库初始化错误: {e}")
            raise

# 根据用户角色重定向到对应页面
def redirect_by_role(user_role):
    """统一的角色重定向逻辑"""
    if user_role == 'admin':
        return redirect(url_for('application_review'))
    elif user_role == 'teacher':
        return redirect(url_for('teacher_scores'))
    else:
        return redirect(url_for('my_scores'))

# 模板路由
@app.route('/')
def index():
    # 检查是否有静态的index.html文件
    if os.path.exists('index.html'):
        return send_file('index.html')
    
    # 统一重定向到登录页面，让login处理已登录用户
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果已登录，直接重定向到对应角色页面
    if 'user' in session:
        return redirect_by_role(session['user']['role'])
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 支持通过用户名/学号/工号登录，兼容前导零
        candidates = []
        if username:
            candidates.append(username)
            stripped = username.lstrip('0')
            if stripped and stripped != username:
                candidates.append(stripped)
        user = None
        for u in candidates:
            user = User.query.filter((User.username==u) | (User.student_id==u) | (User.employee_id==u)).first()
            if user:
                break
        
        # 尝试密码与去零密码
        def password_matches(u: User) -> bool:
            if u.check_password(password):
                return True
            alt = password.lstrip('0') if password else password
            if alt and alt != password and u.check_password(alt):
                return True
            return False

        if user and password_matches(user):
            session['user'] = user.to_dict()
            flash('登录成功！', 'success')
            return redirect_by_role(user.role)
        else:
            flash('学号/工号或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/application')
def application_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'student':
        flash('仅学生可发起个人申请', 'error')
        return redirect(url_for('login'))
    return render_template('application_form.html')

@app.route('/application/category/<int:category_id>')
def category_application_form(category_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'student':
        flash('仅学生可发起个人申请', 'error')
        return redirect(url_for('login'))
    
    # 获取类别信息
    category = ScoreCategory.query.get_or_404(category_id)
    
    # 获取父类别信息
    parent_category = None
    if category.parent_id:
        parent_category = ScoreCategory.query.get(category.parent_id)
    
    # 创建包含父类别信息的类别对象
    category_with_parent = {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'max_score': category.max_score,
        'parent_id': category.parent_id,
        'parent_name': parent_category.name if parent_category else None
    }
    
    return render_template('category_application_form.html', category=category_with_parent)

@app.route('/my-applications')
def my_applications():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'student':
        flash('仅学生可查看个人申请', 'error')
        return redirect(url_for('index'))
    return render_template('my_applications.html')

@app.route('/my-applications/category/<int:category_id>')
def category_my_applications(category_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'student':
        flash('仅学生可查看个人申请', 'error')
        return redirect(url_for('index'))
    
    # 获取类别信息
    category = ScoreCategory.query.get_or_404(category_id)
    return render_template('category_my_applications.html', category=category)

@app.route('/my-scores')
def my_scores():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['user']['role'] != 'student':
        flash('仅学生可查看个人德育分', 'error')
        return redirect(url_for('index'))
    return render_template('my_scores.html')

@app.route('/announcements')
def announcements():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('announcements.html')

@app.route('/teacher/scores')
def teacher_scores():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher_scores.html')

@app.route('/teacher/group-application')
def teacher_group_application():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('group_application.html')

@app.route('/teacher/group-applications')
def teacher_group_applications():
    if 'user' not in session or session['user']['role'] != 'teacher':
        return redirect(url_for('login'))
    return render_template('my_group_applications.html')

@app.route('/admin/review')
def application_review():
    """统一的审核页面（个人申请和集体申请）"""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('需要管理员权限', 'error')
        return redirect(url_for('login'))
    return render_template('unified_review.html')

@app.route('/admin/statistics')
def statistics():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('需要管理员权限', 'error')
        return redirect(url_for('login'))
    return render_template('statistics.html')

@app.route('/admin/system')
def system_manage():
    """统一的系统管理页面（公告管理和学年管理）"""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('需要管理员权限', 'error')
        return redirect(url_for('login'))
    return render_template('system_manage.html')

@app.route('/api/categories/<int:category_id>', methods=['GET'])
def api_get_category_info(category_id):
    """获取特定类别的详细信息（包含最高分限制）"""
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    category = ScoreCategory.query.get_or_404(category_id)
    
    # 获取父类别信息
    parent_category = None
    if category.parent_id:
        parent_category = ScoreCategory.query.get(category.parent_id)
    
    result = {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'max_score': category.max_score,
        'parent_id': category.parent_id,
        'parent_name': parent_category.name if parent_category else None,
        'parent_max_score': parent_category.max_score if parent_category else None
    }
    
    return jsonify(result)

@app.route('/api/scores/calculate', methods=['GET'])
def api_calculate_scores():
    """计算学生德育分统计（包含特殊规则）"""
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user_id = session['user']['id']
    academic_year = request.args.get('academic_year')
    
    if not academic_year:
        return jsonify({'error': '请指定学年'}), 400
    
    # 获取学生的所有德育分记录
    query = db.session.query(ScoreRecord, ScoreCategory).join(
        ScoreCategory, ScoreRecord.category_id == ScoreCategory.id
    ).filter(ScoreRecord.user_id == user_id, ScoreRecord.academic_year == academic_year)
    
    records = query.all()
    
    # 按主类别分组统计
    category_scores = {}
    total_score = 0
    
    for record, category in records:
        # 获取主类别
        if category.parent_id:
            parent_category = ScoreCategory.query.get(category.parent_id)
            main_category_name = parent_category.name
        else:
            main_category_name = category.name
        
        if main_category_name not in category_scores:
            category_scores[main_category_name] = []
        
        category_scores[main_category_name].append({
            'score': record.score,
            'category_name': category.name,
            'description': record.description
        })
    
    # 应用特殊规则计算最终分数
    final_scores = {}
    
    for main_category, records in category_scores.items():
        # 使用新函数计算最终分数（应用子类别限制，如工时最多1分）
        final_scores[main_category] = calculate_category_score_with_subcategory(main_category, records)
    
    # 计算总分（扣分特殊处理）
    positive_score = sum([score for category, score in final_scores.items() if category != '扣分'])
    negative_score = final_scores.get('扣分', 0)
    
    # 德育分总分（前面所有满分35分）
    moral_score = max(0, positive_score - negative_score)  # 总分不能低于0
    moral_score = min(moral_score, 35)  # 德育分最高35分
    
    # 最终统计时最高不超过100分（这里假设还有其他70分）
    final_total = min(moral_score + 70, 100)  # 德育分35分 + 其他70分，最高100分
    
    return jsonify({
        'academic_year': academic_year,
        'category_scores': final_scores,
        'moral_score': moral_score,
        'final_total': final_total,
        'details': category_scores
    })

if __name__ == '__main__':
    init_db()
    print("德育分管理系统启动中...")
    print("前端地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
