/**
 * 剧情编辑器 JavaScript
 * 提供完整的剧情编辑功能
 */

class StoryEditor {
    constructor() {
        this.currentCampaign = null;
        this.currentStory = null;
        this.storyData = null;
        this.currentNode = null;
        this.hasUnsavedChanges = false;
        this.autoSaveTimer = null;
        this.autoSaveInterval = 30000; // 30秒自动保存
        this.lastSaveTime = null;
        
        // 撤销/重做系统
        this.undoStack = [];
        this.redoStack = [];
        this.maxUndoSteps = 50;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCampaigns();
        this.parseURLParams();
    }
    
    parseURLParams() {
        const params = new URLSearchParams(window.location.search);
        const campaign = params.get('campaign');
        const story = params.get('story');
        
        if (campaign) {
            this.currentCampaign = campaign;
            document.getElementById('campaign-name').textContent = campaign;
            
            if (story) {
                this.currentStory = story;
                document.getElementById('story-name').textContent = story;
                // 延迟加载，等待跑团列表加载完成
                setTimeout(() => this.loadStoryFromParams(campaign, story), 500);
            }
        }
    }
    
    async loadStoryFromParams(campaign, story) {
        try {
            // 设置跑团选择
            const campaignSelect = document.getElementById('campaign-select');
            campaignSelect.value = campaign;
            await this.onCampaignChange();
            
            // 设置剧情选择
            const storySelect = document.getElementById('story-select');
            storySelect.value = story;
            
            // 加载剧情
            await this.loadStory();
        } catch (error) {
            console.error('从URL参数加载剧情失败:', error);
        }
    }
    
    bindEvents() {
        // 跑团和剧情选择
        document.getElementById('campaign-select').addEventListener('change', () => this.onCampaignChange());
        document.getElementById('story-select').addEventListener('change', () => this.onStoryChange());
        document.getElementById('load-story-btn').addEventListener('click', () => this.loadStory());
        
        // 工具栏按钮
        document.getElementById('new-story-btn').addEventListener('click', () => this.newStory());
        document.getElementById('save-btn').addEventListener('click', () => this.saveStory());
        document.getElementById('undo-btn').addEventListener('click', () => this.undo());
        document.getElementById('redo-btn').addEventListener('click', () => this.redo());
        
        // 节点操作
        document.getElementById('add-main-node-btn').addEventListener('click', () => this.addNode('main'));
        document.getElementById('add-branch-node-btn').addEventListener('click', () => this.addNode('branch'));
        document.getElementById('delete-node-btn').addEventListener('click', () => this.deleteNode());
        
        // 标签页切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab-btn').dataset.tab));
        });
        
        // 各标签页功能按钮
        document.getElementById('refresh-chart-btn').addEventListener('click', () => this.refreshFlowChart());
        document.getElementById('export-chart-btn').addEventListener('click', () => this.exportChart());
        document.getElementById('run-validation-btn').addEventListener('click', () => this.runValidation());
        
        // 导出按钮
        document.getElementById('export-txt-btn').addEventListener('click', () => this.exportAs('txt'));
        document.getElementById('export-md-btn').addEventListener('click', () => this.exportAs('md'));
        document.getElementById('export-svg-btn').addEventListener('click', () => this.exportAs('svg'));
        document.getElementById('export-png-btn').addEventListener('click', () => this.exportAs('png'));
        document.getElementById('export-json-btn').addEventListener('click', () => this.exportAs('json'));
        document.getElementById('export-csv-btn').addEventListener('click', () => this.exportAs('csv'));
        
        // 表单变化监听
        this.bindFormEvents();
        
        // 模态对话框
        document.getElementById('modal-close').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-cancel').addEventListener('click', () => this.hideModal());
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.hideModal();
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // 页面离开提醒
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '有未保存的更改，确定要离开吗？';
            }
        });
    }
    
    bindFormEvents() {
        const formElements = [
            'node-id', 'node-type', 'node-title', 'node-next', 'node-content'
        ];
        
        formElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', () => this.onFormChange());
                element.addEventListener('change', () => this.onFormChange());
            }
        });
    }
    
    handleKeyboard(e) {
        // Ctrl+S 保存
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            this.saveStory();
        }
        
        // Ctrl+N 新建
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            this.newStory();
        }
        
        // Ctrl+Z 撤销
        if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
            e.preventDefault();
            this.undo();
        }
        
        // Ctrl+Shift+Z 或 Ctrl+Y 重做
        if (e.ctrlKey && ((e.key === 'z' && e.shiftKey) || e.key === 'y')) {
            e.preventDefault();
            this.redo();
        }
        
        // Delete 删除节点
        if (e.key === 'Delete' && this.currentNode && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            this.deleteNode();
        }
    }
    
    // API 调用方法
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(`/api/${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`API错误响应:`, errorText);
                
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.error || `HTTP ${response.status}`);
                } catch (parseError) {
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error(`API调用失败 (${endpoint}):`, error);
            throw error;
        }
    }
    
    // 状态管理
    setStatus(text, type = 'ready') {
        document.getElementById('status-text').textContent = text;
        const dot = document.getElementById('status-dot');
        dot.className = `status-dot status-${type}`;
    }
    
    showLoading(show = true) {
        document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
    }
    
    showModal(title, message, options = {}) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-message').textContent = message;
        
        const confirmBtn = document.getElementById('modal-confirm');
        const cancelBtn = document.getElementById('modal-cancel');
        
        // 重置按钮
        confirmBtn.onclick = null;
        confirmBtn.textContent = options.confirmText || '确定';
        confirmBtn.className = `btn ${options.confirmClass || 'btn-primary'}`;
        
        cancelBtn.style.display = options.showCancel !== false ? 'inline-flex' : 'none';
        
        document.getElementById('modal-overlay').style.display = 'flex';
        
        return new Promise((resolve) => {
            confirmBtn.onclick = () => {
                this.hideModal();
                resolve(true);
            };
            
            cancelBtn.onclick = () => {
                this.hideModal();
                resolve(false);
            };
        });
    }
    
    hideModal() {
        document.getElementById('modal-overlay').style.display = 'none';
    }
    
    markUnsaved() {
        this.hasUnsavedChanges = true;
        document.getElementById('save-btn').disabled = false;
        this.setStatus('有未保存的更改', 'loading');
        
        // 启动自动保存定时器
        this.startAutoSaveTimer();
    }
    
    markSaved() {
        this.hasUnsavedChanges = false;
        document.getElementById('save-btn').disabled = true;
        this.lastSaveTime = new Date();
        this.setStatus(`已保存 (${this.formatTime(this.lastSaveTime)})`, 'ready');
        
        // 清除自动保存定时器
        this.clearAutoSaveTimer();
    }
    
    startAutoSaveTimer() {
        // 清除现有定时器
        this.clearAutoSaveTimer();
        
        // 只有在有跑团和剧情的情况下才启动自动保存
        if (this.currentCampaign && this.currentStory && this.storyData) {
            this.autoSaveTimer = setTimeout(() => {
                this.autoSave();
            }, this.autoSaveInterval);
        }
    }
    
    clearAutoSaveTimer() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }
    
    async autoSave() {
        if (!this.hasUnsavedChanges || !this.currentCampaign || !this.currentStory) {
            return;
        }
        
        try {
            console.log('执行自动保存...');
            this.setStatus('自动保存中...', 'saving');
            
            // 保存当前编辑的节点
            this.saveCurrentNode();
            
            const result = await this.apiCall('story/save', {
                method: 'POST',
                body: JSON.stringify({
                    campaign: this.currentCampaign,
                    story: this.currentStory,
                    data: this.storyData
                })
            });
            
            if (result.success) {
                this.markSaved();
                console.log('自动保存成功');
            } else {
                throw new Error(result.error || '自动保存失败');
            }
        } catch (error) {
            console.error('自动保存失败:', error);
            this.setStatus('自动保存失败，请手动保存', 'error');
            // 重新启动定时器，稍后再试
            this.startAutoSaveTimer();
        }
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    // 跑团和剧情管理
    async loadCampaigns() {
        try {
            this.setStatus('加载跑团列表...', 'loading');
            
            const data = await this.apiCall('campaigns');
            
            const select = document.getElementById('campaign-select');
            select.innerHTML = '<option value="">请选择跑团</option>';
            
            if (!data.campaigns || data.campaigns.length === 0) {
                select.innerHTML += '<option value="" disabled>没有找到跑团</option>';
                this.setStatus('没有找到跑团', 'error');
                return;
            }
            
            data.campaigns.forEach(campaign => {
                const option = document.createElement('option');
                option.value = campaign;
                option.textContent = campaign;
                select.appendChild(option);
            });
            
            // 如果有预设的跑团，选中它
            if (this.currentCampaign) {
                select.value = this.currentCampaign;
                await this.onCampaignChange();
            }
            
            this.setStatus('就绪', 'ready');
        } catch (error) {
            console.error('加载跑团列表失败:', error);
            this.setStatus('加载跑团列表失败', 'error');
            this.showModal('错误', `加载跑团列表失败: ${error.message}\n\n请检查：\n1. 是否已创建跑团\n2. 数据目录是否存在\n3. 服务器是否正常运行`);
        }
    }
    
    async onCampaignChange() {
        const campaignSelect = document.getElementById('campaign-select');
        const storySelect = document.getElementById('story-select');
        const loadBtn = document.getElementById('load-story-btn');
        
        this.currentCampaign = campaignSelect.value;
        document.getElementById('campaign-name').textContent = this.currentCampaign || '未选择跑团';
        
        if (!this.currentCampaign) {
            storySelect.innerHTML = '<option value="">请先选择跑团</option>';
            storySelect.disabled = true;
            loadBtn.disabled = true;
            return;
        }
        
        try {
            this.setStatus('加载剧情列表...', 'loading');
            const data = await this.apiCall(`stories?campaign=${encodeURIComponent(this.currentCampaign)}`);
            
            storySelect.innerHTML = '<option value="">请选择剧情</option>';
            storySelect.innerHTML += '<option value="__new__">+ 新建剧情</option>';
            
            data.stories.forEach(story => {
                const option = document.createElement('option');
                option.value = story;
                option.textContent = story;
                storySelect.appendChild(option);
            });
            
            storySelect.disabled = false;
            this.setStatus('就绪', 'ready');
        } catch (error) {
            this.setStatus('加载剧情列表失败', 'error');
            storySelect.innerHTML = '<option value="">加载失败</option>';
            storySelect.disabled = true;
        }
    }
    
    onStoryChange() {
        const storySelect = document.getElementById('story-select');
        const loadBtn = document.getElementById('load-story-btn');
        
        this.currentStory = storySelect.value;
        loadBtn.disabled = !this.currentStory;
        
        if (this.currentStory === '__new__') {
            loadBtn.textContent = '新建剧情';
        } else {
            loadBtn.textContent = '加载剧情';
        }
    }
    
    async loadStory() {
        if (!this.currentCampaign) {
            this.showModal('错误', '请先选择跑团');
            return;
        }
        
        const storySelect = document.getElementById('story-select');
        const storyName = storySelect.value;
        
        if (storyName === '__new__') {
            await this.newStory();
            return;
        }
        
        if (!storyName) {
            this.showModal('错误', '请选择要加载的剧情');
            return;
        }
        
        try {
            this.showLoading(true);
            this.setStatus('加载剧情数据...', 'loading');
            
            const data = await this.apiCall(`story?campaign=${encodeURIComponent(this.currentCampaign)}&story=${encodeURIComponent(storyName)}`);
            
            this.storyData = data;
            this.currentStory = storyName;
            this.currentNode = null;
            
            document.getElementById('story-name').textContent = storyName;
            
            this.renderNodeList();
            this.renderNodeEditor();
            this.renderBranchEditor();
            this.updateStatistics();
            
            this.markSaved();
            this.setStatus('剧情加载完成', 'ready');
        } catch (error) {
            this.setStatus('加载剧情失败', 'error');
            this.showModal('错误', `加载剧情失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    async newStory() {
        if (this.hasUnsavedChanges) {
            const confirmed = await this.showModal('确认', '有未保存的更改，确定要新建剧情吗？', {
                confirmText: '确定',
                confirmClass: 'btn-danger'
            });
            if (!confirmed) return;
        }
        
        const title = await this.promptInput('新建剧情', '请输入剧情标题:', '新剧情');
        if (!title) return;
        
        try {
            this.setStatus('创建新剧情...', 'loading');
            
            const data = await this.apiCall('story/new', {
                method: 'POST',
                body: JSON.stringify({ title })
            });
            
            this.storyData = data;
            this.currentStory = null;
            this.currentNode = null;
            
            document.getElementById('story-name').textContent = title;
            document.getElementById('story-select').value = '';
            
            this.renderNodeList();
            this.renderNodeEditor();
            this.renderBranchEditor();
            this.updateStatistics();
            
            this.markUnsaved();
            this.setStatus('新剧情已创建', 'ready');
        } catch (error) {
            this.setStatus('创建剧情失败', 'error');
            this.showModal('错误', `创建剧情失败: ${error.message}`);
        }
    }
    
    async saveStory() {
        if (!this.storyData || !this.currentCampaign) {
            this.showModal('错误', '没有可保存的剧情数据');
            return;
        }
        
        // 保存当前编辑的节点
        this.saveCurrentNode();
        
        let storyName = this.currentStory;
        
        // 如果是新剧情，询问文件名
        if (!storyName) {
            storyName = await this.promptInput('保存剧情', '请输入剧情文件名:', this.storyData.title || '新剧情');
            if (!storyName) return;
        }
        
        try {
            this.showLoading(true);
            this.setStatus('保存剧情...', 'saving');
            
            const result = await this.apiCall('story/save', {
                method: 'POST',
                body: JSON.stringify({
                    campaign: this.currentCampaign,
                    story: storyName,
                    data: this.storyData
                })
            });
            
            if (result.success) {
                this.currentStory = storyName;
                document.getElementById('story-name').textContent = storyName;
                
                // 更新剧情选择列表
                if (!document.querySelector(`#story-select option[value="${storyName}"]`)) {
                    const option = document.createElement('option');
                    option.value = storyName;
                    option.textContent = storyName;
                    document.getElementById('story-select').appendChild(option);
                }
                document.getElementById('story-select').value = storyName;
                
                this.markSaved();
                this.setStatus('保存成功', 'ready');
                this.showModal('成功', '剧情保存成功', { showCancel: false });
            } else {
                throw new Error(result.error || '保存失败');
            }
        } catch (error) {
            this.setStatus('保存失败', 'error');
            this.showModal('错误', `保存剧情失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    // 节点管理
    addNode(type = 'main') {
        if (!this.storyData) {
            this.showModal('错误', '请先加载或创建剧情');
            return;
        }
        
        // 保存状态用于撤销
        this.saveState(`添加${type === 'main' ? '主线' : '分支'}节点`);
        
        const nodeCount = this.storyData.nodes.length;
        const newNode = {
            id: `node_${String(nodeCount + 1).padStart(2, '0')}`,
            type: type,
            title: '新节点',
            content: '',
            next: null
        };
        
        if (type === 'main') {
            newNode.branches = [];
        }
        
        this.storyData.nodes.push(newNode);
        this.renderNodeList();
        this.updateStatistics();
        this.markUnsaved();
        
        // 选中新节点
        this.selectNode(newNode);
    }
    
    async deleteNode() {
        if (!this.currentNode) {
            this.showModal('错误', '请先选择要删除的节点');
            return;
        }
        
        const confirmed = await this.showModal('确认删除', 
            `确定要删除节点 "${this.currentNode.id}" 吗？\n\n这将同时删除所有对该节点的引用。`, {
            confirmText: '删除',
            confirmClass: 'btn-danger'
        });
        
        if (!confirmed) return;
        
        // 保存状态用于撤销
        this.saveState(`删除节点 ${this.currentNode.id}`);
        
        const nodeId = this.currentNode.id;
        
        // 删除节点
        this.storyData.nodes = this.storyData.nodes.filter(node => node.id !== nodeId);
        
        // 清理引用
        this.cleanupNodeReferences(nodeId);
        
        this.currentNode = null;
        this.renderNodeList();
        this.renderNodeEditor();
        this.renderBranchEditor();
        this.updateStatistics();
        this.markUnsaved();
        
        this.setStatus(`节点 "${nodeId}" 已删除`, 'ready');
    }
    
    cleanupNodeReferences(deletedId) {
        this.storyData.nodes.forEach(node => {
            // 清理 next 引用
            if (node.next === deletedId) {
                node.next = null;
            }
            
            // 清理分支引用
            if (node.branches) {
                node.branches.forEach(branch => {
                    if (branch.entry === deletedId) {
                        branch.entry = '';
                    }
                    if (branch.exit === deletedId) {
                        branch.exit = '';
                    }
                });
            }
        });
    }
    
    selectNode(node) {
        // 保存当前节点的修改
        this.saveCurrentNode();
        
        this.currentNode = node;
        this.renderNodeList();
        this.renderNodeEditor();
        this.renderBranchEditor();
        
        // 启用删除按钮
        document.getElementById('delete-node-btn').disabled = false;
    }
    
    saveCurrentNode() {
        if (!this.currentNode) return;
        
        const form = document.getElementById('node-form');
        if (form.style.display === 'none') return;
        
        // 获取表单数据
        const nodeId = document.getElementById('node-id').value.trim();
        const nodeType = document.getElementById('node-type').value;
        const nodeTitle = document.getElementById('node-title').value.trim();
        const nodeNext = document.getElementById('node-next').value || null;
        const nodeContent = document.getElementById('node-content').value.trim();
        
        // 检查ID重复
        if (nodeId !== this.currentNode.id) {
            const existingNode = this.storyData.nodes.find(n => n !== this.currentNode && n.id === nodeId);
            if (existingNode) {
                this.showModal('错误', `节点ID "${nodeId}" 已存在`);
                document.getElementById('node-id').value = this.currentNode.id;
                return;
            }
        }
        
        // 更新节点数据
        const oldId = this.currentNode.id;
        this.currentNode.id = nodeId;
        this.currentNode.type = nodeType;
        this.currentNode.title = nodeTitle;
        this.currentNode.next = nodeNext;
        this.currentNode.content = nodeContent;
        
        // 处理分支
        if (nodeType === 'main') {
            if (!this.currentNode.branches) {
                this.currentNode.branches = [];
            }
        } else {
            delete this.currentNode.branches;
        }
        
        // 如果ID改变了，更新引用
        if (oldId !== nodeId) {
            this.updateNodeReferences(oldId, nodeId);
        }
    }
    
    updateNodeReferences(oldId, newId) {
        this.storyData.nodes.forEach(node => {
            // 更新 next 引用
            if (node.next === oldId) {
                node.next = newId;
            }
            
            // 更新分支引用
            if (node.branches) {
                node.branches.forEach(branch => {
                    if (branch.entry === oldId) {
                        branch.entry = newId;
                    }
                    if (branch.exit === oldId) {
                        branch.exit = newId;
                    }
                });
            }
        });
    }
    
    onFormChange() {
        if (this.currentNode) {
            this.markUnsaved();
        }
    }
    
    // 分支管理
    addBranch() {
        if (!this.currentNode || this.currentNode.type !== 'main') {
            this.showModal('错误', '只有主线节点可以添加分支');
            return;
        }
        
        if (!this.currentNode.branches) {
            this.currentNode.branches = [];
        }
        
        const branchCount = this.currentNode.branches.length;
        const newBranch = {
            choice: `选择${branchCount + 1}`,
            entry: '',
            exit: ''
        };
        
        this.currentNode.branches.push(newBranch);
        this.renderBranchEditor();
        this.markUnsaved();
    }
    
    deleteBranch(index) {
        if (!this.currentNode || !this.currentNode.branches) return;
        
        this.currentNode.branches.splice(index, 1);
        this.renderBranchEditor();
        this.markUnsaved();
    }
    
    // 渲染方法
    renderNodeList() {
        const container = document.getElementById('node-list');
        
        if (!this.storyData || !this.storyData.nodes.length) {
            container.innerHTML = '<div class="empty-state"><p>暂无节点</p></div>';
            return;
        }
        
        container.innerHTML = '';
        
        this.storyData.nodes.forEach(node => {
            const item = document.createElement('div');
            item.className = 'node-item';
            if (this.currentNode && this.currentNode.id === node.id) {
                item.classList.add('active');
            }
            
            item.innerHTML = `
                <div class="node-header">
                    <div class="node-type-icon node-type-${node.type}"></div>
                    <span class="node-id">${node.id}</span>
                </div>
                <div class="node-title">${node.title || '未命名'}</div>
            `;
            
            item.addEventListener('click', () => this.selectNode(node));
            container.appendChild(item);
        });
    }
    
    renderNodeEditor() {
        const editorContainer = document.getElementById('node-editor');
        const form = document.getElementById('node-form');
        
        if (!this.currentNode) {
            editorContainer.innerHTML = '<div class="empty-state"><p>请选择一个节点进行编辑</p></div>';
            form.style.display = 'none';
            return;
        }
        
        // 显示表单
        editorContainer.innerHTML = '';
        form.style.display = 'block';
        
        // 填充表单数据
        document.getElementById('node-id').value = this.currentNode.id || '';
        document.getElementById('node-type').value = this.currentNode.type || 'main';
        document.getElementById('node-title').value = this.currentNode.title || '';
        document.getElementById('node-content').value = this.currentNode.content || '';
        
        // 更新下一个节点选项
        this.updateNodeOptions();
        document.getElementById('node-next').value = this.currentNode.next || '';
    }
    
    renderBranchEditor() {
        const container = document.getElementById('branch-editor');
        const branchList = document.getElementById('branch-list');
        const addBtn = document.getElementById('add-branch-btn');
        
        if (!this.currentNode || this.currentNode.type !== 'main') {
            container.innerHTML = '<div class="empty-state"><p>请选择主线节点编辑分支</p></div>';
            branchList.style.display = 'none';
            addBtn.disabled = true;
            return;
        }
        
        container.innerHTML = '';
        branchList.style.display = 'block';
        addBtn.disabled = false;
        
        const branches = this.currentNode.branches || [];
        
        if (!branches.length) {
            branchList.innerHTML = '<div class="empty-state"><p>暂无分支</p></div>';
            return;
        }
        
        branchList.innerHTML = '';
        
        branches.forEach((branch, index) => {
            const item = document.createElement('div');
            item.className = 'branch-item';
            
            item.innerHTML = `
                <div class="branch-header">
                    <span class="branch-title">${branch.choice || `分支${index + 1}`}</span>
                    <button class="branch-toggle">▼</button>
                </div>
                <div class="branch-content">
                    <div class="form-group">
                        <label>选项文本:</label>
                        <input type="text" class="form-control branch-choice" value="${branch.choice || ''}" data-index="${index}">
                    </div>
                    <div class="form-group">
                        <label>入口节点:</label>
                        <select class="form-control branch-entry" data-index="${index}">
                            <option value="">无</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>出口节点:</label>
                        <select class="form-control branch-exit" data-index="${index}">
                            <option value="">无</option>
                        </select>
                    </div>
                    <div class="branch-actions">
                        <button class="btn btn-sm btn-danger delete-branch-btn" data-index="${index}">删除分支</button>
                    </div>
                </div>
            `;
            
            branchList.appendChild(item);
            
            // 绑定事件
            const header = item.querySelector('.branch-header');
            const content = item.querySelector('.branch-content');
            const toggle = item.querySelector('.branch-toggle');
            
            header.addEventListener('click', () => {
                const isActive = content.classList.contains('active');
                content.classList.toggle('active', !isActive);
                toggle.textContent = isActive ? '▼' : '▲';
            });
            
            // 分支表单事件
            const choiceInput = item.querySelector('.branch-choice');
            const entrySelect = item.querySelector('.branch-entry');
            const exitSelect = item.querySelector('.branch-exit');
            const deleteBtn = item.querySelector('.delete-branch-btn');
            
            // 填充节点选项
            this.populateNodeSelect(entrySelect);
            this.populateNodeSelect(exitSelect);
            entrySelect.value = branch.entry || '';
            exitSelect.value = branch.exit || '';
            
            // 绑定变化事件
            choiceInput.addEventListener('input', (e) => {
                branch.choice = e.target.value;
                item.querySelector('.branch-title').textContent = e.target.value || `分支${index + 1}`;
                this.markUnsaved();
            });
            
            entrySelect.addEventListener('change', (e) => {
                branch.entry = e.target.value;
                this.markUnsaved();
            });
            
            exitSelect.addEventListener('change', (e) => {
                branch.exit = e.target.value;
                this.markUnsaved();
            });
            
            deleteBtn.addEventListener('click', () => this.deleteBranch(index));
        });
    }
    
    updateNodeOptions() {
        const select = document.getElementById('node-next');
        this.populateNodeSelect(select);
    }
    
    populateNodeSelect(select) {
        const currentValue = select.value;
        select.innerHTML = '<option value="">无</option>';
        
        if (this.storyData && this.storyData.nodes) {
            this.storyData.nodes.forEach(node => {
                const option = document.createElement('option');
                option.value = node.id;
                option.textContent = `${node.id}: ${node.title || '未命名'}`;
                select.appendChild(option);
            });
        }
        
        select.value = currentValue;
    }
    
    async updateStatistics() {
        if (!this.storyData) {
            document.getElementById('total-nodes').textContent = '0';
            document.getElementById('main-nodes').textContent = '0';
            document.getElementById('branch-nodes').textContent = '0';
            document.getElementById('total-branches').textContent = '0';
            return;
        }
        
        const stats = this.calculateDetailedStats();
        document.getElementById('total-nodes').textContent = stats.totalNodes;
        document.getElementById('main-nodes').textContent = stats.mainNodes;
        document.getElementById('branch-nodes').textContent = stats.branchNodes;
        document.getElementById('total-branches').textContent = stats.totalBranches;
        
        // 如果当前在概览标签页，更新概览内容
        const activeTab = document.querySelector('.tab-btn.active');
        if (activeTab && activeTab.dataset.tab === 'story-overview') {
            this.loadStoryOverview();
        }
    }
    
    // 工具方法
    async promptInput(title, message, defaultValue = '') {
        return new Promise((resolve) => {
            const modal = document.getElementById('modal-overlay');
            const modalTitle = document.getElementById('modal-title');
            const modalMessage = document.getElementById('modal-message');
            const modalForm = document.getElementById('modal-form');
            const confirmBtn = document.getElementById('modal-confirm');
            const cancelBtn = document.getElementById('modal-cancel');
            
            modalTitle.textContent = title;
            modalMessage.textContent = message;
            
            // 创建输入框
            modalForm.innerHTML = `
                <div class="form-group">
                    <input type="text" id="prompt-input" class="form-control" value="${defaultValue}" placeholder="请输入...">
                </div>
            `;
            modalForm.style.display = 'block';
            
            modal.style.display = 'flex';
            
            const input = document.getElementById('prompt-input');
            input.focus();
            input.select();
            
            const handleConfirm = () => {
                const value = input.value.trim();
                modal.style.display = 'none';
                modalForm.style.display = 'none';
                resolve(value || null);
            };
            
            const handleCancel = () => {
                modal.style.display = 'none';
                modalForm.style.display = 'none';
                resolve(null);
            };
            
            confirmBtn.onclick = handleConfirm;
            cancelBtn.onclick = handleCancel;
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleConfirm();
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    handleCancel();
                }
            });
        });
    }
}

// 撤销/重做系统扩展
StoryEditor.prototype.saveState = function(description = '') {
    if (!this.storyData) return;
    
    const state = {
        data: JSON.parse(JSON.stringify(this.storyData)),
        currentNodeId: this.currentNode ? this.currentNode.id : null,
        timestamp: Date.now(),
        description: description
    };
    
    this.undoStack.push(state);
    
    // 限制撤销栈大小
    if (this.undoStack.length > this.maxUndoSteps) {
        this.undoStack.shift();
    }
    
    // 清空重做栈
    this.redoStack = [];
    
    this.updateUndoRedoButtons();
};

StoryEditor.prototype.undo = function() {
    if (this.undoStack.length === 0) return;
    
    // 保存当前状态到重做栈
    const currentState = {
        data: JSON.parse(JSON.stringify(this.storyData)),
        currentNodeId: this.currentNode ? this.currentNode.id : null,
        timestamp: Date.now(),
        description: '当前状态'
    };
    this.redoStack.push(currentState);
    
    // 恢复上一个状态
    const previousState = this.undoStack.pop();
    this.storyData = previousState.data;
    
    // 重新渲染界面
    this.renderNodeList();
    this.renderNodeEditor();
    this.renderBranchEditor();
    this.updateStatistics();
    
    // 尝试恢复选中的节点
    if (previousState.currentNodeId) {
        const node = this.storyData.nodes.find(n => n.id === previousState.currentNodeId);
        if (node) {
            this.selectNode(node);
        }
    }
    
    this.markUnsaved();
    this.updateUndoRedoButtons();
    this.setStatus(`已撤销: ${previousState.description}`, 'ready');
};

StoryEditor.prototype.redo = function() {
    if (this.redoStack.length === 0) return;
    
    // 保存当前状态到撤销栈
    const currentState = {
        data: JSON.parse(JSON.stringify(this.storyData)),
        currentNodeId: this.currentNode ? this.currentNode.id : null,
        timestamp: Date.now(),
        description: '撤销前状态'
    };
    this.undoStack.push(currentState);
    
    // 恢复重做状态
    const nextState = this.redoStack.pop();
    this.storyData = nextState.data;
    
    // 重新渲染界面
    this.renderNodeList();
    this.renderNodeEditor();
    this.renderBranchEditor();
    this.updateStatistics();
    
    // 尝试恢复选中的节点
    if (nextState.currentNodeId) {
        const node = this.storyData.nodes.find(n => n.id === nextState.currentNodeId);
        if (node) {
            this.selectNode(node);
        }
    }
    
    this.markUnsaved();
    this.updateUndoRedoButtons();
    this.setStatus(`已重做: ${nextState.description}`, 'ready');
};

StoryEditor.prototype.updateUndoRedoButtons = function() {
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    
    if (undoBtn) {
        undoBtn.disabled = this.undoStack.length === 0;
        undoBtn.title = this.undoStack.length > 0 
            ? `撤销: ${this.undoStack[this.undoStack.length - 1].description} (Ctrl+Z)`
            : '撤销 (Ctrl+Z)';
    }
    
    if (redoBtn) {
        redoBtn.disabled = this.redoStack.length === 0;
        redoBtn.title = this.redoStack.length > 0 
            ? `重做: ${this.redoStack[this.redoStack.length - 1].description} (Ctrl+Y)`
            : '重做 (Ctrl+Y)';
    }
};

// 节点搜索功能
StoryEditor.prototype.onNodeSearch = function(searchTerm) {
    const clearBtn = document.getElementById('clear-search-btn');
    
    if (searchTerm.trim()) {
        clearBtn.style.display = 'inline-flex';
        this.filterNodes(searchTerm);
    } else {
        clearBtn.style.display = 'none';
        this.renderNodeList();
    }
};

StoryEditor.prototype.clearNodeSearch = function() {
    document.getElementById('node-search-input').value = '';
    document.getElementById('clear-search-btn').style.display = 'none';
    this.renderNodeList();
};

StoryEditor.prototype.filterNodes = function(searchTerm) {
    const container = document.getElementById('node-list');
    
    if (!this.storyData || !this.storyData.nodes.length) {
        container.innerHTML = '<div class="empty-state"><p>暂无节点</p></div>';
        return;
    }
    
    const term = searchTerm.toLowerCase();
    const filteredNodes = this.storyData.nodes.filter(node => {
        return node.id.toLowerCase().includes(term) ||
               (node.title && node.title.toLowerCase().includes(term)) ||
               (node.content && node.content.toLowerCase().includes(term));
    });
    
    container.innerHTML = '';
    
    if (filteredNodes.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>未找到匹配的节点</p></div>';
        return;
    }
    
    filteredNodes.forEach(node => {
        const item = document.createElement('div');
        item.className = 'node-item';
        if (this.currentNode && this.currentNode.id === node.id) {
            item.classList.add('active');
        }
        
        // 高亮搜索词
        const highlightText = (text) => {
            if (!text) return '';
            const regex = new RegExp(`(${term})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        };
        
        item.innerHTML = `
            <div class="node-header">
                <div class="node-type-icon node-type-${node.type}"></div>
                <span class="node-id">${highlightText(node.id)}</span>
            </div>
            <div class="node-title">${highlightText(node.title || '未命名')}</div>
        `;
        
        item.addEventListener('click', () => this.selectNode(node));
        container.appendChild(item);
    });
};

// 节点拖拽功能
StoryEditor.prototype.onNodeDragStart = function(e, node) {
    e.dataTransfer.setData('text/plain', node.id);
    e.target.classList.add('dragging');
    this.draggedNode = node;
};

StoryEditor.prototype.onNodeDragOver = function(e) {
    e.preventDefault();
    e.target.closest('.node-item')?.classList.add('drag-over');
};

StoryEditor.prototype.onNodeDrop = function(e, targetNode) {
    e.preventDefault();
    
    const draggedNodeId = e.dataTransfer.getData('text/plain');
    const draggedNode = this.storyData.nodes.find(n => n.id === draggedNodeId);
    
    if (!draggedNode || draggedNode === targetNode) {
        this.clearDragStyles();
        return;
    }
    
    // 保存状态用于撤销
    this.saveState(`移动节点 ${draggedNode.id}`);
    
    // 重新排序节点
    const draggedIndex = this.storyData.nodes.indexOf(draggedNode);
    const targetIndex = this.storyData.nodes.indexOf(targetNode);
    
    // 移除拖拽的节点
    this.storyData.nodes.splice(draggedIndex, 1);
    
    // 插入到目标位置
    const newIndex = draggedIndex < targetIndex ? targetIndex - 1 : targetIndex;
    this.storyData.nodes.splice(newIndex, 0, draggedNode);
    
    this.renderNodeList();
    this.markUnsaved();
    this.clearDragStyles();
};

// 标签页系统
StoryEditor.prototype.switchTab = function(tabId) {
    // 更新标签按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // 更新标签页内容
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`tab-${tabId}`).classList.add('active');
    
    // 根据标签页类型加载内容
    switch(tabId) {
        case 'story-overview':
            this.loadStoryOverview();
            break;
        case 'flow-chart':
            this.loadFlowChart();
            break;
        case 'validation':
            this.loadValidation();
            break;
        case 'export':
            this.loadExportOptions();
            break;
    }
};

// 剧情概览功能
StoryEditor.prototype.loadStoryOverview = function() {
    if (!this.storyData) return;
    
    const statsContainer = document.getElementById('overview-stats');
    const stats = this.calculateDetailedStats();
    
    statsContainer.innerHTML = `
        <div class="stat-card">
            <span class="stat-number">${stats.totalNodes}</span>
            <div class="stat-label">总节点数</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.mainNodes}</span>
            <div class="stat-label">主线节点</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.branchNodes}</span>
            <div class="stat-label">分支节点</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.totalBranches}</span>
            <div class="stat-label">分支选项</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.avgContentLength}</span>
            <div class="stat-label">平均内容长度</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">${stats.completionRate}%</span>
            <div class="stat-label">完成度</div>
        </div>
    `;
    
    // 加载节点分布图
    this.loadNodeDistribution();
    
    // 加载问题检测
    this.loadIssueDetection();
    
    // 加载剧情路径
    this.loadStoryPaths();
};

StoryEditor.prototype.calculateDetailedStats = function() {
    if (!this.storyData || !this.storyData.nodes) {
        return {
            totalNodes: 0, mainNodes: 0, branchNodes: 0, totalBranches: 0,
            avgContentLength: 0, completionRate: 0
        };
    }
    
    const nodes = this.storyData.nodes;
    const mainNodes = nodes.filter(n => n.type === 'main');
    const branchNodes = nodes.filter(n => n.type === 'branch');
    const totalBranches = mainNodes.reduce((sum, n) => sum + (n.branches ? n.branches.length : 0), 0);
    
    const totalContentLength = nodes.reduce((sum, n) => sum + (n.content ? n.content.length : 0), 0);
    const avgContentLength = nodes.length > 0 ? Math.round(totalContentLength / nodes.length) : 0;
    
    const completeNodes = nodes.filter(n => n.title && n.title.trim() && n.content && n.content.trim()).length;
    const completionRate = nodes.length > 0 ? Math.round((completeNodes / nodes.length) * 100) : 0;
    
    return {
        totalNodes: nodes.length,
        mainNodes: mainNodes.length,
        branchNodes: branchNodes.length,
        totalBranches,
        avgContentLength,
        completionRate
    };
};

StoryEditor.prototype.loadNodeDistribution = function() {
    const container = document.getElementById('node-distribution');
    const stats = this.calculateDetailedStats();
    
    // 简单的文本图表，后续可以用真正的图表库
    container.innerHTML = `
        <div style="display: flex; align-items: end; gap: 10px; height: 100px; padding: 20px;">
            <div style="background: #667eea; width: 40px; height: ${(stats.mainNodes / stats.totalNodes) * 80}px; border-radius: 4px 4px 0 0;"></div>
            <div style="background: #17a2b8; width: 40px; height: ${(stats.branchNodes / stats.totalNodes) * 80}px; border-radius: 4px 4px 0 0;"></div>
        </div>
        <div style="display: flex; gap: 10px; padding: 0 20px;">
            <div style="width: 40px; text-align: center; font-size: 0.8rem;">主线</div>
            <div style="width: 40px; text-align: center; font-size: 0.8rem;">分支</div>
        </div>
    `;
};

StoryEditor.prototype.loadIssueDetection = function() {
    const container = document.getElementById('issue-detection');
    const issues = this.detectIssues();
    
    if (issues.length === 0) {
        container.innerHTML = '<div class="issue-item success">✅ 未发现问题</div>';
        return;
    }
    
    container.innerHTML = issues.map(issue => `
        <div class="issue-item ${issue.type}">
            ${issue.type === 'error' ? '❌' : '⚠️'} ${issue.message}
        </div>
    `).join('');
};

StoryEditor.prototype.detectIssues = function() {
    if (!this.storyData || !this.storyData.nodes) return [];
    
    const issues = [];
    const nodes = this.storyData.nodes;
    const nodeIds = new Set(nodes.map(n => n.id));
    
    nodes.forEach(node => {
        // 检查空标题
        if (!node.title || !node.title.trim()) {
            issues.push({
                type: 'warning',
                message: `节点 ${node.id} 缺少标题`
            });
        }
        
        // 检查空内容
        if (!node.content || !node.content.trim()) {
            issues.push({
                type: 'warning',
                message: `节点 ${node.id} 缺少内容`
            });
        }
        
        // 检查无效的 next 引用
        if (node.next && !nodeIds.has(node.next)) {
            issues.push({
                type: 'error',
                message: `节点 ${node.id} 引用了不存在的节点 ${node.next}`
            });
        }
        
        // 检查分支引用
        if (node.branches) {
            node.branches.forEach((branch, index) => {
                if (branch.entry && !nodeIds.has(branch.entry)) {
                    issues.push({
                        type: 'error',
                        message: `节点 ${node.id} 的分支 ${index + 1} 引用了不存在的入口节点 ${branch.entry}`
                    });
                }
                if (branch.exit && !nodeIds.has(branch.exit)) {
                    issues.push({
                        type: 'error',
                        message: `节点 ${node.id} 的分支 ${index + 1} 引用了不存在的出口节点 ${branch.exit}`
                    });
                }
            });
        }
    });
    
    return issues;
};

StoryEditor.prototype.loadStoryPaths = function() {
    const container = document.getElementById('story-paths');
    const paths = this.analyzeStoryPaths();
    
    if (paths.length === 0) {
        container.innerHTML = '<div class="path-item">暂无完整路径</div>';
        return;
    }
    
    container.innerHTML = paths.slice(0, 5).map((path, index) => `
        <div class="path-item">
            路径 ${index + 1}: ${path.join(' → ')} (${path.length} 步)
        </div>
    `).join('');
};

StoryEditor.prototype.analyzeStoryPaths = function() {
    if (!this.storyData || !this.storyData.nodes || this.storyData.nodes.length === 0) return [];
    
    const paths = [];
    const visited = new Set();
    
    // 从第一个节点开始分析路径
    const startNode = this.storyData.nodes[0];
    if (startNode) {
        this.findPaths(startNode.id, [], paths, visited, 10); // 限制最大深度为10
    }
    
    return paths;
};

StoryEditor.prototype.findPaths = function(nodeId, currentPath, allPaths, visited, maxDepth) {
    if (maxDepth <= 0 || visited.has(nodeId)) return;
    
    const node = this.storyData.nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    const newPath = [...currentPath, node.id];
    visited.add(nodeId);
    
    // 如果没有下一个节点，这是一个完整路径
    if (!node.next && (!node.branches || node.branches.length === 0)) {
        allPaths.push(newPath);
    } else {
        // 继续探索下一个节点
        if (node.next) {
            this.findPaths(node.next, newPath, allPaths, new Set(visited), maxDepth - 1);
        }
        
        // 探索分支
        if (node.branches) {
            node.branches.forEach(branch => {
                if (branch.entry) {
                    this.findPaths(branch.entry, newPath, allPaths, new Set(visited), maxDepth - 1);
                }
            });
        }
    }
};

// 流程图功能
StoryEditor.prototype.loadFlowChart = function() {
    const container = document.getElementById('flow-chart-container');
    container.innerHTML = '<div class="empty-state"><p>点击"刷新图表"生成剧情流程图</p></div>';
};

StoryEditor.prototype.refreshFlowChart = function() {
    if (!this.storyData || !this.storyData.nodes.length) {
        this.showModal('提示', '请先加载剧情数据');
        return;
    }
    
    const container = document.getElementById('flow-chart-container');
    const showContent = document.getElementById('show-content-preview').checked;
    const showBranches = document.getElementById('show-branch-details').checked;
    
    // 生成简单的文本流程图
    let chartHtml = '<div style="padding: 20px; font-family: monospace; line-height: 1.6;">';
    
    this.storyData.nodes.forEach((node, index) => {
        const indent = node.type === 'branch' ? '    ' : '';
        const icon = node.type === 'main' ? '●' : '○';
        
        chartHtml += `<div style="margin: 10px 0; padding: 10px; background: ${node.type === 'main' ? '#f0f8ff' : '#fff8f0'}; border-radius: 4px;">`;
        chartHtml += `${indent}${icon} <strong>${node.id}</strong>: ${node.title || '未命名'}`;
        
        if (showContent && node.content) {
            const preview = node.content.length > 50 ? node.content.substring(0, 50) + '...' : node.content;
            chartHtml += `<br>${indent}   "${preview}"`;
        }
        
        if (node.next) {
            chartHtml += `<br>${indent}   → ${node.next}`;
        }
        
        if (showBranches && node.branches && node.branches.length > 0) {
            node.branches.forEach(branch => {
                chartHtml += `<br>${indent}   ├─ ${branch.choice} → ${branch.entry || '?'} → ${branch.exit || '?'}`;
            });
        }
        
        chartHtml += '</div>';
    });
    
    chartHtml += '</div>';
    container.innerHTML = chartHtml;
};

StoryEditor.prototype.exportChart = function() {
    this.showModal('提示', '图表导出功能开发中...', { showCancel: false });
};

// 验证功能
StoryEditor.prototype.loadValidation = function() {
    const container = document.getElementById('validation-results');
    container.innerHTML = '<div class="empty-state"><p>点击"运行检查"开始验证剧情完整性</p></div>';
};

StoryEditor.prototype.runValidation = function() {
    if (!this.storyData) {
        this.showModal('提示', '请先加载剧情数据');
        return;
    }
    
    const container = document.getElementById('validation-results');
    const issues = this.detectIssues();
    const stats = this.calculateDetailedStats();
    
    let html = '';
    
    // 基本统计
    html += `
        <div class="validation-item success">
            <div class="validation-icon">📊</div>
            <div class="validation-message">
                <div class="validation-title">基本统计</div>
                <div class="validation-description">
                    总节点: ${stats.totalNodes}, 主线: ${stats.mainNodes}, 分支: ${stats.branchNodes}, 完成度: ${stats.completionRate}%
                </div>
            </div>
        </div>
    `;
    
    // 问题检测
    if (issues.length === 0) {
        html += `
            <div class="validation-item success">
                <div class="validation-icon">✅</div>
                <div class="validation-message">
                    <div class="validation-title">验证通过</div>
                    <div class="validation-description">未发现任何问题，剧情结构完整</div>
                </div>
            </div>
        `;
    } else {
        issues.forEach(issue => {
            html += `
                <div class="validation-item ${issue.type}">
                    <div class="validation-icon">${issue.type === 'error' ? '❌' : '⚠️'}</div>
                    <div class="validation-message">
                        <div class="validation-title">${issue.type === 'error' ? '错误' : '警告'}</div>
                        <div class="validation-description">${issue.message}</div>
                    </div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
};

// 导出功能
StoryEditor.prototype.loadExportOptions = function() {
    // 导出选项已在 HTML 中定义，无需额外加载
};

StoryEditor.prototype.exportAs = function(format) {
    if (!this.storyData) {
        this.showModal('提示', '请先加载剧情数据');
        return;
    }
    
    switch(format) {
        case 'txt':
            this.exportAsText();
            break;
        case 'md':
            this.exportAsMarkdown();
            break;
        case 'json':
            this.exportAsJSON();
            break;
        case 'csv':
            this.exportAsCSV();
            break;
        default:
            this.showModal('提示', `${format.toUpperCase()} 导出功能开发中...`, { showCancel: false });
    }
};

StoryEditor.prototype.exportAsText = function() {
    let content = `剧情：${this.storyData.title}\n`;
    content += `生成时间：${new Date().toLocaleString()}\n`;
    content += `节点总数：${this.storyData.nodes.length}\n\n`;
    content += '='.repeat(50) + '\n\n';
    
    this.storyData.nodes.forEach((node, index) => {
        content += `${index + 1}. 节点ID：${node.id}\n`;
        content += `   类型：${node.type === 'main' ? '主线节点' : '分支节点'}\n`;
        content += `   标题：${node.title || '未命名'}\n`;
        content += `   内容：${node.content || '无内容'}\n`;
        
        if (node.next) {
            content += `   下一节点：${node.next}\n`;
        }
        
        if (node.branches && node.branches.length > 0) {
            content += `   分支选项：\n`;
            node.branches.forEach((branch, i) => {
                content += `     ${i + 1}. ${branch.choice} → ${branch.entry} → ${branch.exit}\n`;
            });
        }
        
        content += '\n' + '-'.repeat(30) + '\n\n';
    });
    
    this.downloadFile(`${this.storyData.title || '剧情'}.txt`, content, 'text/plain');
};

StoryEditor.prototype.exportAsMarkdown = function() {
    let content = `# ${this.storyData.title}\n\n`;
    content += `**生成时间：** ${new Date().toLocaleString()}  \n`;
    content += `**节点总数：** ${this.storyData.nodes.length}\n\n`;
    
    this.storyData.nodes.forEach((node, index) => {
        content += `## ${index + 1}. ${node.id}\n\n`;
        content += `**类型：** ${node.type === 'main' ? '主线节点' : '分支节点'}  \n`;
        content += `**标题：** ${node.title || '未命名'}  \n\n`;
        
        if (node.content) {
            content += `**内容：**\n\n${node.content}\n\n`;
        }
        
        if (node.next) {
            content += `**下一节点：** ${node.next}\n\n`;
        }
        
        if (node.branches && node.branches.length > 0) {
            content += `**分支选项：**\n\n`;
            node.branches.forEach((branch, i) => {
                content += `${i + 1}. ${branch.choice} → ${branch.entry} → ${branch.exit}\n`;
            });
            content += '\n';
        }
        
        content += '---\n\n';
    });
    
    this.downloadFile(`${this.storyData.title || '剧情'}.md`, content, 'text/markdown');
};

StoryEditor.prototype.exportAsJSON = function() {
    const content = JSON.stringify(this.storyData, null, 2);
    this.downloadFile(`${this.storyData.title || '剧情'}.json`, content, 'application/json');
};

StoryEditor.prototype.exportAsCSV = function() {
    let content = 'ID,类型,标题,内容,下一节点,分支数量\n';
    
    this.storyData.nodes.forEach(node => {
        const row = [
            node.id,
            node.type === 'main' ? '主线节点' : '分支节点',
            `"${(node.title || '').replace(/"/g, '""')}"`,
            `"${(node.content || '').replace(/"/g, '""')}"`,
            node.next || '',
            node.branches ? node.branches.length : 0
        ];
        content += row.join(',') + '\n';
    });
    
    this.downloadFile(`${this.storyData.title || '剧情'}.csv`, content, 'text/csv');
};

StoryEditor.prototype.downloadFile = function(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    this.showModal('成功', `文件 "${filename}" 已下载`, { showCancel: false });
};

StoryEditor.prototype.clearDragStyles = function() {
    document.querySelectorAll('.node-item').forEach(item => {
        item.classList.remove('dragging', 'drag-over');
    });
    this.draggedNode = null;
};

// 初始化编辑器
document.addEventListener('DOMContentLoaded', () => {
    window.storyEditor = new StoryEditor();
});