import socket
import time

# 配置日志采集器的地址和端口（与log_collector.py中一致）
HOST = '127.0.0.1'
PORT = 1514   # 如果之前修改过端口，请同步修改

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 要发送的日志内容（可以变化源IP以模拟不同来源，这里固定一个源IP）
base_message = "Mar 18 10:30:01 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2"

print(f"开始发送测试日志到 {HOST}:{PORT}...")

for i in range(4):
    print(f"发送第 {i+1} 条日志...")
    sock.sendto(base_message.encode(), (HOST, PORT))
    time.sleep(1)   # 每条间隔1秒，确保在60秒窗口内

print("发送完成。")
sock.close()