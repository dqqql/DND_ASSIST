# DND 跑团管理器 - Web UI 故障排除指南

## 🚨 常见问题及解决方案

### 问题1: 按钮无法点击 / JavaScript不工作

#### 可能原因：
1. **JavaScript错误**: 脚本执行过程中出现错误，导致整个脚本停止
2. **DOM元素缺失**: JavaScript尝试绑定不存在的DOM元素
3. **浏览器兼容性**: 使用了不兼容的JavaScript特性
4. **网络问题**: 静态资源加载失败

#### 诊断步骤：

##### 步骤1: 检查浏览器控制台
1. 打开浏览器开发者工具 (F12)
2. 切换到 "Console" 标签
3. 刷新页面，查看是否有红色错误信息
4. 常见错误类型：
   - `Uncaught TypeError: Cannot read property 'addEventListener' of null`
   - `Uncaught ReferenceError: fetch is not defined`
   - `Uncaught SyntaxError: Unexpected token`

##### 步骤2: 检查网络请求
1. 在开发者工具中切换到 "Network" 标签
2. 刷新页面
3. 检查是否有失败的请求（红色状态）
4. 特别关注：
   - `index.js` 是否成功加载 (状态码200)
   - `index.css` 是否成功加载
   - API请求是否正常

##### 步骤3: 使用测试页面
```bash
# 运行快速测试
python quick_test.py

# 选择1: 简化测试页面
# 选择2: 完整调试页面  
# 选择3: 主界面
```

#### 解决方案：

##### 方案1: 重启服务器
```bash
# 停止所有Python进程
taskkill /f /im python.exe  # Windows
# 或
pkill python  # Linux/Mac

# 重新启动
python main_web.py --dev
```

##### 方案2: 清除浏览器缓存
1. 按 Ctrl+Shift+R 强制刷新
2. 或在开发者工具中右键刷新按钮，选择"清空缓存并硬性重新加载"

##### 方案3: 检查端口冲突
```bash
# 指定不同端口启动
python main_web.py --port 8080 --dev
```

##### 方案4: 使用兼容模式
如果浏览器版本较老，可能不支持某些ES6+特性：
1. 使用Chrome 60+、Firefox 55+、Safari 12+等现代浏览器
2. 或者修改JavaScript代码使用ES5语法

### 问题2: API请求失败

#### 症状：
- 按钮可以点击，但没有响应
- 控制台显示网络错误
- 数据无法加载

#### 诊断：
```bash
# 测试API连接
python -c "import requests; print(requests.get('http://localhost:端口号/api/campaigns').json())"
```

#### 解决方案：
1. **检查服务器状态**: 确保`main_web.py`正在运行
2. **检查端口**: 确保使用正确的端口号
3. **检查防火墙**: 确保防火墙允许本地连接
4. **检查CORS**: 如果从不同域名访问，可能有跨域问题

### 问题3: 页面样式异常

#### 症状：
- 页面布局混乱
- 按钮样式不正确
- 响应式布局失效

#### 解决方案：
1. **检查CSS加载**: 确保`index.css`成功加载
2. **清除缓存**: 强制刷新页面
3. **检查浏览器兼容性**: 使用现代浏览器

### 问题4: 数据无法保存

#### 症状：
- 创建跑团后不显示
- 文件操作无效果
- 数据丢失

#### 解决方案：
1. **检查文件权限**: 确保有写入`data`目录的权限
2. **检查磁盘空间**: 确保有足够的存储空间
3. **检查API响应**: 查看网络标签中的API响应

## 🔧 调试工具

### 1. 简化测试页面
访问: `http://localhost:端口号/tools/web_ui/test_simple.html`
- 测试基本JavaScript功能
- 测试API连接
- 最小化的测试环境

### 2. 完整调试页面
访问: `http://localhost:端口号/debug_web_ui.html`
- 完整的API测试套件
- JavaScript功能测试
- 错误日志记录

### 3. 浏览器开发者工具
- **Console**: 查看JavaScript错误和日志
- **Network**: 查看网络请求状态
- **Elements**: 检查DOM结构
- **Sources**: 调试JavaScript代码

## 📋 检查清单

在报告问题前，请确认以下项目：

- [ ] 服务器正在运行 (`python main_web.py`)
- [ ] 使用现代浏览器 (Chrome 60+, Firefox 55+, Safari 12+)
- [ ] 浏览器控制台无JavaScript错误
- [ ] 网络请求正常 (无404或500错误)
- [ ] 端口未被其他程序占用
- [ ] 有足够的磁盘空间和文件权限

## 🆘 获取帮助

如果以上方法都无法解决问题，请提供以下信息：

1. **操作系统**: Windows/Mac/Linux版本
2. **浏览器**: 类型和版本号
3. **Python版本**: `python --version`
4. **错误信息**: 浏览器控制台的完整错误信息
5. **网络状态**: 开发者工具Network标签的截图
6. **复现步骤**: 详细的操作步骤

### 快速诊断命令
```bash
# 系统信息
python --version
python -c "import sys; print(f'Python: {sys.version}')"

# 依赖检查
python -c "import requests; print('requests: OK')"
python -c "from PIL import Image; print('Pillow: OK')"

# 服务器测试
python -c "
import requests
try:
    r = requests.get('http://localhost:58184/api/campaigns', timeout=5)
    print(f'API Status: {r.status_code}')
    print(f'Response: {r.json()}')
except Exception as e:
    print(f'API Error: {e}')
"
```

## 🔄 重置和恢复

### 完全重置
如果问题持续存在，可以尝试完全重置：

```bash
# 1. 停止所有服务
taskkill /f /im python.exe

# 2. 清理临时文件
# 删除 __pycache__ 目录
# 清除浏览器缓存

# 3. 重新启动
python main_web.py --dev
```

### 数据备份
在重置前，建议备份重要数据：
```bash
# 备份跑团数据
cp -r data/campaigns data_backup/
```

---

**💡 提示**: 大多数问题都可以通过重启服务器和清除浏览器缓存解决。如果问题持续存在，请使用调试页面进行详细诊断。