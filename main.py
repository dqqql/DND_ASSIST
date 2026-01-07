import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess
import sys

# ==================== 常量定义区域 ====================
# Prompt 2: 所有路径和分类相关的常量集中在文件顶部

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")

CATEGORIES = {
    "人物卡": "characters",
    "怪物卡": "monsters",
    "地图": "maps",
    "剧情": "notes"
}

# 文件名非法字符（Prompt 9）
INVALID_FILENAME_CHARS = r'/\:*?"<>|'

# 图片预览最大尺寸（Prompt 6）
IMAGE_PREVIEW_MAX_WIDTH = 600
IMAGE_PREVIEW_MAX_HEIGHT = 600

# 隐藏文件列表文件名
HIDDEN_FILES_LIST = ".hidden_files"

# ==================== 常量定义结束 ====================


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def open_file_with_system(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("darwin"):
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DND 跑团管理器")
        self.root.geometry("900x500")

        ensure_dirs()

        self.current_campaign = None
        self.current_category = None
        self.category_buttons = {}  # 存储分类按钮
        self.current_notes_path = ""  # Prompt 5: notes 当前路径（相对于 notes 根目录）
        self.hidden_files = {}  # 存储每个跑团分类的隐藏文件列表

        self.build_ui()
        self.load_campaigns()

    def build_ui(self):
        # 左侧面板 - 增加内边距
        left = tk.Frame(self.root, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)

        # 右侧面板 - 增加内边距
        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # 跑团列表标题 - 改进字体和间距
        tk.Label(left, text="跑团列表", font=("Arial", 12, "bold")).pack(pady=(0, 8))

        self.campaign_list = tk.Listbox(left, font=("Arial", 10))
        self.campaign_list.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.campaign_list.bind("<<ListboxSelect>>", self.on_campaign_select)

        # 按钮样式优化 - 统一字体、间距和大小
        tk.Button(left, text="新建跑团", command=self.create_campaign, 
                 font=("Arial", 10), height=2).pack(fill=tk.X, pady=2)
        tk.Button(left, text="删除跑团", command=self.delete_campaign,
                 font=("Arial", 10), height=2).pack(fill=tk.X, pady=2)

        # 顶部分类按钮区域 - 增加内边距
        top = tk.Frame(right)
        top.pack(fill=tk.X, pady=(0, 10))

        self.category_frame = tk.Frame(top)
        self.category_frame.pack(side=tk.LEFT, padx=(0, 10))

        # 操作按钮放在右上角
        button_frame = tk.Frame(top)
        button_frame.pack(side=tk.RIGHT)
        
        self.action_button = tk.Button(button_frame, text="请选择分类", font=("Arial", 10), height=2, width=12, state=tk.DISABLED)
        self.action_button.pack(side=tk.LEFT, padx=2)
        
        # 删除按钮
        self.delete_button = tk.Button(button_frame, text="删除文件", font=("Arial", 10), height=2, width=12, command=self.delete_file, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        # Prompt 5: 返回上级按钮（仅在 notes 分类显示）
        self.back_button = tk.Button(top, text="返回上级", font=("Arial", 10), height=2, width=12, command=self.go_back_notes)
        # 初始不显示

        # 文件管理区域 - 改进布局和间距
        self.file_frame = tk.Frame(right)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧文件列表 - 优化间距和字体
        file_list_frame = tk.Frame(self.file_frame)
        file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        self.file_list = tk.Listbox(file_list_frame, width=30, font=("Arial", 10))
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind("<Double-Button-1>", self.open_selected_file)
        self.file_list.bind("<<ListboxSelect>>", self.on_file_select)

        scrollbar = tk.Scrollbar(file_list_frame, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=scrollbar.set)

        # 右侧内容查看器 - 改进标题和布局
        content_frame = tk.Frame(self.file_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        content_label = tk.Label(content_frame, text="文件内容", font=("Arial", 12, "bold"))
        content_label.pack(anchor=tk.W, pady=(0, 8))

        # 文本显示区域 - 改进字体和背景
        self.text_frame = tk.Frame(content_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.content_text = tk.Text(self.text_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                   font=("Consolas", 11), bg="#f8f8f8", relief=tk.SUNKEN, bd=1)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_scrollbar = tk.Scrollbar(self.text_frame, command=self.content_text.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_scrollbar.set)

        # 图片显示区域（初始隐藏）- 改进样式
        self.image_frame = tk.Frame(content_frame)
        self.image_label = tk.Label(self.image_frame, text="选择地图文件查看", 
                                   bg="#f0f0f0", relief=tk.SUNKEN, bd=1, font=("Arial", 11))
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def load_campaigns(self):
        self.campaign_list.delete(0, tk.END)
        for name in os.listdir(DATA_DIR):
            if os.path.isdir(os.path.join(DATA_DIR, name)):
                self.campaign_list.insert(tk.END, name)

    def create_campaign(self):
        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("新建跑团")
        dialog.geometry("450x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # 添加内边距的主框架
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="请输入跑团名称:", font=("Arial", 11)).pack(pady=(0, 15))
        
        entry = tk.Entry(main_frame, width=35, font=("Arial", 12), relief=tk.SUNKEN, bd=2)
        entry.pack(pady=(0, 20))
        entry.focus()
        
        result = {"name": None}
        
        def on_ok():
            result["name"] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="确定", command=on_ok, width=12, height=2, 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="取消", command=on_cancel, width=12, height=2,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        
        name = result["name"]
        if not name:
            return
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            messagebox.showerror("错误", "跑团已存在")
            return

        os.makedirs(path)
        for folder in CATEGORIES.values():
            os.makedirs(os.path.join(path, folder))

        self.load_campaigns()

    def delete_campaign(self):
        sel = self.campaign_list.curselection()
        if not sel:
            return
        name = self.campaign_list.get(sel[0])
        path = os.path.join(DATA_DIR, name)
        if messagebox.askyesno("确认", f"确定删除跑团【{name}】？"):
            shutil.rmtree(path)
            self.current_campaign = None
            self.clear_categories()
            self.file_list.delete(0, tk.END)
            self.load_campaigns()

    def on_campaign_select(self, event):
        sel = self.campaign_list.curselection()
        if not sel:
            return
        self.current_campaign = self.campaign_list.get(sel[0])
        self.load_hidden_files()  # 加载隐藏文件列表
        self.show_categories()

    def clear_categories(self):
        for w in self.category_frame.winfo_children():
            w.destroy()
        self.category_buttons.clear()

    def show_categories(self):
        self.clear_categories()
        for name in CATEGORIES:
            btn = tk.Button(
                self.category_frame,
                text=name,
                command=lambda n=name: self.select_category(n),
                relief=tk.RAISED,
                font=("Arial", 10),
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.category_buttons[name] = btn

    def select_category(self, name):
        # 重置所有按钮状态
        for btn in self.category_buttons.values():
            btn.config(relief=tk.RAISED)
        
        # 设置当前按钮为按下状态
        if name in self.category_buttons:
            self.category_buttons[name].config(relief=tk.SUNKEN)
        
        self.current_category = CATEGORIES[name]
        
        # Prompt 5: 重置 notes 路径
        if self.current_category == "notes":
            self.current_notes_path = ""
        
        # 根据分类设置操作按钮
        if self.current_category == "maps":
            self.action_button.config(text="导入文件", command=self.import_file, state=tk.NORMAL)
        else:
            self.action_button.config(text="新建文件", command=self.create_file, state=tk.NORMAL)
        
        # 启用删除按钮
        self.delete_button.config(state=tk.NORMAL)
        
        # Prompt 5: 显示或隐藏返回上级按钮
        self.update_back_button()
        
        self.load_files()

    def load_files(self):
        """Prompt 3: 文件列表按文件名升序排序
           Prompt 4: notes 支持子文件夹，文件夹显示在前"""
        self.file_list.delete(0, tk.END)
        self.clear_content_viewer()
        if not self.current_campaign or not self.current_category:
            return
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        
        if not os.path.exists(current_path):
            return
        
        items = os.listdir(current_path)
        
        # 获取当前路径的隐藏文件列表
        hidden_key = f"{self.current_category}:{self.current_notes_path}" if self.current_category == "notes" else self.current_category
        hidden_set = self.hidden_files.get(hidden_key, set())
        
        # Prompt 4: notes 分类支持子文件夹
        if self.current_category == "notes":
            folders = []
            files = []
            for item in items:
                # 跳过隐藏的文件和文件夹
                if item in hidden_set:
                    continue
                    
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    folders.append(item)
                else:
                    files.append(item)
            
            # Prompt 3: 排序
            folders.sort()
            files.sort()
            
            # Prompt 4: 文件夹显示在前，格式为 "[DIR] 文件夹名"
            for folder in folders:
                self.file_list.insert(tk.END, f"[DIR] {folder}")
            for file in files:
                self.file_list.insert(tk.END, file)
        else:
            # 其他分类只显示文件，按文件名排序，过滤隐藏文件
            visible_items = [item for item in items if item not in hidden_set]
            visible_items.sort()
            for item in visible_items:
                self.file_list.insert(tk.END, item)

    def import_file(self):
        if not self.current_campaign or not self.current_category:
            return
        files = filedialog.askopenfilenames()
        if not files:
            return
        target_dir = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        for f in files:
            shutil.copy(f, target_dir)
        self.load_files()

    def get_template_content(self, category):
        """根据分类返回模板内容，如果不需要模板则返回空字符串"""
        if category == "characters":
            return "姓名: \n\n种族: \n\n职业: \n\n技能: \n\n装备: \n\n背景: \n\n"
        elif category == "monsters":
            return "姓名: \n\nCR: \n\n属性: \n\n攻击: \n\n特性: 无\n\n"
        return ""

    def create_file(self):
        if not self.current_campaign or not self.current_category:
            return
        
        # 创建一个自定义对话框 - 改进样式
        dialog = tk.Toplevel(self.root)
        dialog.title("新建文件")
        dialog.geometry("450x180")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # 添加内边距的主框架
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="请输入文件名（不需要扩展名）:", font=("Arial", 11)).pack(pady=(0, 15))
        
        entry = tk.Entry(main_frame, width=35, font=("Arial", 12), relief=tk.SUNKEN, bd=2)
        entry.pack(pady=(0, 20))
        entry.focus()
        
        result = {"filename": None}
        
        def on_ok():
            result["filename"] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack()
        
        tk.Button(button_frame, text="确定", command=on_ok, width=12, height=2, 
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="取消", command=on_cancel, width=12, height=2,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        
        filename = result["filename"]
        if not filename:
            return
        
        # Prompt 9: 文件名合法性检查
        for char in INVALID_FILENAME_CHARS:
            if char in filename:
                messagebox.showerror("错误", f"文件名不能包含以下字符: {INVALID_FILENAME_CHARS}")
                return
        
        # 添加.txt扩展名
        filename = filename + ".txt"
        base_dir = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        target_dir = os.path.join(base_dir, self.current_notes_path) if self.current_category == "notes" else base_dir
        file_path = os.path.join(target_dir, filename)
        
        if os.path.exists(file_path):
            messagebox.showerror("错误", "文件已存在")
            return
        
        # 获取模板内容并创建文件
        template_content = self.get_template_content(self.current_category)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.load_files()
        # 创建后自动打开文件
        open_file_with_system(file_path)

    def on_file_select(self, event):
        """文件列表选择事件处理
           Prompt 5: notes 分类支持双击文件夹进入"""
        sel = self.file_list.curselection()
        if not sel:
            self.clear_content_viewer()
            return
        
        display_name = self.file_list.get(sel[0])
        
        # Prompt 4 & 5: 处理 notes 文件夹
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            # 文件夹不显示内容
            self.clear_content_viewer()
            return
        
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        file_path = os.path.join(current_path, filename)

        # 如果是文本文件，显示内容
        if self.current_category in ["characters", "monsters", "notes"] and filename.endswith('.txt'):
            self.show_text_content(file_path)
        # 如果是地图文件，显示图片
        elif self.current_category == "maps":
            self.show_image_content(file_path)
        else:
            self.clear_content_viewer()

    def show_text_content(self, file_path):
        """显示文本文件内容
           Prompt 7: 每次从磁盘重新读取
           Prompt 8: 错误处理不弹窗"""
        try:
            # Prompt 7: 每次从磁盘重新读取，不使用缓存
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示文本区域，隐藏图片区域
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, content)
            self.content_text.config(state=tk.DISABLED)
        except Exception as e:
            # Prompt 8: 错误信息显示在文本区域，不弹窗
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.image_frame.pack_forget()
            
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, f"无法读取文件: {str(e)}")
            self.content_text.config(state=tk.DISABLED)

    def show_image_content(self, file_path):
        """在右侧显示图片内容
           Prompt 6: 按右侧显示区域大小自适应缩放，保持宽高比"""
        try:
            # 隐藏文本区域，显示图片区域
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.BOTH, expand=True)
            
            # 强制更新以获取实际显示区域大小
            self.image_frame.update_idletasks()
            
            # Prompt 6: 获取右侧显示区域的实际大小
            frame_width = self.image_frame.winfo_width()
            frame_height = self.image_frame.winfo_height()
            
            # 如果窗口还没有完全渲染，使用默认值
            if frame_width <= 1:
                frame_width = IMAGE_PREVIEW_MAX_WIDTH
            if frame_height <= 1:
                frame_height = IMAGE_PREVIEW_MAX_HEIGHT
            
            img = Image.open(file_path)
            
            # Prompt 6: 按显示区域大小自适应缩放，保持宽高比
            img.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            self.image_label.config(image="", text=f"无法显示图片: {str(e)}")



    def clear_content_viewer(self):
        """清空内容查看器"""
        # 显示文本区域，隐藏图片区域
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.image_frame.pack_forget()
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.config(state=tk.DISABLED)
        
        # 清除图片
        self.image_label.config(image="", text="选择地图文件查看")

    def open_selected_file(self, event):
        """Prompt 5: 双击文件打开，notes 分类双击文件夹进入"""
        sel = self.file_list.curselection()
        if not sel:
            return
        
        display_name = self.file_list.get(sel[0])
        
        # Prompt 5: notes 分类双击文件夹进入
        if self.current_category == "notes" and display_name.startswith("[DIR] "):
            folder_name = display_name.replace("[DIR] ", "")
            self.enter_notes_folder(folder_name)
            return
        
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        base_path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        current_path = os.path.join(base_path, self.current_notes_path) if self.current_category == "notes" else base_path
        path = os.path.join(current_path, filename)
        
        open_file_with_system(path)
    
    def enter_notes_folder(self, folder_name):
        """Prompt 5: 进入 notes 子文件夹"""
        if self.current_notes_path:
            self.current_notes_path = os.path.join(self.current_notes_path, folder_name)
        else:
            self.current_notes_path = folder_name
        
        self.update_back_button()
        self.load_files()
    
    def go_back_notes(self):
        """Prompt 5: 返回 notes 上级目录"""
        if not self.current_notes_path:
            return
        
        # 返回上级目录
        parent = os.path.dirname(self.current_notes_path)
        self.current_notes_path = parent
        
        self.update_back_button()
        self.load_files()
    
    def update_back_button(self):
        """Prompt 5: 更新返回上级按钮的显示状态"""
        if self.current_category == "notes" and self.current_notes_path:
            # 在 notes 分类且不在根目录时显示
            self.back_button.pack(side=tk.RIGHT, padx=(0, 5))
        else:
            # 其他情况隐藏
            self.back_button.pack_forget()
    
    def load_hidden_files(self):
        """加载当前跑团的隐藏文件列表"""
        if not self.current_campaign:
            return
        
        hidden_file_path = os.path.join(DATA_DIR, self.current_campaign, HIDDEN_FILES_LIST)
        self.hidden_files = {}
        
        if os.path.exists(hidden_file_path):
            try:
                with open(hidden_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            key, filename = line.split(':', 1)
                            if key not in self.hidden_files:
                                self.hidden_files[key] = set()
                            self.hidden_files[key].add(filename)
            except Exception:
                # 如果读取失败，使用空的隐藏列表
                self.hidden_files = {}
    
    def save_hidden_files(self):
        """保存当前跑团的隐藏文件列表"""
        if not self.current_campaign:
            return
        
        hidden_file_path = os.path.join(DATA_DIR, self.current_campaign, HIDDEN_FILES_LIST)
        
        try:
            with open(hidden_file_path, 'w', encoding='utf-8') as f:
                for key, filenames in self.hidden_files.items():
                    for filename in filenames:
                        f.write(f"{key}:{filename}\n")
        except Exception:
            # 保存失败时静默处理
            pass
    
    def delete_file(self):
        """删除选中的文件（仅从界面隐藏，不删除实际文件）"""
        sel = self.file_list.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要删除的文件")
            return
        
        display_name = self.file_list.get(sel[0])
        filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        # 确认删除
        file_type = "文件夹" if display_name.startswith("[DIR] ") else "文件"
        if not messagebox.askyesno("确认删除", f"确定要删除{file_type}【{filename}】吗？\n\n注意：这只会从软件中隐藏，不会删除实际文件。"):
            return
        
        # 添加到隐藏列表
        hidden_key = f"{self.current_category}:{self.current_notes_path}" if self.current_category == "notes" else self.current_category
        if hidden_key not in self.hidden_files:
            self.hidden_files[hidden_key] = set()
        
        self.hidden_files[hidden_key].add(filename)
        self.save_hidden_files()
        
        # 刷新文件列表
        self.load_files()
        self.clear_content_viewer()
        
        messagebox.showinfo("删除成功", f"{file_type}【{filename}】已从软件中删除\n\n实际文件仍保存在磁盘上")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
