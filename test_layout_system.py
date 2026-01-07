#!/usr/bin/env python3
"""
布局和间距系统测试
验证8px网格对齐系统、间距优化和视觉层次改进的正确实现
"""

import tkinter as tk
import sys
import traceback
from layout_system import (
    get_layout_manager, 
    LayoutConfig, 
    LayoutManager,
    get_grid_aligned_spacing,
    get_component_spacing,
    apply_layout_improvements,
    setup_responsive_layout
)
from theme_system import get_theme_manager


class LayoutSystemTester:
    """布局系统测试器"""
    
    def __init__(self):
        self.test_results = []
        self.layout_manager = get_layout_manager()
        self.theme_manager = get_theme_manager()
        
    def run_all_tests(self):
        """运行所有测试"""
        print("开始布局和间距系统验证测试...")
        print("=" * 50)
        
        # 测试8px网格系统
        self.test_grid_alignment_system()
        
        # 测试间距计算
        self.test_spacing_calculations()
        
        # 测试布局配置
        self.test_layout_configuration()
        
        # 测试组件间距优化
        self.test_component_spacing_optimization()
        
        # 测试视觉层次改进
        self.test_visual_hierarchy_improvements()
        
        # 测试响应式布局
        self.test_responsive_layout()
        
        # 输出测试结果
        self.print_test_results()
        
        return all(result['passed'] for result in self.test_results)
    
    def test_grid_alignment_system(self):
        """测试8px网格对齐系统"""
        print("测试 1: 8px网格对齐系统")
        
        try:
            config = self.layout_manager.config
            
            # 验证基础网格单位
            assert config.grid_size == 8, f"网格基础单位错误: {config.grid_size} != 8"
            
            # 测试网格对齐函数
            test_values = [1, 5, 9, 12, 15, 20, 25]
            expected_aligned = [0, 8, 8, 16, 16, 16, 24]
            
            for test_val, expected in zip(test_values, expected_aligned):
                aligned = config.get_grid_aligned_value(test_val)
                assert aligned == expected, f"网格对齐错误: {test_val} -> {aligned} != {expected}"
            
            # 测试便捷函数
            aligned_spacing = get_grid_aligned_spacing(10)
            assert aligned_spacing == 8, f"便捷函数网格对齐错误: {aligned_spacing} != 8"
            
            # 验证预定义间距值符合网格
            spacing_values = [config.xs, config.sm, config.md, config.lg, config.xl]
            expected_grid_values = [4, 8, 16, 24, 32]  # xs是特殊的0.5单位
            
            for actual, expected in zip(spacing_values, expected_grid_values):
                assert actual == expected, f"预定义间距不符合网格: {actual} != {expected}"
            
            self.test_results.append({
                'name': '8px网格对齐系统',
                'passed': True,
                'message': '网格对齐计算正确，所有预定义值符合8px网格'
            })
            print("✓ 8px网格对齐系统测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '8px网格对齐系统',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 8px网格对齐系统测试失败: {str(e)}")
    
    def test_spacing_calculations(self):
        """测试间距计算"""
        print("测试 2: 间距计算和上下文适配")
        
        try:
            config = self.layout_manager.config
            
            # 测试基础间距计算
            button_spacing = config.calculate_spacing("button_group")
            assert isinstance(button_spacing, int), "间距计算返回类型错误"
            assert button_spacing > 0, "间距计算返回值无效"
            
            # 测试上下文适配
            default_spacing = config.calculate_spacing("section", "default")
            compact_spacing = config.calculate_spacing("section", "compact")
            spacious_spacing = config.calculate_spacing("section", "spacious")
            
            assert compact_spacing < default_spacing, "紧凑模式间距应小于默认间距"
            assert spacious_spacing > default_spacing, "宽松模式间距应大于默认间距"
            
            # 测试便捷函数
            component_spacing = get_component_spacing("button_group")
            assert isinstance(component_spacing, int), "便捷函数返回类型错误"
            assert component_spacing > 0, "便捷函数返回值无效"
            
            # 验证所有预定义组件间距
            required_components = [
                "button_group", "section", "panel", "list_item", 
                "content", "dialog", "window_edge", "category_button"
            ]
            
            for component in required_components:
                spacing = config.calculate_spacing(component)
                assert isinstance(spacing, int), f"组件间距类型错误: {component}"
                assert spacing >= 0, f"组件间距值无效: {component} = {spacing}"
            
            self.test_results.append({
                'name': '间距计算和上下文适配',
                'passed': True,
                'message': '所有间距计算正确，上下文适配功能正常'
            })
            print("✓ 间距计算测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '间距计算和上下文适配',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 间距计算测试失败: {str(e)}")
    
    def test_layout_configuration(self):
        """测试布局配置"""
        print("测试 3: 布局配置完整性")
        
        try:
            config = self.layout_manager.config
            
            # 验证组件间距配置
            assert config.component_spacing is not None, "组件间距配置未初始化"
            assert isinstance(config.component_spacing, dict), "组件间距配置类型错误"
            
            required_component_spacing = [
                "button_group", "section", "panel", "list_item",
                "content", "dialog", "window_edge", "category_button"
            ]
            
            for key in required_component_spacing:
                assert key in config.component_spacing, f"缺少组件间距配置: {key}"
                value = config.component_spacing[key]
                assert isinstance(value, int), f"组件间距值类型错误: {key}"
                assert value >= 0, f"组件间距值无效: {key} = {value}"
            
            # 验证区域边距配置
            assert config.section_margins is not None, "区域边距配置未初始化"
            assert isinstance(config.section_margins, dict), "区域边距配置类型错误"
            
            required_section_margins = [
                "left_panel", "right_panel", "top_section",
                "content_viewer", "file_list", "button_area"
            ]
            
            for key in required_section_margins:
                assert key in config.section_margins, f"缺少区域边距配置: {key}"
                value = config.section_margins[key]
                assert isinstance(value, int), f"区域边距值类型错误: {key}"
                assert value >= 0, f"区域边距值无效: {key} = {value}"
            
            # 验证响应式断点配置
            assert config.responsive_breakpoints is not None, "响应式断点配置未初始化"
            assert isinstance(config.responsive_breakpoints, dict), "响应式断点配置类型错误"
            
            required_breakpoints = ["small", "medium", "large"]
            for key in required_breakpoints:
                assert key in config.responsive_breakpoints, f"缺少响应式断点: {key}"
                value = config.responsive_breakpoints[key]
                assert isinstance(value, int), f"响应式断点值类型错误: {key}"
                assert value > 0, f"响应式断点值无效: {key} = {value}"
            
            # 验证断点顺序
            small = config.responsive_breakpoints["small"]
            medium = config.responsive_breakpoints["medium"]
            large = config.responsive_breakpoints["large"]
            
            assert small < medium < large, f"响应式断点顺序错误: {small}, {medium}, {large}"
            
            self.test_results.append({
                'name': '布局配置完整性',
                'passed': True,
                'message': '所有布局配置项完整且值有效'
            })
            print("✓ 布局配置测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '布局配置完整性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 布局配置测试失败: {str(e)}")
    
    def test_component_spacing_optimization(self):
        """测试组件间距优化"""
        print("测试 4: 组件间距优化")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 测试按钮间距优化
            test_button = tk.Button(test_window, text="测试按钮")
            self.layout_manager.optimize_widget_spacing(test_button, "button")
            
            # 验证按钮配置是否被优化
            padx = test_button.cget('padx')
            pady = test_button.cget('pady')
            
            # 验证内边距是网格对齐的
            theme = self.theme_manager.get_current_theme()
            expected_padx = self.layout_manager.config.get_grid_aligned_value(theme.spacing.button_padding_x)
            expected_pady = self.layout_manager.config.get_grid_aligned_value(theme.spacing.button_padding_y)
            
            assert padx == expected_padx, f"按钮水平内边距优化错误: {padx} != {expected_padx}"
            assert pady == expected_pady, f"按钮垂直内边距优化错误: {pady} != {expected_pady}"
            
            # 测试列表框间距优化
            test_listbox = tk.Listbox(test_window)
            self.layout_manager.optimize_widget_spacing(test_listbox, "listbox")
            
            # 验证列表框配置
            selectborderwidth = test_listbox.cget('selectborderwidth')
            activestyle = test_listbox.cget('activestyle')
            
            assert selectborderwidth == 0, f"列表框选择边框宽度错误: {selectborderwidth}"
            assert activestyle == "dotbox", f"列表框激活样式错误: {activestyle}"
            
            # 测试文本控件间距优化
            test_text = tk.Text(test_window)
            self.layout_manager.optimize_widget_spacing(test_text, "text")
            
            # 验证文本控件内边距
            text_padx = test_text.cget('padx')
            text_pady = test_text.cget('pady')
            expected_padding = self.layout_manager.config.grid_size
            
            assert text_padx == expected_padding, f"文本控件水平内边距错误: {text_padx} != {expected_padding}"
            assert text_pady == expected_padding, f"文本控件垂直内边距错误: {text_pady} != {expected_padding}"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '组件间距优化',
                'passed': True,
                'message': '所有组件间距优化正确应用'
            })
            print("✓ 组件间距优化测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '组件间距优化',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 组件间距优化测试失败: {str(e)}")
    
    def test_visual_hierarchy_improvements(self):
        """测试视觉层次改进"""
        print("测试 5: 视觉层次和组件对齐")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建测试容器
            test_container = tk.Frame(test_window)
            
            # 添加一些子控件
            child1 = tk.Label(test_container, text="标签1")
            child1.pack(side=tk.TOP, pady=5)
            
            child2 = tk.Button(test_container, text="按钮1")
            child2.pack(side=tk.TOP, pady=3)
            
            child3 = tk.Frame(test_container)
            child3.pack(side=tk.LEFT, padx=7)
            
            # 应用视觉层次改进
            self.layout_manager.apply_visual_hierarchy(test_container)
            
            # 验证网格对齐是否应用
            # 注意：由于Tkinter的限制，我们主要验证函数能正常执行而不出错
            
            # 测试网格对齐函数
            test_widget = tk.Label(test_container, text="测试")
            test_widget.pack(padx=10, pady=15)
            
            self.layout_manager._align_widget_to_grid(test_widget)
            
            # 获取对齐后的间距
            pack_info = test_widget.pack_info()
            aligned_padx = pack_info.get('padx', 0)
            aligned_pady = pack_info.get('pady', 0)
            
            # 验证间距是网格对齐的
            expected_padx = self.layout_manager.config.get_grid_aligned_value(10)
            expected_pady = self.layout_manager.config.get_grid_aligned_value(15)
            
            assert aligned_padx == expected_padx, f"水平间距网格对齐错误: {aligned_padx} != {expected_padx}"
            assert aligned_pady == expected_pady, f"垂直间距网格对齐错误: {aligned_pady} != {expected_pady}"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '视觉层次和组件对齐',
                'passed': True,
                'message': '视觉层次改进和网格对齐功能正常'
            })
            print("✓ 视觉层次改进测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '视觉层次和组件对齐',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 视觉层次改进测试失败: {str(e)}")
    
    def test_responsive_layout(self):
        """测试响应式布局"""
        print("测试 6: 响应式布局适配")
        
        try:
            config = self.layout_manager.config
            base_spacing = 16
            
            # 测试不同窗口宽度的响应式间距
            small_width = 500  # 小于small断点
            medium_width = 800  # 在medium范围内
            large_width = 1300  # 大于large断点
            
            small_spacing = self.layout_manager.get_responsive_spacing(small_width, base_spacing)
            medium_spacing = self.layout_manager.get_responsive_spacing(medium_width, base_spacing)
            large_spacing = self.layout_manager.get_responsive_spacing(large_width, base_spacing)
            
            # 验证响应式间距计算
            assert small_spacing == int(base_spacing * 0.75), f"小屏幕间距计算错误: {small_spacing}"
            assert medium_spacing == base_spacing, f"中等屏幕间距计算错误: {medium_spacing}"
            assert large_spacing == int(base_spacing * 1.25), f"大屏幕间距计算错误: {large_spacing}"
            
            # 验证间距递增关系
            assert small_spacing < medium_spacing < large_spacing, "响应式间距递增关系错误"
            
            # 测试响应式布局应用
            test_window = tk.Tk()
            test_window.withdraw()
            test_window.geometry("800x600")
            
            # 应用响应式布局
            self.layout_manager.apply_responsive_layout(test_window)
            
            # 验证函数执行无错误
            test_window.destroy()
            
            self.test_results.append({
                'name': '响应式布局适配',
                'passed': True,
                'message': '响应式间距计算正确，布局适配功能正常'
            })
            print("✓ 响应式布局测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '响应式布局适配',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 响应式布局测试失败: {str(e)}")
    
    def print_test_results(self):
        """输出测试结果"""
        print("\n" + "=" * 50)
        print("测试结果汇总:")
        print("=" * 50)
        
        passed_count = 0
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            print(f"{status} - {result['name']}: {result['message']}")
            if result['passed']:
                passed_count += 1
        
        print("=" * 50)
        print(f"总计: {passed_count}/{total_count} 测试通过")
        
        if passed_count == total_count:
            print("🎉 所有布局和间距系统验证通过！")
            return True
        else:
            print("⚠️  部分测试失败，需要检查相关布局实现")
            return False


def run_layout_visual_test():
    """运行布局系统可视化测试"""
    print("\n启动布局系统可视化测试窗口...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("布局和间距系统验证 - 可视化测试")
    root.geometry("1000x700")
    
    # 应用主题和布局
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    root.configure(bg=theme.colors.primary_bg)
    
    # 应用布局改进
    from layout_system import apply_layout_improvements
    
    # 创建模拟应用实例
    class MockApp:
        def __init__(self, root):
            self.root = root
    
    mock_app = MockApp(root)
    apply_layout_improvements(mock_app)
    
    # 设置响应式布局
    setup_responsive_layout(root)
    
    # 创建主框架 - 使用网格对齐的间距
    from layout_system import get_component_spacing, get_grid_aligned_spacing
    
    main_padding = get_component_spacing("window_edge")
    main_frame = tk.Frame(root, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=main_padding, pady=main_padding)
    
    # 标题
    title_spacing = get_grid_aligned_spacing(16)
    title_label = tk.Label(main_frame,
                          text="布局和间距系统验证",
                          font=theme.typography.get_font_tuple(theme.typography.size_title, theme.typography.weight_bold),
                          bg=theme.colors.primary_bg,
                          fg=theme.colors.text_primary)
    title_label.pack(pady=(0, title_spacing))
    
    # 网格演示区域
    grid_frame = tk.Frame(main_frame, bg=theme.colors.secondary_bg, relief=tk.SUNKEN, bd=1)
    grid_frame.pack(fill=tk.X, pady=(0, get_component_spacing("section")))
    
    grid_title = tk.Label(grid_frame,
                         text="8px网格系统演示 (间距: 8px, 16px, 24px, 32px)",
                         font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                         bg=theme.colors.secondary_bg,
                         fg=theme.colors.text_primary)
    grid_title.pack(pady=get_grid_aligned_spacing(8))
    
    # 创建网格演示按钮
    grid_demo_frame = tk.Frame(grid_frame, bg=theme.colors.secondary_bg)
    grid_demo_frame.pack(pady=get_grid_aligned_spacing(8))
    
    from theme_utils import create_themed_button, add_interaction_feedback
    
    spacings = [8, 16, 24, 32]
    for i, spacing in enumerate(spacings):
        btn = create_themed_button(grid_demo_frame, text=f"{spacing}px", width=8)
        btn.pack(side=tk.LEFT, padx=spacing//2)
        add_interaction_feedback(btn, "button")
    
    # 组件间距演示
    component_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    component_frame.pack(fill=tk.BOTH, expand=True)
    
    # 左侧面板演示
    left_demo = tk.Frame(component_frame, bg=theme.colors.secondary_bg, relief=tk.SUNKEN, bd=1, width=200)
    left_demo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, get_component_spacing("panel")))
    left_demo.pack_propagate(False)
    
    left_title = tk.Label(left_demo,
                         text="左侧面板演示",
                         font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                         bg=theme.colors.secondary_bg,
                         fg=theme.colors.text_primary)
    left_title.pack(pady=(get_grid_aligned_spacing(8), get_grid_aligned_spacing(8)))
    
    # 添加演示按钮
    button_spacing = get_component_spacing("button_group") // 2
    for i in range(3):
        demo_btn = create_themed_button(left_demo, text=f"按钮 {i+1}")
        demo_btn.pack(fill=tk.X, padx=get_grid_aligned_spacing(8), pady=button_spacing)
        add_interaction_feedback(demo_btn, "button")
    
    # 右侧内容演示
    right_demo = tk.Frame(component_frame, bg=theme.colors.primary_bg)
    right_demo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # 顶部按钮组
    top_demo = tk.Frame(right_demo, bg=theme.colors.primary_bg)
    top_demo.pack(fill=tk.X, pady=(0, get_component_spacing("section")))
    
    category_demo = tk.Frame(top_demo, bg=theme.colors.primary_bg)
    category_demo.pack(side=tk.LEFT)
    
    categories = ["人物卡", "怪物卡", "地图", "剧情"]
    category_spacing = get_component_spacing("category_button")
    
    for category in categories:
        cat_btn = create_themed_button(category_demo, text=category, width=8)
        cat_btn.pack(side=tk.LEFT, padx=category_spacing)
        add_interaction_feedback(cat_btn, "button")
    
    # 操作按钮
    action_demo = tk.Frame(top_demo, bg=theme.colors.primary_bg)
    action_demo.pack(side=tk.RIGHT)
    
    action_spacing = get_component_spacing("button_group") // 2
    action_btn1 = create_themed_button(action_demo, text="新建文件", width=10)
    action_btn1.pack(side=tk.LEFT, padx=action_spacing)
    add_interaction_feedback(action_btn1, "button")
    
    action_btn2 = create_themed_button(action_demo, text="删除文件", width=10)
    action_btn2.pack(side=tk.LEFT, padx=action_spacing)
    add_interaction_feedback(action_btn2, "button")
    
    # 内容区域演示
    content_demo = tk.Frame(right_demo, bg=theme.colors.secondary_bg, relief=tk.SUNKEN, bd=1)
    content_demo.pack(fill=tk.BOTH, expand=True)
    
    content_title = tk.Label(content_demo,
                           text="内容区域演示 - 网格对齐的间距和边距",
                           font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                           bg=theme.colors.secondary_bg,
                           fg=theme.colors.text_primary)
    content_title.pack(pady=get_grid_aligned_spacing(8))
    
    # 说明文本
    info_text = f"""
布局系统特性验证：
• 8px网格对齐: 所有间距都是8的倍数（除了4px的xs间距）
• 组件间距优化: 按钮组{get_component_spacing('button_group')}px，区域间距{get_component_spacing('section')}px
• 视觉层次改进: 通过间距创建清晰的视觉分组
• 响应式布局: 窗口大小变化时自动调整间距
• 网格对齐: 所有元素位置都对齐到8px网格

测试说明：
• 调整窗口大小观察响应式效果
• 检查所有间距是否符合8px网格系统
• 验证组件对齐和视觉层次
    """
    
    info_label = tk.Label(content_demo,
                         text=info_text.strip(),
                         font=theme.typography.get_font_tuple(theme.typography.size_small),
                         bg=theme.colors.secondary_bg,
                         fg=theme.colors.text_secondary,
                         justify=tk.LEFT)
    info_label.pack(padx=get_grid_aligned_spacing(16), pady=get_grid_aligned_spacing(8), anchor=tk.W)
    
    print("布局系统可视化测试窗口已启动")
    print("请调整窗口大小测试响应式布局，检查间距和对齐效果")
    root.mainloop()


def main():
    """主测试函数"""
    try:
        # 运行自动化测试
        tester = LayoutSystemTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n✅ 所有自动化测试通过！布局和间距系统验证成功。")
            
            # 询问是否运行可视化测试
            print("\n是否启动可视化测试窗口进行手动验证？(y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes', '是', '']:
                    run_layout_visual_test()
            except (EOFError, KeyboardInterrupt):
                print("\n跳过可视化测试")
            
            return True
        else:
            print("\n❌ 部分测试失败，请检查相关布局实现")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)