#!/usr/bin/env python3
"""
性能监控模块
实时监控应用性能，确保UI更新的响应性和内存使用稳定性

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import sys
import time
import gc
import threading
import tkinter as tk
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import json

@dataclass
class PerformanceSnapshot:
    """性能快照数据类"""
    timestamp: float
    memory_objects: int
    ui_response_time: float = 0.0
    operation_name: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp,
            'memory_objects': self.memory_objects,
            'ui_response_time': self.ui_response_time,
            'operation_name': self.operation_name
        }


@dataclass
class PerformanceThresholds:
    """性能阈值配置"""
    max_ui_response_time: float = 0.1  # 最大UI响应时间（秒）
    max_memory_growth: int = 10000  # 最大内存对象增长数量
    monitoring_interval: float = 1.0  # 监控间隔（秒）
    max_snapshots: int = 1000  # 最大快照数量
    alert_threshold: int = 5  # 连续超阈值次数触发警报


class PerformanceMonitor:
    """性能监控器 - 实时监控应用性能"""
    
    def __init__(self, app_instance=None, thresholds: PerformanceThresholds = None):
        self.app = app_instance
        self.thresholds = thresholds or PerformanceThresholds()
        self.snapshots: deque = deque(maxlen=self.thresholds.max_snapshots)
        self.baseline_memory = 0
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable] = []
        self.performance_alerts = []
        
        # 性能统计
        self.stats = {
            'total_operations': 0,
            'slow_operations': 0,
            'memory_warnings': 0,
            'peak_memory': 0,
            'average_response_time': 0.0
        }
        
        # 设置基准内存
        self._set_baseline_memory()
    
    def _set_baseline_memory(self):
        """设置基准内存使用量"""
        self.baseline_memory = len(gc.get_objects())
    
    def add_alert_callback(self, callback: Callable[[str, Dict], None]):
        """添加性能警报回调函数"""
        self.alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, data: Dict):
        """触发性能警报"""
        alert_info = {
            'type': alert_type,
            'timestamp': time.time(),
            'data': data
        }
        self.performance_alerts.append(alert_info)
        
        # 调用所有注册的回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                print(f"警报回调执行失败: {e}")
    
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        print("性能监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        consecutive_alerts = 0
        
        while self.monitoring_active:
            try:
                # 创建性能快照
                snapshot = self._create_snapshot()
                self.snapshots.append(snapshot)
                
                # 检查性能阈值
                alerts = self._check_thresholds(snapshot)
                
                if alerts:
                    consecutive_alerts += 1
                    if consecutive_alerts >= self.thresholds.alert_threshold:
                        for alert in alerts:
                            self._trigger_alert(alert['type'], alert['data'])
                        consecutive_alerts = 0  # 重置计数器
                else:
                    consecutive_alerts = 0
                
                # 更新统计信息
                self._update_stats(snapshot)
                
                # 等待下一次监控
                time.sleep(self.thresholds.monitoring_interval)
                
            except Exception as e:
                print(f"性能监控错误: {e}")
                time.sleep(self.thresholds.monitoring_interval)
    
    def _create_snapshot(self) -> PerformanceSnapshot:
        """创建性能快照"""
        current_memory = len(gc.get_objects())
        
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            memory_objects=current_memory
        )
        
        return snapshot
    
    def _check_thresholds(self, snapshot: PerformanceSnapshot) -> List[Dict]:
        """检查性能阈值"""
        alerts = []
        
        # 检查内存增长
        memory_growth = snapshot.memory_objects - self.baseline_memory
        if memory_growth > self.thresholds.max_memory_growth:
            alerts.append({
                'type': 'memory_growth',
                'data': {
                    'current_objects': snapshot.memory_objects,
                    'baseline_objects': self.baseline_memory,
                    'growth': memory_growth,
                    'threshold': self.thresholds.max_memory_growth
                }
            })
        
        # 检查UI响应时间（如果有测量数据）
        if snapshot.ui_response_time > self.thresholds.max_ui_response_time:
            alerts.append({
                'type': 'slow_ui_response',
                'data': {
                    'response_time': snapshot.ui_response_time,
                    'threshold': self.thresholds.max_ui_response_time,
                    'operation': snapshot.operation_name
                }
            })
        
        return alerts
    
    def _update_stats(self, snapshot: PerformanceSnapshot):
        """更新性能统计信息"""
        self.stats['total_operations'] += 1
        
        # 更新峰值内存
        if snapshot.memory_objects > self.stats['peak_memory']:
            self.stats['peak_memory'] = snapshot.memory_objects
        
        # 更新慢操作计数
        if snapshot.ui_response_time > self.thresholds.max_ui_response_time:
            self.stats['slow_operations'] += 1
        
        # 更新平均响应时间
        if snapshot.ui_response_time > 0:
            total_ops = self.stats['total_operations']
            current_avg = self.stats['average_response_time']
            self.stats['average_response_time'] = (
                (current_avg * (total_ops - 1) + snapshot.ui_response_time) / total_ops
            )
    
    def measure_operation(self, operation_name: str):
        """测量操作性能的上下文管理器"""
        return OperationMeasurement(self, operation_name)
    
    def get_performance_summary(self) -> Dict:
        """获取性能摘要"""
        if not self.snapshots:
            return {'status': 'no_data'}
        
        recent_snapshots = list(self.snapshots)[-10:]  # 最近10个快照
        
        current_memory = recent_snapshots[-1].memory_objects
        memory_trend = 'stable'
        
        if len(recent_snapshots) >= 2:
            memory_change = current_memory - recent_snapshots[0].memory_objects
            if memory_change > 1000:
                memory_trend = 'increasing'
            elif memory_change < -1000:
                memory_trend = 'decreasing'
        
        return {
            'status': 'active' if self.monitoring_active else 'inactive',
            'current_memory_objects': current_memory,
            'baseline_memory_objects': self.baseline_memory,
            'memory_growth': current_memory - self.baseline_memory,
            'memory_trend': memory_trend,
            'total_snapshots': len(self.snapshots),
            'recent_alerts': len([a for a in self.performance_alerts if time.time() - a['timestamp'] < 300]),  # 5分钟内的警报
            'stats': self.stats.copy()
        }
    
    def get_performance_history(self, minutes: int = 10) -> List[Dict]:
        """获取性能历史数据"""
        cutoff_time = time.time() - (minutes * 60)
        recent_snapshots = [
            s for s in self.snapshots 
            if s.timestamp >= cutoff_time
        ]
        
        return [s.to_dict() for s in recent_snapshots]
    
    def export_performance_data(self, filename: str = None) -> str:
        """导出性能数据到文件"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_data_{timestamp}.json"
        
        data = {
            'export_time': time.time(),
            'monitoring_config': {
                'max_ui_response_time': self.thresholds.max_ui_response_time,
                'max_memory_growth': self.thresholds.max_memory_growth,
                'monitoring_interval': self.thresholds.monitoring_interval
            },
            'performance_summary': self.get_performance_summary(),
            'performance_history': self.get_performance_history(60),  # 1小时历史
            'alerts': self.performance_alerts[-100:]  # 最近100个警报
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"性能数据已导出到: {filename}")
            return filename
        except Exception as e:
            print(f"导出性能数据失败: {e}")
            return ""
    
    def reset_baseline(self):
        """重置性能基准"""
        self._set_baseline_memory()
        self.snapshots.clear()
        self.performance_alerts.clear()
        self.stats = {
            'total_operations': 0,
            'slow_operations': 0,
            'memory_warnings': 0,
            'peak_memory': 0,
            'average_response_time': 0.0
        }
        print("性能基准已重置")


class OperationMeasurement:
    """操作性能测量上下文管理器"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        duration = end_time - self.start_time
        
        # 创建包含操作时间的快照
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            memory_objects=len(gc.get_objects()),
            ui_response_time=duration,
            operation_name=self.operation_name
        )
        
        # 添加到监控器
        if self.monitor.monitoring_active:
            self.monitor.snapshots.append(snapshot)
            
            # 检查是否超过阈值
            if duration > self.monitor.thresholds.max_ui_response_time:
                self.monitor._trigger_alert('slow_operation', {
                    'operation_name': self.operation_name,
                    'duration': duration,
                    'threshold': self.monitor.thresholds.max_ui_response_time
                })


def create_performance_monitor(app_instance=None) -> PerformanceMonitor:
    """创建性能监控器实例"""
    # 配置性能阈值
    thresholds = PerformanceThresholds(
        max_ui_response_time=0.1,  # 100ms
        max_memory_growth=10000,   # 10k对象
        monitoring_interval=2.0,   # 2秒监控间隔
        max_snapshots=500,         # 保留500个快照
        alert_threshold=3          # 连续3次超阈值触发警报
    )
    
    monitor = PerformanceMonitor(app_instance, thresholds)
    
    # 添加默认的警报处理
    def default_alert_handler(alert_type: str, data: Dict):
        print(f"性能警报 [{alert_type}]: {data}")
    
    monitor.add_alert_callback(default_alert_handler)
    
    return monitor


# 全局性能监控器实例
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_performance_monitor() -> Optional[PerformanceMonitor]:
    """获取全局性能监控器"""
    return _global_monitor


def initialize_global_monitor(app_instance=None):
    """初始化全局性能监控器"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = create_performance_monitor(app_instance)
        _global_monitor.start_monitoring()
    return _global_monitor


def shutdown_global_monitor():
    """关闭全局性能监控器"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()
        _global_monitor = None


if __name__ == "__main__":
    # 演示性能监控器的使用
    print("性能监控器演示")
    
    # 创建监控器
    monitor = create_performance_monitor()
    monitor.start_monitoring()
    
    try:
        # 模拟一些操作
        for i in range(5):
            with monitor.measure_operation(f"test_operation_{i}"):
                time.sleep(0.05)  # 模拟50ms操作
                # 创建一些对象来模拟内存使用
                temp_objects = [f"object_{j}" for j in range(100)]
        
        # 等待监控数据收集
        time.sleep(3)
        
        # 显示性能摘要
        summary = monitor.get_performance_summary()
        print("\n性能摘要:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # 导出性能数据
        export_file = monitor.export_performance_data()
        if export_file:
            print(f"\n性能数据已导出到: {export_file}")
    
    finally:
        monitor.stop_monitoring()
        print("\n演示完成")