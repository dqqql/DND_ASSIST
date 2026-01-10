# DND 跑团管理器 - Web UI 重构版本

## 🎯 项目概述

本项目已成功重构为以 **Web UI 为唯一用户界面** 的现代化跑团管理工具。采用前后端分离架构，提供统一的Web界面体验，完全移除了对 Tkinter 的依赖。

## 🏗️ 架构特点

### 前后端分离架构
```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Web UI)                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   主界面        │ │   Web编辑器     │ │  角色卡查看器   │ │
│  │  (index.html)   │ │ (editor.html)   │ │(characters.html)│ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP API (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    后端 (Python)                           │
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

- **🌐 纯Web界面**: 无需安装任何桌面应用，浏览器即可使用
- **📱 响应式设计**: 完美适配桌面、平板、手机等各种设备
- **🔄 实时同步**: 前后端数据实时同步，自动保存
- **🚀 一键启动**: 单个命令启动完整服务
- **🔒 本地安全**: 所有数据本地存储，无需联网
- **⚡ 高性能**: 智能缓存和优化的API设计

## 🚀 快速开始

### 启动Web UI版本

```bash
# 基本启动（推荐）
python main_web.py

# 指定端口启动
python main_web.py --port 8080

# 开发模式（不自动关闭）
python main_web.py --dev

# 仅启动服务器（不打开浏览器）
python main_web.py --no-browser

# 查看所有选项
python main_web.py --help
```

### 功能特性

#### 🎯 统一的Web界面
- **跑团管理**: 创建、删除、切换跑团
- **分类管理**: 人物卡、怪物卡、地图、剧情四大分类
- **文件操作**: 新建、编辑、删除、导入文件
- **内容预览**: 实时预览文件内容

#### 📝 现代化编辑体验
- **Web编辑器**: 专为JSON剧情设计的可视化编辑器
- **实时保存**: 自动保存编辑内容，无需手动操作
- **数据验证**: 实时验证数据完整性和格式正确性
- **快捷键支持**: Ctrl+S保存、Ctrl+N新建等

#### 📊 可视化功能
- **剧情流程图**: 自动生成交互式剧情图表
- **统计分析**: 剧情复杂度和完整性分析
- **预览系统**: 多格式文件预览支持

#### 🔒 安全机制
- **软删除**: 删除文件仅隐藏，可随时恢复
- **本地存储**: 所有数据存储在本地，保护隐私
- **备份友好**: 标准文件结构，易于备份和迁移

## 📁 项目结构

```
dnd-manager/
├── main_web.py                  # 🚀 Web UI 主入口
├── main.py                      # 📱 Legacy Tkinter 入口（开发用）
├── start_web_editor.py          # 🌐 独立Web编辑器启动器
├── src/                         # 📦 后端核心代码
│   ├── core/                    # 🏗️ 业务逻辑层
│   │   ├── campaign.py          # 跑团管理服务
│   │   ├── file_manager.py      # 文件管理服务
│   │   ├── story_editor_service.py # 剧情编辑服务
│   │   ├── models.py            # 数据模型定义
│   │   └── config.py            # 配置管理
│   └── ui/                      # 🎨 UI层（保留用于开发）
│       ├── web_preview/         # Web服务模块
│       │   ├── server.py        # HTTP服务器
│       │   ├── manager.py       # Web预览管理器
│       │   └── editor_api.py    # API处理器
│       └── theme_system.py      # 主题系统（Legacy）
├── tools/                       # 🌐 Web前端资源
│   ├── web_ui/                  # 🏠 主界面
│   │   ├── index.html           # 主页面
│   │   ├── index.css            # 主样式
│   │   └── index.js             # 主逻辑
│   ├── editor/                  # ✏️ Web编辑器
│   │   ├── editor.html          # 编辑器页面
│   │   ├── editor.css           # 编辑器样式
│   │   └── editor.js            # 编辑器逻辑
│   ├── characters/              # 👥 角色卡查看器
│   │   ├── characters.html      # 查看器页面
│   │   ├── characters.css       # 查看器样式
│   │   └── characters.js        # 查看器逻辑
│   └── preview/                 # 🎭 剧情预览器
├── data/                        # 💾 用户数据存储
│   └── campaigns/               # 跑团数据目录
└── examples/                    # 📚 示例和工具
    └── sample_campaign.py       # 示例数据生成器
```

## 🔧 技术栈

### 后端技术
- **Python 3.7+**: 核心运行环境
- **HTTP Server**: 内置http.server，轻量级Web服务
- **JSON API**: RESTful API设计，标准HTTP方法
- **文件系统**: 基于本地文件系统的数据存储
- **多线程**: 智能浏览器监控和自动关闭

### 前端技术
- **HTML5**: 语义化标记，现代Web标准
- **CSS3**: 响应式设计，CSS Grid + Flexbox布局
- **JavaScript ES6+**: 原生JavaScript，无框架依赖
- **Fetch API**: 现代HTTP客户端
- **Web Components**: 模块化组件设计

### 设计特点
- **移动优先**: 响应式设计，适配各种屏幕尺寸
- **无障碍**: 遵循WCAG指南，支持键盘导航
- **性能优化**: 懒加载、缓存策略、压缩资源
- **用户体验**: 流畅动画、即时反馈、直观操作

## 🌟 功能对比

| 功能特性 | Web UI版本 | Legacy版本 |
|---------|-----------|------------|
| **界面技术** | HTML5 + CSS3 + JS | Tkinter |
| **跨平台** | ✅ 浏览器通用 | ✅ Python环境 |
| **响应式设计** | ✅ 完全支持 | ❌ 固定布局 |
| **移动设备** | ✅ 完美适配 | ❌ 不支持 |
| **实时保存** | ✅ 自动保存 | ❌ 手动保存 |
| **现代化UI** | ✅ 现代设计 | ❌ 传统界面 |
| **维护状态** | 🚀 主要版本 | 🔧 开发工具 |
| **用户体验** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 📋 API 接口

### 跑团管理
```http
GET    /api/campaigns              # 获取跑团列表
POST   /api/campaigns              # 创建新跑团
DELETE /api/campaigns              # 删除跑团
```

### 文件管理
```http
GET    /api/characters             # 获取人物卡列表
GET    /api/character              # 获取人物卡详情
GET    /api/monsters               # 获取怪物卡列表
GET    /api/monster                # 获取怪物卡详情
GET    /api/maps                   # 获取地图列表
GET    /api/map                    # 获取地图详情
POST   /api/files                  # 创建文件
DELETE /api/files                  # 删除文件
```

### 剧情编辑
```http
GET    /api/stories                # 获取剧情列表
GET    /api/story                  # 获取剧情数据
POST   /api/story/save             # 保存剧情
POST   /api/story/validate         # 验证剧情数据
POST   /api/story/new              # 创建新剧情
GET    /api/story/statistics       # 获取剧情统计
```

## 🎨 界面预览

### 主界面
- **现代化设计**: 清爽的卡片式布局
- **直观导航**: 左侧跑团列表，顶部分类标签
- **实时预览**: 右侧内容查看器，支持多种格式
- **响应式布局**: 自适应不同屏幕尺寸

### Web编辑器
- **可视化编辑**: 节点式剧情编辑界面
- **实时验证**: 即时数据格式检查
- **快捷操作**: 丰富的键盘快捷键支持
- **自动保存**: 编辑内容自动同步保存

### 角色卡查看器
- **多视图模式**: 卡片视图和列表视图切换
- **分类浏览**: 人物卡、怪物卡、地图分类显示
- **详情展示**: 结构化数据美观展示
- **搜索功能**: 快速查找特定内容

## 🔄 迁移指南

### 从Legacy版本迁移

1. **数据兼容**: 现有数据完全兼容，无需转换
2. **功能对等**: 所有核心功能在Web版本中都有对应
3. **操作习惯**: Web界面更加直观，学习成本低
4. **性能提升**: Web版本响应更快，体验更流畅

### 保留Legacy版本

Legacy版本（main.py）仍然保留，可用于：
- **开发调试**: 快速测试和调试功能
- **应急备用**: 在Web版本出现问题时的备用方案
- **功能验证**: 对比验证新功能的正确性

## 🚀 部署和分发

### 本地使用
```bash
# 直接运行
python main_web.py

# 后台运行
nohup python main_web.py --no-browser > server.log 2>&1 &
```

### 打包分发

#### 使用 PyInstaller
```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单个可执行文件
pyinstaller --onefile --add-data "tools;tools" --add-data "src;src" main_web.py

# 打包为目录（推荐）
pyinstaller --add-data "tools;tools" --add-data "src;src" main_web.py
```

#### 使用 Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "main_web.py", "--port", "8080", "--host", "0.0.0.0"]
```

### 生产环境

对于生产环境部署，建议：
- 使用专业的Web服务器（如Nginx + uWSGI）
- 配置HTTPS证书
- 设置防火墙规则
- 定期备份数据目录

## 🛠️ 开发指南

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd dnd-manager

# 安装依赖
pip install -r requirements.txt

# 创建示例数据
python examples/sample_campaign.py

# 启动开发服务器
python main_web.py --dev
```

### 代码结构

- **后端API**: 在 `src/ui/web_preview/server.py` 中添加新的API端点
- **前端界面**: 在 `tools/web_ui/` 中修改主界面
- **业务逻辑**: 在 `src/core/` 中实现核心功能
- **数据模型**: 在 `src/core/models.py` 中定义数据结构

### 扩展功能

1. **添加新的文件类型**: 修改 `src/core/config.py` 中的配置
2. **扩展API接口**: 在服务器中添加新的路由处理
3. **增强前端功能**: 修改对应的HTML/CSS/JS文件
4. **优化用户体验**: 改进响应式设计和交互逻辑

## 📈 性能优化

### 已实现的优化
- **智能缓存**: API响应缓存，减少重复请求
- **懒加载**: 按需加载文件内容，提升响应速度
- **压缩传输**: JSON数据压缩，减少网络传输
- **异步处理**: 非阻塞的文件操作和网络请求

### 进一步优化建议
- **CDN加速**: 静态资源使用CDN分发
- **数据库**: 大量数据时考虑使用SQLite
- **缓存策略**: 实现更智能的缓存机制
- **负载均衡**: 多实例部署时的负载分配

## 🔒 安全考虑

### 当前安全措施
- **本地访问**: 默认仅监听localhost，防止外部访问
- **输入验证**: 严格的输入参数验证和清理
- **文件权限**: 合理的文件系统权限控制
- **CORS配置**: 适当的跨域资源共享设置

### 安全建议
- **定期更新**: 保持Python和依赖库的最新版本
- **访问控制**: 生产环境中配置适当的访问控制
- **数据备份**: 定期备份重要数据
- **监控日志**: 记录和监控系统访问日志

## 🎯 未来规划

### 短期目标
- [ ] 完善文件导入功能
- [ ] 增强隐藏文件管理
- [ ] 优化移动端体验
- [ ] 添加更多快捷键支持

### 中期目标
- [ ] 多用户支持和权限管理
- [ ] 云端同步功能
- [ ] 插件系统架构
- [ ] 主题定制功能

### 长期目标
- [ ] 多语言国际化支持
- [ ] 离线PWA应用
- [ ] 协作编辑功能
- [ ] 移动端原生应用

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. **Fork项目**: 创建项目的分支
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -am 'Add some feature'`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建PR**: 提交Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档
- 编写单元测试覆盖新功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

<div align="center">

**🎲 让每一次跑团都成为难忘的冒险！**

**现在就体验全新的Web UI版本吧！**

`python main_web.py`

</div>