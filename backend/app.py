# backend/app.py
from flask import Flask

# 创建 Flask 应用实例
# __name__ 是当前模块名，Flask 需要它来确定应用的根路径
app = Flask(__name__)

# 定义路由和视图函数
# @app.route('/') 是装饰器，告诉 Flask 当用户访问根路径（/）时，调用下面的函数
@app.route('/')
def hello_world():
    # 这个函数返回的内容就是用户在浏览器看到的内容
    return 'Hello, Flask World! 后端服务启动成功！'

# 添加一个测试 API，后续前端会调用它
@app.route('/api/health')
def health_check():
    # 返回 JSON 格式的数据
    from flask import jsonify
    return jsonify({"status": "ok", "message": "后端服务运行正常"})

# 启动应用
# 这个判断确保只有直接运行此文件时才启动服务器，如果是被其他文件导入则不会启动
if __name__ == '__main__':
    # debug=True 开启调试模式：代码修改后自动重启，出错时显示详细错误页面
    app.run(debug=True, host='127.0.0.1', port=5000)