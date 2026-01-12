"""
配置管理
定义路径、常量等配置信息
"""

import os
from pathlib import Path
from typing import Dict

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "campaigns"

# 分类映射
CATEGORIES = {
    "人物卡": "characters",
    "怪物卡": "monsters",
    "地图": "maps",
    "剧情": "notes"
}

# 文件相关配置
INVALID_FILENAME_CHARS = r'/\:*?"<>|'
HIDDEN_FILES_LIST = ".hidden_files"

# 图片预览最大尺寸
IMAGE_PREVIEW_MAX_WIDTH = 600
IMAGE_PREVIEW_MAX_HEIGHT = 600

# 支持的文件类型
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
SUPPORTED_TEXT_EXTENSIONS = {'.txt', '.md'}
SUPPORTED_JSON_EXTENSIONS = {'.json'}

# 模板内容
TEMPLATES = {
    "characters": """姓名: 
种族: 
职业: 
等级: 
生命值: 
护甲等级: 
技能: 
装备: 
背景: 
""",
    
    "monsters": """名称: 
类型: 
挑战等级: 
护甲等级: 14
生命值: 10
速度: 30
属性: 力量 -1
敏捷+3
体质+0
智力+0
感知+0
魅力-1
技能: 隐匿+5
感官: 黑暗视觉60尺，被动察觉10
语言: 通用语，地精语
特殊能力: 迅捷逃生：附赠撤离或躲藏
动作: 匕首。rd+3+5，1d4+3
轻弩。rd+3+5,  1d8+3
""",
    
    "notes": """# 剧情标题

## 背景
描述剧情背景...

## 主要事件
1. 事件一
2. 事件二

## 重要NPC
- NPC名称：描述

## 奖励
- 经验值：
- 物品：
""",
    
    "json_story": """{
  "title": "新剧情",
  "nodes": [
    {
      "id": "start",
      "type": "main",
      "title": "开始",
      "content": "剧情开始...",
      "next": "node_1",
      "branches": []
    },
    {
      "id": "node_1", 
      "type": "main",
      "title": "第一个场景",
      "content": "描述第一个场景...",
      "next": null,
      "branches": [
        {
          "choice": "选择A",
          "entry": "branch_a",
          "exit": "node_2"
        },
        {
          "choice": "选择B", 
          "entry": "branch_b",
          "exit": "node_2"
        }
      ]
    },
    {
      "id": "branch_a",
      "type": "branch", 
      "title": "分支A",
      "content": "选择A的结果...",
      "next": null,
      "branches": []
    },
    {
      "id": "branch_b",
      "type": "branch",
      "title": "分支B", 
      "content": "选择B的结果...",
      "next": null,
      "branches": []
    },
    {
      "id": "node_2",
      "type": "main",
      "title": "汇合点",
      "content": "两个分支汇合...",
      "next": null,
      "branches": []
    }
  ]
}"""
}


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_template_content(category: str) -> str:
    """获取模板内容"""
    return TEMPLATES.get(category, "")


def get_json_story_template() -> str:
    """获取JSON剧情模板"""
    return TEMPLATES["json_story"]


def is_valid_filename(filename: str) -> bool:
    """检查文件名是否合法"""
    return not any(char in filename for char in INVALID_FILENAME_CHARS)


def get_file_type(file_path: Path) -> str:
    """获取文件类型"""
    suffix = file_path.suffix.lower()
    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    elif suffix in SUPPORTED_TEXT_EXTENSIONS:
        return "text"
    elif suffix in SUPPORTED_JSON_EXTENSIONS:
        return "json"
    else:
        return "unknown"