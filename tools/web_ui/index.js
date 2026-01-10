/**
 * DND 跑团管理器 - 主界面脚本
 * 提供完整的Web界面交互功能
 */

class DNDManager {
    constructor() {
        console.log('DNDManager构造函数开始执行');
        
        this.currentCampaign = null;
        this.currentCategory = 'characters';
        this.currentFile = null;
        this.showHidden = false;
        
        console.log('DNDManager属性初始化完成');
        
        this.init();
        
        console.log('DNDManager初始化完成');
    }
    
    init() {
        console.log('开始绑定事件');
        this.bindEvents();
        console.log('事件绑定完成');
        
        console.log('开始加载跑团列表');
        this.loadCampaigns();
        console.log('跑团列表加载请求已发送');
        
        console.log('显示欢迎页面');
        this.showWelcomePage();
        console.log('初始化流程完成');
    }
    
    bindEvents() {
        // 头部按钮
        const refreshBtn = document.getElementById('refreshBtn');
        const helpBtn = document.getElementById('helpBtn');
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.refresh());
        if (helpBtn) helpBtn.addEventListener('click', () => this.showHelp());
        
        // 跑团管理
        const createCampaignBtn = document.getElementById('createCampaignBtn');
        const createFirstCampaignBtn = document.getElementById('createFirstCampaignBtn');
        const deleteCampaignBtn = document.getElementById('deleteCampaignBtn');
        const webViewBtn = document.getElementById('webViewBtn');
        
        if (createCampaignBtn) createCampaignBtn.addEventListener('click', () => this.showCreateCampaignDialog());
        if (createFirstCampaignBtn) createFirstCampaignBtn.addEventListener('click', () => this.showCreateCampaignDialog());
        if (deleteCampaignBtn) deleteCampaignBtn.addEventListener('click', () => this.deleteCampaign());
        if (webViewBtn) webViewBtn.addEventListener('click', () => this.openWebViewer());
        
        // 分类标签
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.currentTarget.dataset.category;
                this.selectCategory(category);
            });
        });
        
        // 文件操作
        const createFileBtn = document.getElementById('createFileBtn');
        const importFileBtn = document.getElementById('importFileBtn');
        const showHiddenBtn = document.getElementById('showHiddenBtn');
        const editFileBtn = document.getElementById('editFileBtn');
        const deleteFileBtn = document.getElementById('deleteFileBtn');
        
        if (createFileBtn) createFileBtn.addEventListener('click', () => this.showCreateFileDialog());
        if (importFileBtn) importFileBtn.addEventListener('click', () => this.importFile());
        if (showHiddenBtn) showHiddenBtn.addEventListener('click', () => this.toggleHiddenFiles());
        if (editFileBtn) editFileBtn.addEventListener('click', () => this.editFile());
        if (deleteFileBtn) deleteFileBtn.addEventListener('click', () => this.deleteFile());
        
        // 模态对话框
        const modalClose = document.getElementById('modalClose');
        const modalCancel = document.getElementById('modalCancel');
        
        if (modalClose) modalClose.addEventListener('click', () => this.hideModal());
        if (modalCancel) modalCancel.addEventListener('click', () => this.hideModal());
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // 点击模态背景关闭
        const modal = document.getElementById('modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === e.currentTarget) {
                    this.hideModal();
                }
            });
        }
    }
    
    // ==================== 跑团管理 ====================
    
    async loadCampaigns() {
        try {
            const response = await fetch('/api/campaigns');
            const data = await response.json();
            
            if (data.campaigns && data.campaigns.length > 0) {
                this.renderCampaignList(data.campaigns);
                this.hideWelcomePage();
            } else {
                this.showWelcomePage();
            }
        } catch (error) {
            console.error('加载跑团列表失败:', error);
            this.showNotification('加载跑团列表失败', 'error');
            this.showWelcomePage();
        }
    }
    
    renderCampaignList(campaigns) {
        const listElement = document.getElementById('campaignList');
        
        if (campaigns.length === 0) {
            listElement.innerHTML = '<div class="empty-state"><div class="empty-icon">📁</div><p>暂无跑团</p></div>';
            return;
        }
        
        listElement.innerHTML = campaigns.map(campaign => `
            <div class="campaign-item" data-campaign="${campaign}">
                <div class="campaign-name">${campaign}</div>
                <div class="campaign-status">📁</div>
            </div>
        `).join('');
        
        // 绑定点击事件
        listElement.querySelectorAll('.campaign-item').forEach(item => {
            item.addEventListener('click', () => {
                const campaignName = item.dataset.campaign;
                this.selectCampaign(campaignName);
            });
        });
    }
    
    selectCampaign(campaignName) {
        // 更新UI状态
        document.querySelectorAll('.campaign-item').forEach(item => {
            item.classList.toggle('active', item.dataset.campaign === campaignName);
        });
        
        this.currentCampaign = campaignName;
        this.showCampaignPage();
        this.showCampaignActions();
        this.loadFiles();
        
        this.showNotification(`已选择跑团：${campaignName}`, 'success');
    }
    
    showCreateCampaignDialog() {
        this.showModal('创建新跑团', `
            <div class="form-group">
                <label class="form-label" for="campaignName">跑团名称</label>
                <input type="text" id="campaignName" class="form-input" placeholder="请输入跑团名称" maxlength="50">
            </div>
            <div class="form-group">
                <p class="text-secondary">跑团将包含以下分类：</p>
                <ul class="text-secondary" style="margin-left: 1rem; margin-top: 0.5rem;">
                    <li>👥 人物卡 - 管理角色信息</li>
                    <li>👹 怪物卡 - 管理怪物数据</li>
                    <li>🗺️ 地图 - 管理地图资源</li>
                    <li>📖 剧情 - 管理剧情文件</li>
                </ul>
            </div>
        `, async () => {
            const name = document.getElementById('campaignName').value.trim();
            if (!name) {
                this.showNotification('请输入跑团名称', 'warning');
                return false;
            }
            
            try {
                const response = await fetch('/api/campaigns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.showNotification(`跑团"${name}"创建成功`, 'success');
                    this.loadCampaigns();
                    return true;
                } else {
                    this.showNotification(result.error || '创建跑团失败', 'error');
                    return false;
                }
            } catch (error) {
                console.error('创建跑团失败:', error);
                this.showNotification('创建跑团失败', 'error');
                return false;
            }
        });
        
        // 聚焦输入框
        setTimeout(() => {
            document.getElementById('campaignName').focus();
        }, 100);
    }
    
    async deleteCampaign() {
        if (!this.currentCampaign) {
            this.showNotification('请先选择一个跑团', 'warning');
            return;
        }
        
        this.showModal('确认删除', `
            <div class="form-group">
                <p>确定要删除跑团 <strong>"${this.currentCampaign}"</strong> 吗？</p>
                <p class="text-secondary" style="margin-top: 1rem;">
                    ⚠️ 此操作将删除跑团下的所有文件，且无法恢复！
                </p>
            </div>
        `, async () => {
            try {
                const response = await fetch('/api/campaigns', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: this.currentCampaign })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.showNotification(`跑团"${this.currentCampaign}"已删除`, 'success');
                    this.currentCampaign = null;
                    this.hideCampaignActions();
                    this.loadCampaigns();
                    return true;
                } else {
                    this.showNotification(result.error || '删除跑团失败', 'error');
                    return false;
                }
            } catch (error) {
                console.error('删除跑团失败:', error);
                this.showNotification('删除跑团失败', 'error');
                return false;
            }
        });
    }
    
    openWebViewer() {
        if (!this.currentCampaign) {
            this.showNotification('请先选择一个跑团', 'warning');
            return;
        }
        
        const url = `/tools/characters/characters.html?campaign=${encodeURIComponent(this.currentCampaign)}`;
        window.open(url, '_blank');
        this.showNotification('角色卡查看器已在新标签页中打开', 'info');
    }
    
    // ==================== 页面切换 ====================
    
    showWelcomePage() {
        document.getElementById('welcomePage').style.display = 'block';
        document.getElementById('campaignPage').style.display = 'none';
    }
    
    hideWelcomePage() {
        document.getElementById('welcomePage').style.display = 'none';
    }
    
    showCampaignPage() {
        this.hideWelcomePage();
        document.getElementById('campaignPage').style.display = 'block';
    }
    
    showCampaignActions() {
        document.getElementById('campaignActions').style.display = 'block';
    }
    
    hideCampaignActions() {
        document.getElementById('campaignActions').style.display = 'none';
    }
    
    // ==================== 分类管理 ====================
    
    selectCategory(category) {
        this.currentCategory = category;
        this.currentFile = null;
        
        // 更新标签状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });
        
        // 更新标题
        const titles = {
            'characters': '人物卡',
            'monsters': '怪物卡',
            'maps': '地图',
            'notes': '剧情'
        };
        document.getElementById('categoryTitle').textContent = titles[category];
        
        // 显示/隐藏导入按钮（仅地图分类显示）
        const importBtn = document.getElementById('importFileBtn');
        if (category === 'maps') {
            importBtn.style.display = 'inline-flex';
        } else {
            importBtn.style.display = 'none';
        }
        
        // 清空查看器
        this.clearViewer();
        
        // 加载文件列表
        this.loadFiles();
    }
    
    // ==================== 文件管理 ====================
    
    async loadFiles() {
        if (!this.currentCampaign) return;
        
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '<div class="loading">正在加载文件列表...</div>';
        
        try {
            const endpoint = `/api/${this.currentCategory}?campaign=${encodeURIComponent(this.currentCampaign)}`;
            const response = await fetch(endpoint);
            const data = await response.json();
            
            const files = data[this.currentCategory] || [];
            this.renderFileList(files);
            
            // 更新文件计数
            document.getElementById('fileCount').textContent = `${files.length} 个文件`;
            
        } catch (error) {
            console.error('加载文件列表失败:', error);
            fileList.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>加载失败</p></div>';
            this.showNotification('加载文件列表失败', 'error');
        }
    }
    
    renderFileList(files) {
        const fileList = document.getElementById('fileList');
        
        if (files.length === 0) {
            fileList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📄</div>
                    <div class="empty-title">暂无文件</div>
                    <div class="empty-description">点击"新建文件"开始创建内容</div>
                </div>
            `;
            return;
        }
        
        fileList.innerHTML = files.map(file => {
            const isDirectory = file.name.startsWith('[DIR]');
            const displayName = isDirectory ? file.name.replace('[DIR] ', '') : file.name;
            const icon = this.getFileIcon(file, isDirectory);
            
            return `
                <div class="file-item ${isDirectory ? 'directory' : ''}" data-file="${file.name}">
                    <div class="file-icon">${icon}</div>
                    <div class="file-name">${displayName}</div>
                    ${file.file_type ? `<div class="file-type">${file.file_type}</div>` : ''}
                </div>
            `;
        }).join('');
        
        // 绑定点击事件
        fileList.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', () => {
                const fileName = item.dataset.file;
                this.selectFile(fileName);
            });
            
            // 双击事件
            item.addEventListener('dblclick', () => {
                const fileName = item.dataset.file;
                this.openFile(fileName);
            });
        });
    }
    
    getFileIcon(file, isDirectory) {
        if (isDirectory) return '📁';
        
        switch (this.currentCategory) {
            case 'characters': return '👤';
            case 'monsters': return '👹';
            case 'maps': return file.file_type === 'image' ? '🖼️' : '🗺️';
            case 'notes': return file.file_type === 'json' ? '📊' : '📝';
            default: return '📄';
        }
    }
    
    selectFile(fileName) {
        // 更新选中状态
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.toggle('active', item.dataset.file === fileName);
        });
        
        this.currentFile = fileName;
        this.loadFileContent(fileName);
        this.showViewerActions();
    }
    
    async loadFileContent(fileName) {
        if (!this.currentCampaign || !fileName) return;
        
        const viewerContent = document.getElementById('viewerContent');
        viewerContent.innerHTML = '<div class="loading">正在加载文件内容...</div>';
        
        try {
            // 构建API端点
            const endpoint = this.getFileContentEndpoint(fileName);
            const response = await fetch(endpoint);
            const data = await response.json();
            
            this.renderFileContent(data);
            
        } catch (error) {
            console.error('加载文件内容失败:', error);
            viewerContent.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>加载失败</p></div>';
            this.showNotification('加载文件内容失败', 'error');
        }
    }
    
    getFileContentEndpoint(fileName) {
        const category = this.currentCategory.slice(0, -1); // 去掉复数形式的s
        return `/api/${category}?campaign=${encodeURIComponent(this.currentCampaign)}&name=${encodeURIComponent(fileName)}`;
    }
    
    renderFileContent(data) {
        const viewerContent = document.getElementById('viewerContent');
        
        if (data.type === 'image') {
            // 图片文件
            const imagePath = `/data/campaigns/${this.currentCampaign}/maps/${data.filename}`;
            viewerContent.innerHTML = `
                <div style="text-align: center;">
                    <img src="${imagePath}" alt="${data.name}" class="viewer-image" 
                         onerror="this.parentElement.innerHTML='<div class=\\"empty-state\\"><div class=\\"empty-icon\\">🖼️</div><p>无法显示图片</p></div>'">
                </div>
            `;
        } else if (data.raw_content) {
            // 文本文件
            viewerContent.innerHTML = `<pre class="viewer-text">${this.escapeHtml(data.raw_content)}</pre>`;
        } else if (data.fields) {
            // 结构化数据（人物卡/怪物卡）
            viewerContent.innerHTML = this.renderStructuredContent(data);
        } else {
            viewerContent.innerHTML = '<div class="empty-state"><div class="empty-icon">📄</div><p>无内容</p></div>';
        }
    }
    
    renderStructuredContent(data) {
        const fields = Object.entries(data.fields).map(([key, value]) => `
            <div class="field-row" style="margin-bottom: 1rem;">
                <div class="field-label" style="font-weight: 600; color: var(--text-secondary); margin-bottom: 0.25rem;">
                    ${this.escapeHtml(key)}:
                </div>
                <div class="field-value" style="padding: 0.5rem; background: var(--bg-secondary); border-radius: var(--radius-sm);">
                    ${this.escapeHtml(value) || '<em style="color: var(--text-muted);">未填写</em>'}
                </div>
            </div>
        `).join('');
        
        return `
            <div class="structured-content">
                <div class="content-header" style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
                    <h3 style="margin: 0; color: var(--text-primary);">${this.escapeHtml(data.name)}</h3>
                    <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.875rem;">
                        ${data.type === 'character' ? '人物卡' : '怪物卡'}
                    </p>
                </div>
                <div class="content-fields">
                    ${fields}
                </div>
            </div>
        `;
    }
    
    showCreateFileDialog() {
        if (!this.currentCampaign) {
            this.showNotification('请先选择一个跑团', 'warning');
            return;
        }
        
        const isNotesCategory = this.currentCategory === 'notes';
        
        this.showModal('新建文件', `
            <div class="form-group">
                <label class="form-label" for="fileName">文件名</label>
                <input type="text" id="fileName" class="form-input" placeholder="请输入文件名（不需要扩展名）" maxlength="50">
            </div>
            ${isNotesCategory ? `
                <div class="form-group">
                    <label class="form-label" for="fileType">文件类型</label>
                    <select id="fileType" class="form-select">
                        <option value="txt">普通剧情 (.txt)</option>
                        <option value="json">结构化剧情 (.json)</option>
                    </select>
                </div>
            ` : ''}
            <div class="form-group">
                <p class="text-secondary">
                    ${this.getFileTypeDescription()}
                </p>
            </div>
        `, async () => {
            const name = document.getElementById('fileName').value.trim();
            if (!name) {
                this.showNotification('请输入文件名', 'warning');
                return false;
            }
            
            const fileType = isNotesCategory ? document.getElementById('fileType').value : 'txt';
            
            try {
                const response = await fetch('/api/files', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        campaign: this.currentCampaign,
                        category: this.currentCategory,
                        filename: name,
                        file_type: fileType
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.showNotification(`文件"${name}"创建成功`, 'success');
                    this.loadFiles();
                    return true;
                } else {
                    this.showNotification(result.error || '创建文件失败', 'error');
                    return false;
                }
            } catch (error) {
                console.error('创建文件失败:', error);
                this.showNotification('创建文件失败', 'error');
                return false;
            }
        });
        
        // 聚焦输入框
        setTimeout(() => {
            document.getElementById('fileName').focus();
        }, 100);
    }
    
    getFileTypeDescription() {
        switch (this.currentCategory) {
            case 'characters':
                return '将创建人物卡模板，包含姓名、种族、职业等基础字段。';
            case 'monsters':
                return '将创建怪物卡模板，包含名称、类型、挑战等级等字段。';
            case 'maps':
                return '将创建地图说明文件，您也可以使用"导入文件"功能导入图片。';
            case 'notes':
                return '普通剧情适合记录文本笔记，结构化剧情支持节点和分支逻辑。';
            default:
                return '将创建新的文本文件。';
        }
    }
    
    editFile() {
        if (!this.currentFile) {
            this.showNotification('请先选择一个文件', 'warning');
            return;
        }
        
        // 根据文件类型选择编辑器
        if (this.currentCategory === 'notes' && this.currentFile.endsWith('.json')) {
            // 使用Web编辑器编辑JSON剧情
            const url = `/tools/editor/editor.html?campaign=${encodeURIComponent(this.currentCampaign)}&story=${encodeURIComponent(this.currentFile.replace('.json', ''))}`;
            window.open(url, '_blank');
            this.showNotification('剧情编辑器已在新标签页中打开', 'info');
        } else {
            // 使用通用文件编辑器
            const url = `/tools/web_ui/file_editor.html?campaign=${encodeURIComponent(this.currentCampaign)}&category=${encodeURIComponent(this.currentCategory)}&file=${encodeURIComponent(this.currentFile)}`;
            window.open(url, '_blank');
            this.showNotification('文件编辑器已在新标签页中打开', 'info');
        }
    }
    
    async deleteFile() {
        if (!this.currentFile) {
            this.showNotification('请先选择一个文件', 'warning');
            return;
        }
        
        this.showModal('确认删除', `
            <div class="form-group">
                <p>确定要删除文件 <strong>"${this.currentFile}"</strong> 吗？</p>
                <p class="text-secondary" style="margin-top: 1rem;">
                    💡 此操作为软删除，文件将被隐藏但不会真正删除，可以通过"显示隐藏"功能恢复。
                </p>
            </div>
        `, async () => {
            try {
                const response = await fetch('/api/files', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        campaign: this.currentCampaign,
                        category: this.currentCategory,
                        filename: this.currentFile
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.showNotification(`文件"${this.currentFile}"已删除`, 'success');
                    this.currentFile = null;
                    this.clearViewer();
                    this.hideViewerActions();
                    this.loadFiles();
                    return true;
                } else {
                    this.showNotification(result.error || '删除文件失败', 'error');
                    return false;
                }
            } catch (error) {
                console.error('删除文件失败:', error);
                this.showNotification('删除文件失败', 'error');
                return false;
            }
        });
    }
    
    openFile(fileName) {
        // 双击打开文件的逻辑
        if (fileName.startsWith('[DIR]')) {
            // 如果是目录，进入目录
            this.showNotification('目录导航功能开发中', 'info');
        } else {
            // 如果是文件，使用系统默认程序打开
            this.showNotification('请使用右侧的编辑按钮编辑文件', 'info');
        }
    }
    
    importFile() {
        this.showNotification('文件导入功能开发中', 'info');
    }
    
    toggleHiddenFiles() {
        this.showHidden = !this.showHidden;
        const btn = document.getElementById('showHiddenBtn');
        
        if (this.showHidden) {
            btn.innerHTML = '<span class="icon">👁️‍🗨️</span>隐藏已删除';
            this.showNotification('隐藏文件显示功能开发中', 'info');
        } else {
            btn.innerHTML = '<span class="icon">👁️</span>显示隐藏';
        }
        
        // 重新加载文件列表
        this.loadFiles();
    }
    
    // ==================== 查看器管理 ====================
    
    clearViewer() {
        document.getElementById('viewerContent').innerHTML = `
            <div class="viewer-placeholder">
                <span class="placeholder-icon">📄</span>
                <p>选择文件查看内容</p>
            </div>
        `;
        this.hideViewerActions();
    }
    
    showViewerActions() {
        document.getElementById('viewerActions').style.display = 'flex';
    }
    
    hideViewerActions() {
        document.getElementById('viewerActions').style.display = 'none';
    }
    
    // ==================== 模态对话框 ====================
    
    showModal(title, content, onConfirm = null) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalBody').innerHTML = content;
        document.getElementById('modal').style.display = 'flex';
        
        // 设置确认按钮事件
        const confirmBtn = document.getElementById('modalConfirm');
        confirmBtn.onclick = async () => {
            if (onConfirm) {
                const result = await onConfirm();
                if (result !== false) {
                    this.hideModal();
                }
            } else {
                this.hideModal();
            }
        };
    }
    
    hideModal() {
        document.getElementById('modal').style.display = 'none';
    }
    
    // ==================== 通知系统 ====================
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.getElementById('notifications').appendChild(notification);
        
        // 自动移除
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // ==================== 工具方法 ====================
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    refresh() {
        this.loadCampaigns();
        if (this.currentCampaign) {
            this.loadFiles();
        }
        this.showNotification('数据已刷新', 'success');
    }
    
    showHelp() {
        this.showModal('帮助信息', `
            <div class="help-content">
                <h4>🎯 基本操作</h4>
                <ul style="margin: 0.5rem 0 1rem 1rem;">
                    <li>创建跑团：点击左侧"新建"按钮</li>
                    <li>选择跑团：点击跑团名称</li>
                    <li>切换分类：点击顶部标签</li>
                    <li>管理文件：使用工具栏按钮</li>
                </ul>
                
                <h4>📝 文件类型</h4>
                <ul style="margin: 0.5rem 0 1rem 1rem;">
                    <li>👥 人物卡：角色信息和属性</li>
                    <li>👹 怪物卡：怪物数据和能力</li>
                    <li>🗺️ 地图：地图图片和说明</li>
                    <li>📖 剧情：文本笔记和结构化剧情</li>
                </ul>
                
                <h4>🌐 Web编辑器</h4>
                <ul style="margin: 0.5rem 0 1rem 1rem;">
                    <li>JSON剧情文件支持Web编辑器</li>
                    <li>提供可视化节点编辑</li>
                    <li>实时保存和数据验证</li>
                    <li>支持剧情流程图生成</li>
                </ul>
                
                <h4>🔒 安全机制</h4>
                <ul style="margin: 0.5rem 0 1rem 1rem;">
                    <li>删除文件为软删除（隐藏）</li>
                    <li>可通过"显示隐藏"恢复文件</li>
                    <li>所有数据本地存储</li>
                </ul>
            </div>
        `);
    }
    
    handleKeyboard(e) {
        // 快捷键处理
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'n':
                    e.preventDefault();
                    if (this.currentCampaign) {
                        this.showCreateFileDialog();
                    } else {
                        this.showCreateCampaignDialog();
                    }
                    break;
                case 'r':
                    e.preventDefault();
                    this.refresh();
                    break;
            }
        }
        
        // ESC键关闭模态框
        if (e.key === 'Escape') {
            this.hideModal();
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM加载完成，开始初始化DND管理器');
    
    // 过滤扩展程序错误
    const originalError = window.onerror;
    window.onerror = function(message, source, lineno, colno, error) {
        // 忽略浏览器扩展程序的错误
        if (message && message.includes('runtime.lastError')) {
            return true; // 阻止错误显示
        }
        
        // 显示真正的错误
        console.error('页面JavaScript错误:', message, 'at', source + ':' + lineno);
        
        if (originalError) {
            return originalError(message, source, lineno, colno, error);
        }
        return false;
    };
    
    // 过滤Promise rejection错误
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.toString().includes('runtime.lastError')) {
            event.preventDefault(); // 阻止错误显示
            return;
        }
        
        console.error('未处理的Promise rejection:', event.reason);
    });
    
    try {
        window.dndManager = new DNDManager();
        console.log('✅ DND管理器初始化成功');
    } catch (error) {
        console.error('❌ DND管理器初始化失败:', error);
        
        // 显示错误信息给用户
        const body = document.body;
        if (body) {
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                max-width: 400px;
                z-index: 9999;
                font-family: Arial, sans-serif;
            `;
            errorDiv.innerHTML = `
                <strong>⚠️ 初始化错误</strong><br>
                ${error.message}<br>
                <small>请检查浏览器控制台获取详细信息</small>
            `;
            body.appendChild(errorDiv);
        }
    }
});