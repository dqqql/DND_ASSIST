#!/usr/bin/env python3
"""
DND 跑团管理器 - Web UI 功能测试
验证Web UI版本的核心功能是否正常工作
"""

import sys
import time
import requests
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.web_preview.server import WebPreviewServer


class WebUITester:
    def __init__(self):
        self.server = None
        self.base_url = None
        self.test_results = []
    
    def start_test_server(self):
        """启动测试服务器"""
        print("🚀 启动测试服务器...")
        
        self.server = WebPreviewServer(project_root)
        success = self.server.start(auto_monitor=False)
        
        if success:
            self.base_url = f"http://localhost:{self.server.get_port()}"
            print(f"   ✅ 服务器启动成功: {self.base_url}")
            time.sleep(1)  # 等待服务器完全启动
            return True
        else:
            print("   ❌ 服务器启动失败")
            return False
    
    def stop_test_server(self):
        """停止测试服务器"""
        if self.server:
            self.server.stop()
            print("   ⏹️  测试服务器已停止")
    
    def test_api_endpoint(self, endpoint, method='GET', data=None, expected_status=200):
        """测试API端点"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=5)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            success = response.status_code == expected_status
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': success,
                'response_size': len(response.content)
            }
            
            if success:
                print(f"   ✅ {method} {endpoint} - {response.status_code}")
            else:
                print(f"   ❌ {method} {endpoint} - {response.status_code} (期望: {expected_status})")
            
            self.test_results.append(result)
            return success, response
            
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - 异常: {e}")
            result = {
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            return False, None
    
    def test_static_files(self):
        """测试静态文件访问"""
        print("📄 测试静态文件访问...")
        
        static_files = [
            '/tools/web_ui/index.html',
            '/tools/web_ui/index.css',
            '/tools/web_ui/index.js',
            '/tools/editor/editor.html',
            '/tools/characters/characters.html'
        ]
        
        success_count = 0
        for file_path in static_files:
            success, _ = self.test_api_endpoint(file_path, expected_status=200)
            if success:
                success_count += 1
        
        print(f"   📊 静态文件测试: {success_count}/{len(static_files)} 通过")
        return success_count == len(static_files)
    
    def test_api_endpoints(self):
        """测试API端点"""
        print("🔌 测试API端点...")
        
        # 测试基础API
        api_tests = [
            ('/api/campaigns', 'GET', None, 200),
            ('/api/campaigns', 'POST', {'name': 'test_campaign'}, 200),
            ('/api/campaigns', 'DELETE', {'name': 'test_campaign'}, 200),
        ]
        
        success_count = 0
        for endpoint, method, data, expected_status in api_tests:
            success, _ = self.test_api_endpoint(endpoint, method, data, expected_status)
            if success:
                success_count += 1
        
        print(f"   📊 API端点测试: {success_count}/{len(api_tests)} 通过")
        return success_count == len(api_tests)
    
    def test_campaign_workflow(self):
        """测试跑团工作流程"""
        print("🎲 测试跑团工作流程...")
        
        workflow_success = True
        
        # 1. 创建测试跑团
        print("   1️⃣ 创建测试跑团...")
        success, response = self.test_api_endpoint(
            '/api/campaigns', 'POST', 
            {'name': 'workflow_test'}, 200
        )
        if not success:
            workflow_success = False
        
        # 2. 获取跑团列表
        print("   2️⃣ 获取跑团列表...")
        success, response = self.test_api_endpoint('/api/campaigns', 'GET')
        if success and response:
            try:
                data = response.json()
                campaigns = data.get('campaigns', [])
                if 'workflow_test' not in campaigns:
                    print("   ❌ 创建的跑团未出现在列表中")
                    workflow_success = False
                else:
                    print("   ✅ 跑团列表包含创建的跑团")
            except Exception as e:
                print(f"   ❌ 解析跑团列表失败: {e}")
                workflow_success = False
        else:
            workflow_success = False
        
        # 3. 测试文件管理API（如果跑团存在）
        if workflow_success:
            print("   3️⃣ 测试文件管理...")
            file_apis = [
                f'/api/characters?campaign=workflow_test',
                f'/api/monsters?campaign=workflow_test',
                f'/api/maps?campaign=workflow_test'
            ]
            
            for api in file_apis:
                success, _ = self.test_api_endpoint(api, 'GET')
                if not success:
                    workflow_success = False
        
        # 4. 清理测试跑团
        print("   4️⃣ 清理测试跑团...")
        success, _ = self.test_api_endpoint(
            '/api/campaigns', 'DELETE', 
            {'name': 'workflow_test'}, 200
        )
        if not success:
            print("   ⚠️  清理测试跑团失败，可能需要手动删除")
        
        if workflow_success:
            print("   ✅ 跑团工作流程测试通过")
        else:
            print("   ❌ 跑团工作流程测试失败")
        
        return workflow_success
    
    def test_error_handling(self):
        """测试错误处理"""
        print("🚨 测试错误处理...")
        
        error_tests = [
            ('/api/nonexistent', 'GET', None, 404),
            ('/api/campaigns', 'POST', {}, 400),  # 缺少参数
            ('/api/campaigns', 'DELETE', {}, 400),  # 缺少参数
        ]
        
        success_count = 0
        for endpoint, method, data, expected_status in error_tests:
            success, _ = self.test_api_endpoint(endpoint, method, data, expected_status)
            if success:
                success_count += 1
        
        print(f"   📊 错误处理测试: {success_count}/{len(error_tests)} 通过")
        return success_count == len(error_tests)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始Web UI功能测试")
        print("="*60)
        
        # 启动服务器
        if not self.start_test_server():
            print("❌ 无法启动测试服务器，测试终止")
            return False
        
        try:
            # 运行各项测试
            test_results = []
            
            test_results.append(self.test_static_files())
            test_results.append(self.test_api_endpoints())
            test_results.append(self.test_campaign_workflow())
            test_results.append(self.test_error_handling())
            
            # 统计结果
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            print("\n" + "="*60)
            print("📊 测试结果汇总")
            print("="*60)
            
            test_names = [
                "静态文件访问",
                "API端点功能", 
                "跑团工作流程",
                "错误处理机制"
            ]
            
            for i, (name, result) in enumerate(zip(test_names, test_results)):
                status = "✅ 通过" if result else "❌ 失败"
                print(f"   {i+1}. {name}: {status}")
            
            print(f"\n总体结果: {passed_tests}/{total_tests} 项测试通过")
            
            if passed_tests == total_tests:
                print("🎉 所有测试通过！Web UI功能正常")
                return True
            else:
                print("⚠️  部分测试失败，请检查相关功能")
                return False
                
        finally:
            self.stop_test_server()
    
    def generate_test_report(self):
        """生成测试报告"""
        if not self.test_results:
            return
        
        print("\n📋 详细测试报告")
        print("="*60)
        
        for i, result in enumerate(self.test_results, 1):
            print(f"{i}. {result.get('method', 'N/A')} {result.get('endpoint', 'N/A')}")
            
            if result.get('success'):
                print(f"   ✅ 成功 - 状态码: {result.get('status_code', 'N/A')}")
                if 'response_size' in result:
                    print(f"   📦 响应大小: {result['response_size']} 字节")
            else:
                if 'error' in result:
                    print(f"   ❌ 异常: {result['error']}")
                else:
                    print(f"   ❌ 失败 - 状态码: {result.get('status_code', 'N/A')} (期望: {result.get('expected_status', 'N/A')})")
            print()


def main():
    """主测试函数"""
    print("🎲 DND 跑团管理器 - Web UI 功能测试")
    print("="*60)
    
    tester = WebUITester()
    
    try:
        success = tester.run_all_tests()
        tester.generate_test_report()
        
        if success:
            print("\n🎯 测试结论: Web UI版本功能正常，可以投入使用！")
            sys.exit(0)
        else:
            print("\n⚠️  测试结论: 发现问题，建议修复后再次测试")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        tester.stop_test_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        tester.stop_test_server()
        sys.exit(1)


if __name__ == "__main__":
    main()