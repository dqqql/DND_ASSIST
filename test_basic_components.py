#!/usr/bin/env python3
"""
基础组件样式验证测试
验证主题系统、按钮样式和列表组件的正确实现
"""

import tkinter as tk
import sys
import traceback
from theme_system import get_theme_manager, ColorPalette, Typography, Spacing
from theme_utils import (
    create_themed_button, 
    create_enhanced_listbox, 
    add_interaction_feedback,
    get_themed_colors,
    get_themed_fonts,
    get_themed_spacing
)
from theme_integration import integrate_theme_with_app, create_themed_dialog, create_themed_dialog_content


class ComponentStyleTester:
    """组件样式测试器"""
    
    def __init__(self):
        self.test_results = []
        self.theme_manager = get_theme_manager()
        
    def run_all_tests(self):
        """运行所有测试"""
        print("开始基础组件样式验证测试...")
        print("=" * 50)
        
        # 测试主题系统
        self.test_theme_system()
        
        # 测试按钮样式
        self.test_button_styles()
        
        # 测试列表组件
        self.test_list_components()
        
        # 测试颜色系统
        self.test_color_system()
        
        # 测试字体系统
        self.test_typography_system()
        
        # 测试间距系统
        self.test_spacing_system()
        
        # 输出测试结果
        self.print_test_results()
        
        return all(result['passed'] for result in self.test_results)
    
    def test_theme_system(self):
        """测试主题系统基础架构"""
        print("测试 1: 主题系统基础架构")
        
        try:
            # 验证主题管理器存在
            assert self.theme_manager is not None, "主题管理器未初始化"
            
            # 验证当前主题存在
            current_theme = self.theme_manager.get_current_theme()
            assert current_theme is not None, "当前主题未设置"
            
            # 验证主题组件存在
            assert hasattr(current_theme, 'colors'), "主题缺少颜色配置"
            assert hasattr(current_theme, 'typography'), "主题缺少字体配置"
            assert hasattr(current_theme, 'spacing'), "主题缺少间距配置"
            
            # 验证颜色配置
            colors = current_theme.colors
            required_colors = [
                'primary_bg', 'secondary_bg', 'accent_color',
                'text_primary', 'text_secondary', 'text_disabled',
                'button_normal', 'button_hover', 'button_active',
                'selection_bg', 'border_color', 'focus_color'
            ]
            
            for color_name in required_colors:
                assert hasattr(colors, color_name), f"缺少颜色配置: {color_name}"
                color_value = getattr(colors, color_name)
                assert isinstance(color_value, str), f"颜色值类型错误: {color_name}"
                assert color_value.startswith('#'), f"颜色格式错误: {color_name} = {color_value}"
            
            self.test_results.append({
                'name': '主题系统基础架构',
                'passed': True,
                'message': '所有主题组件正确初始化'
            })
            print("✓ 主题系统基础架构测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '主题系统基础架构',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 主题系统基础架构测试失败: {str(e)}")
    
    def test_button_styles(self):
        """测试按钮样式"""
        print("测试 2: 按钮和控件现代化样式")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建主题化按钮
            button = create_themed_button(test_window, text="测试按钮")
            
            # 验证按钮配置
            theme = self.theme_manager.get_current_theme()
            
            # 检查基本样式属性
            bg_color = button.cget('bg')
            fg_color = button.cget('fg')
            font = button.cget('font')
            relief = button.cget('relief')
            
            assert bg_color == theme.colors.button_normal, f"按钮背景色不正确: {bg_color} != {theme.colors.button_normal}"
            assert fg_color == theme.colors.text_primary, f"按钮文字色不正确: {fg_color} != {theme.colors.text_primary}"
            assert relief in [tk.RAISED, 'raised'], f"按钮浮雕效果不正确: {relief}"
            
            # 测试交互反馈
            handler = add_interaction_feedback(button, "button")
            assert handler is not None, "交互反馈处理器创建失败"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '按钮和控件现代化样式',
                'passed': True,
                'message': '按钮样式和交互反馈正确实现'
            })
            print("✓ 按钮样式测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '按钮和控件现代化样式',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 按钮样式测试失败: {str(e)}")
    
    def test_list_components(self):
        """测试列表和选择器组件"""
        print("测试 3: 列表和选择器优化")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建增强列表
            listbox = create_enhanced_listbox(test_window)
            
            # 验证列表配置
            theme = self.theme_manager.get_current_theme()
            
            bg_color = listbox.cget('bg')
            fg_color = listbox.cget('fg')
            select_bg = listbox.cget('selectbackground')
            select_fg = listbox.cget('selectforeground')
            font = listbox.cget('font')
            
            assert bg_color == theme.colors.secondary_bg, f"列表背景色不正确: {bg_color} != {theme.colors.secondary_bg}"
            assert fg_color == theme.colors.text_primary, f"列表文字色不正确: {fg_color} != {theme.colors.text_primary}"
            assert select_bg == theme.colors.selection_bg, f"选择背景色不正确: {select_bg} != {theme.colors.selection_bg}"
            assert select_fg == theme.colors.text_primary, f"选择文字色不正确: {select_fg} != {theme.colors.text_primary}"
            
            # 测试列表项添加
            test_items = ["测试项目1", "测试项目2", "测试项目3"]
            for item in test_items:
                listbox.insert(tk.END, item)
            
            assert listbox.size() == len(test_items), f"列表项数量不正确: {listbox.size()} != {len(test_items)}"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '列表和选择器优化',
                'passed': True,
                'message': '列表组件样式和功能正确实现'
            })
            print("✓ 列表组件测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '列表和选择器优化',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 列表组件测试失败: {str(e)}")
    
    def test_color_system(self):
        """测试颜色系统一致性"""
        print("测试 4: 颜色系统一致性")
        
        try:
            colors = get_themed_colors()
            
            # 验证所有必需的颜色都存在
            required_colors = [
                'primary_bg', 'secondary_bg', 'accent_color',
                'text_primary', 'text_secondary', 'text_disabled',
                'button_normal', 'button_hover', 'button_active',
                'selection_bg', 'border_color', 'focus_color',
                'content_bg', 'content_border'
            ]
            
            for color_name in required_colors:
                assert color_name in colors, f"缺少颜色定义: {color_name}"
                color_value = colors[color_name]
                assert isinstance(color_value, str), f"颜色值类型错误: {color_name}"
                assert color_value.startswith('#'), f"颜色格式错误: {color_name} = {color_value}"
                assert len(color_value) in [4, 7], f"颜色长度错误: {color_name} = {color_value}"
            
            self.test_results.append({
                'name': '颜色系统一致性',
                'passed': True,
                'message': '所有颜色定义正确且格式一致'
            })
            print("✓ 颜色系统测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '颜色系统一致性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 颜色系统测试失败: {str(e)}")
    
    def test_typography_system(self):
        """测试字体系统统一性"""
        print("测试 5: 字体系统统一性")
        
        try:
            fonts = get_themed_fonts()
            
            # 验证所有必需的字体都存在
            required_fonts = [
                'normal', 'small', 'medium', 'large', 'title',
                'monospace', 'monospace_small'
            ]
            
            for font_name in required_fonts:
                assert font_name in fonts, f"缺少字体定义: {font_name}"
                font_tuple = fonts[font_name]
                assert isinstance(font_tuple, tuple), f"字体格式错误: {font_name}"
                assert len(font_tuple) >= 2, f"字体元组长度不足: {font_name}"
                assert isinstance(font_tuple[1], int), f"字体大小类型错误: {font_name}"
                assert font_tuple[1] > 0, f"字体大小无效: {font_name}"
            
            self.test_results.append({
                'name': '字体系统统一性',
                'passed': True,
                'message': '所有字体定义正确且格式统一'
            })
            print("✓ 字体系统测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '字体系统统一性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 字体系统测试失败: {str(e)}")
    
    def test_spacing_system(self):
        """测试间距系统遵循性"""
        print("测试 6: 间距系统遵循性")
        
        try:
            spacing = get_themed_spacing()
            
            # 验证所有必需的间距都存在
            required_spacing = [
                'xs', 'sm', 'md', 'lg', 'xl',
                'button_padding_x', 'button_padding_y',
                'list_item_height', 'section_margin',
                'window_padding', 'panel_spacing'
            ]
            
            for spacing_name in required_spacing:
                assert spacing_name in spacing, f"缺少间距定义: {spacing_name}"
                spacing_value = spacing[spacing_name]
                assert isinstance(spacing_value, int), f"间距值类型错误: {spacing_name}"
                assert spacing_value >= 0, f"间距值无效: {spacing_name} = {spacing_value}"
            
            # 验证8px网格系统
            base_unit = 8
            grid_values = ['xs', 'sm', 'md', 'lg', 'xl']
            for value_name in grid_values:
                value = spacing[value_name]
                if value_name != 'xs':  # xs是4px，是0.5单位
                    assert value % base_unit == 0 or value == 4, f"间距值不符合8px网格: {value_name} = {value}"
            
            self.test_results.append({
                'name': '间距系统遵循性',
                'passed': True,
                'message': '所有间距定义正确且遵循8px网格系统'
            })
            print("✓ 间距系统测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '间距系统遵循性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 间距系统测试失败: {str(e)}")
    
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
            print("🎉 所有基础组件样式验证通过！")
            return True
        else:
            print("⚠️  部分测试失败，需要检查相关组件实现")
            return False


def run_visual_test():
    """运行可视化测试"""
    print("\n启动可视化测试窗口...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("基础组件样式验证 - 可视化测试")
    root.geometry("800x600")
    
    # 应用主题
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    root.configure(bg=theme.colors.primary_bg)
    
    # 创建主框架
    main_frame = tk.Frame(root, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    title_label = tk.Label(main_frame,
                          text="基础组件样式验证",
                          font=theme.typography.get_font_tuple(theme.typography.size_title, theme.typography.weight_bold),
                          bg=theme.colors.primary_bg,
                          fg=theme.colors.text_primary)
    title_label.pack(pady=(0, 20))
    
    # 按钮测试区域
    button_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    button_label = tk.Label(button_frame,
                           text="按钮样式测试:",
                           font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                           bg=theme.colors.primary_bg,
                           fg=theme.colors.text_primary)
    button_label.pack(anchor=tk.W, pady=(0, 10))
    
    # 创建测试按钮
    button_test_frame = tk.Frame(button_frame, bg=theme.colors.primary_bg)
    button_test_frame.pack(fill=tk.X)
    
    normal_btn = create_themed_button(button_test_frame, text="普通按钮", width=12)
    normal_btn.pack(side=tk.LEFT, padx=(0, 10))
    add_interaction_feedback(normal_btn, "button")
    
    disabled_btn = create_themed_button(button_test_frame, text="禁用按钮", width=12, state=tk.DISABLED)
    disabled_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    action_btn = create_themed_button(button_test_frame, text="操作按钮", width=12, 
                                     command=lambda: print("按钮点击测试"))
    action_btn.pack(side=tk.LEFT)
    add_interaction_feedback(action_btn, "button")
    
    # 列表测试区域
    list_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    list_label = tk.Label(list_frame,
                         text="列表组件测试:",
                         font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                         bg=theme.colors.primary_bg,
                         fg=theme.colors.text_primary)
    list_label.pack(anchor=tk.W, pady=(0, 10))
    
    # 创建测试列表
    test_list = create_enhanced_listbox(list_frame, height=10)
    test_list.pack(fill=tk.BOTH, expand=True)
    
    # 添加测试数据
    test_items = [
        "跑团：矿坑探险",
        "跑团：城市迷雾", 
        "跑团：古堡之谜",
        "跑团：海盗传说",
        "跑团：魔法学院",
        "跑团：龙与地下城",
        "跑团：星际探索",
        "跑团：末日求生"
    ]
    
    for item in test_items:
        test_list.insert(tk.END, item)
    
    # 说明文本
    info_text = """
测试说明：
• 测试按钮的hover效果、点击反馈和禁用状态
• 测试列表的选择效果、hover反馈和焦点指示器
• 验证颜色、字体和间距的一致性
• 所有组件应遵循统一的视觉主题
    """
    
    info_label = tk.Label(main_frame,
                         text=info_text.strip(),
                         font=theme.typography.get_font_tuple(theme.typography.size_small),
                         bg=theme.colors.primary_bg,
                         fg=theme.colors.text_secondary,
                         justify=tk.LEFT)
    info_label.pack(pady=(20, 0), anchor=tk.W)
    
    print("可视化测试窗口已启动，请手动测试各组件的交互效果")
    root.mainloop()


def main():
    """主测试函数"""
    try:
        # 运行自动化测试
        tester = ComponentStyleTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n✅ 所有自动化测试通过！基础组件样式验证成功。")
            
            # 询问是否运行可视化测试
            print("\n是否启动可视化测试窗口进行手动验证？(y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes', '是', '']:
                    run_visual_test()
            except (EOFError, KeyboardInterrupt):
                print("\n跳过可视化测试")
            
            return True
        else:
            print("\n❌ 部分测试失败，请检查相关组件实现")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)