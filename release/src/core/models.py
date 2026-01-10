"""
数据模型定义
定义跑团、剧情节点等核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path


@dataclass
class Campaign:
    """跑团数据模型"""
    name: str
    path: Path
    categories: Dict[str, str] = field(default_factory=lambda: {
        "人物卡": "characters",
        "怪物卡": "monsters", 
        "地图": "maps",
        "剧情": "notes"
    })
    hidden_files: Dict[str, Set[str]] = field(default_factory=dict)
    
    def get_category_path(self, category: str) -> Path:
        """获取分类目录路径"""
        return self.path / category
    
    def get_notes_path(self, sub_path: str = "") -> Path:
        """获取notes子路径"""
        notes_path = self.path / "notes"
        if sub_path:
            return notes_path / sub_path
        return notes_path


@dataclass
class StoryBranch:
    """剧情分支"""
    choice: str
    entry: Optional[str] = None
    exit: Optional[str] = None


@dataclass 
class StoryNode:
    """剧情节点"""
    id: str
    title: str = ""
    content: str = ""
    node_type: str = "main"  # main, branch
    next_id: Optional[str] = None
    branches: List[StoryBranch] = field(default_factory=list)
    
    def has_branches(self) -> bool:
        """是否有分支"""
        return len(self.branches) > 0
    
    def is_meaningful(self) -> bool:
        """是否是有意义的节点（非空标题且非默认值）"""
        return (self.title and 
                self.title.strip() and 
                self.title not in ["新节点", "未命名节点", "未命名"])


@dataclass
class StoryGraph:
    """剧情图"""
    title: str = ""
    nodes: List[StoryNode] = field(default_factory=list)
    
    def get_node_by_id(self, node_id: str) -> Optional[StoryNode]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_main_nodes(self) -> List[StoryNode]:
        """获取主线节点"""
        return [node for node in self.nodes if node.node_type == "main"]
    
    def get_branch_nodes(self) -> List[StoryNode]:
        """获取分支节点"""
        return [node for node in self.nodes if node.node_type == "branch"]
    
    def get_meaningful_nodes(self) -> List[StoryNode]:
        """获取有意义的节点"""
        return [node for node in self.nodes if node.is_meaningful()]
    
    def get_connected_node_ids(self) -> Set[str]:
        """获取所有被连接的节点ID"""
        connected = set()
        for node in self.nodes:
            if node.next_id:
                connected.add(node.next_id)
            for branch in node.branches:
                if branch.entry:
                    connected.add(branch.entry)
                if branch.exit:
                    connected.add(branch.exit)
        return connected
    
    def get_orphaned_nodes(self) -> List[str]:
        """获取孤立节点（除第一个节点外）"""
        if not self.nodes:
            return []
        
        connected = self.get_connected_node_ids()
        first_node_id = self.nodes[0].id
        
        orphaned = []
        for node in self.nodes[1:]:  # 跳过第一个节点
            if node.id not in connected:
                orphaned.append(node.id)
        
        return orphaned
    
    def calculate_statistics(self) -> Dict:
        """计算剧情统计信息"""
        main_nodes = self.get_main_nodes()
        branch_nodes = self.get_branch_nodes()
        meaningful_nodes = self.get_meaningful_nodes()
        orphaned_nodes = self.get_orphaned_nodes()
        
        # 分支统计
        total_branches = sum(len(node.branches) for node in main_nodes)
        nodes_with_branches = sum(1 for node in main_nodes if node.has_branches())
        
        # 内容完整性
        empty_title_count = sum(1 for node in self.nodes 
                               if not node.title or node.title.strip() in ["新节点", "未命名节点", "未命名"])
        empty_content_count = sum(1 for node in self.nodes if not node.content.strip())
        
        return {
            "total_nodes": len(self.nodes),
            "main_nodes": len(main_nodes),
            "branch_nodes": len(branch_nodes),
            "meaningful_nodes": len(meaningful_nodes),
            "total_branches": total_branches,
            "nodes_with_branches": nodes_with_branches,
            "avg_branches": total_branches / nodes_with_branches if nodes_with_branches > 0 else 0,
            "empty_title_count": empty_title_count,
            "empty_content_count": empty_content_count,
            "orphaned_nodes": orphaned_nodes
        }


@dataclass
class FileInfo:
    """文件信息"""
    name: str
    path: Path
    is_directory: bool = False
    is_hidden: bool = False
    file_type: Optional[str] = None
    original_name: Optional[str] = None  # 保存原始文件名（含扩展名）
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.is_directory:
            return f"[DIR] {self.name}"
        return self.name
    
    def get_actual_filename(self) -> str:
        """获取实际文件名（用于文件操作）"""
        return self.original_name if self.original_name else self.name