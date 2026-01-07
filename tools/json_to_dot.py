import json
import sys
import os
from pathlib import Path


MAIN_COLOR = "#4CAF50"
BRANCH_COLOR = "#2196F3"
FAIL_COLOR = "#9E9E9E"
CHOICE_COLOR = "#FF9800"


def load_story(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_dot(story: dict) -> str:
    lines = []

    lines.append("digraph Story {")
    lines.append("    rankdir=TB;")
    lines.append("    splines=ortho;")
    lines.append("    nodesep=0.6;")
    lines.append("    ranksep=0.8;")
    lines.append("")
    lines.append("    node [shape=box, style=filled, fontcolor=white];")
    lines.append("")

    nodes = {n["id"]: n for n in story.get("nodes", [])}

    # ---------- 节点定义 ----------
    for node in nodes.values():
        nid = node["id"]
        title = node.get("title", "")
        label = f"{title}\\n[{nid}]"

        if node["type"] == "main":
            color = MAIN_COLOR
        else:
            color = BRANCH_COLOR

        lines.append(
            f'    "{nid}" [label="{label}", fillcolor="{color}"];'
        )

    lines.append("")

    # ---------- 主线 next ----------
    for node in nodes.values():
        if node.get("type") == "main" and node.get("next"):
            if node["next"] in nodes:
                lines.append(f'    "{node["id"]}" -> "{node["next"]}";')

    lines.append("")

    # ---------- 分支 ----------
    for node in nodes.values():
        if node.get("type") != "main":
            continue

        for branch in node.get("branches", []):
            entry = branch.get("entry")
            exit_ = branch.get("exit")
            choice = branch.get("choice", "")

            if entry and entry in nodes:
                lines.append(
                    f'    "{node["id"]}" -> "{entry}" '
                    f'[label="{choice}", color="{CHOICE_COLOR}"];'
                )

            if entry and exit_ and entry in nodes and exit_ in nodes:
                # 回归主线用虚线，避免结构混乱
                lines.append(
                    f'    "{entry}" -> "{exit_}" '
                    f'[style=dashed, color="gray"];'
                )

    lines.append("}")
    return "\n".join(lines)


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
                        # 新结构：output/跑团/剧本/文件.json
                        for json_file in script_dir.glob("*.json"):
                            json_files.append(json_file)
                    elif campaign_dir.name != "__pycache__":
                        # 兼容旧结构：output/跑团/文件.json
                        for json_file in campaign_dir.glob("*.json"):
                            json_files.append(json_file)
    
    return json_files


def ask_user_confirmation(json_files):
    """询问用户是否要转换文件"""
    print(f"\n找到 {len(json_files)} 个JSON文件：")
    
    for i, json_file in enumerate(json_files, 1):
        # 解析路径结构
        parts = json_file.parts
        if len(parts) >= 4 and parts[-4] == "output":
            # 新结构：output/跑团/剧本/文件.json
            campaign = parts[-3]
            script = parts[-2]
            filename = parts[-1]
            print(f"  {i}. {campaign}/{script}/{filename}")
        elif len(parts) >= 3 and parts[-3] == "output":
            # 旧结构：output/跑团/文件.json
            campaign = parts[-2]
            filename = parts[-1]
            print(f"  {i}. {campaign}/{filename}")
        else:
            print(f"  {i}. {json_file}")
    
    print("\n选项：")
    print("  a) 转换所有文件")
    print("  s) 跳过已存在的DOT文件，只转换新文件")
    print("  n) 取消转换")
    
    while True:
        choice = input("\n请选择 (a/s/n): ").lower().strip()
        if choice in ['a', 's', 'n']:
            return choice
        print("无效选择，请输入 a、s 或 n")


def should_process_file(json_file, mode):
    """判断是否应该处理文件"""
    if mode == 'n':  # 取消
        return False
    elif mode == 'a':  # 转换所有
        return True
    elif mode == 's':  # 跳过已存在的
        dot_file = json_file.with_suffix('.dot')
        if dot_file.exists():
            print(f"跳过 {json_file.name}（DOT文件已存在）")
            return False
        return True
    return False


def process_json_file(json_path: Path):
    """处理单个JSON文件，生成对应的DOT文件"""
    try:
        story = load_story(json_path)
        dot_content = generate_dot(story)
        
        # 生成DOT文件路径（与JSON文件同目录，同名但扩展名为.dot）
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
        # 无参数模式：处理output目录下的所有JSON文件
        json_files = find_json_files()
        if not json_files:
            print("未找到任何JSON文件")
            return
        
        # 询问用户确认
        mode = ask_user_confirmation(json_files)
        if mode == 'n':
            print("已取消转换")
            return
        
        print(f"\n开始处理...")
        
        success_count = 0
        skipped_count = 0
        
        for json_file in json_files:
            if should_process_file(json_file, mode):
                if process_json_file(json_file):
                    success_count += 1
            else:
                skipped_count += 1
        
        print(f"\n处理完成：{success_count} 个文件成功，{skipped_count} 个文件跳过")
        
    elif len(sys.argv) == 2 and sys.argv[1] == "--auto":
        # 自动模式：跳过已存在的文件，不询问用户
        json_files = find_json_files()
        if not json_files:
            print("未找到任何JSON文件")
            return
        
        print(f"找到 {len(json_files)} 个JSON文件，自动处理模式...")
        
        success_count = 0
        skipped_count = 0
        
        for json_file in json_files:
            if should_process_file(json_file, 's'):  # 使用跳过模式
                if process_json_file(json_file):
                    success_count += 1
            else:
                skipped_count += 1
        
        print(f"处理完成：{success_count} 个文件成功，{skipped_count} 个文件跳过")
        
    elif len(sys.argv) == 3:
        # 传统模式：指定输入输出文件
        input_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])

        story = load_story(input_path)
        dot = generate_dot(story)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot)

        print(f"[OK] DOT 文件已生成：{output_path}")
        
    else:
        print("用法：")
        print("  python json_to_dot.py                    # 处理output目录下的所有JSON文件（交互模式）")
        print("  python json_to_dot.py --auto             # 处理output目录下的所有JSON文件（自动模式）")
        print("  python json_to_dot.py input.json output.dot  # 处理指定文件")
        sys.exit(1)


if __name__ == "__main__":
    main()
