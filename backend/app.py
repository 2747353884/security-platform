# backend/app.py
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from celery_app import celery, scan_network_task

# 创建 Flask 应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'  # 用于 session 加密，生产环境请使用强密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sec_user:sec_password@localhost/security_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 指定未登录时重定向的端点
CORS(app, supports_credentials=True)  # 允许跨域，虽然我们配置了代理，但保留无害

# 导入模型
# 用户角色关联表（多对多）
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} at {self.timestamp}>'

class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), nullable=False)          # IPv4或IPv6
    hostname = db.Column(db.String(255))
    os = db.Column(db.String(100))
    status = db.Column(db.String(20), default='unknown')   # up/down/unknown
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_scan = db.Column(db.DateTime)
    risk_score = db.Column(db.Float, default=0.0)           # 风险评分（0-10）
    
    # 关系：一个资产有多个端口
    ports = db.relationship('Port', backref='asset', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Asset {self.ip}>'

class Port(db.Model):
    __tablename__ = 'port'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    protocol = db.Column(db.String(10))          # tcp/udp
    service = db.Column(db.String(100))
    version = db.Column(db.String(100))
    state = db.Column(db.String(20))              # open/closed/filtered
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系：一个端口有多个漏洞
    vulnerabilities = db.relationship('Vulnerability', backref='port', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('asset_id', 'port', 'protocol', name='unique_port'),)
    
    def __repr__(self):
        return f'<Port {self.port}/{self.protocol} on asset {self.asset_id}>'

class Vulnerability(db.Model):
    __tablename__ = 'vulnerability'
    id = db.Column(db.Integer, primary_key=True)
    port_id = db.Column(db.Integer, db.ForeignKey('port.id'), nullable=False)
    cve_id = db.Column(db.String(20))             # CVE编号，如 CVE-2021-44228
    description = db.Column(db.Text)
    cvss_score = db.Column(db.Float)               # 通用漏洞评分系统分数
    severity = db.Column(db.String(20))             # 高危/中危/低危
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vulnerability {self.cve_id}>'


# 用户加载回调，用于 Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 根路由，仅用于测试
@app.route('/')
def hello():
    return 'Hello, Flask!'

# 测试 API
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "后端服务运行正常"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # 验证输入
    if not username or not email or not password:
        return jsonify({'code': 400, 'msg': '缺少必要字段'}), 400
    
    # 检查用户名或邮箱是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'msg': '邮箱已被注册'}), 400
    
    # 创建新用户
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    
    # 默认分配 viewer 角色
    viewer_role = Role.query.filter_by(name='viewer').first()
    if viewer_role:
        user.roles.append(viewer_role)
    
    db.session.commit()
    
    # 记录审计日志
    log = AuditLog(user_id=user.id, action='用户注册', ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'))
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'code': 200, 'msg': '注册成功', 'data': {'id': user.id, 'username': user.username, 'email': user.email}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if not user.is_active:
            return jsonify({'code': 403, 'msg': '账户已被禁用'}), 403
        
        # 登录用户
        login_user(user, remember=data.get('remember', False))
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 记录审计日志
        log = AuditLog(user_id=user.id, action='用户登录', ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'))
        db.session.add(log)
        db.session.commit()
        
        # 返回用户信息（注意不要返回密码）
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        }
        return jsonify({'code': 200, 'msg': '登录成功', 'data': user_data})
    else:
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    # 记录审计日志（注意：注销后 current_user 已不可用，需要提前获取 user_id）
    log = AuditLog(user_id=user_id, action='用户注销', ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent'))
    db.session.add(log)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '注销成功'})

@app.route('/api/user/info', methods=['GET'])
@login_required
def user_info():
    user = current_user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': [role.name for role in user.roles]
    }
    return jsonify({'code': 200, 'data': user_data})

from functools import wraps

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'code': 401, 'msg': '请先登录'}), 401
            user_roles = [role.name for role in current_user.roles]
            if not any(role in user_roles for role in roles):
                return jsonify({'code': 403, 'msg': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    return jsonify({'msg': '欢迎管理员'})

@app.route('/api/scan/start', methods=['POST'])
@login_required
@role_required('admin')
def start_scan():
    data = request.get_json()
    target = data.get('target')
    if not target:
        return jsonify({'code': 400, 'msg': '目标IP段不能为空'}), 400
    
    # 异步执行扫描任务
    task = scan_network_task.apply_async(args=[target])
    
    return jsonify({'code': 200, 'msg': '扫描任务已启动', 'data': {'task_id': task.id}})

@app.route('/api/scan/status/<task_id>', methods=['GET'])
@login_required
def scan_status(task_id):
    task = scan_network_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'current': 0, 'total': 100, 'status': '任务等待中'}
    elif task.state == 'STARTED' or task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 100),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': 100,
            'total': 100,
            'status': '扫描完成',
            'result': task.result
        }
    else:
        response = {'state': task.state, 'status': str(task.info)}
    return jsonify({'code': 200, 'data': response})

@app.route('/api/assets', methods=['GET'])
@login_required
def get_assets():
    assets = Asset.query.all()
    result = []
    for asset in assets:
        result.append({
            'id': asset.id,
            'ip': asset.ip,
            'hostname': asset.hostname,
            'os': asset.os,
            'status': asset.status,
            'risk_score': asset.risk_score,
            'discovered_at': asset.discovered_at,
            'last_scan': asset.last_scan,
            'ports_count': asset.ports.count()
        })
    return jsonify({'code': 200, 'data': result})

@app.route('/api/assets/<int:asset_id>', methods=['GET'])
@login_required
def get_asset_detail(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    ports = []
    for port in asset.ports:
        vulns = []
        for vuln in port.vulnerabilities:
            vulns.append({
                'id': vuln.id,
                'cve_id': vuln.cve_id,
                'description': vuln.description,
                'cvss_score': vuln.cvss_score,
                'severity': vuln.severity
            })
        ports.append({
            'id': port.id,
            'port': port.port,
            'protocol': port.protocol,
            'service': port.service,
            'version': port.version,
            'state': port.state,
            'vulnerabilities': vulns
        })
    result = {
        'id': asset.id,
        'ip': asset.ip,
        'hostname': asset.hostname,
        'os': asset.os,
        'status': asset.status,
        'risk_score': asset.risk_score,
        'discovered_at': asset.discovered_at,
        'last_scan': asset.last_scan,
        'ports': ports
    }
    return jsonify({'code': 200, 'data': result})

@app.route('/api/vulnerabilities', methods=['GET'])
@login_required
def get_vulnerabilities():
    vulns = Vulnerability.query.all()
    result = []
    for vuln in vulns:
        result.append({
            'id': vuln.id,
            'cve_id': vuln.cve_id,
            'description': vuln.description[:100] + '...' if vuln.description and len(vuln.description) > 100 else vuln.description,
            'cvss_score': vuln.cvss_score,
            'severity': vuln.severity,
            'asset_ip': vuln.port.asset.ip,
            'port': vuln.port.port,
            'protocol': vuln.port.protocol
        })
    return jsonify({'code': 200, 'data': result})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)