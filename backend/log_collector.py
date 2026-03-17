# log_collector.py
import socket
import threading
import re
import time
from datetime import datetime
from collections import defaultdict, deque
import sys
import os

# 将项目路径添加到系统路径，以便能导入 app 和模型
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import LogSource, Rule, Alert  # 直接从 app 导入模型类

class SyslogServer:
    """Syslog 服务器，监听 UDP 端口接收日志"""
    
    def __init__(self, host='0.0.0.0', port=1514):
        """
        初始化服务器
        :param host: 监听地址，0.0.0.0 表示所有接口
        :param port: 监听端口，Windows 上 514 可能需要管理员权限，默认用 1514
        """
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.rule_engine = RuleEngine()  # 创建规则引擎实例
        
    def start(self):
        """启动 UDP 服务器"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"[*] Syslog server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(65535)  # 接收数据，最大 64KB
                    message = data.decode('utf-8', errors='ignore')  # 忽略无法解码的字符
                    print(f"[+] Received log from {addr[0]}: {message[:100]}...")  # 打印前100字符
                    
                    # 构建日志条目
                    log_entry = {
                        'raw': message,
                        'src_ip': addr[0],
                        'timestamp': datetime.utcnow()
                    }
                    
                    # 交给规则引擎处理
                    self.rule_engine.process_log(log_entry)
                    
                except socket.error as e:
                    if self.running:
                        print(f"[-] Socket error: {e}")
                        
        except Exception as e:
            print(f"[-] Failed to start server: {e}")
        finally:
            if self.sock:
                self.sock.close()
                
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.sock:
            self.sock.close()
        print("[*] Syslog server stopped")

class RuleEngine:
    """规则引擎，加载规则并对日志进行匹配"""
    
    def __init__(self):
        self.rules = []  # 存储规则对象
        # 阈值计数器：key = (rule_id, src_ip), value = deque of timestamps
        self.threshold_counters = defaultdict(lambda: deque(maxlen=1000))
        self.load_rules()  # 启动时加载规则
        # 启动定时重载规则线程（可选，每60秒）
        self.start_reloader()
        
    def load_rules(self):
        """从数据库加载所有启用的规则"""
        with app.app_context():
            self.rules = Rule.query.filter_by(enabled=True).all()
            print(f"[*] Loaded {len(self.rules)} enabled rules")
            
    def reload_rules(self):
        """重新加载规则（可定时调用或通过 API 触发）"""
        self.load_rules()
        
    def start_reloader(self, interval=60):
        """启动后台线程定时重载规则"""
        def reloader():
            while True:
                time.sleep(interval)
                self.reload_rules()
        thread = threading.Thread(target=reloader, daemon=True)
        thread.start()
        
    def process_log(self, log_entry):
        """处理单条日志，依次匹配所有规则"""
        with app.app_context():
            for rule in self.rules:
                if rule.rule_type == 'regex':
                    self._process_regex_rule(rule, log_entry)
                elif rule.rule_type == 'threshold':
                    self._process_threshold_rule(rule, log_entry)
                    
    def _process_regex_rule(self, rule, log_entry):
        """处理正则类型规则"""
        try:
            if re.search(rule.pattern, log_entry['raw'], re.IGNORECASE):
                self._create_alert(rule, log_entry)
        except re.error as e:
            print(f"[-] Regex error in rule {rule.name}: {e}")
            
    def _process_threshold_rule(self, rule, log_entry):
        """处理阈值类型规则（例如：5分钟内失败登录超过10次）"""
        # 首先匹配正则
        if re.search(rule.pattern, log_entry['raw'], re.IGNORECASE):
            key = (rule.id, log_entry.get('src_ip', 'unknown'))
            now = time.time()
            self.threshold_counters[key].append(now)
            
            # 清理超出时间窗口的记录
            while (self.threshold_counters[key] and 
                   self.threshold_counters[key][0] < now - rule.threshold_seconds):
                self.threshold_counters[key].popleft()
                
            # 判断是否达到阈值
            if len(self.threshold_counters[key]) >= rule.threshold_count:
                self._create_alert(rule, log_entry)
                # 清空计数器，避免重复告警（可根据需求调整）
                self.threshold_counters[key].clear()
                
    def _create_alert(self, rule, log_entry):
        """创建告警记录并存入数据库"""
        alert = Alert(
            rule_id=rule.id,
            src_ip=log_entry.get('src_ip'),
            message=f"Rule '{rule.name}' matched",
            raw_log=log_entry['raw'][:500],  # 只存前500字符
            severity=rule.severity,
            status='new'
        )
        db.session.add(alert)
        db.session.commit()
        print(f"[ALERT] {rule.severity.upper()}: {rule.name} from {log_entry.get('src_ip')}")

# 如果直接运行此文件，启动服务器
if __name__ == '__main__':
    server = SyslogServer(host='0.0.0.0', port=1514)  # 使用1514端口避免权限问题
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
        server.stop()