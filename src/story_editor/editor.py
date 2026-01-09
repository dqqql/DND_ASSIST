import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os

TEMPLATE = {
    "title": "新剧情",
    "nodes": []
}

# 数据目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")


class StoryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("剧情编辑器 (Legacy) - Story Editor")
        self.root.geometry("1200x700")
        
        # Legacy 编辑器标识
        self._is_legacy_editor = True
        
        # 设置窗口图标和样式
        self.setup_styles()

        self.data = TEMPLATE.copy()
        self.current_node = None
        self.file_path = None
        self.campaigns = self.get_available_campaigns()
        self.unsaved_changes = False
        self._loading_branch = False  # 标志是否正在加载分支数据
        self._previous_branch_index = None  # 记录上一个选择的分支索引

        self.build_ui()
        self.update_title()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """设置UI样式"""
        style = ttk.Style()
        
        # 配置按钮样式
        style.configure("Action.TButton", padding=(10, 5))
        style.configure("Primary.TButton", padding=(15, 8))
        
        # 配置标签样式
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Section.TLabel", font=("Arial", 10, "bold"))

    def build_ui(self):
        # 创建主菜单
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主要内容区域
        self.create_main_content()
        
        # 创建状态栏
        self.create_status_bar()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建剧情", command=self.new_story, accelerator="Ctrl+N")
        file_menu.add_command(label="打开剧情", command=self.load_story, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="保存到跑团", command=self.save_to_campaign, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="添加节点", command=self.add_node, accelerator="Ctrl+A")
        edit_menu.add_command(label="删除节点", command=self.delete_node, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="添加分支", command=self.add_branch, accelerator="Ctrl+B")
        
        # 绑定快捷键
        self.root.bind('<Control-n>', lambda e: self.new_story())
        self.root.bind('<Control-o>', lambda e: self.load_story())
        self.root.bind('<Control-s>', lambda e: self.save_story())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_to_campaign())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-a>', lambda e: self.add_node())
        self.root.bind('<Delete>', lambda e: self.delete_node())
        self.root.bind('<Control-b>', lambda e: self.add_branch())

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Legacy 编辑器提示
        legacy_frame = ttk.Frame(toolbar)
        legacy_frame.pack(fill=tk.X, pady=(0, 5))
        
        legacy_label = ttk.Label(legacy_frame, 
                                text="⚠️ Legacy 编辑器 - 仅用于基础维护和应急修改，推荐使用新的 Web 编辑器",
                                foreground="orange", font=("Arial", 9, "bold"))
        legacy_label.pack(side=tk.LEFT)
        
        # 文件操作按钮
        ttk.Button(toolbar, text="新建", command=self.new_story, 
                  style="Action.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="打开", command=self.load_story, 
                  style="Action.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="保存", command=self.save_story, 
                  style="Action.TButton").pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 编辑操作按钮
        ttk.Button(toolbar, text="添加节点", command=self.add_node, 
                  style="Action.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除节点", command=self.delete_node, 
                  style="Action.TButton").pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 剧情标题编辑
        ttk.Label(toolbar, text="剧情标题:", style="Section.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.title_var = tk.StringVar()
        self.title_var.set(self.data.get("title", ""))
        self.title_var.trace('w', self.on_title_change)
        title_entry = ttk.Entry(toolbar, textvariable=self.title_var, width=20)
        title_entry.pack(side=tk.LEFT, padx=2)
        


    def create_main_content(self):
        """创建主要内容区域"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：节点列表区域
        self.create_node_list_panel(main_frame)
        
        # 中间：节点编辑区域
        self.create_node_edit_panel(main_frame)
        
        # 右侧：分支编辑区域
        self.create_branch_edit_panel(main_frame)

    def create_node_list_panel(self, parent):
        """创建节点列表面板"""
        # 左侧面板
        left_panel = ttk.LabelFrame(parent, text="节点列表", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 节点列表
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.node_list = tk.Listbox(list_frame, width=25, font=("Consolas", 10))
        scrollbar_nodes = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.node_list.yview)
        self.node_list.config(yscrollcommand=scrollbar_nodes.set)
        
        self.node_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_nodes.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.node_list.bind("<<ListboxSelect>>", self.on_select_node)
        self.node_list.bind("<Double-Button-1>", self.on_double_click_node)
        
        # 节点操作按钮
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="添加主线节点", 
                  command=lambda: self.add_node("main")).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="添加分支节点", 
                  command=lambda: self.add_node("branch")).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="删除选中节点", 
                  command=self.delete_node).pack(fill=tk.X, pady=2)
        
        # 节点排序按钮
        sort_frame = ttk.Frame(left_panel)
        sort_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(sort_frame, text="↑", command=self.move_node_up, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_frame, text="↓", command=self.move_node_down, width=3).pack(side=tk.LEFT, padx=2)

    def create_node_edit_panel(self, parent):
        """创建节点编辑面板"""
        # 中间面板
        middle_panel = ttk.LabelFrame(parent, text="节点编辑", padding=10)
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 创建滚动区域
        canvas = tk.Canvas(middle_panel)
        scrollbar = ttk.Scrollbar(middle_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 节点编辑表单
        form = ttk.Frame(scrollable_frame)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID字段
        ttk.Label(form, text="节点ID:", style="Section.TLabel").grid(row=0, column=0, sticky="nw", pady=5)
        self.id_entry = ttk.Entry(form, width=30)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.id_entry.bind('<KeyRelease>', self.on_node_change)
        
        # 类型字段
        ttk.Label(form, text="节点类型:", style="Section.TLabel").grid(row=1, column=0, sticky="nw", pady=5)
        self.type_box = ttk.Combobox(form, values=["main", "branch"], state="readonly", width=28)
        self.type_box.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.type_box.bind('<<ComboboxSelected>>', self.on_type_change)
        
        # 标题字段
        ttk.Label(form, text="节点标题:", style="Section.TLabel").grid(row=2, column=0, sticky="nw", pady=5)
        self.title_entry = ttk.Entry(form, width=30)
        self.title_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.title_entry.bind('<KeyRelease>', self.on_node_change)
        
        # 下一个节点字段
        ttk.Label(form, text="下一个节点:", style="Section.TLabel").grid(row=3, column=0, sticky="nw", pady=5)
        self.next_entry = ttk.Combobox(form, width=28, state="readonly")
        self.next_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.next_entry.bind('<<ComboboxSelected>>', self.on_node_change)
        
        # 内容字段
        ttk.Label(form, text="节点内容:", style="Section.TLabel").grid(row=4, column=0, sticky="nw", pady=5)
        
        text_frame = ttk.Frame(form)
        text_frame.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.content_text = tk.Text(text_frame, height=8, width=40, wrap=tk.WORD)
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.config(yscrollcommand=text_scrollbar.set)
        
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.content_text.bind('<KeyRelease>', self.on_node_change)
        
        # 保存按钮
        save_frame = ttk.Frame(form)
        save_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(save_frame, text="保存节点修改", command=self.save_node, 
                  style="Primary.TButton").pack()
        
        form.columnconfigure(1, weight=1)
        
        # 配置滚动
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

    def create_branch_edit_panel(self, parent):
        """创建分支编辑面板"""
        # 右侧面板
        self.branch_frame = ttk.LabelFrame(parent, text="分支编辑（仅主线节点）", padding=10)
        self.branch_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # 分支列表
        list_frame = ttk.Frame(self.branch_frame)
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(list_frame, text="分支列表:", style="Section.TLabel").pack(anchor="w")
        
        branch_list_frame = ttk.Frame(list_frame)
        branch_list_frame.pack(fill=tk.X, pady=5)
        
        self.branch_list = tk.Listbox(branch_list_frame, height=8, width=25)
        branch_scrollbar = ttk.Scrollbar(branch_list_frame, orient=tk.VERTICAL, command=self.branch_list.yview)
        self.branch_list.config(yscrollcommand=branch_scrollbar.set)
        
        self.branch_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        branch_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.branch_list.bind("<<ListboxSelect>>", self.on_select_branch)
        
        # 分支操作按钮
        branch_btn_frame = ttk.Frame(list_frame)
        branch_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(branch_btn_frame, text="添加分支", command=self.add_branch).pack(fill=tk.X, pady=2)
        ttk.Button(branch_btn_frame, text="删除分支", command=self.delete_branch).pack(fill=tk.X, pady=2)
        
        # 分支编辑表单
        form_frame = ttk.Frame(self.branch_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="分支编辑:", style="Section.TLabel").pack(anchor="w")
        
        # 选项文本
        ttk.Label(form_frame, text="选项文本:").pack(anchor="w", pady=(10, 2))
        self.branch_choice = ttk.Entry(form_frame, width=25)
        self.branch_choice.pack(fill=tk.X, pady=2)
        self.branch_choice.bind('<KeyRelease>', self.on_branch_change)
        
        # 入口节点
        ttk.Label(form_frame, text="入口节点:").pack(anchor="w", pady=(10, 2))
        self.branch_entry = ttk.Combobox(form_frame, state="readonly", width=23)
        self.branch_entry.pack(fill=tk.X, pady=2)
        self.branch_entry.bind('<<ComboboxSelected>>', self.on_branch_change)
        
        # 回归节点
        ttk.Label(form_frame, text="回归节点:").pack(anchor="w", pady=(10, 2))
        self.branch_exit = ttk.Combobox(form_frame, state="readonly", width=23)
        self.branch_exit.pack(fill=tk.X, pady=2)
        self.branch_exit.bind('<<ComboboxSelected>>', self.on_branch_change)
        


    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 节点计数
        self.node_count_label = ttk.Label(self.status_bar, text="节点: 0")
        self.node_count_label.pack(side=tk.RIGHT, padx=5, pady=2)

    # ---------- UI事件处理 ----------

    def on_title_change(self, *args):
        """剧情标题改变事件"""
        self.data["title"] = self.title_var.get()
        self.mark_unsaved()
        self.update_title()

    def on_node_change(self, event=None):
        """节点内容改变事件"""
        self.mark_unsaved()

    def on_type_change(self, event=None):
        """节点类型改变事件"""
        if self.current_node:
            node_type = self.type_box.get()
            if node_type == "branch":
                # 分支节点不能有分支
                self.current_node.pop("branches", None)
                self.refresh_branches()
            elif node_type == "main":
                # 主线节点确保有分支列表
                self.current_node.setdefault("branches", [])
                self.refresh_branches()
        self.mark_unsaved()

    def on_branch_change(self, event=None):
        """分支内容改变事件"""
        # 只在不是加载状态时才自动保存
        if not getattr(self, '_loading_branch', False) and self.branch_list.curselection():
            self.auto_save_current_branch()
        self.mark_unsaved()

    def auto_save_current_branch(self):
        """自动保存当前编辑的分支"""
        if not self.branch_list.curselection() or not self.current_node:
            return
        
        idx = self.branch_list.curselection()[0]
        if "branches" not in self.current_node or idx >= len(self.current_node["branches"]):
            return
            
        branch = self.current_node["branches"][idx]
        
        # 获取当前编辑区的值
        choice = self.branch_choice.get().strip()
        entry = self.branch_entry.get()
        exit_node = self.branch_exit.get()
        
        # 更新分支数据
        branch["choice"] = choice if choice else f"分支{idx+1}"
        branch["entry"] = entry
        branch["exit"] = exit_node
        
        # 刷新显示但保持选中状态
        selected_idx = idx
        self.refresh_branches()
        if selected_idx < self.branch_list.size():
            self.branch_list.selection_set(selected_idx)

    def on_double_click_node(self, event):
        """双击节点事件 - 快速编辑标题"""
        if self.current_node:
            self.title_entry.focus_set()
            self.title_entry.select_range(0, tk.END)

    def on_select_branch(self, event):
        """选择分支事件"""
        # 先保存之前选择的分支（如果有的话）
        if hasattr(self, '_previous_branch_index') and self._previous_branch_index is not None:
            self.save_previous_branch(self._previous_branch_index)
        
        if not self.branch_list.curselection():
            self._previous_branch_index = None
            return
        
        idx = self.branch_list.curselection()[0]
        self._previous_branch_index = idx
        
        if self.current_node and "branches" in self.current_node:
            branch = self.current_node["branches"][idx]
            
            # 临时禁用自动保存，避免在加载数据时触发
            self._loading_branch = True
            
            # 加载分支数据到编辑区
            self.branch_choice.delete(0, tk.END)
            self.branch_choice.insert(0, branch.get("choice", ""))
            
            self.branch_entry.set(branch.get("entry", ""))
            self.branch_exit.set(branch.get("exit", ""))
            
            # 重新启用自动保存
            self._loading_branch = False

    def save_previous_branch(self, idx):
        """保存之前编辑的分支"""
        if not self.current_node or "branches" not in self.current_node:
            return
        
        if idx >= len(self.current_node["branches"]):
            return
            
        branch = self.current_node["branches"][idx]
        
        # 获取当前编辑区的值
        choice = self.branch_choice.get().strip()
        entry = self.branch_entry.get()
        exit_node = self.branch_exit.get()
        
        # 更新分支数据
        branch["choice"] = choice if choice else f"分支{idx+1}"
        branch["entry"] = entry
        branch["exit"] = exit_node
        
        # 刷新显示
        self.refresh_branches()
        self.mark_unsaved()

    def on_closing(self):
        """窗口关闭事件"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "未保存的更改", 
                "有未保存的更改，是否保存？\n\n是：保存并退出\n否：不保存直接退出\n取消：返回编辑"
            )
            if result is True:  # 保存并退出
                if self.save_story():
                    self.root.destroy()
            elif result is False:  # 不保存直接退出
                self.root.destroy()
            # 取消则什么都不做
        else:
            self.root.destroy()

    def mark_unsaved(self):
        """标记为未保存状态"""
        self.unsaved_changes = True
        self.update_title()
        self.update_status("已修改")

    def mark_saved(self):
        """标记为已保存状态"""
        self.unsaved_changes = False
        self.update_title()
        self.update_status("已保存")

    def update_title(self):
        """更新窗口标题"""
        title = "剧情编辑器"
        story_title = self.data.get("title", "")
        if story_title and story_title != "新剧情":
            title += f" - {story_title}"
        
        if self.file_path:
            filename = os.path.basename(self.file_path)
            title += f" ({filename})"
        
        if self.unsaved_changes:
            title += " *"
        
        self.root.title(title)

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        
        # 更新节点计数
        node_count = len(self.data.get("nodes", []))
        main_count = len([n for n in self.data.get("nodes", []) if n.get("type") == "main"])
        branch_count = len([n for n in self.data.get("nodes", []) if n.get("type") == "branch"])
        
        self.node_count_label.config(text=f"节点: {node_count} (主线: {main_count}, 分支: {branch_count})")

    def move_node_up(self):
        """上移节点"""
        if not self.node_list.curselection():
            return
        
        idx = self.node_list.curselection()[0]
        if idx > 0:
            # 交换节点位置
            self.data["nodes"][idx], self.data["nodes"][idx-1] = \
                self.data["nodes"][idx-1], self.data["nodes"][idx]
            
            self.refresh_node_list()
            self.node_list.selection_set(idx-1)
            self.mark_unsaved()

    def move_node_down(self):
        """下移节点"""
        if not self.node_list.curselection():
            return
        
        idx = self.node_list.curselection()[0]
        if idx < len(self.data["nodes"]) - 1:
            # 交换节点位置
            self.data["nodes"][idx], self.data["nodes"][idx+1] = \
                self.data["nodes"][idx+1], self.data["nodes"][idx]
            
            self.refresh_node_list()
            self.node_list.selection_set(idx+1)
            self.mark_unsaved()

    # ---------- 通用方法 ----------

    def refresh_node_list(self):
        """刷新节点列表显示"""
        self.node_list.delete(0, tk.END)
        for i, n in enumerate(self.data["nodes"]):
            node_type = n.get("type", "main")
            node_id = n.get("id", f"node_{i+1}")
            node_title = n.get("title", "未命名")
            
            # 使用不同的图标表示节点类型
            icon = "●" if node_type == "main" else "○"
            display_text = f"{icon} {node_id}: {node_title}"
            
            self.node_list.insert(tk.END, display_text)

        # 更新下拉框选项
        ids = [n["id"] for n in self.data["nodes"]]
        self.next_entry["values"] = [""] + ids
        self.branch_entry["values"] = ids
        self.branch_exit["values"] = ids
        
        # 更新状态
        self.update_status("节点列表已刷新")

    def on_select_node(self, event):
        """选择节点事件"""
        # 先保存当前分支的修改（如果有的话）
        if hasattr(self, '_previous_branch_index') and self._previous_branch_index is not None:
            self.save_previous_branch(self._previous_branch_index)
        
        if not self.node_list.curselection():
            return
        idx = self.node_list.curselection()[0]
        self.current_node = self.data["nodes"][idx]
        self.load_node()
        self.refresh_branches()
        
        # 重置分支选择状态
        self._previous_branch_index = None
        
        self.update_status(f"已选择节点: {self.current_node.get('id', '')}")

    def load_node(self):
        """加载节点数据到编辑区"""
        if not self.current_node:
            return
            
        n = self.current_node
        
        # 加载基本信息
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, n.get("id", ""))

        self.type_box.set(n.get("type", "main"))

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, n.get("title", ""))

        # 加载下一个节点
        next_node = n.get("next", "")
        if next_node:
            self.next_entry.set(next_node)
        else:
            self.next_entry.set("")

        # 加载内容
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, n.get("content", ""))

    def save_node(self):
        """保存节点修改"""
        if not self.current_node:
            messagebox.showwarning("警告", "请先选择一个节点")
            return

        # 验证节点ID
        new_id = self.id_entry.get().strip()
        if not new_id:
            messagebox.showerror("错误", "节点ID不能为空")
            return
        
        # 检查ID重复（除了当前节点）
        old_id = self.current_node.get("id", "")
        if new_id != old_id:
            existing_ids = [n.get("id") for n in self.data["nodes"] if n != self.current_node]
            if new_id in existing_ids:
                messagebox.showerror("错误", f"节点ID '{new_id}' 已存在")
                return

        # 保存数据
        old_id = self.current_node.get("id", "")
        self.current_node["id"] = new_id
        self.current_node["type"] = self.type_box.get()
        self.current_node["title"] = self.title_entry.get().strip()
        
        next_value = self.next_entry.get()
        self.current_node["next"] = next_value if next_value else None
        
        self.current_node["content"] = self.content_text.get("1.0", tk.END).strip()

        # 处理分支
        if self.current_node["type"] == "main":
            self.current_node.setdefault("branches", [])
        else:
            self.current_node.pop("branches", None)

        # 如果ID改变了，更新所有引用
        if old_id != new_id:
            self.update_node_references(old_id, new_id)

        self.refresh_node_list()
        self.refresh_branches()
        self.mark_unsaved()
        self.update_status("节点已保存")

    def update_node_references(self, old_id, new_id):
        """更新节点ID引用"""
        for node in self.data["nodes"]:
            # 更新next引用
            if node.get("next") == old_id:
                node["next"] = new_id
            
            # 更新分支引用
            if "branches" in node:
                for branch in node["branches"]:
                    if branch.get("entry") == old_id:
                        branch["entry"] = new_id
                    if branch.get("exit") == old_id:
                        branch["exit"] = new_id

    # ---------- 分支相关 ----------

    def refresh_branches(self):
        """刷新分支列表"""
        # 记录当前选中的分支
        current_selection = None
        if self.branch_list.curselection():
            current_selection = self.branch_list.curselection()[0]
        
        self.branch_list.delete(0, tk.END)

        if not self.current_node or self.current_node.get("type") != "main":
            # 清空分支编辑区
            self.branch_choice.delete(0, tk.END)
            self.branch_entry.set("")
            self.branch_exit.set("")
            self._previous_branch_index = None
            return

        branches = self.current_node.get("branches", [])
        for i, b in enumerate(branches):
            choice = b.get("choice", f"分支{i+1}")
            entry = b.get("entry", "")
            exit_node = b.get("exit", "")
            display_text = f"{choice} → {entry} → {exit_node}"
            self.branch_list.insert(tk.END, display_text)
        
        # 恢复选中状态
        if current_selection is not None and current_selection < len(branches):
            self.branch_list.selection_set(current_selection)
            self._previous_branch_index = current_selection

    def add_branch(self):
        """添加分支"""
        if not self.current_node or self.current_node.get("type") != "main":
            messagebox.showwarning("警告", "只有主线节点可以添加分支")
            return

        # 先保存当前分支的修改（如果有的话）
        if hasattr(self, '_previous_branch_index') and self._previous_branch_index is not None:
            self.save_previous_branch(self._previous_branch_index)

        branch_count = len(self.current_node.get("branches", []))
        new_branch = {
            "choice": f"选择{branch_count + 1}",
            "entry": "",
            "exit": ""
        }
        
        self.current_node.setdefault("branches", []).append(new_branch)
        self.refresh_branches()
        
        # 选中新添加的分支
        new_index = len(self.current_node["branches"]) - 1
        self.branch_list.selection_set(new_index)
        self._previous_branch_index = new_index
        self.on_select_branch(None)
        
        self.mark_unsaved()
        self.update_status("已添加新分支")

    def delete_branch(self):
        """删除分支"""
        if not self.branch_list.curselection():
            messagebox.showwarning("警告", "请先选择要删除的分支")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的分支吗？"):
            idx = self.branch_list.curselection()[0]
            del self.current_node["branches"][idx]
            
            # 重置分支选择状态
            self._previous_branch_index = None
            
            self.refresh_branches()
            
            # 清空分支编辑区
            self.branch_choice.delete(0, tk.END)
            self.branch_entry.set("")
            self.branch_exit.set("")
            
            self.mark_unsaved()
            self.update_status("分支已删除")



    # ---------- 文件 ----------

    def get_available_campaigns(self):
        """获取可用的跑团列表"""
        campaigns = []
        if os.path.exists(DATA_DIR):
            for name in os.listdir(DATA_DIR):
                campaign_path = os.path.join(DATA_DIR, name)
                if os.path.isdir(campaign_path):
                    # 检查是否有notes目录
                    notes_path = os.path.join(campaign_path, "notes")
                    if os.path.exists(notes_path):
                        campaigns.append(name)
        return campaigns

    def refresh_campaigns(self):
        """刷新跑团列表"""
        self.campaigns = self.get_available_campaigns()

    def save_to_campaign(self):
        """保存剧情到指定跑团"""
        if not self.data.get("nodes"):
            messagebox.showwarning("警告", "剧情为空，请先添加节点")
            return False
        
        # 刷新跑团列表
        self.refresh_campaigns()
        
        if not self.campaigns:
            messagebox.showerror("错误", "没有找到可用的跑团\n请先在主程序中创建跑团")
            return False
        
        # 创建选择跑团的对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择跑团和剧本")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {"campaign": None, "script": None, "filename": None}
        
        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 跑团选择
        ttk.Label(main_frame, text="选择跑团:").pack(anchor="w")
        campaign_var = tk.StringVar()
        campaign_combo = ttk.Combobox(main_frame, textvariable=campaign_var, 
                                     values=self.campaigns, state="readonly")
        campaign_combo.pack(fill=tk.X, pady=(5, 15))
        if self.campaigns:
            campaign_combo.set(self.campaigns[0])
        
        # 剧本选择
        ttk.Label(main_frame, text="剧本名称:").pack(anchor="w")
        script_var = tk.StringVar()
        script_entry = ttk.Entry(main_frame, textvariable=script_var)
        script_entry.pack(fill=tk.X, pady=(5, 5))
        
        # 剧本提示
        script_hint = ttk.Label(main_frame, text="输入剧本名称（如：龙与地下城、克苏鲁的呼唤等）", 
                               foreground="gray", font=("Arial", 8))
        script_hint.pack(anchor="w", pady=(0, 15))
        
        # 文件名输入
        ttk.Label(main_frame, text="剧情文件名:").pack(anchor="w")
        filename_var = tk.StringVar()
        filename_var.set(self.data.get("title", "新剧情"))
        filename_entry = ttk.Entry(main_frame, textvariable=filename_var)
        filename_entry.pack(fill=tk.X, pady=(5, 15))
        
        # 提示信息
        info_label = ttk.Label(main_frame, text="文件将保存为 .json 格式", 
                              foreground="gray")
        info_label.pack(anchor="w", pady=(0, 15))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def on_save():
            campaign = campaign_var.get()
            script = script_var.get().strip()
            filename = filename_var.get().strip()
            
            if not campaign:
                messagebox.showerror("错误", "请选择跑团")
                return
            
            if not script:
                messagebox.showerror("错误", "请输入剧本名称")
                return
            
            if not filename:
                messagebox.showerror("错误", "请输入文件名")
                return
            
            # 检查文件名合法性
            invalid_chars = r'/\:*?"<>|'
            for char in invalid_chars:
                if char in script:
                    messagebox.showerror("错误", f"剧本名称不能包含以下字符: {invalid_chars}")
                    return
                if char in filename:
                    messagebox.showerror("错误", f"文件名不能包含以下字符: {invalid_chars}")
                    return
            
            result["campaign"] = campaign
            result["script"] = script
            result["filename"] = filename
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=on_save).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=(0, 10))
        
        # 绑定回车键
        filename_entry.bind("<Return>", lambda e: on_save())
        
        dialog.wait_window()
        
        # 执行保存
        if result["campaign"] and result["script"] and result["filename"]:
            return self._save_to_campaign_path(result["campaign"], result["script"], result["filename"])
        
        return False

    def _save_to_campaign_path(self, campaign, script, filename):
        """实际执行保存到跑团目录"""
        try:
            # 确保文件名以.json结尾
            if not filename.endswith('.json'):
                filename += '.json'
            
            # 构建保存路径
            campaign_notes_dir = os.path.join(DATA_DIR, campaign, "notes")
            if not os.path.exists(campaign_notes_dir):
                os.makedirs(campaign_notes_dir)
            
            save_path = os.path.join(campaign_notes_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(save_path):
                if not messagebox.askyesno("文件已存在", 
                                         f"文件 {filename} 已存在，是否覆盖？"):
                    return False
            
            # 确保当前编辑的节点已保存
            if self.current_node:
                self.save_node()
            
            # 保存文件
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # 注释掉output目录保存功能，因为工具链现在直接从data/campaigns读取
            # self._save_to_output_dir(campaign, script, filename)
            
            # 更新文件路径和状态
            self.file_path = save_path
            self.mark_saved()
            
            messagebox.showinfo("保存成功", 
                              f"剧情已保存到跑团【{campaign}】的剧本【{script}】\n文件路径: {save_path}")
            
            return True
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件时发生错误:\n{str(e)}")
            return False
    
    def _save_to_output_dir(self, campaign, script, filename):
        """同时保存到output目录以供工具链使用"""
        try:
            # 创建output目录结构：output/跑团名/剧本名/
            output_dir = os.path.join(BASE_DIR, "output", campaign, script)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存到output目录
            output_path = os.path.join(output_dir, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # output目录保存失败不影响主要保存流程
            print(f"Warning: Failed to save to output directory: {e}")

    def add_node(self, node_type="main"):
        """添加节点"""
        node_count = len(self.data["nodes"])
        new_node = {
            "id": f"node_{node_count + 1:02d}",
            "type": node_type,
            "title": "新节点",
            "content": "",
            "next": None
        }
        
        if node_type == "main":
            new_node["branches"] = []
        
        self.data["nodes"].append(new_node)
        self.refresh_node_list()
        
        # 选中新添加的节点
        self.node_list.selection_set(len(self.data["nodes"]) - 1)
        self.on_select_node(None)
        
        # 自动聚焦到标题编辑
        self.title_entry.focus_set()
        self.title_entry.select_range(0, tk.END)
        
        self.mark_unsaved()
        self.update_status(f"已添加新的{node_type}节点")

    def delete_node(self):
        """删除节点"""
        if not self.node_list.curselection():
            messagebox.showwarning("警告", "请先选择要删除的节点")
            return
        
        idx = self.node_list.curselection()[0]
        node = self.data["nodes"][idx]
        node_id = node.get("id", "")
        
        if messagebox.askyesno("确认删除", f"确定要删除节点 '{node_id}' 吗？\n\n注意：这将同时删除所有对该节点的引用。"):
            # 删除节点
            del self.data["nodes"][idx]
            
            # 清理引用
            self.cleanup_node_references(node_id)
            
            self.current_node = None
            self.refresh_node_list()
            self.refresh_branches()
            
            # 清空编辑区
            self.clear_edit_area()
            
            self.mark_unsaved()
            self.update_status(f"节点 '{node_id}' 已删除")

    def cleanup_node_references(self, deleted_id):
        """清理被删除节点的引用"""
        for node in self.data["nodes"]:
            # 清理next引用
            if node.get("next") == deleted_id:
                node["next"] = None
            
            # 清理分支引用
            if "branches" in node:
                for branch in node["branches"]:
                    if branch.get("entry") == deleted_id:
                        branch["entry"] = ""
                    if branch.get("exit") == deleted_id:
                        branch["exit"] = ""

    def clear_edit_area(self):
        """清空编辑区域"""
        self.id_entry.delete(0, tk.END)
        self.type_box.set("")
        self.title_entry.delete(0, tk.END)
        self.next_entry.set("")
        self.content_text.delete("1.0", tk.END)
        
        self.branch_choice.delete(0, tk.END)
        self.branch_entry.set("")
        self.branch_exit.set("")

    def new_story(self):
        """新建剧情"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "未保存的更改", 
                "当前有未保存的更改，是否保存？"
            )
            if result is True:  # 保存
                if not self.save_story():
                    return
            elif result is None:  # 取消
                return
        
        self.data = {"title": "新剧情", "nodes": []}
        self.file_path = None
        self.current_node = None
        
        self.title_var.set("新剧情")
        self.refresh_node_list()
        self.clear_edit_area()
        self.refresh_branches()
        
        self.mark_saved()
        self.update_status("已创建新剧情")

    def load_story(self):
        """加载剧情文件"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "未保存的更改", 
                "当前有未保存的更改，是否保存？"
            )
            if result is True:  # 保存
                if not self.save_story():
                    return
            elif result is None:  # 取消
                return
        
        path = filedialog.askopenfilename(
            title="打开剧情文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if not path:
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            
            self.file_path = path
            self.current_node = None
            
            # 更新UI
            self.title_var.set(self.data.get("title", ""))
            self.refresh_node_list()
            self.clear_edit_area()
            self.refresh_branches()
            
            self.mark_saved()
            self.update_status(f"已加载: {os.path.basename(path)}")
            
        except Exception as e:
            messagebox.showerror("加载失败", f"无法加载文件:\n{str(e)}")

    def save_story(self):
        """保存剧情文件 - 必须选择跑团"""
        # 强制使用保存到跑团功能
        return self.save_to_campaign()

    def save_story_as(self):
        """另存为剧情文件 - 重定向到保存到跑团"""
        return self.save_to_campaign()


if __name__ == "__main__":
    root = tk.Tk()
    StoryEditor(root)
    root.mainloop()
