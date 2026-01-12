# DND 跑团管理器 - 文档索引

## 📚 文档概览

本项目包含两个主要分支的完整文档，每个分支都有其特定的重点和价值。

## 🌿 分支文档对比

| 方面 | 主分支 (main) | Web UI分支 (web-ui-refactor) |
|------|---------------|-------------------------------|
| **重点** | 架构设计和重构过程 | 功能实现和用户体验 |
| **内容** | 设计文档、规格说明 | 实施总结、修改记录 |
| **价值** | 理解架构原理 | 了解实际实现 |
| **状态** | 设计和规划阶段 | 实施和优化阶段 |

## 📖 文档结构

### 主分支文档 (`docs/MAIN_BRANCH_DOCS.md`)

#### 核心架构文档
- **README.md** - 完整的项目介绍和使用指南
- **EDITOR_ARCHITECTURE.md** - 双编辑器系统架构说明
- **REFACTORING_SUMMARY.md** - Core层与UI层分离的重构总结
- **UI_REFACTORING_SUMMARY.md** - Web预览系统集成总结

#### 规格说明文档
- **UI现代化规格** - 统一视觉主题、现代化控件设计
- **用户体验优化规格** - 拖拽支持、搜索过滤、偏好设置
- **设计文档** - 详细的技术实现和测试策略

### Web UI分支文档 (`docs/CURRENT_BRANCH_DOCS.md`)

#### 实施记录文档
- **README.md** - Web UI版本的项目说明
- **IMPLEMENTATION_SUMMARY.md** - Web UI重构的完整实施总结
- **BUILD_RELEASE_GUIDE.md** - 构建发行版的详细指南
- **MODIFICATION_SUMMARY.md** - 版本号和服务器管理的最新修改

#### 使用和维护文档
- **WEB_FILE_EDITOR_GUIDE.md** - Web文件编辑器使用指南
- **TROUBLESHOOTING.md** - 故障排除和问题解决
- **PATH_FIX_SUMMARY.md** - PyInstaller打包路径问题修复
- **CLEANUP_SUMMARY.md** - 项目文件清理记录

## 🎯 文档使用指南

### 🏗️ 架构理解
**推荐阅读顺序：**
1. 主分支 `README.md` - 了解项目整体架构
2. `REFACTORING_SUMMARY.md` - 理解Core层设计原理
3. `EDITOR_ARCHITECTURE.md` - 掌握编辑器架构
4. Web UI分支 `IMPLEMENTATION_SUMMARY.md` - 了解实际实现

### 🚀 快速上手
**推荐阅读顺序：**
1. Web UI分支 `README.md` - 了解当前版本功能
2. `BUILD_RELEASE_GUIDE.md` - 学习如何构建和部署
3. `WEB_FILE_EDITOR_GUIDE.md` - 掌握Web编辑器使用
4. `TROUBLESHOOTING.md` - 了解常见问题解决

### 🔧 开发参考
**推荐阅读顺序：**
1. 主分支规格文档 - 了解设计原则和需求
2. `REFACTORING_SUMMARY.md` - 理解代码组织原则
3. `MODIFICATION_SUMMARY.md` - 了解最新的技术修改
4. `PATH_FIX_SUMMARY.md` - 掌握打包相关技术

### 🐛 问题排查
**推荐阅读顺序：**
1. `TROUBLESHOOTING.md` - 查看常见问题解决方案
2. `PATH_FIX_SUMMARY.md` - 了解打包相关问题
3. `IMPLEMENTATION_SUMMARY.md` - 理解系统架构
4. 主分支技术文档 - 深入了解设计原理

## 📊 文档统计

### 主分支文档
- **总文档数**: 7个
- **核心文档**: 4个
- **规格文档**: 3个
- **重点**: 架构设计、重构过程、规格说明

### Web UI分支文档
- **总文档数**: 8个
- **实施文档**: 4个
- **使用文档**: 4个
- **重点**: 功能实现、使用指南、问题解决

## 🔄 文档维护

### 更新策略
- **主分支文档**: 主要更新架构设计和规格说明
- **Web UI分支文档**: 主要更新实施记录和使用指南
- **索引文档**: 定期同步两个分支的文档变化

### 版本控制
- 每个分支独立维护其文档
- 重要修改在对应分支提交
- 定期整合到文档索引中

## 🎉 总结

这套文档体系提供了从架构设计到实际实现的完整记录：

- **设计阶段** - 主分支提供了完整的架构设计和规格说明
- **实施阶段** - Web UI分支记录了实际的实现过程和结果
- **使用阶段** - 两个分支都提供了详细的使用指南
- **维护阶段** - 包含了问题排查和技术修改的完整记录

无论你是新用户、开发者还是维护者，都能在这套文档中找到所需的信息。

---

**文档索引创建时间：** 2026年1月12日  
**覆盖分支：** main, web-ui-refactor  
**文档总数：** 15个  
**状态：** ✅ 完整整合