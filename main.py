import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")

CATEGORIES = {
    "人物卡": "characters",
    "怪物卡": "monsters",
    "地图": "maps",
    "剧情": "notes"
}


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
        self.root.title("DND 跑团管理器（极简版）")
        self.root.geometry("900x500")

        ensure_dirs()

        self.current_campaign = None
        self.current_category = None
        self.category_buttons = {}  # 存储分类按钮

        self.build_ui()
        self.load_campaigns()

    def build_ui(self):
        left = tk.Frame(self.root, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(left, text="跑团列表").pack()

        self.campaign_list = tk.Listbox(left)
        self.campaign_list.pack(fill=tk.BOTH, expand=True)
        self.campaign_list.bind("<<ListboxSelect>>", self.on_campaign_select)

        tk.Button(left, text="新建跑团", command=self.create_campaign).pack(fill=tk.X)
        tk.Button(left, text="删除跑团", command=self.delete_campaign).pack(fill=tk.X)

        top = tk.Frame(right)
        top.pack(fill=tk.X)

        self.category_frame = tk.Frame(top)
        self.category_frame.pack(side=tk.LEFT)

        self.file_frame = tk.Frame(right)
        self.file_frame.pack(fill=tk.BOTH, expand=True)

        self.file_list = tk.Listbox(self.file_frame)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_list.bind("<Double-Button-1>", self.open_selected_file)

        scrollbar = tk.Scrollbar(self.file_frame, command=self.file_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=scrollbar.set)

        bottom = tk.Frame(right)
        bottom.pack(fill=tk.X)

        self.action_button = tk.Button(bottom, text="")
        self.action_button.pack(side=tk.LEFT)

        self.preview_label = tk.Label(bottom)
        self.preview_label.pack(side=tk.RIGHT)

    def load_campaigns(self):
        self.campaign_list.delete(0, tk.END)
        for name in os.listdir(DATA_DIR):
            if os.path.isdir(os.path.join(DATA_DIR, name)):
                self.campaign_list.insert(tk.END, name)

    def create_campaign(self):
        name = tk.simpledialog.askstring("新建跑团", "请输入跑团名称")
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
                relief=tk.RAISED
            )
            btn.pack(side=tk.LEFT)
            self.category_buttons[name] = btn

    def select_category(self, name):
        # 重置所有按钮状态
        for btn in self.category_buttons.values():
            btn.config(relief=tk.RAISED)
        
        # 设置当前按钮为按下状态
        if name in self.category_buttons:
            self.category_buttons[name].config(relief=tk.SUNKEN)
        
        self.current_category = CATEGORIES[name]
        
        # 根据分类设置操作按钮
        if self.current_category == "maps":
            self.action_button.config(text="导入文件", command=self.import_file)
        else:
            self.action_button.config(text="新建文件", command=self.create_file)
        
        self.load_files()

    def load_files(self):
        self.file_list.delete(0, tk.END)
        self.preview_label.config(image="", text="")
        if not self.current_campaign or not self.current_category:
            return
        path = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        for f in os.listdir(path):
            self.file_list.insert(tk.END, f)

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

    def create_file(self):
        if not self.current_campaign or not self.current_category:
            return
        
        # 创建一个自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("新建文件")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        tk.Label(dialog, text="请输入文件名（不需要扩展名）:").pack(pady=10)
        
        entry = tk.Entry(dialog, width=40, font=("Arial", 12))
        entry.pack(pady=10)
        entry.focus()
        
        result = {"filename": None}
        
        def on_ok():
            result["filename"] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="确定", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 绑定回车键
        entry.bind("<Return>", lambda e: on_ok())
        
        dialog.wait_window()
        
        filename = result["filename"]
        if not filename:
            return
        
        # 添加.txt扩展名
        filename = filename + ".txt"
        target_dir = os.path.join(DATA_DIR, self.current_campaign, self.current_category)
        file_path = os.path.join(target_dir, filename)
        
        if os.path.exists(file_path):
            messagebox.showerror("错误", "文件已存在")
            return
        
        # 创建空的文本文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        self.load_files()
        # 创建后自动打开文件
        open_file_with_system(file_path)

    def open_selected_file(self, event):
        sel = self.file_list.curselection()
        if not sel:
            return
        filename = self.file_list.get(sel[0])
        path = os.path.join(
            DATA_DIR, self.current_campaign, self.current_category, filename
        )

        if self.current_category == "maps":
            try:
                img = Image.open(path)
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo
            except Exception:
                pass

        open_file_with_system(path)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
