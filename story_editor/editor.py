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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "campaigns")


class StoryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Story JSON Editor")

        self.data = TEMPLATE.copy()
        self.current_node = None
        self.file_path = None
        self.campaigns = self.get_available_campaigns()

        self.build_ui()

    def build_ui(self):
        self.root.geometry("1000x520")

        # 左侧：节点列表
        left = ttk.Frame(self.root, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left, text="节点列表").pack(anchor="w")

        self.node_list = tk.Listbox(left)
        self.node_list.pack(fill=tk.BOTH, expand=True)
        self.node_list.bind("<<ListboxSelect>>", self.on_select_node)

        ttk.Button(left, text="新增节点", command=self.add_node).pack(fill=tk.X, pady=2)
        ttk.Button(left, text="删除节点", command=self.delete_node).pack(fill=tk.X, pady=2)

        # 中间：节点编辑
        middle = ttk.Frame(self.root)
        middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        form = ttk.Frame(middle)
        form.pack(fill=tk.X)

        ttk.Label(form, text="ID").grid(row=0, column=0, sticky="e")
        self.id_entry = ttk.Entry(form)
        self.id_entry.grid(row=0, column=1, sticky="we")

        ttk.Label(form, text="类型").grid(row=1, column=0, sticky="e")
        self.type_box = ttk.Combobox(form, values=["main", "branch"], state="readonly")
        self.type_box.grid(row=1, column=1, sticky="we")

        ttk.Label(form, text="标题").grid(row=2, column=0, sticky="e")
        self.title_entry = ttk.Entry(form)
        self.title_entry.grid(row=2, column=1, sticky="we")

        ttk.Label(form, text="Next").grid(row=3, column=0, sticky="e")
        self.next_entry = ttk.Entry(form)
        self.next_entry.grid(row=3, column=1, sticky="we")

        ttk.Label(form, text="内容").grid(row=4, column=0, sticky="ne")
        self.content_text = tk.Text(form, height=6)
        self.content_text.grid(row=4, column=1, sticky="we")

        form.columnconfigure(1, weight=1)

        ttk.Button(middle, text="保存节点修改", command=self.save_node).pack(anchor="e", pady=4)

        # 右侧：分支编辑区（关键新增）
        self.branch_frame = ttk.LabelFrame(self.root, text="分支编辑（仅主线节点）")
        self.branch_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.branch_list = tk.Listbox(self.branch_frame, height=10)
        self.branch_list.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(self.branch_frame, text="新增分支", command=self.add_branch).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(self.branch_frame, text="删除分支", command=self.delete_branch).pack(fill=tk.X, padx=5, pady=2)

        # 分支编辑表单
        bf = ttk.Frame(self.branch_frame)
        bf.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(bf, text="选项文本").grid(row=0, column=0, sticky="e")
        self.branch_choice = ttk.Entry(bf)
        self.branch_choice.grid(row=0, column=1, sticky="we")

        ttk.Label(bf, text="入口节点").grid(row=1, column=0, sticky="e")
        self.branch_entry = ttk.Combobox(bf, state="readonly")
        self.branch_entry.grid(row=1, column=1, sticky="we")

        ttk.Label(bf, text="回归节点").grid(row=2, column=0, sticky="e")
        self.branch_exit = ttk.Combobox(bf, state="readonly")
        self.branch_exit.grid(row=2, column=1, sticky="we")

        ttk.Button(self.branch_frame, text="保存分支修改", command=self.save_branch).pack(fill=tk.X, padx=5, pady=4)

        bf.columnconfigure(1, weight=1)

        # 底部
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(bottom, text="新建剧情", command=self.new_story).pack(side=tk.LEFT)
        ttk.Button(bottom, text="打开剧情", command=self.load_story).pack(side=tk.LEFT)
        ttk.Button(bottom, text="保存剧情", command=self.save_story).pack(side=tk.RIGHT)
        ttk.Button(bottom, text="保存到跑团", command=self.save_to_campaign).pack(side=tk.RIGHT, padx=(0, 5))

    # ---------- 通用 ----------

    def refresh_node_list(self):
        self.node_list.delete(0, tk.END)
        for n in self.data["nodes"]:
            self.node_list.insert(tk.END, f'{n["id"]} ({n["type"]})')

        ids = [n["id"] for n in self.data["nodes"]]
        self.branch_entry["values"] = ids
        self.branch_exit["values"] = ids

    def on_select_node(self, event):
        if not self.node_list.curselection():
            return
        idx = self.node_list.curselection()[0]
        self.current_node = self.data["nodes"][idx]
        self.load_node()
        self.refresh_branches()

    def load_node(self):
        n = self.current_node
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, n.get("id", ""))

        self.type_box.set(n.get("type", "main"))

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, n.get("title", ""))

        self.next_entry.delete(0, tk.END)
        if n.get("next"):
            self.next_entry.insert(0, n["next"])

        self.content_text.delete("1.0", tk.END)
        self.content_text.insert(tk.END, n.get("content", ""))

    def save_node(self):
        if not self.current_node:
            return

        self.current_node["id"] = self.id_entry.get().strip()
        self.current_node["type"] = self.type_box.get()
        self.current_node["title"] = self.title_entry.get().strip()
        self.current_node["next"] = self.next_entry.get().strip() or None
        self.current_node["content"] = self.content_text.get("1.0", tk.END).strip()

        if self.current_node["type"] == "main":
            self.current_node.setdefault("branches", [])
        else:
            self.current_node.pop("branches", None)

        self.refresh_node_list()

    # ---------- 分支相关 ----------

    def refresh_branches(self):
        self.branch_list.delete(0, tk.END)

        if not self.current_node or self.current_node.get("type") != "main":
            return

        for b in self.current_node.get("branches", []):
            self.branch_list.insert(tk.END, b["choice"])

    def add_branch(self):
        if not self.current_node or self.current_node.get("type") != "main":
            return

        self.current_node.setdefault("branches", []).append({
            "choice": "新分支",
            "entry": "",
            "exit": ""
        })
        self.refresh_branches()

    def delete_branch(self):
        if not self.branch_list.curselection():
            return
        idx = self.branch_list.curselection()[0]
        del self.current_node["branches"][idx]
        self.refresh_branches()

    def save_branch(self):
        if not self.branch_list.curselection():
            return

        idx = self.branch_list.curselection()[0]
        b = self.current_node["branches"][idx]

        b["choice"] = self.branch_choice.get().strip()
        b["entry"] = self.branch_entry.get()
        b["exit"] = self.branch_exit.get()

        self.refresh_branches()

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
            return
        
        # 刷新跑团列表
        self.refresh_campaigns()
        
        if not self.campaigns:
            messagebox.showerror("错误", "没有找到可用的跑团\n请先在主程序中创建跑团")
            return
        
        # 创建选择跑团的对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择跑团")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {"campaign": None, "filename": None}
        
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
        
        # 文件名输入
        ttk.Label(main_frame, text="文件名:").pack(anchor="w")
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
            filename = filename_var.get().strip()
            
            if not campaign:
                messagebox.showerror("错误", "请选择跑团")
                return
            
            if not filename:
                messagebox.showerror("错误", "请输入文件名")
                return
            
            # 检查文件名合法性
            invalid_chars = r'/\:*?"<>|'
            for char in invalid_chars:
                if char in filename:
                    messagebox.showerror("错误", f"文件名不能包含以下字符: {invalid_chars}")
                    return
            
            result["campaign"] = campaign
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
        if result["campaign"] and result["filename"]:
            self._save_to_campaign_path(result["campaign"], result["filename"])

    def _save_to_campaign_path(self, campaign, filename):
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
                    return
            
            # 保存文件
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("保存成功", 
                              f"剧情已保存到跑团【{campaign}】\n文件路径: {save_path}")
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存文件时发生错误:\n{str(e)}")

    def add_node(self):
        self.data["nodes"].append({
            "id": f"node_{len(self.data['nodes']) + 1:02d}",
            "type": "main",
            "title": "新节点",
            "content": "",
            "next": None,
            "branches": []
        })
        self.refresh_node_list()

    def delete_node(self):
        if not self.node_list.curselection():
            return
        del self.data["nodes"][self.node_list.curselection()[0]]
        self.current_node = None
        self.refresh_node_list()
        self.branch_list.delete(0, tk.END)

    def new_story(self):
        self.data = {"title": "新剧情", "nodes": []}
        self.file_path = None
        self.refresh_node_list()

    def load_story(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.file_path = path
        self.refresh_node_list()

    def save_story(self):
        if not self.file_path:
            path = filedialog.asksaveasfilename(defaultextension=".json")
            if not path:
                return
            self.file_path = path
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存成功", "剧情文件已保存")


if __name__ == "__main__":
    root = tk.Tk()
    StoryEditor(root)
    root.mainloop()
