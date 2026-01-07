# 结构化分支剧情系统需求文档

## 介绍

为现有的DND跑团管理器添加结构化分支剧情系统，支持"主线剧情 + 多分支选择 + 分支结束后回到主线"的跑团剧本逻辑。采用JSON格式存储，UI以列表形式展示。

## 术语表

- **Story_System**: 结构化分支剧情系统
- **Story_File**: JSON格式的剧情文件
- **Story_Viewer**: 剧情查看器组件

## 需求

### 需求 1: JSON剧情文件支持

**用户故事:** 作为跑团DM，我希望能够创建JSON格式的结构化剧情文件。

#### 验收标准

1. WHEN 在notes分类中创建新文件 THEN Story_System SHALL 提供创建.json剧情文件的选项
2. WHEN 创建.json文件 THEN Story_System SHALL 生成包含示例结构的模板
3. THE Story_System SHALL 支持主线节点和分支节点的JSON结构

### 需求 2: 剧情查看器

**用户故事:** 作为跑团DM，我希望能够在右侧内容区域查看结构化剧情。

#### 验收标准

1. WHEN 选择.json剧情文件 THEN Story_Viewer SHALL 解析并显示结构化内容
2. WHEN 显示剧情结构 THEN Story_Viewer SHALL 以可展开的列表形式显示主线和分支
3. WHEN JSON格式错误 THEN Story_Viewer SHALL 显示错误信息

### 需求 3: 文件编辑

**用户故事:** 作为跑团DM，我希望能够编辑JSON剧情文件。

#### 验收标准

1. WHEN 双击.json文件 THEN Story_System SHALL 使用系统默认编辑器打开
2. WHEN 重新选择文件 THEN Story_Viewer SHALL 显示更新后的内容

### 需求 4: 向后兼容

**用户故事:** 作为现有用户，我希望新功能不影响现有.txt文件。

#### 验收标准

1. THE Story_System SHALL 完全保持现有.txt文件功能
2. THE Story_System SHALL 不修改现有核心功能