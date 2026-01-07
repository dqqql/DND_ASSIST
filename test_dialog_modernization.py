#!/usr/bin/env python3
"""
对话框现代化测试
验证所有对话框和弹窗的现代化样式实现
"""

import tkinter as tk
import sys
import traceback
from theme_integration import (
    create_themed_dialog, create_themed_dialog_content,
    create_themed_message_dialog, show_themed_info, show_themed_error,
    show_themed_warning, ask_themed_yesno
)
from theme_system import get_theme_manager


class DialogModernizationTester:
    """对话框现代化测试器"""
    
    def __init__(self):
        self.test_results = []
        self.theme_manager = get_theme_manager()
        
    def run_all_tests(self):
        """运行所有测试"""
        print("开始对话框现代化验证测试...")
        print("=" * 50)
        
        # 测试输入对话框
        self.test_input_dialog()
        
        # 测试消息对话框
        self.test_message_dialogs()
        
        # 测试对话框样式一致性
        self.test_dialog_consistency()
        
        # 输出测试结果
        self.print_test_results()
        
        return all(result['passed'] for result in self.test_results)
    
    def test_input_dialog(self):
        """测试输入对话框"""
        print("测试 1: 输入对话框现代化")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 创建主题化对话框
            dialog = create_themed_dialog(test_window, "测试对话框", "450x180")
            
            # 验证对话框基本属性
            theme = self.theme_manager.get_current_theme()
            
            # 检查背景色
            bg_color = dialog.cget('bg')
            assert bg_color == theme.colors.primary_bg, f"对话框背景色不正确: {bg_color} != {theme.colors.primary_bg}"
            
            # 检查对话框属性
            assert dialog.winfo_class() == 'Toplevel', "对话框类型不正确"
            assert dialog.transient() is not None, "对话框未设置为临时窗口"
            
            # 创建对话框内容
            main_frame, entry, ok_button, cancel_button = create_themed_dialog_content(
                dialog, "请输入测试内容:", 35
            )
            
            # 验证输入框样式
            entry_bg = entry.cget('bg')
            entry_fg = entry.cget('fg')
            assert entry_bg == theme.colors.secondary_bg, f"输入框背景色不正确: {entry_bg} != {theme.colors.secondary_bg}"
            assert entry_fg == theme.colors.text_primary, f"输入框文字色不正确: {entry_fg} != {theme.colors.text_primary}"
            
            # 验证按钮样式
            ok_bg = ok_button.cget('bg')
            cancel_bg = cancel_button.cget('bg')
            assert ok_bg == theme.colors.button_normal, f"确定按钮背景色不正确: {ok_bg} != {theme.colors.button_normal}"
            assert cancel_bg == theme.colors.button_normal, f"取消按钮背景色不正确: {cancel_bg} != {theme.colors.button_normal}"
            
            dialog.destroy()
            test_window.destroy()
            
            self.test_results.append({
                'name': '输入对话框现代化',
                'passed': True,
                'message': '输入对话框样式和布局正确实现'
            })
            print("✓ 输入对话框测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '输入对话框现代化',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 输入对话框测试失败: {str(e)}")
    
    def test_message_dialogs(self):
        """测试消息对话框"""
        print("测试 2: 消息对话框现代化")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            # 测试不同类型的消息对话框创建（不显示）
            dialog_types = ["info", "error", "warning", "question"]
            
            for dialog_type in dialog_types:
                # 创建对话框但立即销毁（测试创建过程）
                dialog = create_themed_dialog(test_window, f"测试{dialog_type}对话框", "400x200")
                
                # 验证基本属性
                theme = self.theme_manager.get_current_theme()
                bg_color = dialog.cget('bg')
                assert bg_color == theme.colors.primary_bg, f"{dialog_type}对话框背景色不正确"
                
                dialog.destroy()
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '消息对话框现代化',
                'passed': True,
                'message': '所有类型的消息对话框创建成功'
            })
            print("✓ 消息对话框测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '消息对话框现代化',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 消息对话框测试失败: {str(e)}")
    
    def test_dialog_consistency(self):
        """测试对话框样式一致性"""
        print("测试 3: 对话框样式一致性")
        
        try:
            # 创建测试窗口
            test_window = tk.Tk()
            test_window.withdraw()  # 隐藏窗口
            
            theme = self.theme_manager.get_current_theme()
            
            # 测试多个对话框的样式一致性
            dialogs = []
            for i in range(3):
                dialog = create_themed_dialog(test_window, f"测试对话框{i+1}", "400x150")
                dialogs.append(dialog)
            
            # 验证所有对话框的样式一致性
            first_bg = dialogs[0].cget('bg')
            for i, dialog in enumerate(dialogs[1:], 1):
                bg_color = dialog.cget('bg')
                assert bg_color == first_bg, f"对话框{i+1}背景色与第一个对话框不一致"
                assert bg_color == theme.colors.primary_bg, f"对话框{i+1}背景色不符合主题"
            
            # 清理对话框
            for dialog in dialogs:
                dialog.destroy()
            
            test_window.destroy()
            
            self.test_results.append({
                'name': '对话框样式一致性',
                'passed': True,
                'message': '所有对话框样式保持一致'
            })
            print("✓ 对话框一致性测试通过")
            
        except Exception as e:
            self.test_results.append({
                'name': '对话框样式一致性',
                'passed': False,
                'message': f'测试失败: {str(e)}'
            })
            print(f"✗ 对话框一致性测试失败: {str(e)}")
    
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
            print("🎉 所有对话框现代化验证通过！")
            return True
        else:
            print("⚠️  部分测试失败，需要检查相关对话框实现")
            return False


def run_visual_dialog_test():
    """运行对话框可视化测试"""
    print("\n启动对话框可视化测试...")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("对话框现代化验证 - 可视化测试")
    root.geometry("600x400")
    
    # 应用主题
    theme_manager = get_theme_manager()
    theme = theme_manager.get_current_theme()
    root.configure(bg=theme.colors.primary_bg)
    
    # 创建主框架
    main_frame = tk.Frame(root, bg=theme.colors.primary_bg)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    title_label = tk.Label(main_frame,
                          text="对话框现代化验证",
                          font=theme.typography.get_font_tuple(theme.typography.size_title, theme.typography.weight_bold),
                          bg=theme.colors.primary_bg,
                          fg=theme.colors.text_primary)
    title_label.pack(pady=(0, 20))
    
    # 输入对话框测试
    def test_input_dialog():
        dialog = create_themed_dialog(root, "新建跑团", "450x180")
        main_frame, entry, ok_button, cancel_button = create_themed_dialog_content(
            dialog, "请输入跑团名称:", 35
        )
        
        def on_ok():
            print(f"输入内容: {entry.get()}")
            dialog.destroy()
        
        def on_cancel():
            print("取消输入")
            dialog.destroy()
        
        ok_button.config(command=on_ok)
        cancel_button.config(command=on_cancel)
        entry.bind("<Return>", lambda e: on_ok())
    
    # 消息对话框测试
    def test_info_dialog():
        show_themed_info(root, "信息", "这是一个信息对话框测试")
    
    def test_error_dialog():
        show_themed_error(root, "错误", "这是一个错误对话框测试")
    
    def test_warning_dialog():
        show_themed_warning(root, "警告", "这是一个警告对话框测试")
    
    def test_question_dialog():
        result = ask_themed_yesno(root, "确认", "这是一个确认对话框测试\n您确定要继续吗？")
        print(f"用户选择: {'是' if result else '否'}")
    
    # 创建测试按钮
    from theme_utils import create_themed_button, add_interaction_feedback
    
    button_frame = tk.Frame(main_frame, bg=theme.colors.primary_bg)
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    buttons = [
        ("测试输入对话框", test_input_dialog),
        ("测试信息对话框", test_info_dialog),
        ("测试错误对话框", test_error_dialog),
        ("测试警告对话框", test_warning_dialog),
        ("测试确认对话框", test_question_dialog)
    ]
    
    for i, (text, command) in enumerate(buttons):
        btn = create_themed_button(button_frame, text=text, width=15, command=command)
        btn.pack(pady=5)
        add_interaction_feedback(btn, "button")
    
    # 说明文本
    info_text = """
测试说明：
• 点击按钮测试不同类型的对话框
• 验证对话框的居中定位和尺寸
• 检查按钮样式与主界面的一致性
• 测试对话框的交互反馈和键盘操作
    """
    
    info_label = tk.Label(main_frame,
                         text=info_text.strip(),
                         font=theme.typography.get_font_tuple(theme.typography.size_small),
                         bg=theme.colors.primary_bg,
                         fg=theme.colors.text_secondary,
                         justify=tk.LEFT)
    info_label.pack(pady=(20, 0), anchor=tk.W)
    
    print("对话框可视化测试窗口已启动，请点击按钮测试各种对话框")
    root.mainloop()


def main():
    """主测试函数"""
    try:
        # 运行自动化测试
        tester = DialogModernizationTester()
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n✅ 所有自动化测试通过！对话框现代化验证成功。")
            
            # 询问是否运行可视化测试
            print("\n是否启动可视化测试窗口进行手动验证？(y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes', '是', '']:
                    run_visual_dialog_test()
            except (EOFError, KeyboardInterrupt):
                print("\n跳过可视化测试")
            
            return True
        else:
            print("\n❌ 部分测试失败，请检查相关对话框实现")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)