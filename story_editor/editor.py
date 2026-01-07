import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

TEMPLATE = {
    "title": "新剧情",
    "nodes": []
}


class StoryEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Story JSON Editor")

        self.data = TEMPLATE.copy()
        self.current_node = None
        self.file_path = None

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
