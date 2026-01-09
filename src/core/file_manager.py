"""
文件管理服务
处理文件的创建、删除、导入、列表等操作
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict

from .models import Campaign, FileInfo
from .config import (
    get_template_content, get_json_story_template, 
    is_valid_filename, get_file_type,
    SUPPORTED_IMAGE_EXTENSIONS, SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_JSON_EXTENSIONS
)


class FileManagerService:
    """文件管理服务"""
    
    def __init__(self, campaign_service):
        """初始化文件管理服务
        
        Args:
            campaign_service: 跑团管理服务实例
        """
        self.campaign_service = campaign_service
    
    def list_files(self, category: str, sub_path: str = "") -> List[FileInfo]:
        """获取文件列表
        
        Args:
            category: 分类名称
            sub_path: 子路径（用于notes分类）
            
        Returns:
            List[FileInfo]: 文件信息列表
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return []
        
        # 构建目标路径
        if category == "notes" and sub_path:
            target_path = campaign.get_notes_path(sub_path)
        else:
            target_path = campaign.get_category_path(category)
        
        if not target_path.exists():
            return []
        
        files = []
        hidden_key = f"{category}:{sub_path}" if category == "notes" and sub_path else category
        hidden_files = self.campaign_service.get_hidden_files_for_category(campaign, hidden_key)
        
        try:
            for item in target_path.iterdir():
                # 跳过隐藏文件
                if item.name in hidden_files:
                    continue
                
                # 跳过系统隐藏文件
                if item.name.startswith('.'):
                    continue
                
                # 对于notes分类，进行特殊过滤
                if category == "notes":
                    if item.is_dir():
                        # 目录始终显示
                        file_info = FileInfo(
                            name=item.name,
                            path=item,
                            is_directory=True,
                            file_type=None
                        )
                        files.append(file_info)
                    elif item.suffix.lower() == '.json':
                        # 只显示JSON文件，且去掉后缀
                        display_name = item.stem  # 不含扩展名的文件名
                        file_info = FileInfo(
                            name=display_name,
                            path=item,
                            is_directory=False,
                            file_type="json"
                        )
                        # 保存原始文件名用于后续操作
                        file_info.original_name = item.name
                        files.append(file_info)
                else:
                    # 其他分类保持原有逻辑
                    file_info = FileInfo(
                        name=item.name,
                        path=item,
                        is_directory=item.is_dir(),
                        file_type=get_file_type(item) if item.is_file() else None
                    )
                    files.append(file_info)
        except Exception:
            return []
        
        # 排序：目录在前，然后按名称排序
        files.sort(key=lambda x: (not x.is_directory, x.name.lower()))
        return files
    
    def create_file(self, category: str, filename: str, sub_path: str = "") -> bool:
        """创建文件
        
        Args:
            category: 分类名称
            filename: 文件名（不含扩展名）
            sub_path: 子路径（用于notes分类）
            
        Returns:
            bool: 创建是否成功
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return False
        
        # 验证文件名
        if not filename or not filename.strip() or not is_valid_filename(filename):
            return False
        
        filename = filename.strip()
        
        # 根据分类确定文件类型和扩展名
        if category == "notes":
            # notes分类支持txt和json
            if filename.endswith('.json'):
                file_type = "json"
                full_filename = filename
            else:
                file_type = "txt"
                full_filename = filename + ".txt" if not filename.endswith('.txt') else filename
        else:
            # 其他分类默认为txt
            file_type = "txt"
            full_filename = filename + ".txt" if not filename.endswith('.txt') else filename
        
        # 构建目标路径
        if category == "notes" and sub_path:
            target_dir = campaign.get_notes_path(sub_path)
        else:
            target_dir = campaign.get_category_path(category)
        
        # 确保目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / full_filename
        
        # 检查文件是否已存在
        if file_path.exists():
            return False
        
        try:
            # 获取模板内容
            if file_type == "json":
                content = get_json_story_template()
            else:
                content = get_template_content(category)
            
            # 创建文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception:
            return False
    
    def delete_file(self, category: str, display_name: str, sub_path: str = "") -> bool:
        """删除文件（软删除，添加到隐藏列表）
        
        Args:
            category: 分类名称
            display_name: 显示名称（可能是去掉扩展名的）
            sub_path: 子路径（用于notes分类）
            
        Returns:
            bool: 删除是否成功
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return False
        
        # 构建隐藏键
        hidden_key = f"{category}:{sub_path}" if category == "notes" and sub_path else category
        
        # 对于notes分类，需要还原实际文件名
        if category == "notes" and not display_name.startswith("[DIR] "):
            # 获取实际文件名
            actual_filename = f"{display_name}.json"
        else:
            # 其他分类或目录，使用显示名称
            actual_filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
        
        # 添加到隐藏列表
        return self.campaign_service.add_hidden_file(campaign, hidden_key, actual_filename)
    
    def restore_file(self, category: str, filename: str, sub_path: str = "") -> bool:
        """恢复文件（从隐藏列表移除）
        
        Args:
            category: 分类名称
            filename: 文件名
            sub_path: 子路径（用于notes分类）
            
        Returns:
            bool: 恢复是否成功
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return False
        
        # 构建隐藏键
        hidden_key = f"{category}:{sub_path}" if category == "notes" and sub_path else category
        
        # 从隐藏列表移除
        return self.campaign_service.remove_hidden_file(campaign, hidden_key, filename)
    
    def import_file(self, category: str, source_path: str, sub_path: str = "") -> bool:
        """导入文件
        
        Args:
            category: 分类名称
            source_path: 源文件路径
            sub_path: 子路径（用于notes分类）
            
        Returns:
            bool: 导入是否成功
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return False
        
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            return False
        
        # 构建目标路径
        if category == "notes" and sub_path:
            target_dir = campaign.get_notes_path(sub_path)
        else:
            target_dir = campaign.get_category_path(category)
        
        # 确保目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source.name
        
        # 检查是否已存在
        if target_path.exists():
            return False
        
        try:
            shutil.copy2(source, target_path)
            return True
        except Exception:
            return False
    
    def read_text_file(self, file_path: Path) -> Optional[str]:
        """读取文本文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: 文件内容，失败返回None
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def get_file_path(self, category: str, display_name: str, sub_path: str = "") -> Optional[Path]:
        """获取文件完整路径
        
        Args:
            category: 分类名称
            display_name: 显示名称（可能是去掉扩展名的）
            sub_path: 子路径（用于notes分类）
            
        Returns:
            Optional[Path]: 文件路径，失败返回None
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return None
        
        # 构建目标目录
        if category == "notes" and sub_path:
            target_dir = campaign.get_notes_path(sub_path)
        else:
            target_dir = campaign.get_category_path(category)
        
        # 对于notes分类，需要还原完整文件名
        if category == "notes" and not display_name.startswith("[DIR] "):
            # 尝试找到对应的JSON文件
            json_file = target_dir / f"{display_name}.json"
            if json_file.exists():
                return json_file
            # 如果没找到，可能是完整文件名
            direct_file = target_dir / display_name
            if direct_file.exists():
                return direct_file
        else:
            # 其他分类或目录，直接使用显示名称
            filename = display_name.replace("[DIR] ", "") if display_name.startswith("[DIR] ") else display_name
            file_path = target_dir / filename
            return file_path if file_path.exists() else None
        
        return None
    
    def is_supported_file_type(self, file_path: Path, category: str) -> bool:
        """检查文件类型是否受支持
        
        Args:
            file_path: 文件路径
            category: 分类名称
            
        Returns:
            bool: 是否支持
        """
        suffix = file_path.suffix.lower()
        
        if category == "maps":
            return suffix in SUPPORTED_IMAGE_EXTENSIONS
        elif category in ["characters", "monsters", "notes"]:
            return suffix in SUPPORTED_TEXT_EXTENSIONS or suffix in SUPPORTED_JSON_EXTENSIONS
        
        return False
    
    def get_hidden_files(self, category: str, sub_path: str = "") -> List[str]:
        """获取隐藏文件列表
        
        Args:
            category: 分类名称
            sub_path: 子路径（用于notes分类）
            
        Returns:
            List[str]: 隐藏文件名列表
        """
        campaign = self.campaign_service.get_current_campaign()
        if not campaign:
            return []
        
        hidden_key = f"{category}:{sub_path}" if category == "notes" and sub_path else category
        hidden_files = self.campaign_service.get_hidden_files_for_category(campaign, hidden_key)
        
        return sorted(list(hidden_files))
    
    def read_file_content(self, category: str, display_name: str, sub_path: str = "") -> Optional[str]:
        """读取文件内容
        
        Args:
            category: 分类名称
            display_name: 显示名称（可能是去掉扩展名的）
            sub_path: 子路径（用于notes分类）
            
        Returns:
            Optional[str]: 文件内容，失败返回None
        """
        file_path = self.get_file_path(category, display_name, sub_path)
        if not file_path:
            return None
        
        return self.read_text_file(file_path)