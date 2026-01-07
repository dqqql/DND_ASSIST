#!/usr/bin/env python3
"""
交互反馈增强测试
验证所有可点击元素的即时视觉反馈、hover状态和焦点指示器
"""

import tkinter as tk
import sys
import traceback
from theme_system import get_theme_manager
from theme_utils import (
    create_themed_button, 
    create_enhanced_listbox,
    apply_enhanced_interaction_feedback,
    enhance_category_button_feedback,
    update_category_button_states
)
from theme_integration import integrate_theme_with_app


class InteractionFeedbackTester:
    """交互反馈测试器"""
    
    def __init__(self):
        self.test_results = []
        self.theme_manager = get_theme_manager()
        
    def run_all_tests(self):
        """运行所有测试"""
        print("开始交互反馈增强测试...")
        print("=" * 50)
        
        # 测试按钮交互反馈
        self.test_button_interaction_feedback()
        
        # 测试列表交互反馈
        self.test_list_interaction_feedback()
        
        # 测试焦点指示器
        self.test_focus_indicators()
        
        # 测试分类按钮状态管理
        self.test_category_button_states()
        
        # 测试全局交互反馈应用
        self.test_global_feedback_application()
        
        # 输出测试结果
        self.print_test_results()
        
        return all(result['passed'] for result in self.test_results)
    
    def test_button_interaction_feedback(self):
        """测试按钮交互反馈"""
        print("测试 1: 按钮即时视觉反馈")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建测试按钮
            button = create_themed_button(test_window, text="测试按钮")
            
            # 应用增强交互反馈
            apply_enhanced_interaction_feedback(test_window)
            
            # 验证按钮配置
            theme = self.theme_manager.get_current_theme()
            
            # 检查基本样式属性
            bg_color = button.cget('bg')
            cursor = button.cget('cursor')
            highlight_thickness = button.cget('highlightthickness')
            
            assert bg_color == theme.colors.button_normal, f"按钮背景色不正确: {bg_color}"
            assert cursor == "hand2", f"按钮光标样式不正确: {cursor}"
            assert highlight_thickness >= 1, f"按钮边框厚度不正确: {highlight_thickness}"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '按钮即时视觉反馈',
                'passed': True,
                'message': '按钮交互反馈正确实现'
            })
            print("✓ 按钮交互反馈测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '按钮即时视觉反馈',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 按钮交互反馈测试失败: {str(e)}")
    
    def test_list_interaction_feedback(self):
        """测试列表交互反馈"""
        print("测试 2: 列表hover状态和选择反馈")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建增强列表
            listbox = create_enhanced_listbox(test_window)
            
            # 验证列表配置
            theme = self.theme_manager.get_current_theme()
            
            cursor = listbox.cget('cursor')
            highlight_color = listbox.cget('highlightcolor')
            select_bg = listbox.cget('selectbackground')
            
            assert cursor == "hand2", f"列表光标样式不正确: {cursor}"
            assert highlight_color == theme.colors.focus_color, f"列表焦点颜色不正确: {highlight_color}"
            assert select_bg == theme.colors.selection_bg, f"列表选择背景不正确: {select_bg}"
            
            # 测试列表项添加
            test_items = ["测试项目1", "测试项目2", "测试项目3"]
            for item in test_items:
                listbox.insert(tk.END, item)
            
            assert listbox.size() == len(test_items), f"列表项数量不正确"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '列表hover状态和选择反馈',
                'passed': True,
                'message': '列表交互反馈正确实现'
            })
            print("✓ 列表交互反馈测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '列表hover状态和选择反馈',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 列表交互反馈测试失败: {str(e)}")
    
    def test_focus_indicators(self):
        """测试焦点指示器清晰可见性"""
        print("测试 3: 焦点指示器清晰可见性")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建各种控件
            button = create_themed_button(test_window, text="测试按钮")
            entry = tk.Entry(test_window)
            text = tk.Text(test_window, height=3)
            listbox = create_enhanced_listbox(test_window)
            
            # 应用增强交互反馈
            apply_enhanced_interaction_feedback(test_window)
            
            theme = self.theme_manager.get_current_theme()
            
            # 验证焦点指示器配置
            widgets_to_test = [button, entry, text, listbox]
            
            for widget in widgets_to_test:
                try:
                    highlight_color = widget.cget('highlightcolor')
                    highlight_bg = widget.cget('highlightbackground')
                    
                    # 焦点颜色应该是主题定义的焦点色
                    assert highlight_color in [theme.colors.focus_color, theme.colors.border_color], \
                        f"控件 {widget.__class__.__name__} 焦点颜色不正确: {highlight_color}"
                    
                except tk.TclError:
                    # 某些控件可能不支持这些属性
                    pass
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '焦点指示器清晰可见性',
                'passed': True,
                'message': '所有控件的焦点指示器正确配置'
            })
            print("✓ 焦点指示器测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '焦点指示器清晰可见性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 焦点指示器测试失败: {str(e)}")
    
    def test_category_button_states(self):
        """测试分类按钮状态管理"""
        print("测试 4: 分类按钮激活状态管理")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建分类按钮
            categories = {"人物卡": "characters", "怪物卡": "monsters", "地图": "maps"}
            buttons = {}
            
            for name in categories:
                btn = create_themed_button(test_window, text=name)
                buttons[name] = btn
            
            # 为分类按钮添加增强反馈
            handlers = enhance_category_button_feedback(buttons)
            
            # 验证处理器创建
            assert len(handlers) == len(buttons), "处理器数量与按钮数量不匹配"
            
            # 测试状态更新
            update_category_button_states(handlers, "人物卡")
            
            # 验证激活状态
            for name, handler in handlers.items():
                expected_active = (name == "人物卡")
                actual_active = handler.is_active()
                assert actual_active == expected_active, \
                    f"按钮 {name} 激活状态不正确: expected={expected_active}, actual={actual_active}"
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '分类按钮激活状态管理',
                'passed': True,
                'message': '分类按钮状态管理正确实现'
            })
            print("✓ 分类按钮状态管理测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '分类按钮激活状态管理',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 分类按钮状态管理测试失败: {str(e)}")
    
    def test_global_feedback_application(self):
        """测试全局交互反馈应用"""
        print("测试 5: 全局交互反馈应用")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建复杂的控件层次结构
            main_frame = tk.Frame(test_window)
            
            # 第一层控件
            button1 = tk.Button(main_frame, text="按钮1")
            listbox1 = tk.Listbox(main_frame)
            entry1 = tk.Entry(main_frame)
            
            # 第二层控件（嵌套）
            sub_frame = tk.Frame(main_frame)
            button2 = tk.Button(sub_frame, text="按钮2")
            text1 = tk.Text(sub_frame, height=2)
            
            # 应用全局交互反馈
            apply_enhanced_interaction_feedback(test_window)
            
            # 验证所有控件都有适当的配置
            interactive_widgets = [button1, button2, listbox1, entry1, text1]
            
            for widget in interactive_widgets:
                widget_class = widget.__class__.__name__
                
                # 检查光标配置（对于可点击控件）
                if widget_class in ["Button", "Listbox"]:
                    try:
                        cursor = widget.cget('cursor')
                        assert cursor == "hand2", f"{widget_class} 光标样式不正确: {cursor}"
                    except tk.TclError:
                        pass
                
                # 检查焦点指示器配置
                try:
                    highlight_thickness = widget.cget('highlightthickness')
                    assert highlight_thickness >= 1, f"{widget_class} 焦点边框厚度不正确"
                except tk.TclError:
                    pass
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '全局交互反馈应用',
                'passed': True,
                'message': '全局交互反馈正确应用到所有控件'
            })
            print("✓ 全局交互反馈应用测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '全局交互反馈应用',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 全局交互反馈应用测试失败: {str(e)}")
    
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
            print("🎉 所有交互反馈增强测试通过！")
            return True
        else:
            print("⚠️  部分测试失败，需要检查相关实现")
            return False


def run_visual_test():
    """运行可视化测试"""
    print("\n启动交互反馈可视化测试窗口...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("交互反馈增强测试 - 可视化验证")
    root.geometry("900x700")
    
    # 应用主题
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    root.configure(bg=theme.colors.primary_bg)
    
    # 创建主框架
    main_frame = tk.Frame(root, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    title_label = tk.Label(main_frame,
                          text="交互反馈增强测试",
                          font=theme.typography.get_font_tuple(theme.typography.size_title, theme.typography.weight_bold),
                          bg=theme.colors.primary_bg,
                          fg=theme.colors.text_primary)
    title_label.pack(pady=(0, 20))
    
    # 按钮测试区域
    button_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    button_label = tk.Label(button_frame,
                           text="按钮交互反馈测试 (测试hover、点击、焦点效果):",
                           font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                           bg=theme.colors.primary_bg,
                           fg=theme.colors.text_primary)
    button_label.pack(anchor=tk.W, pady=(0, 10))
    
    # 创建测试按钮
    button_test_frame = tk.Frame(button_frame, bg=theme.colors.primary_bg)
    button_test_frame.pack(fill=tk.X)
    
    normal_btn = create_themed_button(button_test_frame, text="普通按钮", width=12)
    normal_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    disabled_btn = create_themed_button(button_test_frame, text="禁用按钮", width=12, state=tk.DISABLED)
    disabled_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    action_btn = create_themed_button(button_test_frame, text="操作按钮", width=12, 
                                     command=lambda: print("按钮点击测试 - 即时反馈正常"))
    action_btn.pack(side=tk.LEFT)
    
    # 分类按钮测试区域
    category_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    category_frame.pack(fill=tk.X, pady=(0, 20))
    
    category_label = tk.Label(category_frame,
                             text="分类按钮状态管理测试 (点击切换激活状态):",
                             font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                             bg=theme.colors.primary_bg,
                             fg=theme.colors.text_primary)
    category_label.pack(anchor=tk.W, pady=(0, 10))
    
    # 创建分类按钮
    category_test_frame = tk.Frame(category_frame, bg=theme.colors.primary_bg)
    category_test_frame.pack(fill=tk.X)
    
    categories = {"人物卡": "characters", "怪物卡": "monsters", "地图": "maps", "剧情": "notes"}
    category_buttons = {}
    
    for name in categories:
        btn = create_themed_button(category_test_frame, text=name, width=10)
        btn.pack(side=tk.LEFT, padx=(0, 10))
        category_buttons[name] = btn
    
    # 为分类按钮添加状态管理
    category_handlers = enhance_category_button_feedback(category_buttons)
    
    def select_category(name):
        update_category_button_states(category_handlers, name)
        print(f"选择分类: {name} - 状态更新正常")
    
    # 绑定分类按钮命令
    for name, btn in category_buttons.items():
        btn.config(command=lambda n=name: select_category(n))
    
    # 列表测试区域
    list_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    list_label = tk.Label(list_frame,
                         text="列表交互反馈测试 (测试hover、选择、焦点效果):",
                         font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                         bg=theme.colors.primary_bg,
                         fg=theme.colors.text_primary)
    list_label.pack(anchor=tk.W, pady=(0, 10))
    
    # 创建测试列表
    list_test_frame = tk.Frame(list_frame, bg=theme.colors.primary_bg)
    list_test_frame.pack(fill=tk.BOTH, expand=True)
    
    test_list = create_enhanced_listbox(list_test_frame, height=8)
    test_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # 添加测试数据
    test_items = [
        "跑团：矿坑探险 (测试hover效果)",
        "跑团：城市迷雾 (测试选择反馈)", 
        "跑团：古堡之谜 (测试焦点指示器)",
        "跑团：海盗传说 (测试键盘导航)",
        "跑团：魔法学院 (测试双击反馈)",
        "跑团：龙与地下城 (测试即时反馈)",
        "跑团：星际探索 (测试视觉状态)",
        "跑团：末日求生 (测试交互体验)"
    ]
    
    for item in test_items:
        test_list.insert(tk.END, item)
    
    # 输入控件测试区域
    input_frame = tk.Frame(list_test_frame, bg=theme.colors.primary_bg)
    input_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    input_label = tk.Label(input_frame,
                          text="输入控件焦点测试:",
                          font=theme.typography.get_font_tuple(theme.typography.size_medium, theme.typography.weight_bold),
                          bg=theme.colors.primary_bg,
                          fg=theme.colors.text_primary)
    input_label.pack(anchor=tk.W, pady=(0, 10))
    
    # Entry控件
    entry_label = tk.Label(input_frame, text="文本输入:", bg=theme.colors.primary_bg, fg=theme.colors.text_primary)
    entry_label.pack(anchor=tk.W, pady=(0, 5))
    
    test_entry = tk.Entry(input_frame, width=20)
    test_entry.pack(fill=tk.X, pady=(0, 10))
    
    # Text控件
    text_label = tk.Label(input_frame, text="多行文本:", bg=theme.colors.primary_bg, fg=theme.colors.text_primary)
    text_label.pack(anchor=tk.W, pady=(0, 5))
    
    test_text = tk.Text(input_frame, height=4, width=20)
    test_text.pack(fill=tk.X)
    
    # 应用增强交互反馈到整个窗口
    apply_enhanced_interaction_feedback(root)
    
    # 说明文本
    info_text = """
测试说明：
• 测试所有按钮的hover效果、点击反馈和焦点指示器
• 测试分类按钮的激活状态切换
• 测试列表的hover反馈、选择效果和键盘导航
• 测试输入控件的焦点指示器清晰度
• 验证所有交互元素的即时视觉反馈
• 确保焦点指示器在所有控件上都清晰可见
    """
    
    info_label = tk.Label(main_frame,
                         text=info_text.strip(),
                         font=theme.typography.get_font_tuple(theme.typography.size_small),
                         bg=theme.colors.primary_bg,
                         fg=theme.colors.text_secondary,
                         justify=tk.LEFT)
    info_label.pack(pady=(20, 0), anchor=tk.W)
    
    print("交互反馈可视化测试窗口已启动")
    print("请手动测试各控件的交互效果:")
    print("- 鼠标hover效果")
    print("- 点击反馈")
    print("- 焦点指示器")
    print("- 键盘导航")
    print("- 状态切换")
    
    root.mainloop()


def main():
    """主测试函数"""
    try:
        # 运行自动化测试
        tester = InteractionFeedbackTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n✅ 所有自动化测试通过！交互反馈增强验证成功。")
            
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
            print("\n❌ 部分测试失败，请检查相关实现")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)