import json
import sys
import os
from pathlib import Path

# 定义颜色常量
MAIN_COLOR = "#4CAF50"    # 主线节点：绿色
BRANCH_COLOR = "#2196F3"  # 分支节点：蓝色
FAIL_COLOR = "#9E9E9E"    # 虚线/失败：灰色
CHOICE_COLOR = "#FF9800"  # 分支连线：橙色

def load_story(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_dot(story: dict) -> str:
    lines = []

    lines.append("digraph Story {")
    lines.append("    rankdir=TB;")      # 从上至下布局
    lines.append("    splines=ortho;")    # 使用直角连线
    lines.append("    nodesep=0.6;")
    lines.append("    ranksep=0.8;")
    lines.append("")
    lines.append("    node [shape=box, style=filled, fontcolor=white, fontname=\"Microsoft YaHei\"];")
    lines.append("    edge [fontname=\"Microsoft YaHei\"];")
    lines.append("")

    nodes = {n["id"]: n for n in story.get("nodes", [])}

    # ---------- 1. 节点定义 ----------
    for node in nodes.values():
        nid = node["id"]
        title = node.get("title", "")
        label = f"{title}\\n[{nid}]"

        # 根据类型决定颜色
        if node.get("type") == "main":
            color = MAIN_COLOR
        else:
            color = BRANCH_COLOR

        lines.append(
            f'    "{nid}" [label="{label}", fillcolor="{color}", border="none"];'
        )

    lines.append("")

    # ---------- 2. 节点间的 Next 连线 (实线) ----------
    # 修改点：不再限制只有 main 节点能连线，让 branch 节点也能连向下一个节点
    for node in nodes.values():
        next_id = node.get("next")
        if next_id and next_id in nodes:
            lines.append(f'    "{node["id"]}" -> "{next_id}" [color="#333333"];')

    lines.append("")

    # ---------- 3. 分支入口与逻辑回归 ----------
    for node in nodes.values():
        # 只有主线节点可以作为分支的起点
        if node.get("type") != "main":
            continue

        for branch in node.get("branches", []):
            entry = branch.get("entry")
            exit_node = branch.get("exit")
            choice = branch.get("choice", "选择")

            # 绘制分支入口连线 (橙色实线)
            if entry and entry in nodes:
                lines.append(
                    f'    "{node["id"]}" -> "{entry}" '
                    f'[label="{choice}", color="{CHOICE_COLOR}", fontcolor="{CHOICE_COLOR}"];'
                )

                # 修改点：回归虚线的判定
                # 只有当分支入口节点 node[entry] 自身没有设置 next 时，才绘制到 exit_node 的回归虚线。
                # 这支持了“结婚 -> 离婚 -> 死亡”这种长链条分支。
                if exit_node and exit_node in nodes:
                    entry_node_data = nodes[entry]
                    if not entry_node_data.get("next"):
                        lines.append(
                            f'    "{entry}" -> "{exit_node}" '
                            f'[style=dashed, color="{FAIL_COLOR}"];'
                        )

    lines.append("}")
    return "\n".join(lines)

# --- 以下为原有的文件处理和 CLI 逻辑，保持不变 ---

def find_json_files():
    """查找output目录下的所有JSON文件"""
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "output"
    
    json_files = []
    if output_dir.exists():
        for campaign_dir in output_dir.iterdir():
            if campaign_dir.is_dir():
                for script_dir in campaign_dir.iterdir():
                    if script_dir.is_dir():
                        for json_file in script_dir.glob("*.json"):
                            json_files.append(json_file)
                    elif campaign_dir.name != "__pycache__":
                        for json_file in campaign_dir.glob("*.json"):
                            json_files.append(json_file)
    return json_files

def ask_user_confirmation(json_files):
    print(f"\n找到 {len(json_files)} 个JSON文件：")
    for i, json_file in enumerate(json_files, 1):
        print(f"  {i}. {json_file}")
    
    print("\n选项：(a) 转换所有, (s) 跳过已存在, (n) 取消")
    while True:
        choice = input("\n请选择 (a/s/n): ").lower().strip()
        if choice in ['a', 's', 'n']: return choice

def process_json_file(json_path: Path):
    try:
        story = load_story(json_path)
        dot_content = generate_dot(story)
        dot_path = json_path.with_suffix('.dot')
        with open(dot_path, "w", encoding="utf-8") as f:
            f.write(dot_content)
        print(f"[OK] DOT 文件已生成：{dot_path}")
        return dot_path
    except Exception as e:
        print(f"[ERROR] 处理文件 {json_path} 时出错：{e}")
        return None

def main():
    if len(sys.argv) == 1:
        json_files = find_json_files()
        if not json_files: return
        mode = ask_user_confirmation(json_files)
        if mode == 'n': return
        for json_file in json_files:
            process_json_file(json_file)
    elif len(sys.argv) == 3:
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
        story = load_story(input_path)
        dot = generate_dot(story)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot)
        print(f"[OK] DOT 文件已生成：{output_path}")
    else:
        print("用法：python json_to_dot.py [input.json output.dot]")

if __name__ == "__main__":
    main()