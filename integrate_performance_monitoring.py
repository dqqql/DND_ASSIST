#!/usr/bin/env python3
"""
性能监控集成脚本
将性能监控集成到主应用中，实现实时性能监控和优化

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import sys
import time
import tkinter as tk
from typing import Dict, Any

# 导入性能监控模块
from performance_monitor import (
    PerformanceMonitor, create_performance_monitor, 
    initialize_global_monitor, get_global_performance_monitor
)
from run_performance_test import SimplePerformanceTest
from main import App


class PerformanceIntegratedApp:
    """集成性能监控的应用包装器"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.performance_monitor = None
        self.app = None
        self.performance_window = None
        
        # 创建应用实例
        self.app = App(root)
        
        # 初始化性能监控
        self.initialize_performance_monitoring()
        
        # 添加性能监控菜单
        self.add_performance_menu()
    
    def initialize_performance_monitoring(self):
        """初始化性能监控"""
        self.performance_monitor = create_performance_monitor(self.app)
        
        # 添加自定义警报处理
        self.performance_monitor.add_alert_callback(self.handle_performance_alert)
        
        # 启动监控
        self.performance_monitor.start_monitoring()
        
        print("性能监控已集成到应用中")
    
    def handle_performance_alert(self, alert_type: str, data: Dict):
        """处理性能警报"""
        print(f"性能警报: {alert_type}")
        print(f"详细信息: {data}")
        
        # 根据警报类型采取相应措施
        if alert_type == 'memory_growth':
            self.handle_memory_growth_alert(data)
        elif alert_type == 'slow_ui_response':
            self.handle_slow_ui_alert(data)
        elif alert_type == 'slow_operation':
            self.handle_slow_operation_alert(data)
    
    def handle_memory_growth_alert(self, data: Dict):
        """处理内存增长警报"""
        growth = data.get('growth', 0)
        print(f"内存使用增长过多: {growth} 对象")
        
        # 触发垃圾回收
        import gc
        gc.collect()
        print("已执行垃圾回收优化")
    
    def handle_slow_ui_alert(self, data: Dict):
        """处理UI响应慢警报"""
        response_time = data.get('response_time', 0)
        operation = data.get('operation', 'unknown')
        print(f"UI响应时间过长: {response_time:.3f}s (操作: {operation})")
        
        # 可以在这里添加UI优化措施
        self.optimize_ui_performance()
    
    def handle_slow_operation_alert(self, data: Dict):
        """处理慢操作警报"""
        operation_name = data.get('operation_name', 'unknown')
        duration = data.get('duration', 0)
        print(f"操作执行时间过长: {operation_name} ({duration:.3f}s)")
    
    def optimize_ui_performance(self):
        """优化UI性能"""
        # 减少不必要的UI更新
        if hasattr(self.app, 'root'):
            self.app.root.update_idletasks()
        
        # 清理图片缓存
        if hasattr(self.app, 'image_label') and hasattr(self.app.image_label, 'image'):
            # 清理图片缓存
            pass
        
        print("已应用UI性能优化")
    
    def add_performance_menu(self):
        """添加性能监控菜单"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 添加性能菜单
        performance_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="性能监控", menu=performance_menu)
        
        performance_menu.add_command(label="显示性能状态", command=self.show_performance_status)
        performance_menu.add_command(label="运行性能测试", command=self.run_performance_test)
        performance_menu.add_command(label="导出性能数据", command=self.export_performance_data)
        performance_menu.add_separator()
        performance_menu.add_command(label="重置性能基准", command=self.reset_performance_baseline)
        performance_menu.add_command(label="优化性能", command=self.manual_performance_optimization)
    
    def show_performance_status(self):
        """显示性能状态窗口"""
        if self.performance_window and self.performance_window.winfo_exists():
            self.performance_window.lift()
            return
        
        self.performance_window = tk.Toplevel(self.root)
        self.performance_window.title("性能监控状态")
        self.performance_window.geometry("600x400")
        
        # 创建文本显示区域
        text_frame = tk.Frame(self.performance_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示性能摘要
        if self.performance_monitor:
            summary = self.performance_monitor.get_performance_summary()
            
            text_widget.insert(tk.END, "性能监控状态\n")
            text_widget.insert(tk.END, "=" * 50 + "\n\n")
            
            for key, value in summary.items():
                text_widget.insert(tk.END, f"{key}: {value}\n")
            
            text_widget.insert(tk.END, "\n最近性能历史:\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            
            history = self.performance_monitor.get_performance_history(5)  # 5分钟历史
            for record in history[-10:]:  # 显示最近10条记录
                timestamp = time.strftime("%H:%M:%S", time.localtime(record['timestamp']))
                text_widget.insert(tk.END, f"{timestamp}: 内存对象={record['memory_objects']}")
                if record['ui_response_time'] > 0:
                    text_widget.insert(tk.END, f", 响应时间={record['ui_response_time']:.3f}s")
                text_widget.insert(tk.END, "\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # 添加刷新按钮
        button_frame = tk.Frame(self.performance_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = tk.Button(button_frame, text="刷新", 
                               command=lambda: self.refresh_performance_status(text_widget))
        refresh_btn.pack(side=tk.LEFT)
        
        close_btn = tk.Button(button_frame, text="关闭", 
                             command=self.performance_window.destroy)
        close_btn.pack(side=tk.RIGHT)
    
    def refresh_performance_status(self, text_widget: tk.Text):
        """刷新性能状态显示"""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        if self.performance_monitor:
            summary = self.performance_monitor.get_performance_summary()
            
            text_widget.insert(tk.END, "性能监控状态 (已刷新)\n")
            text_widget.insert(tk.END, "=" * 50 + "\n\n")
            
            for key, value in summary.items():
                text_widget.insert(tk.END, f"{key}: {value}\n")
            
            text_widget.insert(tk.END, "\n最近性能历史:\n")
            text_widget.insert(tk.END, "-" * 30 + "\n")
            
            history = self.performance_monitor.get_performance_history(5)
            for record in history[-10:]:
                timestamp = time.strftime("%H:%M:%S", time.localtime(record['timestamp']))
                text_widget.insert(tk.END, f"{timestamp}: 内存对象={record['memory_objects']}")
                if record['ui_response_time'] > 0:
                    text_widget.insert(tk.END, f", 响应时间={record['ui_response_time']:.3f}s")
                text_widget.insert(tk.END, "\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def run_performance_test(self):
        """运行性能测试"""
        print("开始运行性能测试...")
        
        # 创建性能测试实例
        perf_test = SimplePerformanceTest()
        
        # 在后台线程中运行测试，避免阻塞UI
        import threading
        
        def run_test():
            try:
                measurements, all_passed = perf_test.run_performance_test()
                
                # 在主线程中显示结果
                self.root.after(0, lambda: self.show_test_results(measurements, all_passed))
                
            except Exception as e:
                print(f"性能测试失败: {e}")
                self.root.after(0, lambda: tk.messagebox.showerror("错误", f"性能测试失败: {e}"))
        
        test_thread = threading.Thread(target=run_test, daemon=True)
        test_thread.start()
    
    def show_test_results(self, measurements: Dict, all_passed: bool):
        """显示测试结果"""
        import tkinter.messagebox as messagebox
        
        result_text = "性能测试结果:\n\n"
        for metric, value in measurements.items():
            metric_name = metric.replace('_', ' ').title()
            result_text += f"{metric_name}: {value:.3f}\n"
        
        result_text += f"\n总体评估: {'通过' if all_passed else '需要优化'}"
        
        if all_passed:
            messagebox.showinfo("性能测试结果", result_text)
        else:
            messagebox.showwarning("性能测试结果", result_text)
    
    def export_performance_data(self):
        """导出性能数据"""
        if self.performance_monitor:
            filename = self.performance_monitor.export_performance_data()
            if filename:
                import tkinter.messagebox as messagebox
                messagebox.showinfo("导出成功", f"性能数据已导出到:\n{filename}")
        else:
            import tkinter.messagebox as messagebox
            messagebox.showerror("错误", "性能监控未启用")
    
    def reset_performance_baseline(self):
        """重置性能基准"""
        if self.performance_monitor:
            self.performance_monitor.reset_baseline()
            import tkinter.messagebox as messagebox
            messagebox.showinfo("重置成功", "性能基准已重置")
    
    def manual_performance_optimization(self):
        """手动性能优化"""
        print("执行手动性能优化...")
        
        # 执行垃圾回收
        import gc
        gc.collect()
        
        # 应用UI优化
        self.optimize_ui_performance()
        
        # 重置性能基准
        if self.performance_monitor:
            self.performance_monitor.reset_baseline()
        
        import tkinter.messagebox as messagebox
        messagebox.showinfo("优化完成", "性能优化已完成")
    
    def cleanup(self):
        """清理资源"""
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()
        
        if self.performance_window and self.performance_window.winfo_exists():
            self.performance_window.destroy()


def main():
    """主函数 - 启动集成性能监控的应用"""
    print("启动集成性能监控的DND跑团管理器...")
    
    # 创建主窗口
    root = tk.Tk()
    
    try:
        # 创建集成性能监控的应用
        integrated_app = PerformanceIntegratedApp(root)
        
        # 设置窗口关闭事件处理
        def on_closing():
            integrated_app.cleanup()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动应用
        print("应用已启动，性能监控正在运行...")
        root.mainloop()
        
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("应用已关闭")


if __name__ == "__main__":
    main()