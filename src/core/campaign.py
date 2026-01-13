"""
跑团管理服务
处理跑团的创建、删除、选择等操作
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Set
from functools import lru_cache

from .models import Campaign
from .config import DATA_DIR, CATEGORIES, HIDDEN_FILES_LIST, ensure_data_dir


class CampaignService:
    """跑团管理服务"""
    
    def __init__(self):
        ensure_data_dir()
        self._current_campaign: Optional[Campaign] = None
        # 添加缓存以提高性能
        self._campaigns_cache = None
        self._cache_timestamp = 0
    
    def get_current_campaign(self) -> Optional[Campaign]:
        """获取当前选中的跑团"""
        return self._current_campaign
    
    def list_campaigns(self) -> List[str]:
        """获取所有跑团列表（带缓存优化）"""
        if not DATA_DIR.exists():
            return []
        
        # 检查缓存是否有效（1秒内）
        import time
        current_time = time.time()
        if (self._campaigns_cache is not None and 
            current_time - self._cache_timestamp < 1.0):
            return self._campaigns_cache
        
        campaigns = []
        for item in DATA_DIR.iterdir():
            if item.is_dir():
                campaigns.append(item.name)
        
        campaigns = sorted(campaigns)
        
        # 更新缓存
        self._campaigns_cache = campaigns
        self._cache_timestamp = current_time
        
        return campaigns
    
    def _invalidate_cache(self):
        """使缓存失效"""
        self._campaigns_cache = None
        self._cache_timestamp = 0
    
    def create_campaign(self, name: str) -> bool:
        """创建新跑团
        
        Args:
            name: 跑团名称
            
        Returns:
            bool: 创建是否成功
        """
        if not name or not name.strip():
            return False
        
        campaign_path = DATA_DIR / name.strip()
        
        # 检查是否已存在
        if campaign_path.exists():
            return False
        
        try:
            # 创建跑团目录
            campaign_path.mkdir(parents=True)
            
            # 创建分类子目录
            for category in CATEGORIES.values():
                (campaign_path / category).mkdir()
            
            # 使缓存失效
            self._invalidate_cache()
            
            return True
        except Exception:
            # 创建失败时清理
            if campaign_path.exists():
                shutil.rmtree(campaign_path, ignore_errors=True)
            return False
    
    def delete_campaign(self, name: str) -> bool:
        """删除跑团
        
        Args:
            name: 跑团名称
            
        Returns:
            bool: 删除是否成功
        """
        if not name:
            return False
        
        campaign_path = DATA_DIR / name
        
        if not campaign_path.exists():
            return False
        
        try:
            shutil.rmtree(campaign_path)
            
            # 如果删除的是当前跑团，清空当前选择
            if self._current_campaign and self._current_campaign.name == name:
                self._current_campaign = None
            
            # 使缓存失效
            self._invalidate_cache()
            
            return True
        except Exception:
            return False
    
    def select_campaign(self, name: str) -> Optional[Campaign]:
        """选择跑团
        
        Args:
            name: 跑团名称
            
        Returns:
            Campaign: 跑团对象，失败返回None
        """
        if not name:
            return None
        
        campaign_path = DATA_DIR / name
        
        if not campaign_path.exists():
            return None
        
        # 创建跑团对象
        campaign = Campaign(name=name, path=campaign_path)
        
        # 加载隐藏文件列表
        campaign.hidden_files = self._load_hidden_files(campaign_path)
        
        self._current_campaign = campaign
        return campaign
    
    def _load_hidden_files(self, campaign_path: Path) -> Dict[str, Set[str]]:
        """加载隐藏文件列表
        
        Args:
            campaign_path: 跑团路径
            
        Returns:
            Dict[str, Set[str]]: 隐藏文件映射
        """
        hidden_files = {}
        hidden_file_path = campaign_path / HIDDEN_FILES_LIST
        
        if not hidden_file_path.exists():
            return hidden_files
        
        try:
            with open(hidden_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line:
                        key, filename = line.split(':', 1)
                        if key not in hidden_files:
                            hidden_files[key] = set()
                        hidden_files[key].add(filename)
        except Exception:
            # 读取失败时返回空字典
            pass
        
        return hidden_files
    
    def save_hidden_files(self, campaign: Campaign) -> bool:
        """保存隐藏文件列表
        
        Args:
            campaign: 跑团对象
            
        Returns:
            bool: 保存是否成功
        """
        if not campaign:
            return False
        
        hidden_file_path = campaign.path / HIDDEN_FILES_LIST
        
        try:
            with open(hidden_file_path, 'w', encoding='utf-8') as f:
                for key, filenames in campaign.hidden_files.items():
                    for filename in filenames:
                        f.write(f"{key}:{filename}\n")
            return True
        except Exception:
            return False
    
    def add_hidden_file(self, campaign: Campaign, category_key: str, filename: str) -> bool:
        """添加隐藏文件
        
        Args:
            campaign: 跑团对象
            category_key: 分类键
            filename: 文件名
            
        Returns:
            bool: 操作是否成功
        """
        if not campaign or not category_key or not filename:
            return False
        
        if category_key not in campaign.hidden_files:
            campaign.hidden_files[category_key] = set()
        
        campaign.hidden_files[category_key].add(filename)
        return self.save_hidden_files(campaign)
    
    def remove_hidden_file(self, campaign: Campaign, category_key: str, filename: str) -> bool:
        """移除隐藏文件
        
        Args:
            campaign: 跑团对象
            category_key: 分类键
            filename: 文件名
            
        Returns:
            bool: 操作是否成功
        """
        if not campaign or not category_key or not filename:
            return False
        
        if category_key not in campaign.hidden_files:
            return True
        
        campaign.hidden_files[category_key].discard(filename)
        
        # 如果集合为空，删除键
        if not campaign.hidden_files[category_key]:
            del campaign.hidden_files[category_key]
        
        return self.save_hidden_files(campaign)
    
    def is_file_hidden(self, campaign: Campaign, category_key: str, filename: str) -> bool:
        """检查文件是否被隐藏
        
        Args:
            campaign: 跑团对象
            category_key: 分类键
            filename: 文件名
            
        Returns:
            bool: 是否被隐藏
        """
        if not campaign or not category_key or not filename:
            return False
        
        return (category_key in campaign.hidden_files and 
                filename in campaign.hidden_files[category_key])
    
    def get_hidden_files_for_category(self, campaign: Campaign, category_key: str) -> Set[str]:
        """获取指定分类的隐藏文件列表
        
        Args:
            campaign: 跑团对象
            category_key: 分类键
            
        Returns:
            Set[str]: 隐藏文件集合
        """
        if not campaign or not category_key:
            return set()
        
        return campaign.hidden_files.get(category_key, set())