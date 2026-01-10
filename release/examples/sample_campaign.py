#!/usr/bin/env python3
"""
示例跑团数据生成器
创建一个完整的示例跑团，包含人物卡、怪物卡、地图和剧情
"""

import os
import json
import shutil
from pathlib import Path


def create_sample_campaign():
    """创建示例跑团数据"""
    
    # 基础路径
    base_dir = Path(__file__).parent.parent
    campaign_dir = base_dir / "data" / "campaigns" / "失落的矿坑"
    
    # 创建目录结构
    for category in ["characters", "monsters", "maps", "notes"]:
        (campaign_dir / category).mkdir(parents=True, exist_ok=True)
    
    # 创建人物卡
    character_template = """姓名: {name}
种族: {race}
职业: {class_name}
等级: {level}
生命值: {hp}
护甲等级: {ac}
技能: {skills}
装备: {equipment}
背景: {background}
"""
    
    characters = [
        {
            "name": "艾莉娅·月影",
            "race": "精灵",
            "class_name": "游侠",
            "level": "3",
            "hp": "28",
            "ac": "15",
            "skills": "射击、追踪、野外生存、隐匿",
            "equipment": "长弓、皮甲、匕首、探险包",
            "background": "来自月光森林的精灵游侠，擅长追踪和射击。因为家园被邪恶势力侵犯而踏上冒险之路。"
        },
        {
            "name": "格里姆·铁锤",
            "race": "矮人",
            "class_name": "战士",
            "level": "3",
            "hp": "35",
            "ac": "18",
            "skills": "重武器、防御、锻造、战术",
            "equipment": "战锤、板甲、盾牌、锻造工具",
            "background": "来自铁山氏族的矮人战士，以勇猛和忠诚著称。正在寻找失落的矮人宝藏。"
        }
    ]
    
    for char in characters:
        char_file = campaign_dir / "characters" / f"{char['name']}.txt"
        char_file.write_text(character_template.format(**char), encoding='utf-8')
    
    # 创建怪物卡
    monster_template = """名称: {name}
类型: {type}
挑战等级: {cr}
生命值: {hp}
护甲等级: {ac}
速度: {speed}
属性: {stats}
技能: {skills}
抗性: {resistances}
攻击: {attacks}
特殊能力: {abilities}
描述: {description}
"""
    
    monsters = [
        {
            "name": "矿坑蜘蛛",
            "type": "野兽",
            "cr": "1/2",
            "hp": "26 (4d8+8)",
            "ac": "14",
            "speed": "30尺，攀爬30尺",
            "stats": "力量14，敏捷16，体质15，智力2，感知11，魅力4",
            "skills": "隐匿+7",
            "resistances": "无",
            "attacks": "咬击 +5命中，伤害1d8+3穿刺伤害，目标需进行DC11体质豁免，失败则中毒1小时",
            "abilities": "蛛网感知、攀爬",
            "description": "生活在废弃矿坑中的巨型蜘蛛，以小动物和迷路的冒险者为食。"
        },
        {
            "name": "骷髅矿工",
            "type": "不死生物",
            "cr": "1/4",
            "hp": "13 (2d8+4)",
            "ac": "13",
            "speed": "30尺",
            "stats": "力量10，敏捷14，体质15，智力6，感知8，魅力5",
            "skills": "无",
            "resistances": "免疫毒素和魅惑",
            "attacks": "镐头 +4命中，伤害1d6+2钝击伤害",
            "abilities": "黑暗视觉60尺",
            "description": "死在矿坑中的矿工，被邪恶力量复活，永远重复着挖掘的动作。"
        }
    ]
    
    for monster in monsters:
        monster_file = campaign_dir / "monsters" / f"{monster['name']}.txt"
        monster_file.write_text(monster_template.format(**monster), encoding='utf-8')
    
    # 创建剧情文件
    story_json = {
        "title": "失落的矿坑",
        "description": "一个关于废弃矿坑中隐藏秘密的冒险故事",
        "nodes": [
            {
                "id": "start",
                "type": "main",
                "title": "矿坑入口",
                "content": "你们来到了传说中的失落矿坑入口。这里曾经是繁荣的矿场，但现在只剩下破败的建筑和诡异的寂静。入口处有两条路径。",
                "next": "choice_01",
                "branches": [
                    {
                        "choice": "走左边的主通道",
                        "entry": "left_path",
                        "exit": "spider_encounter"
                    },
                    {
                        "choice": "走右边的小径",
                        "entry": "right_path", 
                        "exit": "skeleton_encounter"
                    }
                ]
            },
            {
                "id": "left_path",
                "type": "branch",
                "title": "主通道",
                "content": "主通道宽阔但昏暗，墙壁上还能看到当年矿工留下的工具痕迹。空气中弥漫着潮湿和腐朽的味道。",
                "next": "spider_encounter"
            },
            {
                "id": "right_path", 
                "type": "branch",
                "title": "小径",
                "content": "小径狭窄崎岖，似乎是后来开凿的。地面上散落着一些骨头碎片，让人不安。",
                "next": "skeleton_encounter"
            },
            {
                "id": "spider_encounter",
                "type": "main",
                "title": "蜘蛛巢穴",
                "content": "你们进入了一个宽阔的洞穴，天花板上挂满了蛛网。突然，几只巨大的矿坑蜘蛛从阴影中爬出！",
                "next": "treasure_room"
            },
            {
                "id": "skeleton_encounter", 
                "type": "main",
                "title": "骷髅矿工",
                "content": "在一个废弃的工作面前，几具骷髅矿工仍在机械地挥舞着镐头。它们注意到了你们的到来！",
                "next": "treasure_room"
            },
            {
                "id": "treasure_room",
                "type": "main", 
                "title": "宝藏室",
                "content": "经过战斗后，你们发现了矿坑深处的秘密宝藏室。这里存放着珍贵的矿石和古老的魔法物品。",
                "next": "end"
            },
            {
                "id": "end",
                "type": "main",
                "title": "冒险结束",
                "content": "你们成功探索了失落的矿坑，获得了丰厚的奖励。但这只是更大冒险的开始...",
                "next": None
            }
        ]
    }
    
    story_file = campaign_dir / "notes" / "失落的矿坑.json"
    story_file.write_text(json.dumps(story_json, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 创建普通剧情笔记
    notes_content = """# 失落的矿坑 - 游戏笔记

## 背景设定
- 矿坑废弃已有50年
- 曾经是王国最重要的铁矿来源
- 突然有一天所有矿工都消失了
- 当地人传说矿坑被诅咒

## 重要NPC
- **老矿工汤姆**：唯一的幸存者，知道矿坑的秘密
- **村长玛丽**：委托冒险者调查矿坑的真相
- **神秘法师**：幕后黑手，操控着不死生物

## 关键线索
1. 矿坑深处有古老的魔法阵
2. 矿工们被转化为不死生物
3. 宝藏室中藏着封印法师的神器

## 奖励
- 经验值：每人300XP
- 金币：每人50金币
- 魔法物品：+1武器或护甲（随机）
"""
    
    notes_file = campaign_dir / "notes" / "游戏笔记.txt"
    notes_file.write_text(notes_content, encoding='utf-8')
    
    print("示例跑团 '失落的矿坑' 创建完成！")
    print(f"位置: {campaign_dir}")
    print("包含: 2个人物卡, 2个怪物卡, 1个剧情文件, 1个笔记文件")


if __name__ == "__main__":
    create_sample_campaign()