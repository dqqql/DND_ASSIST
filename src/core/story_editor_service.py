"""
剧情编辑服务
为 Web 编辑器提供后端服务，处理剧情数据的 CRUD 操作
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from functools import lru_cache
import time
import hashlib

from .models import StoryGraph, StoryNode, StoryBranch
from .story_parser import StoryGraphService
from .campaign import CampaignService


class StoryEditorService:
    """剧情编辑服务"""
    
    def __init__(self, campaign_service: CampaignService):
        self.campaign_service = campaign_service
        self.story_parser = StoryGraphService()
        # 添加文件内容缓存
        self._story_cache = {}
        self._cache_timestamps = {}
        self._file_hashes = {}
    
    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件内容哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _is_cache_valid(self, cache_key: str, file_path: Path) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._story_cache:
            return False
        
        # 检查时间戳（5秒内有效）
        current_time = time.time()
        if current_time - self._cache_timestamps.get(cache_key, 0) > 5.0:
            return False
        
        # 检查文件哈希值
        current_hash = self._get_file_hash(file_path)
        if current_hash != self._file_hashes.get(cache_key, ""):
            return False
        
        return True
    
    def load_story(self, campaign_name: str, story_name: str) -> Optional[Dict[str, Any]]:
        """
        加载剧情数据（带缓存优化）
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            
        Returns:
            Dict: 剧情数据，失败返回 None
        """
        try:
            # 选择跑团
            campaign = self.campaign_service.select_campaign(campaign_name)
            if not campaign:
                return None
            
            # 构建文件路径
            story_path = campaign.get_notes_path() / f"{story_name}.json"
            if not story_path.exists():
                return None
            
            # 检查缓存
            cache_key = f"{campaign_name}:{story_name}"
            if self._is_cache_valid(cache_key, story_path):
                return self._story_cache[cache_key]
            
            # 读取文件
            with open(story_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新缓存
            self._story_cache[cache_key] = data
            self._cache_timestamps[cache_key] = time.time()
            self._file_hashes[cache_key] = self._get_file_hash(story_path)
            
            return data
            
        except Exception as e:
            print(f"加载剧情失败: {e}")
            return None
    
    def save_story(self, campaign_name: str, story_name: str, story_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        保存剧情数据
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            story_data: 剧情数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        try:
            # 选择跑团
            campaign = self.campaign_service.select_campaign(campaign_name)
            if not campaign:
                return False, "跑团不存在"
            
            # 快速验证数据格式（优化版本）
            validation_result = self._quick_validate_story_data(story_data)
            if not validation_result[0]:
                return False, f"数据验证失败: {validation_result[1]}"
            
            # 构建文件路径
            story_path = campaign.get_notes_path() / f"{story_name}.json"
            
            # 备份原文件（如果存在）
            backup_path = None
            if story_path.exists():
                backup_path = story_path.with_suffix('.json.backup')
                story_path.rename(backup_path)
            
            try:
                # 保存新文件
                with open(story_path, 'w', encoding='utf-8') as f:
                    json.dump(story_data, f, ensure_ascii=False, indent=2)
                
                # 删除备份文件
                if backup_path and backup_path.exists():
                    backup_path.unlink()
                
                # 更新缓存
                cache_key = f"{campaign_name}:{story_name}"
                self._story_cache[cache_key] = story_data
                self._cache_timestamps[cache_key] = time.time()
                self._file_hashes[cache_key] = self._get_file_hash(story_path)
                
                return True, "保存成功"
                
            except Exception as e:
                # 保存失败，恢复备份
                if backup_path and backup_path.exists():
                    backup_path.rename(story_path)
                raise e
                
        except Exception as e:
            print(f"保存剧情失败: {e}")
            return False, f"保存失败: {str(e)}"
    
    def _quick_validate_story_data(self, story_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        快速验证剧情数据格式（优化版本）
        
        Args:
            story_data: 剧情数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 基本结构检查
            if not isinstance(story_data, dict):
                return False, "数据必须是字典格式"
            
            if 'title' not in story_data:
                return False, "缺少 title 字段"
            
            if 'nodes' not in story_data:
                return False, "缺少 nodes 字段"
            
            nodes = story_data['nodes']
            if not isinstance(nodes, list):
                return False, "nodes 必须是数组格式"
            
            # 快速检查节点ID唯一性
            node_ids = set()
            for i, node in enumerate(nodes):
                if not isinstance(node, dict):
                    return False, f"节点 {i} 必须是字典格式"
                
                node_id = node.get('id')
                if not node_id or not isinstance(node_id, str):
                    return False, f"节点 {i} 的 id 必须是非空字符串"
                
                if node_id in node_ids:
                    return False, f"节点 ID '{node_id}' 重复"
                node_ids.add(node_id)
            
            return True, "验证通过"
            
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"
    
    def validate_story_data(self, story_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        验证剧情数据格式
        
        Args:
            story_data: 剧情数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 检查基本结构
            if not isinstance(story_data, dict):
                return False, "数据必须是字典格式"
            
            if 'title' not in story_data:
                return False, "缺少 title 字段"
            
            if 'nodes' not in story_data:
                return False, "缺少 nodes 字段"
            
            if not isinstance(story_data['nodes'], list):
                return False, "nodes 必须是数组格式"
            
            # 检查节点格式
            node_ids = set()
            for i, node in enumerate(story_data['nodes']):
                if not isinstance(node, dict):
                    return False, f"节点 {i} 必须是字典格式"
                
                # 检查必需字段
                if 'id' not in node:
                    return False, f"节点 {i} 缺少 id 字段"
                
                node_id = node['id']
                if not node_id or not isinstance(node_id, str):
                    return False, f"节点 {i} 的 id 必须是非空字符串"
                
                # 检查 ID 重复
                if node_id in node_ids:
                    return False, f"节点 ID '{node_id}' 重复"
                node_ids.add(node_id)
                
                # 检查节点类型
                node_type = node.get('type', 'main')
                if node_type not in ['main', 'branch']:
                    return False, f"节点 '{node_id}' 的类型必须是 'main' 或 'branch'"
                
                # 检查分支格式
                if 'branches' in node:
                    if not isinstance(node['branches'], list):
                        return False, f"节点 '{node_id}' 的 branches 必须是数组格式"
                    
                    for j, branch in enumerate(node['branches']):
                        if not isinstance(branch, dict):
                            return False, f"节点 '{node_id}' 的分支 {j} 必须是字典格式"
                        
                        if 'choice' not in branch:
                            return False, f"节点 '{node_id}' 的分支 {j} 缺少 choice 字段"
            
            # 检查节点引用
            for node in story_data['nodes']:
                node_id = node['id']
                
                # 检查 next 引用
                if 'next' in node and node['next']:
                    if node['next'] not in node_ids:
                        return False, f"节点 '{node_id}' 引用了不存在的节点 '{node['next']}'"
                
                # 检查分支引用
                if 'branches' in node:
                    for j, branch in enumerate(node['branches']):
                        if 'entry' in branch and branch['entry']:
                            if branch['entry'] not in node_ids:
                                return False, f"节点 '{node_id}' 的分支 {j} 引用了不存在的入口节点 '{branch['entry']}'"
                        
                        if 'exit' in branch and branch['exit']:
                            if branch['exit'] not in node_ids:
                                return False, f"节点 '{node_id}' 的分支 {j} 引用了不存在的出口节点 '{branch['exit']}'"
            
            return True, "验证通过"
            
        except Exception as e:
            return False, f"验证过程出错: {str(e)}"
    
    def create_new_story(self, title: str = "新剧情") -> Dict[str, Any]:
        """
        创建新剧情数据
        
        Args:
            title: 剧情标题
            
        Returns:
            Dict: 新剧情数据
        """
        return {
            "title": title,
            "nodes": []
        }
    
    def add_node(self, story_data: Dict[str, Any], node_type: str = "main") -> Dict[str, Any]:
        """
        添加新节点
        
        Args:
            story_data: 剧情数据
            node_type: 节点类型 ('main' 或 'branch')
            
        Returns:
            Dict: 新节点数据
        """
        node_count = len(story_data.get('nodes', []))
        new_node = {
            "id": f"node_{node_count + 1:02d}",
            "type": node_type,
            "title": "新节点",
            "content": "",
            "next": None
        }
        
        if node_type == "main":
            new_node["branches"] = []
        
        story_data.setdefault('nodes', []).append(new_node)
        return new_node
    
    def delete_node(self, story_data: Dict[str, Any], node_id: str) -> bool:
        """
        删除节点
        
        Args:
            story_data: 剧情数据
            node_id: 节点ID
            
        Returns:
            bool: 是否成功删除
        """
        nodes = story_data.get('nodes', [])
        
        # 找到并删除节点
        node_index = None
        for i, node in enumerate(nodes):
            if node.get('id') == node_id:
                node_index = i
                break
        
        if node_index is None:
            return False
        
        # 删除节点
        del nodes[node_index]
        
        # 清理引用
        self._cleanup_node_references(story_data, node_id)
        
        return True
    
    def _cleanup_node_references(self, story_data: Dict[str, Any], deleted_id: str):
        """清理被删除节点的引用"""
        for node in story_data.get('nodes', []):
            # 清理 next 引用
            if node.get('next') == deleted_id:
                node['next'] = None
            
            # 清理分支引用
            if 'branches' in node:
                for branch in node['branches']:
                    if branch.get('entry') == deleted_id:
                        branch['entry'] = ""
                    if branch.get('exit') == deleted_id:
                        branch['exit'] = ""
    
    def get_node_options(self, story_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        获取节点选项列表（用于下拉框）
        
        Args:
            story_data: 剧情数据
            
        Returns:
            List[Dict]: 节点选项列表
        """
        options = [{"id": "", "label": "无"}]
        
        for node in story_data.get('nodes', []):
            node_id = node.get('id', '')
            node_title = node.get('title', '未命名')
            options.append({
                "id": node_id,
                "label": f"{node_id}: {node_title}"
            })
        
        return options
    
    def get_story_statistics(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取剧情统计信息
        
        Args:
            story_data: 剧情数据
            
        Returns:
            Dict: 统计信息
        """
        try:
            # 转换为 StoryGraph 对象进行统计
            story_graph = self.story_parser.parse_story_data(story_data)
            return story_graph.calculate_statistics()
        except Exception:
            # 如果解析失败，返回基本统计
            nodes = story_data.get('nodes', [])
            return {
                "total_nodes": len(nodes),
                "main_nodes": len([n for n in nodes if n.get('type') == 'main']),
                "branch_nodes": len([n for n in nodes if n.get('type') == 'branch']),
                "meaningful_nodes": len([n for n in nodes if n.get('title', '').strip() and n.get('title') not in ['新节点', '未命名']]),
                "total_branches": sum(len(n.get('branches', [])) for n in nodes),
                "nodes_with_branches": len([n for n in nodes if n.get('branches')]),
                "avg_branches": 0,
                "empty_title_count": len([n for n in nodes if not n.get('title', '').strip() or n.get('title') in ['新节点', '未命名']]),
                "empty_content_count": len([n for n in nodes if not n.get('content', '').strip()]),
                "orphaned_nodes": []
            }
    
    def list_available_stories(self, campaign_name: str) -> List[str]:
        """
        列出可用的剧情文件
        
        Args:
            campaign_name: 跑团名称
            
        Returns:
            List[str]: 剧情文件名列表（不含扩展名）
        """
        try:
            campaign = self.campaign_service.select_campaign(campaign_name)
            if not campaign:
                return []
            
            notes_path = campaign.get_notes_path()
            if not notes_path.exists():
                return []
            
            stories = []
            for file_path in notes_path.glob("*.json"):
                stories.append(file_path.stem)
            
            return sorted(stories)
            
        except Exception:
            return []