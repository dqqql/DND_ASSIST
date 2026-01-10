/**
 * 角色卡查看器 JavaScript
 */

class CharacterViewer {
    constructor() {
        this.currentCampaign = '';
        this.currentCategory = 'characters';
        this.currentView = 'card';
        this.data = [];
        this.preselectedCampaign = null; // 预选的跑团（来自 URL 参数）
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCampaigns();
        
        // 检查 URL 参数中是否指定了跑团
        const urlParams = new URLSearchParams(window.location.search);
        const campaignParam = urlParams.get('campaign');
        if (campaignParam) {
            this.preselectedCampaign = campaignParam;
        }
    }
    
    bindEvents() {
        // 跑团选择
        document.getElementById('campaignSelect').addEventListener('change', (e) => {
            this.currentCampaign = e.target.value;
            if (this.currentCampaign) {
                this.loadData();
            } else {
                this.clearData();
            }
        });
        
        // 视图切换
        document.getElementById('cardViewBtn').addEventListener('click', () => {
            this.switchView('card');
        });
        
        document.getElementById('listViewBtn').addEventListener('click', () => {
            this.switchView('list');
        });
        
        // 分类切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchCategory(e.target.dataset.category);
            });
        });
        
        // 模态框关闭
        document.getElementById('closeModal').addEventListener('click', () => {
            this.closeModal();
        });
        
        // 点击模态框背景关闭
        document.getElementById('detailModal').addEventListener('click', (e) => {
            if (e.target.id === 'detailModal') {
                this.closeModal();
            }
        });
        
        // ESC 键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }
    
    async loadCampaigns() {
        try {
            const response = await fetch('/api/campaigns');
            const data = await response.json();
            
            if (data.campaigns) {
                this.populateCampaignSelect(data.campaigns);
            }
        } catch (error) {
            console.error('加载跑团列表失败:', error);
            this.showError('加载跑团列表失败');
        }
    }
    
    populateCampaignSelect(campaigns) {
        const select = document.getElementById('campaignSelect');
        select.innerHTML = '<option value="">选择跑团...</option>';
        
        campaigns.forEach(campaign => {
            const option = document.createElement('option');
            option.value = campaign;
            option.textContent = campaign;
            select.appendChild(option);
        });
        
        // 确定要选择的跑团
        let selectedCampaign = null;
        
        if (this.preselectedCampaign && campaigns.includes(this.preselectedCampaign)) {
            // 优先使用 URL 参数指定的跑团
            selectedCampaign = this.preselectedCampaign;
        } else if (campaigns.length > 0) {
            // 否则选择最新的跑团（列表中的最后一个）
            selectedCampaign = campaigns[campaigns.length - 1];
        }
        
        if (selectedCampaign) {
            select.value = selectedCampaign;
            this.currentCampaign = selectedCampaign;
            
            // 自动加载数据
            this.loadData().then(() => {
                // 数据加载完成后，确保界面正确显示
                setTimeout(() => {
                    this.forceRefresh();
                }, 100);
            });
        }
    }
    
    async loadData() {
        if (!this.currentCampaign) return;
        
        this.showLoading();
        
        try {
            const endpoint = `/api/${this.currentCategory}?campaign=${encodeURIComponent(this.currentCampaign)}`;
            const response = await fetch(endpoint);
            const data = await response.json();
            
            if (response.ok) {
                const key = this.currentCategory;
                this.data = data[key] || [];
                this.renderData();
            } else {
                throw new Error(data.error || '加载数据失败');
            }
        } catch (error) {
            console.error('加载数据失败:', error);
            this.showError('加载数据失败: ' + error.message);
        }
    }
    
    renderData() {
        this.hideLoading();
        
        if (this.data.length === 0) {
            this.showEmptyState();
            return;
        }
        
        this.hideEmptyState();
        
        // 确保容器可见
        this.showCurrentView();
        
        if (this.currentView === 'card') {
            this.renderCardView();
        } else {
            this.renderListView();
        }
    }
    
    showCurrentView() {
        /* 确保当前视图容器可见 */
        if (this.currentView === 'card') {
            document.getElementById('cardsContainer').style.display = 'grid';
            document.getElementById('listContainer').style.display = 'none';
        } else {
            document.getElementById('cardsContainer').style.display = 'none';
            document.getElementById('listContainer').style.display = 'block';
        }
    }
    
    renderCardView() {
        const container = document.getElementById('cardsContainer');
        container.innerHTML = '';
        
        this.data.forEach(item => {
            const card = this.createCard(item);
            container.appendChild(card);
        });
    }
    
    createCard(item) {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.onclick = () => this.showDetail(item);
        
        const iconClass = this.getIconClass(this.currentCategory);
        const icon = this.getIcon(this.currentCategory);
        const typeName = this.getTypeName(this.currentCategory);
        
        // 根据名称生成颜色变体
        const colorVariant = this.getColorVariant(item.name);
        
        card.innerHTML = `
            <div class="card-header">
                <div class="card-icon ${iconClass} ${colorVariant}">${icon}</div>
                <div>
                    <div class="card-title">${this.escapeHtml(item.name)}</div>
                    <div class="card-type">${typeName}</div>
                </div>
            </div>
            <div class="card-content">
                <div class="card-preview">
                    ${this.getPreviewText(item)}
                </div>
                ${item.file_type ? `<span class="file-type-badge ${item.file_type}">${item.file_type}</span>` : ''}
            </div>
        `;
        
        return card;
    }
    
    renderListView() {
        const tbody = document.getElementById('listTableBody');
        tbody.innerHTML = '';
        
        this.data.forEach(item => {
            const row = this.createListRow(item);
            tbody.appendChild(row);
        });
    }
    
    createListRow(item) {
        const row = document.createElement('tr');
        
        const typeName = this.getTypeName(this.currentCategory);
        
        row.innerHTML = `
            <td>
                <div class="list-name">${this.escapeHtml(item.name)}</div>
                <div class="list-type">${typeName}</div>
            </td>
            <td>
                ${item.file_type ? `<span class="file-type-badge ${item.file_type}">${item.file_type}</span>` : ''}
            </td>
            <td>
                <div class="list-info">${this.getPreviewText(item)}</div>
            </td>
            <td>
                <button class="view-btn-small" onclick="characterViewer.showDetail(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                    查看详情
                </button>
            </td>
        `;
        
        return row;
    }
    
    async showDetail(item) {
        const modal = document.getElementById('detailModal');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        
        title.textContent = item.name;
        body.innerHTML = '<div class="loading"><div class="spinner"></div><p>加载中...</p></div>';
        
        modal.style.display = 'block';
        
        try {
            // 获取详细数据
            const categoryMap = {
                'characters': 'character',
                'monsters': 'monster',
                'maps': 'map'
            };
            
            const endpoint = `/api/${categoryMap[this.currentCategory]}?campaign=${encodeURIComponent(this.currentCampaign)}&name=${encodeURIComponent(item.name)}`;
            const response = await fetch(endpoint);
            const data = await response.json();
            
            if (response.ok) {
                this.renderDetailContent(data, body);
            } else {
                throw new Error(data.error || '加载详情失败');
            }
        } catch (error) {
            console.error('加载详情失败:', error);
            body.innerHTML = `
                <div class="error-message">
                    <p>加载详情失败: ${error.message}</p>
                    <button onclick="characterViewer.closeModal()">关闭</button>
                </div>
            `;
        }
    }
    
    renderDetailContent(data, container) {
        let content = '';
        
        if (data.type === 'image') {
            // 图片类型
            content = `
                <div class="detail-section">
                    <h3>图片信息</h3>
                    <div class="detail-field">
                        <span class="detail-label">文件名:</span>
                        <span class="detail-value">${this.escapeHtml(data.filename)}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">类型:</span>
                        <span class="detail-value">${data.file_type}</span>
                    </div>
                </div>
                <div class="detail-section">
                    <h3>预览</h3>
                    <p style="color: #666; font-style: italic;">图片预览功能暂未实现</p>
                </div>
            `;
        } else {
            // 文本类型
            content = `
                <div class="detail-section">
                    <h3>基本信息</h3>
                    <div class="detail-field">
                        <span class="detail-label">名称:</span>
                        <span class="detail-value">${this.escapeHtml(data.name)}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">类型:</span>
                        <span class="detail-value">${this.getTypeName(this.currentCategory)}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">文件类型:</span>
                        <span class="detail-value">${data.file_type || 'text'}</span>
                    </div>
                </div>
            `;
            
            // 如果有解析的字段，显示结构化信息
            if (data.fields && Object.keys(data.fields).length > 0) {
                content += `
                    <div class="detail-section">
                        <h3>详细信息</h3>
                `;
                
                Object.entries(data.fields).forEach(([key, value]) => {
                    if (value && value.trim()) {
                        content += `
                            <div class="detail-field">
                                <span class="detail-label">${this.escapeHtml(key)}:</span>
                                <span class="detail-value">${this.escapeHtml(value)}</span>
                            </div>
                        `;
                    }
                });
                
                content += '</div>';
            }
            
            // 显示原始内容
            if (data.raw_content) {
                content += `
                    <div class="detail-section">
                        <h3>原始内容</h3>
                        <div class="raw-content">${this.escapeHtml(data.raw_content)}</div>
                    </div>
                `;
            }
        }
        
        container.innerHTML = content;
    }
    
    closeModal() {
        document.getElementById('detailModal').style.display = 'none';
    }
    
    switchView(view) {
        this.currentView = view;
        
        // 更新按钮状态
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (view === 'card') {
            document.getElementById('cardViewBtn').classList.add('active');
        } else {
            document.getElementById('listViewBtn').classList.add('active');
        }
        
        // 显示对应的视图容器
        this.showCurrentView();
        
        // 重新渲染数据
        if (this.data.length > 0) {
            this.renderData();
        }
    }
    
    switchCategory(category) {
        this.currentCategory = category;
        
        // 更新按钮状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelector(`[data-category="${category}"]`).classList.add('active');
        
        // 重新加载数据
        if (this.currentCampaign) {
            this.loadData();
        }
    }
    
    showLoading() {
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('errorMessage').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('cardsContainer').style.display = 'none';
        document.getElementById('listContainer').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
    
    showError(message) {
        this.hideLoading();
        const errorElement = document.getElementById('errorMessage');
        errorElement.querySelector('p').textContent = message;
        errorElement.style.display = 'block';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('cardsContainer').style.display = 'none';
        document.getElementById('listContainer').style.display = 'none';
    }
    
    showEmptyState() {
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('errorMessage').style.display = 'none';
        document.getElementById('cardsContainer').style.display = 'none';
        document.getElementById('listContainer').style.display = 'none';
    }
    
    hideEmptyState() {
        document.getElementById('emptyState').style.display = 'none';
    }
    
    clearData() {
        this.data = [];
        this.hideLoading();
        this.hideEmptyState();
        document.getElementById('errorMessage').style.display = 'none';
        document.getElementById('cardsContainer').innerHTML = '';
        document.getElementById('listTableBody').innerHTML = '';
    }
    
    getIconClass(category) {
        const map = {
            'characters': 'character',
            'monsters': 'monster',
            'maps': 'map'
        };
        return map[category] || 'character';
    }
    
    getIcon(category) {
        const map = {
            'characters': '👤',
            'monsters': '👹',
            'maps': '🗺️'
        };
        return map[category] || '📄';
    }
    
    getTypeName(category) {
        const map = {
            'characters': '人物卡',
            'monsters': '怪物卡',
            'maps': '地图'
        };
        return map[category] || '文件';
    }
    
    getPreviewText(item) {
        // 这里可以根据需要添加预览文本的逻辑
        // 目前只显示文件类型信息
        if (item.file_type === 'image') {
            return '图片文件';
        } else if (item.file_type === 'json') {
            return 'JSON 格式数据';
        } else {
            return '文本文件';
        }
    }
    
    getColorVariant(name) {
        /* 根据名称生成颜色变体 */
        // 使用简单的哈希算法为每个名称分配一个颜色变体
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            const char = name.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        
        // 将哈希值映射到1-5的变体
        const variant = Math.abs(hash) % 5 + 1;
        return `variant-${variant}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    forceRefresh() {
        /* 强制刷新界面显示 */
        if (this.data.length > 0) {
            // 确保视图容器正确显示
            this.showCurrentView();
            
            // 重新渲染数据
            if (this.currentView === 'card') {
                this.renderCardView();
            } else {
                this.renderListView();
            }
            
            console.log('强制刷新完成，数据量:', this.data.length);
        }
    }
}

// 初始化应用
let characterViewer;
document.addEventListener('DOMContentLoaded', () => {
    characterViewer = new CharacterViewer();
    
    // 页面加载完成后，额外等待一下再刷新一次
    window.addEventListener('load', () => {
        setTimeout(() => {
            if (characterViewer && characterViewer.data.length > 0) {
                console.log('页面完全加载后执行强制刷新');
                characterViewer.forceRefresh();
            }
        }, 200);
    });
});