"""
剧情解析服务
处理JSON剧情的解析、统计、转换等操作
"""

import json
from pathlib import Path
from typing import Optional, Dict, List

from .models import StoryGraph, StoryNode, StoryBranch


class StoryGraphService:
    """剧情图服务"""
    
    def parse_json_story(self, file_path: Path) -> Optional[StoryGraph]:
        """解析JSON剧情文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            Optional[StoryGraph]: 剧情图对象，失败返回None
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._parse_story_data(data)
        except (json.JSONDecodeError, Exception):
            return None
    
    def _parse_story_data(self, data: Dict) -> StoryGraph:
        """解析剧情数据
        
        Args:
            data: JSON数据字典
            
        Returns:
            StoryGraph: 剧情图对象
        """
        story = StoryGraph(title=data.get("title", ""))
        
        nodes_data = data.get("nodes", [])
        for node_data in nodes_data:
            node = self._parse_node_data(node_data)
            if node:
                story.nodes.append(node)
        
        return story
    
    def _parse_node_data(self, node_data: Dict) -> Optional[StoryNode]:
        """解析节点数据
        
        Args:
            node_data: 节点数据字典
            
        Returns:
            Optional[StoryNode]: 节点对象，失败返回None
        """
        node_id = node_data.get("id")
        if not node_id:
            return None
        
        # 解析分支
        branches = []
        branches_data = node_data.get("branches", [])
        for branch_data in branches_data:
            branch = StoryBranch(
                choice=branch_data.get("choice", ""),
                entry=branch_data.get("entry"),
                exit=branch_data.get("exit")
            )
            branches.append(branch)
        
        return StoryNode(
            id=node_id,
            title=node_data.get("title", ""),
            content=node_data.get("content", ""),
            node_type=node_data.get("type", "main"),
            next_id=node_data.get("next"),
            branches=branches
        )
    
    def generate_statistics_text(self, story: StoryGraph, file_path: Path) -> str:
        """生成剧情统计文本
        
        Args:
            story: 剧情图对象
            file_path: 文件路径（用于查找SVG）
            
        Returns:
            str: 统计文本
        """
        stats = story.calculate_statistics()
        lines = []
        
        # 基本信息
        lines.append(f"📖 剧情：{story.title or '未命名剧情'}")
        lines.append("")
        
        # 节点统计
        lines.append("🎯 节点统计:")
        lines.append(f"   • 总节点数: {stats['total_nodes']}")
        lines.append(f"   • 主线节点: {stats['main_nodes']}")
        lines.append(f"   • 分支节点: {stats['branch_nodes']}")
        if stats['total_nodes'] - stats['main_nodes'] - stats['branch_nodes'] > 0:
            other_count = stats['total_nodes'] - stats['main_nodes'] - stats['branch_nodes']
            lines.append(f"   • 其他节点: {other_count}")
        lines.append("")
        
        # 分支统计
        lines.append("🌿 分支统计:")
        lines.append(f"   • 总分支数: {stats['total_branches']}")
        lines.append(f"   • 有分支的主线节点: {stats['nodes_with_branches']}")
        if stats['nodes_with_branches'] > 0:
            lines.append(f"   • 平均每个分支点的选择数: {stats['avg_branches']:.1f}")
        lines.append("")
        
        # 内容完整性检查
        lines.append("✅ 内容完整性:")
        lines.append(f"   • 有意义的节点: {stats['meaningful_nodes']}/{stats['total_nodes']}")
        if stats['empty_title_count'] > 0:
            lines.append(f"   • 空标题节点: {stats['empty_title_count']}")
        if stats['empty_content_count'] > 0:
            lines.append(f"   • 空内容节点: {stats['empty_content_count']}")
        
        # 连接性检查
        if stats['orphaned_nodes']:
            orphaned_display = stats['orphaned_nodes'][:3]
            if len(stats['orphaned_nodes']) > 3:
                orphaned_display.append('...')
            lines.append(f"   • 孤立节点: {len(stats['orphaned_nodes'])} ({', '.join(orphaned_display)})")
        else:
            lines.append("   • 所有节点都已连接")
        
        lines.append("")
        
        # 主线流程
        main_nodes = story.get_main_nodes()
        if main_nodes:
            lines.append("🎯 主线流程:")
            for i, node in enumerate(main_nodes[:5], 1):
                branches_count = len(node.branches)
                branch_info = f" ({branches_count}个选择)" if branches_count > 0 else ""
                lines.append(f"   {i}. {node.title} [{node.id}]{branch_info}")
            
            if len(main_nodes) > 5:
                lines.append(f"   ... 还有 {len(main_nodes) - 5} 个主线节点")
            lines.append("")
        
        # 检查SVG文件
        svg_path = self._get_svg_path_for_json(file_path)
        if svg_path and svg_path.exists():
            lines.append("")
            lines.append("📈 流程图: 已生成，可双击文件名在外部查看")
        
        return "\n".join(lines)
    
    def _get_svg_path_for_json(self, json_file_path: Path) -> Optional[Path]:
        """根据JSON文件路径查找对应的SVG文件路径
        
        Args:
            json_file_path: JSON文件路径
            
        Returns:
            Optional[Path]: SVG文件路径，未找到返回None
        """
        try:
            # 获取文件名（不含扩展名）
            filename_without_ext = json_file_path.stem
            
            # 在同一目录中查找SVG文件
            svg_path = json_file_path.parent / f"{filename_without_ext}.svg"
            
            return svg_path if svg_path.exists() else None
        except Exception:
            return None
    
    def generate_dot_content(self, story: StoryGraph) -> str:
        """生成DOT格式内容
        
        Args:
            story: 剧情图对象
            
        Returns:
            str: DOT格式内容
        """
        lines = []
        
        # DOT文件头部
        lines.append("digraph Story {")
        lines.append("    rankdir=TB;")
        lines.append("    splines=ortho;")
        lines.append("    nodesep=0.6;")
        lines.append("    ranksep=0.8;")
        lines.append("")
        lines.append('    node [shape=box, style=filled, fontcolor=white, fontname="Microsoft YaHei"];')
        lines.append('    edge [fontname="Microsoft YaHei"];')
        lines.append("")
        
        # 颜色常量
        MAIN_COLOR = "#4CAF50"    # 主线节点：绿色
        BRANCH_COLOR = "#2196F3"  # 分支节点：蓝色
        FAIL_COLOR = "#9E9E9E"    # 虚线/失败：灰色
        CHOICE_COLOR = "#FF9800"  # 分支连线：橙色
        
        # 节点定义
        for node in story.nodes:
            label = f"{node.title}\\n[{node.id}]"
            color = MAIN_COLOR if node.node_type == "main" else BRANCH_COLOR
            lines.append(f'    "{node.id}" [label="{label}", fillcolor="{color}", border="none"];')
        
        lines.append("")
        
        # Next连线（实线）
        for node in story.nodes:
            if node.next_id:
                lines.append(f'    "{node.id}" -> "{node.next_id}";')
        
        lines.append("")
        
        # 分支连线（带标签的彩色线）
        for node in story.nodes:
            for branch in node.branches:
                if branch.entry:
                    choice_label = branch.choice.replace('"', '\\"')
                    lines.append(f'    "{node.id}" -> "{branch.entry}" [label="{choice_label}", color="{CHOICE_COLOR}", fontcolor="{CHOICE_COLOR}"];')
                
                if branch.exit and branch.entry:
                    lines.append(f'    "{branch.entry}" -> "{branch.exit}" [style=dashed, color="{FAIL_COLOR}"];')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def validate_story_structure(self, story: StoryGraph) -> Dict[str, List[str]]:
        """验证剧情结构
        
        Args:
            story: 剧情图对象
            
        Returns:
            Dict[str, List[str]]: 验证结果，包含errors和warnings
        """
        errors = []
        warnings = []
        
        if not story.nodes:
            errors.append("剧情中没有任何节点")
            return {"errors": errors, "warnings": warnings}
        
        # 检查节点ID唯一性
        node_ids = [node.id for node in story.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("存在重复的节点ID")
        
        # 检查引用的节点是否存在
        all_node_ids = set(node_ids)
        for node in story.nodes:
            if node.next_id and node.next_id not in all_node_ids:
                errors.append(f"节点 {node.id} 引用了不存在的节点 {node.next_id}")
            
            for branch in node.branches:
                if branch.entry and branch.entry not in all_node_ids:
                    errors.append(f"节点 {node.id} 的分支引用了不存在的入口节点 {branch.entry}")
                if branch.exit and branch.exit not in all_node_ids:
                    errors.append(f"节点 {node.id} 的分支引用了不存在的出口节点 {branch.exit}")
        
        # 检查孤立节点
        orphaned = story.get_orphaned_nodes()
        if orphaned:
            warnings.append(f"发现 {len(orphaned)} 个孤立节点: {', '.join(orphaned[:3])}")
        
        # 检查空内容
        empty_nodes = [node.id for node in story.nodes if not node.title.strip()]
        if empty_nodes:
            warnings.append(f"发现 {len(empty_nodes)} 个空标题节点")
        
        return {"errors": errors, "warnings": warnings}