let storyData = {};
let activeNodeId = null;
let allNodes = [];
let allEdges = [];

// 从URL参数获取跑团、剧本和剧情名称
function getUrlParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    campaign: params.get('campaign') || '失落的矿坑',
    script: params.get('script') || null,
    story: params.get('story') || '失落的矿坑'
  };
}

// 动态构建文件路径
function buildFilePaths() {
  const { campaign, script, story } = getUrlParams();
  
  // 新的文件结构：data/campaigns/跑团/notes/文件
  return {
    jsonPath: `../../data/campaigns/${campaign}/notes/${story}.json`,
    svgPath: `../../data/campaigns/${campaign}/notes/${story}.svg`
  };
}

// 加载剧情数据和SVG
function loadStoryData() {
  const { jsonPath, svgPath } = buildFilePaths();
  
  // 加载JSON数据
  fetch(jsonPath)
    .then(res => {
      if (!res.ok) {
        throw new Error(`无法加载剧情文件: ${jsonPath}`);
      }
      return res.json();
    })
    .then(data => {
      for (const node of data.nodes) {
        storyData[node.id] = node;
      }
      console.log('剧情数据加载成功');
    })
    .catch(error => {
      console.error('加载剧情数据失败:', error);
      document.getElementById("content").innerHTML = 
        `<p style="color: red;">加载剧情数据失败: ${error.message}</p>`;
    });

  // 加载SVG图形
  fetch(svgPath)
    .then(res => {
      if (!res.ok) {
        throw new Error(`无法加载SVG文件: ${svgPath}`);
      }
      return res.text();
    })
    .then(svgText => {
      document.getElementById("graph").innerHTML = svgText;
      setupSvgInteraction();
      console.log('SVG图形加载成功');
    })
    .catch(error => {
      console.error('加载SVG失败:', error);
      document.getElementById("graph").innerHTML = 
        `<p style="color: red; padding: 20px;">加载SVG图形失败: ${error.message}</p>`;
    });
}

// 设置SVG交互
function setupSvgInteraction() {
  const svg = document.querySelector("svg");
  if (!svg) {
    console.error('未找到SVG元素');
    return;
  }

  allNodes = Array.from(svg.querySelectorAll("g.node"));
  allEdges = Array.from(svg.querySelectorAll("g.edge"));

  allNodes.forEach(node => {
    const title = node.querySelector("title");
    if (!title) return;

    const nodeId = title.textContent.trim();
    node.dataset.id = nodeId;
    node.style.cursor = "pointer";

    node.addEventListener("click", () => {
      activateNode(nodeId);
      showNode(nodeId);
    });
  });

  // 清除按钮
  document.getElementById("clearBtn").addEventListener("click", clearSelection);
  
  // 更新页面标题
  const { campaign, script, story } = getUrlParams();
  if (script) {
    document.title = `剧情预览 - ${campaign}/${script}/${story}`;
  } else {
    document.title = `剧情预览 - ${campaign}/${story}`;
  }
  
  // 更新面板标题
  const panelTitle = document.querySelector("#panel h2");
  if (panelTitle) {
    if (script) {
      panelTitle.textContent = `${campaign} - ${script} - ${story}`;
    } else {
      panelTitle.textContent = `${campaign} - ${story}`;
    }
  }
}

function activateNode(nodeId) {
  activeNodeId = nodeId;

  allNodes.forEach(n => {
    if (n.dataset.id === nodeId) {
      n.classList.add("active");
      n.classList.remove("dimmed");
    } else {
      n.classList.remove("active");
      n.classList.add("dimmed");
    }
  });

  allEdges.forEach(e => {
    const title = e.querySelector("title");
    if (!title) return;

    const text = title.textContent;
    if (text.includes(nodeId)) {
      e.classList.remove("dimmed");
    } else {
      e.classList.add("dimmed");
    }
  });
}

function clearSelection() {
  activeNodeId = null;

  allNodes.forEach(n => {
    n.classList.remove("active");
    n.classList.remove("dimmed");
  });

  allEdges.forEach(e => {
    e.classList.remove("dimmed");
  });

  const div = document.getElementById("content");
  div.innerHTML = "<p class='hint'>已清除选择，点击节点查看剧情内容</p>";
}

function showNode(nodeId) {
  const node = storyData[nodeId];
  if (!node) {
    document.getElementById("content").innerHTML = 
      `<p style="color: orange;">未找到节点数据: ${nodeId}</p>`;
    return;
  }

  const div = document.getElementById("content");
  div.innerHTML = `
    <h3>${node.title}</h3>
    <p><strong>ID：</strong>${node.id}</p>
    <p><strong>类型：</strong>${node.type === 'main' ? '主线' : '分支'}</p>
    <hr>
    <div style="white-space: pre-wrap;">${node.content || "（无内容）"}</div>
  `;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  loadStoryData();
});
