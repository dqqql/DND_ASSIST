#!/usr/bin/env python3
"""
性能优化和验证测试脚本
测试性能优化器的各项功能，验证性能指标是否符合要求

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import sys
import time
import unittest
import tempfile
import shutil
import tkinter as tk
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入我们的简化性能测试
from run_performance_test import SimplePerformanceTest
from main import App, DATA_DIR


class TestPerformanceOptimization(unittest.TestCase):
    """测试性能优化功能"""
    
    def setUp(self):
        self.perf_test = SimplePerformanceTest()
    
    def test_startup_time_measurement(self):
        """测试启动时间测量"""
        startup_time = self.perf_test.measure_startup_time()
        self.assertIsInstance(startup_time, float)
        self.assertGreater(startup_time, 0)
        self.assertLess(startup_time, 10)  # 启动时间应该在合理范围内
    
    def test_memory_usage_measurement(self):
        """测试内存使用测量"""
        memory_usage = self.perf_test.measure_memory_usage()
        self.assertIsInstance(memory_usage, float)
        self.assertGreater(memory_usage, 0)
    
    def test_theme_application_time_measurement(self):
        """测试主题应用时间测量"""
        theme_time = self.perf_test.measure_theme_application_time()
        self.assertIsInstance(theme_time, float)
        self.assertGreaterEqual(theme_time, 0)
        self.assertLess(theme_time, 2)  # 主题应用时间应该在合理范围内
    
    def test_performance_benchmarks(self):
        """测试性能基准验证"""
        # 运行完整的性能测试
        measurements, all_passed = self.perf_test.run_performance_test()
        
        # 验证测量结果
        self.assertIsInstance(measurements, dict)
        self.assertIn('startup_time', measurements)
        self.assertIn('memory_usage', measurements)
        self.assertIn('theme_application_time', measurements)
        
        # 验证所有指标都是数值类型
        for metric, value in measurements.items():
            self.assertIsInstance(value, (int, float))
            self.assertGreaterEqual(value, 0)
    
    def test_optimization_application(self):
        """测试性能优化应用"""
        optimizations = self.perf_test.apply_optimizations()
        self.assertIsInstance(optimizations, list)
        self.assertGreater(len(optimizations), 0)


class TestPerformanceIntegration(unittest.TestCase):
    """测试性能优化与应用集成"""
    
    def setUp(self):
        # 创建临时数据目录
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_dir = DATA_DIR
        
        # 修改DATA_DIR指向临时目录
        import main
        main.DATA_DIR = self.temp_dir
        
        # 创建测试跑团数据
        self.create_test_campaign_data()
    
    def tearDown(self):
        # 恢复原始DATA_DIR
        import main
        main.DATA_DIR = self.original_data_dir
        
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_campaign_data(self):
        """创建测试跑团数据"""
        campaign_dir = os.path.join(self.temp_dir, "测试跑团")
        os.makedirs(campaign_dir, exist_ok=True)
        
        # 创建分类目录
        categories = ["characters", "monsters", "maps", "notes"]
        for category in categories:
            category_dir = os.path.join(campaign_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 创建一些测试文件
            for i in range(3):
                test_file = os.path.join(category_dir, f"test_{category}_{i}.txt")
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(f"测试{category}文件{i}")
    
    def test_app_creation_performance(self):
        """测试应用创建性能"""
        start_time = time.perf_counter()
        
        # 创建应用实例
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        try:
            app = App(root)
            root.update_idletasks()
            
            end_time = time.perf_counter()
            creation_time = end_time - start_time
            
            # 验证创建时间在合理范围内
            self.assertLess(creation_time, 5.0)  # 应用创建时间应该少于5秒
            
        finally:
            root.destroy()
    
    def test_theme_integration_performance(self):
        """测试主题集成性能"""
        root = tk.Tk()
        root.withdraw()
        
        try:
            app = App(root)
            
            # 测量主题重新应用的时间
            start_time = time.perf_counter()
            
            from theme_integration import integrate_theme_with_app
            theme_integrator = integrate_theme_with_app(app)
            root.update_idletasks()
            
            end_time = time.perf_counter()
            theme_time = end_time - start_time
            
            # 验证主题应用时间在合理范围内
            self.assertLess(theme_time, 1.0)  # 主题应用时间应该少于1秒
            
        finally:
            root.destroy()


class TestPerformanceReporting(unittest.TestCase):
    """测试性能报告功能"""
    
    def test_performance_report_generation(self):
        """测试性能报告生成"""
        perf_test = SimplePerformanceTest()
        
        # 运行性能测试
        measurements, all_passed = perf_test.run_performance_test()
        
        # 验证报告数据
        self.assertIsInstance(measurements, dict)
        self.assertIsInstance(all_passed, bool)
        
        # 验证测量数据的完整性
        expected_metrics = ['startup_time', 'memory_usage', 'theme_application_time']
        for metric in expected_metrics:
            self.assertIn(metric, measurements)
            self.assertIsInstance(measurements[metric], (int, float))
    
    def test_performance_report_file_creation(self):
        """测试性能报告文件创建"""
        # 运行性能测试（这会创建报告文件）
        perf_test = SimplePerformanceTest()
        measurements, all_passed = perf_test.run_performance_test()
        
        # 检查是否创建了报告文件
        report_files = [f for f in os.listdir('.') if f.startswith('performance_report_') and f.endswith('.txt')]
        self.assertGreater(len(report_files), 0)
        
        # 验证报告文件内容
        latest_report = max(report_files, key=lambda f: os.path.getctime(f))
        with open(latest_report, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("性能测试报告", content)
            self.assertIn("性能指标", content)
            self.assertIn("总体评估", content)
        
        # 清理测试文件
        os.remove(latest_report)


def run_performance_validation():
    """运行性能验证测试"""
    print("开始性能验证测试...")
    
    # 运行单元测试
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestPerformanceOptimization))
    test_suite.addTest(unittest.makeSuite(TestPerformanceIntegration))
    test_suite.addTest(unittest.makeSuite(TestPerformanceReporting))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    # 运行性能验证测试
    success = run_performance_validation()
    
    if success:
        print("\n✓ 所有性能验证测试通过")
        
        # 运行实际的性能测试
        print("\n开始实际性能测试...")
        try:
            perf_test = SimplePerformanceTest()
            measurements, all_passed = perf_test.run_performance_test()
            
            if all_passed:
                print("\n✓ 所有性能基准测试通过")
            else:
                print("\n⚠ 部分性能基准需要优化")
        
        except Exception as e:
            print(f"\n✗ 性能测试执行失败: {e}")
    else:
        print("\n✗ 性能验证测试失败")
        sys.exit(1)