"""
简单的 Flask Web 应用示例
用于演示 Docker 和 Kubernetes 部署
"""
from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

# 获取主机名（在容器中会显示容器ID）
hostname = socket.gethostname()

@app.route('/')
def hello():
    """主页"""
    return jsonify({
        'message': 'Hello from Gordon!',
        'hostname': hostname,
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'hostname': hostname
    })

@app.route('/info')
def info():
    """获取环境信息"""
    return jsonify({
        'hostname': hostname,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'python_version': os.sys.version.split()[0]
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

