<h1 style="text-align: center;">🎲 DND 跑团管理器</h1>


<div align="center">

![DND Manager](https://img.shields.io/badge/DND-Manager-blue?style=for-the-badge&logo=dungeons-dragons)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**一个现代化的 DND 跑团资料管理工具**

集成数据管理 • 剧情可视化 • Web编辑器 • 现代化界面

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [使用指南](#-使用指南) • [开发](#-开发)

</div>

<img width="2560" height="1229" alt="image" src="https://github.com/user-attachments/assets/dc04d411-323e-4a41-988c-a579ff06965f" />
<img width="1794" height="626" alt="image" src="https://github.com/user-attachments/assets/22715d10-41cb-40f8-9056-404177a80878" />

<img width="1502" height="940" alt="image" src="https://github.com/user-attachments/assets/d0dc5d67-34ba-4990-9a39-2ec2de0c7afa" />

<img width="1465" height="852" alt="image" src="https://github.com/user-attachments/assets/753b375c-15e0-4278-9743-ad44f36d649c" />

<img width="762" height="1045" alt="image" src="https://github.com/user-attachments/assets/67518806-ae80-44ba-9690-58feb6bf7bc2" />




---
有问题请联系qq3486636827，该工具是之前带文字团开发的，目前在使用fvtt，所以废弃了

## 📖 项目简介

DND 跑团管理器是一个专为 D&D 游戏主持人（DM）和玩家设计的现代化综合管理工具。采用分层架构设计，提供直观的桌面界面和强大的Web编辑器，帮助你轻松管理跑团中的所有资料，包括人物卡、怪物数据、地图资源和复杂的剧情结构。

### ✨ 核心亮点

- 🎯 **统一管理** - 人物卡、怪物卡、地图、剧情四大分类一站式管理
- 📊 **剧情可视化** - 将复杂的剧情结构转换为交互式流程图
- 🌐 **双编辑器系统** - 现代化Web编辑器 + 传统桌面编辑器，满足不同需求
- 🎨 **现代化界面** - 统一的主题系统，响应式布局，流畅的交互体验
- 🔒 **安全删除** - 文件隐藏机制，误删文件可轻松恢复
- 🏗️ **分层架构** - Core业务层与UI层分离，代码结构清晰，易于维护和扩展
- 🌐 **多格式支持** - 支持文本、JSON、图片等多种文件格式
- 🚀 **智能服务器** - 自动启动本地HTTP服务器，支持Web功能无缝集成

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.7 或更高版本
- **操作系统**: Windows / macOS / Linux
- **浏览器**: Chrome、Firefox、Safari、Edge（用于Web功能）
- **可选依赖**: Graphviz（用于剧情图生成）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/dnd-manager.git
   cd dnd-manager
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **创建示例数据**（推荐新用户）
   ```bash
   python examples/sample_campaign.py
   ```
   这将创建一个名为"失落的矿坑"的示例跑团，包含完整的人物卡、怪物卡和剧情文件。

4. **启动主程序**
   ```bash
   python main.py
   ```

### 快速体验

#### 🎯 基础功能体验
1. 启动程序后，在左侧选择"失落的矿坑"跑团
2. 点击不同的分类标签（人物卡、怪物卡、地图、剧情）
3. 双击文件名查看内容，体验文件管理功能

#### 🌐 Web编辑器体验
1. 选择"剧情"分类，点击"失落的矿坑.json"文件
2. 点击"🌐 Web 编辑器 (推荐)"按钮
3. 在浏览器中体验现代化的剧情编辑功能

#### 📊 剧情可视化体验
1. 在剧情文件详情页面，点击"🎭 打开剧情图预览"
2. 或者点击"🔄 生成预览文件"（如果预览文件不存在）
3. 在浏览器中查看交互式剧情流程图

#### 📱 角色卡查看器体验
1. 选择任意跑团后，点击右上角"Web 查看"按钮
2. 在浏览器中体验现代化的角色卡查看界面
3. 尝试切换卡片视图和列表视图

### 独立工具使用

```bash
# 独立启动Web编辑器
python start_web_editor.py

# 独立启动剧情预览
python tools/web_preview_standalone.py

# 生成剧情预览文件
python tools/generate_preview.py
```

---

## 🎯 功能特性

### 📋 跑团管理
- ✅ 创建、切换、删除跑团
- ✅ 自动生成标准文件夹结构
- ✅ 跑团数据完全本地化存储
- ✅ 隐藏文件管理和恢复机制

### 📝 内容管理
- ✅ **人物卡管理** - 标准化模板，快速创建角色档案
- ✅ **怪物卡管理** - 完整的怪物数据库，包含属性、技能、描述
- ✅ **地图管理** - 支持图片导入、预览和组织，自适应缩放显示
- ✅ **剧情管理** - 支持文本笔记和结构化剧情文件，支持子文件夹组织

### 🎨 用户体验
- ✅ **现代化主题** - 统一的颜色方案和字体系统，基于8px网格精确对齐
- ✅ **响应式布局** - 智能布局管理，优化的间距和视觉层次
- ✅ **交互反馈** - 悬停效果、点击反馈、状态指示，增强的用户交互体验
- ✅ **安全操作** - 删除确认、文件恢复、操作撤销

### 🌐 Web编辑器（推荐）
- ✅ **现代化界面** - 基于HTML5 + JavaScript的响应式编辑器
- ✅ **实时保存** - 自动保存编辑内容，数据验证和完整性检查
- ✅ **智能节点管理** - 可视化节点编辑，支持拖拽和快捷键操作
- ✅ **自动服务器** - 智能启动本地HTTP服务器，浏览器关闭后自动停止
- ✅ **跨平台兼容** - 支持现代浏览器，无需额外安装

### 📊 剧情可视化
- ✅ **JSON剧情编辑** - 结构化的剧情节点定义，支持复杂分支逻辑
- ✅ **自动图形生成** - JSON → DOT → SVG 自动转换流程
- ✅ **交互式预览** - 基于Web的剧情流程图查看器，支持节点详情显示
- ✅ **分支逻辑** - 支持主线节点、分支选择、条件跳转
- ✅ **统计分析** - 自动生成剧情统计信息，包括节点数量、分支复杂度等

### 🏗️ 技术架构
- ✅ **分层设计** - Core业务层与UI层完全分离，提高代码质量和可维护性
- ✅ **服务化架构** - CampaignService、FileManagerService、StoryEditorService等核心服务
- ✅ **数据模型** - 完整的数据模型定义，支持类型安全和数据验证
- ✅ **Web服务集成** - 内置HTTP服务器，支持Web功能无缝集成

---

---

## 🏗️ 架构特色

### 分层架构设计

本项目采用现代化的分层架构，实现了业务逻辑与UI的完全分离：

```
┌─────────────────────────────────────────────────────────────┐
│                        UI 层                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   Tkinter GUI   │ │   Web Editor    │ │  Web Viewer     │ │
│  │   (main.py)     │ │   (editor.js)   │ │ (characters.js) │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ API Calls
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core 业务层                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Campaign Service│ │FileManager Svc  │ │StoryEditor Svc  │ │
│  │   (campaign.py) │ │(file_manager.py)│ │(story_editor_   │ │
│  │                 │ │                 │ │ service.py)     │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │  Data Models    │ │   Config Mgmt   │ │  Story Parser   │ │
│  │   (models.py)   │ │   (config.py)   │ │(story_parser.py)│ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ File I/O
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                             │
│              (本地文件系统 + JSON)                          │
└─────────────────────────────────────────────────────────────┘
```

### 核心优势

#### 🎯 **完全解耦**
- Core层无任何UI依赖，可独立运行和测试
- UI层通过标准API调用Core服务
- 支持多种前端：桌面GUI、Web界面、CLI工具

#### 🧪 **高可测试性**
- Core层可进行完整的单元测试
- 业务逻辑测试无需启动GUI
- 数据模型使用类型安全的dataclass

#### 🔧 **易于维护**
- 职责分离清晰，修改业务逻辑不影响UI
- 统一的配置管理和错误处理
- 代码结构清晰，便于新人理解

#### 🚀 **高扩展性**
- 可轻松添加新的UI前端（移动端、Web端等）
- 支持插件化扩展
- 为微服务化改造奠定基础

### 双编辑器系统

项目提供两套完整的编辑器解决方案：

| 特性对比 | Web编辑器 | Legacy编辑器 |
|---------|-----------|--------------|
| **技术栈** | HTML5 + JS + CSS | Tkinter |
| **用户体验** | 现代化、响应式 | 传统桌面应用 |
| **实时保存** | ✅ 自动保存 | ❌ 手动保存 |
| **数据验证** | ✅ 实时验证 | ✅ 保存时验证 |
| **跨平台** | ✅ 浏览器通用 | ✅ Python环境 |
| **维护状态** | 🚀 持续开发 | ❄️ 维护模式 |
| **推荐程度** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### Web服务集成

内置智能HTTP服务器，实现桌面应用与Web功能的无缝集成：

- **自动端口管理**: 智能分配可用端口，避免冲突
- **进程监控**: 监控浏览器活动，无活动时自动停止服务器
- **安全机制**: 仅监听本地回环地址，确保安全性
- **资源管理**: 自动清理临时文件和进程资源

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

# 独立启动Web预览
python tools/web_preview_standalone.py
```

### 🌐 Web编辑器使用

#### 通过主应用启动
1. 在主应用中选择跑团和JSON剧情文件
2. 点击 **"🌐 Web 编辑器 (推荐)"** 按钮
3. 编辑器将在浏览器中自动打开

#### 独立启动
```bash
# 交互式选择跑团
python start_web_editor.py

# 指定跑团
python start_web_editor.py "我的跑团"

# 指定跑团和剧情
python start_web_editor.py "我的跑团" "第一章"
```

#### Web编辑器特性
- **实时保存**: 编辑内容自动保存，无需手动操作
- **数据验证**: 实时验证JSON格式和数据完整性
- **快捷键支持**: 
  - `Ctrl+S`: 手动保存
  - `Ctrl+N`: 新建节点
  - `Ctrl+D`: 删除选中节点
- **响应式设计**: 支持不同屏幕尺寸，移动端友好
- **智能监控**: 浏览器关闭后服务器自动停止

### 📱 角色卡Web查看器

在主应用中选择跑团后，点击 **"Web 查看"** 按钮可打开角色卡查看器：

- **多视图模式**: 支持卡片视图和列表视图
- **分类浏览**: 人物卡、怪物卡、地图分类显示
- **详情查看**: 点击卡片查看完整信息
- **搜索功能**: 快速查找特定角色或怪物
- **响应式界面**: 适配不同设备屏幕

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
├── main.py                      # 主程序入口
├── start_web_editor.py          # Web编辑器独立启动器
├── start_server.py              # HTTP服务器启动脚本
├── src/                         # 源代码
│   ├── core/                    # 核心业务层（无UI依赖）
│   │   ├── campaign.py          # 跑团管理服务
│   │   ├── file_manager.py      # 文件管理服务
│   │   ├── story_editor_service.py # 剧情编辑服务
│   │   ├── story_parser.py      # 剧情解析服务
│   │   ├── models.py            # 数据模型定义
│   │   └── config.py            # 配置管理
│   ├── ui/                      # UI层
│   │   ├── theme_system.py      # 主题系统
│   │   ├── layout_system.py     # 布局系统
│   │   ├── theme_integration.py # 主题集成
│   │   ├── theme_utils.py       # 主题工具
│   │   └── web_preview/         # Web预览模块
│   │       ├── server.py        # Web服务器管理
│   │       ├── manager.py       # 预览管理器
│   │       ├── editor_api.py    # 编辑器API处理
│   │       └── preview_generator.py # 预览生成器
│   └── story_editor/            # Legacy编辑器
│       └── editor.py            # 传统Tkinter编辑器
├── tools/                       # 工具脚本
│   ├── generate_preview.py      # 预览生成工具
│   ├── json_to_dot.py           # JSON转DOT工具
│   ├── dot_to_svg.py            # DOT转SVG工具
│   ├── open_preview.py          # 预览查看器
│   ├── web_preview_standalone.py # 独立Web预览启动器
│   ├── characters/              # 角色卡Web查看器
│   │   ├── characters.html      # 查看器界面
│   │   ├── characters.js        # 交互逻辑
│   │   └── characters.css       # 样式定义
│   ├── editor/                  # Web编辑器前端
│   │   ├── editor.html          # 编辑器界面
│   │   ├── editor.js            # 编辑器逻辑
│   │   └── editor.css           # 编辑器样式
│   └── preview/                 # 剧情预览前端
├── data/                        # 用户数据
│   └── campaigns/               # 跑团数据存储
├── examples/                    # 示例文件
│   └── sample_campaign.py       # 示例数据生成器
└── requirements.txt             # 依赖列表
```

### 技术栈

#### 后端技术
- **GUI框架**: Tkinter (Python标准库)
- **HTTP服务器**: Python内置http.server
- **图像处理**: Pillow
- **进程监控**: psutil (可选)
- **数据处理**: JSON, pathlib
- **图形可视化**: Graphviz (外部依赖)

#### 前端技术
- **Web界面**: HTML5 + CSS3 + JavaScript (ES6+)
- **图形渲染**: SVG
- **响应式设计**: CSS Grid + Flexbox
- **交互体验**: 原生JavaScript，无框架依赖

#### 架构特性
- **分层架构**: Core业务层与UI层完全分离
- **服务化设计**: 基于服务的模块化架构
- **数据模型**: 使用dataclass定义类型安全的数据结构
- **配置管理**: 集中化配置管理系统

### 扩展开发

#### 添加新的文件类型
1. 在 `src/core/config.py` 的 `CATEGORIES` 字典中添加新分类
2. 在 `TEMPLATES` 中添加对应模板内容
3. 在 `FileManagerService` 中添加相应的处理逻辑
4. 更新UI布局以支持新分类

#### 自定义主题
1. 修改 `src/ui/theme_system.py` 中的 `ColorPalette` 类
2. 调整颜色、字体、间距等参数
3. 重启程序应用新主题

#### 添加新的Web功能
1. **后端API**: 在 `src/ui/web_preview/editor_api.py` 中添加新的API端点
2. **业务逻辑**: 在相应的Core服务中实现业务逻辑
3. **前端界面**: 在 `tools/editor/` 或 `tools/characters/` 中添加前端代码
4. **集成测试**: 确保新功能与现有系统兼容

#### 扩展剧情编辑器
1. **数据模型**: 在 `src/core/models.py` 中扩展 `StoryNode` 或 `StoryGraph` 模型
2. **解析逻辑**: 在 `src/core/story_parser.py` 中添加新的解析功能
3. **Web编辑器**: 在 `tools/editor/editor.js` 中添加前端编辑功能
4. **可视化**: 更新DOT生成逻辑以支持新的节点类型

#### 添加新的预览格式
1. 在 `src/ui/web_preview/preview_generator.py` 中添加新的生成器
2. 更新 `tools/generate_preview.py` 集成新的转换流程
3. 修改预览HTML模板支持新的格式
4. 确保与现有工具链兼容

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/your-username/dnd-manager.git
cd dnd-manager

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建示例数据
python examples/sample_campaign.py

# 运行主程序
python main.py

# 测试Web编辑器
python start_web_editor.py

# 测试Web预览
python tools/web_preview_standalone.py
```

### 测试和验证
```bash
# 运行架构测试
python test_ui_improvements.py

# 验证Core层独立性
python -c "from src.core import *; print('Core层导入成功')"

# 测试剧情解析
python -c "from src.core.story_parser import StoryGraphService; print('剧情解析服务正常')"

# 验证Web服务器
python -c "from src.ui.web_preview import WebPreviewManager; print('Web预览管理器正常')"
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
- [psutil](https://psutil.readthedocs.io/) - 系统和进程监控库

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个星标支持！**

Made with ❤️ for D&D enthusiasts

**🎲 让每一次跑团都成为难忘的冒险！**

</div>


