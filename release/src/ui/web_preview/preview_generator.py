"""
预览生成器
负责生成剧情预览所需的 SVG 文件
与核心逻辑层交互，但不直接暴露给 UI 层
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple


class PreviewGenerator:
    """预览文件生成器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化生成器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent
        
        self.project_root = project_root
        self.tools_dir = project_root / "tools"
    
    def generate_preview_for_story(self, campaign_name: str, story_name: str) -> bool:
        """
        为指定剧情生成预览文件
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            
        Returns:
            bool: 生成是否成功
        """
        story_dir = self.project_root / "data" / "campaigns" / campaign_name / "notes"
        json_path = story_dir / f"{story_name}.json"
        
        if not json_path.exists():
            return False
        
        # 生成 DOT 文件
        dot_success = self._generate_dot_file(json_path)
        if not dot_success:
            return False
        
        # 生成 SVG 文件
        dot_path = json_path.with_suffix('.dot')
        svg_success = self._generate_svg_file(dot_path)
        
        return svg_success
    
    def _generate_dot_file(self, json_path: Path) -> bool:
        """
        生成 DOT 文件
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            bool: 生成是否成功
        """
        try:
            dot_path = json_path.with_suffix('.dot')
            
            # 调用 json_to_dot.py 工具
            cmd = [
                sys.executable,
                str(self.tools_dir / "json_to_dot.py"),
                str(json_path),
                str(dot_path)
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0 and dot_path.exists()
            
        except Exception:
            return False
    
    def _generate_svg_file(self, dot_path: Path) -> bool:
        """
        生成 SVG 文件
        
        Args:
            dot_path: DOT 文件路径
            
        Returns:
            bool: 生成是否成功
        """
        try:
            svg_path = dot_path.with_suffix('.svg')
            
            # 调用 dot_to_svg.py 工具
            cmd = [
                sys.executable,
                str(self.tools_dir / "dot_to_svg.py"),
                str(dot_path),
                str(svg_path)
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0 and svg_path.exists()
            
        except Exception:
            return False
    
    def check_preview_files_exist(self, campaign_name: str, story_name: str) -> Tuple[bool, bool]:
        """
        检查预览文件是否存在
        
        Args:
            campaign_name: 跑团名称
            story_name: 剧情名称
            
        Returns:
            Tuple[bool, bool]: (DOT文件存在, SVG文件存在)
        """
        story_dir = self.project_root / "data" / "campaigns" / campaign_name / "notes"
        dot_path = story_dir / f"{story_name}.dot"
        svg_path = story_dir / f"{story_name}.svg"
        
        return dot_path.exists(), svg_path.exists()
    
    def list_available_stories(self) -> List[Tuple[str, str]]:
        """
        列出所有可用的剧情
        
        Returns:
            List[Tuple[str, str]]: (跑团名, 剧情名) 的列表
        """
        campaigns_dir = self.project_root / "data" / "campaigns"
        
        if not campaigns_dir.exists():
            return []
        
        stories = []
        for campaign_dir in campaigns_dir.iterdir():
            if campaign_dir.is_dir():
                notes_dir = campaign_dir / "notes"
                if notes_dir.exists():
                    for json_file in notes_dir.glob("*.json"):
                        story_name = json_file.stem
                        stories.append((campaign_dir.name, story_name))
        
        return sorted(stories)
    
    def generate_all_missing_previews(self) -> Tuple[int, int]:
        """
        为所有缺少预览文件的剧情生成预览
        
        Returns:
            Tuple[int, int]: (成功数量, 总数量)
        """
        stories = self.list_available_stories()
        success_count = 0
        
        for campaign_name, story_name in stories:
            dot_exists, svg_exists = self.check_preview_files_exist(campaign_name, story_name)
            
            if not svg_exists:  # 如果 SVG 不存在，尝试生成
                if self.generate_preview_for_story(campaign_name, story_name):
                    success_count += 1
        
        return success_count, len(stories)