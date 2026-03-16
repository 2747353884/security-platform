# celery_app.py
from celery import Celery
import nmap
from datetime import datetime
import sys
import os

# 添加项目路径到 sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def make_celery(app_name=__name__):
    return Celery(app_name, backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')

celery = make_celery()

# 导入 Flask 应用和数据库（延迟导入，避免循环）
def get_app_and_db():
    from app import app, db
    return app, db

@celery.task(bind=True)
def scan_network_task(self, target_range):
    self.update_state(state='STARTED', meta={'current': 0, 'total': 100, 'status': '正在初始化扫描...'})
    
    nm = nmap.PortScanner()
    self.update_state(state='PROGRESS', meta={'current': 10, 'total': 100, 'status': '正在发现存活主机...'})
    nm.scan(hosts=target_range, arguments='-sn')
    hosts_up = [host for host in nm.all_hosts() if nm[host].state() == 'up']
    
    app, db = get_app_and_db()
    
    with app.app_context():
        # 上下文内导入模型，防止循环引用
        from app import Asset, Port, Vulnerability
        
        # 清空旧的资产数据
        Asset.query.delete()
        db.session.commit()
        
        total = len(hosts_up)
        for idx, host in enumerate(hosts_up):
            progress = 10 + int((idx / total) * 80)
            self.update_state(state='PROGRESS', meta={'current': progress, 'total': 100, 'status': f'正在扫描 {host}...'})
            
            nm.scan(hosts=host, arguments='-sV -O --script vuln')
            
            # 创建资产对象
            asset = Asset(
                ip=host,
                hostname=nm[host].hostname(),
                os=nm[host].get('osmatch', [{}])[0].get('name', 'Unknown') if nm[host].get('osmatch') else 'Unknown',
                status=nm[host].state(),
                last_scan=datetime.utcnow()
            )
            db.session.add(asset)
            db.session.flush()  # 获取 asset.id
            
            # 处理端口
            for proto in nm[host].all_protocols():
                for port in nm[host][proto]:
                    service = nm[host][proto][port]
                    port_obj = Port(
                        asset_id=asset.id,
                        port=port,
                        protocol=proto,
                        service=service.get('name', 'unknown'),
                        version=service.get('version', 'unknown'),
                        state=service.get('state', 'unknown')
                    )
                    db.session.add(port_obj)
                    db.session.flush()
                    
                    # 处理漏洞
                    if 'script' in service:
                        for script_name, output in service['script'].items():
                            if 'vuln' in script_name.lower() or 'cve' in output.lower():
                                vuln = Vulnerability(
                                    port_id=port_obj.id,
                                    cve_id='Unknown',
                                    description=output[:500],
                                    severity='unknown'
                                )
                                db.session.add(vuln)
            
            db.session.commit()
        
        self.update_state(state='SUCCESS', meta={'current': 100, 'total': 100, 'status': '扫描完成'})
        return {'message': '扫描完成', 'assets_count': len(hosts_up)}