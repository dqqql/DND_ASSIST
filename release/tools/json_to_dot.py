import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.story_parser import StoryGraphService

def load_story(path: Path) -> dict:
    """加载剧情文件（保留向后兼容）"""
    story_service = StoryGraphService()
    story = story_service.parse_json_story(path)
    
    if story:
        # 转换为原始格式
        return {
            "title": story.title,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.node_type,
                    "title": node.title,
                    "content": node.content,
                    "next": node.next_id,
                    "branches": [
                        {
                            "choice": branch.choice,
                            "entry": branch.entry,
                            "exit": branch.exit
                        }
                        for branch in node.branches
                    ]
                }
                for node in story.nodes
            ]
        }
    return {}

def generate_dot(story: dict) -> str:
    """生成DOT格式内容（保留向后兼容）"""
    story_service = StoryGraphService()
    
    # 创建StoryGraph对象
    from src.core.models import StoryGraph, StoryNode, StoryBranch
    
    graph = StoryGraph(title=story.get("title", ""))
    
    for node_data in story.get("nodes", []):
        branches = []
        for branch_data in node_data.get("branches", []):
            branch = StoryBranch(
                choice=branch_data.get("choice", ""),
                entry=branch_data.get("entry"),
                exit=branch_data.get("exit")
            )
            branches.append(branch)
        
        node = StoryNode(
            id=node_data.get("id", ""),
            title=node_data.get("title", ""),
            content=node_data.get("content", ""),
            node_type=node_data.get("type", "main"),
            next_id=node_data.get("next"),
            branches=branches
        )
        graph.nodes.append(node)
    
    return story_service.generate_dot_content(graph)

# --- 以下为原有的文件处理和 CLI 逻辑，保持不变 ---

def find_json_files():
    """查找data/campaigns目录下的所有JSON文件"""
    base_dir = Path(__file__).parent.parent
    campaigns_dir = base_dir / "data" / "campaigns"
    
    json_files = []
    if campaigns_dir.exists():
        for campaign_dir in campaigns_dir.iterdir():
            if campaign_dir.is_dir():
                notes_dir = campaign_dir / "notes"
                if notes_dir.exists():
                    for json_file in notes_dir.glob("*.json"):
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