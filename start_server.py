#!/usr/bin/env python3
"""
简单的HTTP服务器启动脚本
用于解决浏览器文件协议限制问题
"""

import sys
import os
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def main():
    # 默认端口
    port = 8000
    
    # 如果指定了端口参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("端口必须是数字")
            sys.exit(1)
    
    # 切换到项目根目录
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    # 创建服务器
    try:
        httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
        print(f"启动HTTP服务器：http://localhost:{port}")
        print(f"预览页面：http://localhost:{port}/tools/preview/preview.html")
        print("\n按 Ctrl+C 停止服务器")
        
        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{port}/tools/preview/preview.html")
        
        # 启动服务器
        httpd.serve_forever()
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"端口 {port} 已被占用，请尝试其他端口")
            print(f"用法：python start_server.py [端口号]")
        else:
            print(f"启动服务器失败：{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == "__main__":
    main()