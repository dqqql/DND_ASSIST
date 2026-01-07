# 🎲 DND 跑团管理器

<div align="center">

![DND Manager](https://img.shields.io/badge/DND-Manager-blue?style=for-the-badge&logo=dungeons-dragons)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<img width="1502" height="940" alt="image" src="https://github.com/user-attachments/assets/d0dc5d67-34ba-4990-9a39-2ec2de0c7afa" />

<img width="1465" height="852" alt="image" src="https://github.com/user-attachments/assets/753b375c-15e0-4278-9743-ad44f36d649c" />

<img width="762" height="1045" alt="image" src="https://github.com/user-attachments/assets/67518806-ae80-44ba-9690-58feb6bf7bc2" />


**一个现代化的 DND 跑团资料管理工具**

集成数据管理 • 剧情可视化 • 现代化界面

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [使用指南](#-使用指南) • [开发](#-开发)

</div>

---

## 📖 项目简介

DND 跑团管理器是一个专为 D&D 游戏主持人（DM）和玩家设计的综合性管理工具。它提供了直观的图形界面，帮助你轻松管理跑团中的所有资料，包括人物卡、怪物数据、地图资源和剧情结构。

### ✨ 核心亮点

- 🎯 **统一管理** - 人物卡、怪物卡、地图、剧情四大分类一站式管理
- 📊 **剧情可视化** - 将复杂的剧情结构转换为交互式流程图
- 🎨 **现代化界面** - 统一的主题系统，响应式布局，流畅的交互体验
- 🔒 **安全删除** - 文件隐藏机制，误删文件可轻松恢复
- 🌐 **多格式支持** - 支持文本、JSON、图片等多种文件格式

---

## 🚀 快速开始

### 环境要求

- Python 3.7 或更高版本
- Windows / macOS / Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/dnd-manager.git
   cd dnd-manager
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python main.py
   ```

4. **创建示例数据**（可选）
   ```bash
   python examples/sample_campaign.py
   ```

---

## 🎯 功能特性

### 📋 跑团管理
- ✅ 创建、切换、删除跑团
- ✅ 自动生成标准文件夹结构
- ✅ 跑团数据完全本地化存储

### 📝 内容管理
- ✅ **人物卡管理** - 标准化模板，快速创建角色档案
- ✅ **怪物卡管理** - 完整的怪物数据库，包含属性、技能、描述
- ✅ **地图管理** - 支持图片导入、预览和组织
- ✅ **剧情管理** - 支持文本笔记和结构化剧情文件

### 🎨 用户体验
- ✅ **现代化主题** - 统一的颜色方案和字体系统
- ✅ **响应式布局** - 基于8px网格的精确对齐
- ✅ **交互反馈** - 悬停效果、点击反馈、状态指示
- ✅ **安全操作** - 删除确认、文件恢复、操作撤销

### 📊 剧情可视化
- ✅ **JSON剧情编辑** - 结构化的剧情节点定义
- ✅ **自动图形生成** - JSON → DOT → SVG 自动转换
- ✅ **交互式预览** - 基于Web的剧情流程图查看器
- ✅ **分支逻辑** - 支持复杂的剧情分支和选择

---

## 📚 使用指南

### 🎲 跑团管理

#### 创建新跑团
1. 启动程序后，点击左侧 **"新建跑团"** 按钮
2. 输入跑团名称（支持中文）
3. 程序自动创建标准文件夹结构：
   ```
   data/campaigns/[跑团名]/
   ├── characters/    # 人物卡
   ├── monsters/      # 怪物卡  
   ├── maps/          # 地图
   └── notes/         # 剧情
   ```

#### 切换跑团
- 在左侧跑团列表中点击选择不同的跑团
- 右侧内容区域会自动切换到对应跑团的数据

### 📝 内容创建

#### 人物卡 & 怪物卡
1. 选择对应分类标签
2. 点击 **"新建文件"** 按钮
3. 输入文件名（无需扩展名）
4. 程序自动生成标准模板：

**人物卡模板**
```
姓名: 
种族: 
职业: 
等级: 
生命值: 
护甲等级: 
技能: 
装备: 
背景: 
```

**怪物卡模板**
```
名称: 
类型: 
挑战等级: 
生命值: 
护甲等级: 
速度: 
属性: 
技能: 
抗性: 
攻击: 
特殊能力: 
描述: 
```

#### 地图管理
1. 选择 **"地图"** 分类
2. 点击 **"导入文件"** 按钮
3. 选择图片文件（支持 JPG、PNG、GIF 等格式）
4. 双击文件名可预览地图

#### 剧情管理

**普通文本剧情**
- 创建 `.txt` 文件，用于记录游戏笔记、背景设定等

**结构化剧情**
- 创建 `.json` 文件，用于定义复杂的剧情流程
- 支持主线节点、分支选择、条件跳转

**JSON剧情格式示例**
```json
{
  "title": "剧情名称",
  "nodes": [
    {
      "id": "start",
      "type": "main",
      "title": "开始",
      "content": "剧情描述...",
      "next": "choice_01",
      "branches": [
        {
          "choice": "选择A",
          "entry": "branch_a",
          "exit": "result_a"
        }
      ]
    }
  ]
}
```

### 📊 剧情可视化

#### 生成预览文件
```bash
# 生成所有剧情的预览
python tools/generate_preview.py

# 或者分步执行
python tools/json_to_dot.py    # JSON → DOT
python tools/dot_to_svg.py     # DOT → SVG
```

#### 查看剧情图
```bash
# 交互式选择剧情
python tools/open_preview.py

# 直接打开指定剧情
python tools/open_preview.py "跑团名" "剧本名" "剧情名"
```

### 🔒 安全功能

#### 文件恢复
- 删除的文件不会立即物理删除，而是添加到隐藏列表
- 点击 **"显示隐藏文件"** 可查看已删除的文件
- 选中隐藏文件后点击 **"恢复文件"** 可恢复

#### 数据备份
- 所有数据存储在 `data/campaigns/` 目录下
- 建议定期备份整个 `data` 文件夹
- 支持跨设备数据迁移

---

## 🛠️ 开发

### 项目结构
```
dnd-manager/
├── main.py                 # 主程序入口
├── start_server.py         # HTTP服务器启动脚本
├── src/                    # 源代码
│   ├── ui/                 # UI系统
│   │   ├── theme_system.py      # 主题系统
│   │   ├── layout_system.py     # 布局系统
│   │   ├── theme_integration.py # 主题集成
│   │   └── theme_utils.py       # 主题工具
│   └── story_editor/       # 剧情编辑器
├── tools/                  # 工具脚本
│   ├── generate_preview.py      # 预览生成
│   ├── json_to_dot.py           # JSON转DOT
│   ├── dot_to_svg.py            # DOT转SVG
│   ├── open_preview.py          # 预览查看器
│   └── preview/                 # Web预览文件
├── data/                   # 用户数据
│   └── campaigns/          # 跑团数据
├── examples/               # 示例文件
│   └── sample_campaign.py      # 示例数据生成器
└── requirements.txt        # 依赖列表
```

### 技术栈
- **GUI框架**: Tkinter (Python标准库)
- **图像处理**: Pillow
- **进程监控**: psutil (可选)
- **图形可视化**: Graphviz (外部依赖)
- **Web预览**: HTML5 + JavaScript + SVG

### 扩展开发

#### 添加新的文件类型
1. 在 `CATEGORIES` 字典中添加新分类
2. 在 `create_file_template()` 方法中添加对应模板
3. 更新UI布局以支持新分类

#### 自定义主题
1. 修改 `src/ui/theme_system.py` 中的 `ColorPalette` 类
2. 调整颜色、字体、间距等参数
3. 重启程序应用新主题

#### 添加新的预览格式
1. 在 `tools/` 目录下创建转换脚本
2. 更新 `generate_preview.py` 集成新的转换流程
3. 修改 `preview.html` 支持新的预览格式

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/your-username/dnd-manager.git
cd dnd-manager

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python examples/sample_campaign.py
python main.py
```

### 提交规范
- 🐛 `fix:` 修复bug
- ✨ `feat:` 新功能
- 📝 `docs:` 文档更新
- 🎨 `style:` 代码格式
- ♻️ `refactor:` 代码重构
- ⚡ `perf:` 性能优化

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI 框架
- [Pillow](https://pillow.readthedocs.io/) - Python 图像处理库
- [Graphviz](https://graphviz.org/) - 图形可视化工具
- [D&D 5e](https://dnd.wizards.com/) - 龙与地下城第五版

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个星标支持！**

Made with ❤️ for D&D enthusiasts


</div>
