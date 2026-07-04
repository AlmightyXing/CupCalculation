const API_BASE = '/api';

const state = {
  currentTab: 'total', // 'total', 'idle', 'burst', 'sandbox'
  enemyDef: 2000,
  enemyRes: 40,
  allOperators: []
};

// Elements
const navBtns = document.querySelectorAll('.nav-btn');
const viewSections = document.querySelectorAll('.view-section');
const enemySelect = document.getElementById('enemy-select');
const operatorListEl = document.getElementById('operator-list');
const tableColumnsEl = document.querySelector('.table-columns');

// Initialize
function init() {
  bindEvents();
  loadRankings();
}

function bindEvents() {
  navBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const btnEl = e.currentTarget;
      const tab = btnEl.dataset.view;
      if (tab === 'sandbox') {
        switchView('sandbox');
      } else {
        switchView('leaderboard');
        state.currentTab = tab;
        navBtns.forEach(b => b.classList.remove('active'));
        btnEl.classList.add('active');
        
        let title = "总杯榜";
        if (tab === "idle") title = "挂机榜";
        if (tab === "burst") title = "决战榜";
        document.getElementById('leaderboard-title').innerText = title;
        
        renderList();
      }
    });
  });

  enemySelect.addEventListener('change', (e) => {
    const val = parseInt(e.target.value);
    const mapping = [
      [0, 0], [1000, 20], [2000, 40], [3000, 60], [4000, 80], [5000, 100]
    ];
    state.enemyDef = mapping[val][0];
    state.enemyRes = mapping[val][1];
    loadRankings();
  });
}

function switchView(viewId) {
  viewSections.forEach(sec => {
    if (sec.id === 'view-' + viewId) {
      sec.style.display = 'block';
    } else {
      sec.style.display = 'none';
    }
  });
}

async function loadRankings() {
  operatorListEl.innerHTML = '<div class="loading-state" style="padding:20px;text-align:center;">加载中...</div>';
  try {
    const res = await fetch(`${API_BASE}/rankings?enemy_def=${state.enemyDef}&enemy_res=${state.enemyRes}`);
    const data = await res.json();
    if (data.status === 'success') {
      state.allOperators = data.data.operators;
      renderList();
    }
  } catch (err) {
    console.error(err);
    operatorListEl.innerHTML = '<div class="loading-state" style="padding:20px;text-align:center;color:red;">加载失败</div>';
  }
}

function renderList() {
  if (!state.allOperators || state.allOperators.length === 0) return;
  
  let list = [...state.allOperators];
  
  // Set headers
  if (state.currentTab === 'total') {
    tableColumnsEl.innerHTML = `
      <div class="col col-cup">Cup</div>
      <div class="col col-rank">Rank</div>
      <div class="col col-avatar">头像</div>
      <div class="col col-name">干员</div>
      <div class="col col-prof">职业</div>
      <div class="col col-rank">挂机</div>
      <div class="col col-rank">决战</div>
    `;
    list.sort((a, b) => a.totalRank - b.totalRank);
  } else {
    tableColumnsEl.innerHTML = `
      <div class="col col-rank">Rank</div>
      <div class="col col-avatar">头像</div>
      <div class="col col-name">干员</div>
      <div class="col col-prof">职业</div>
      <div class="col col-num">DPS</div>
      <div class="col col-num">总伤</div>
    `;
    if (state.currentTab === 'idle') {
      list.sort((a, b) => a.idleRank - b.idleRank);
    } else {
      list.sort((a, b) => a.burstRank - b.burstRank);
    }
  }

  operatorListEl.innerHTML = '';
  
  // Render cards
  list.forEach(op => {
    const div = document.createElement('div');
    div.className = 'op-card';
    
    // Avatar placeholder for now
    const avatarUrl = `https://dummyimage.com/100x100/333/fff&text=${op.name[0]}`;
    
    if (state.currentTab === 'total') {
      div.innerHTML = `
        <div class="col col-cup" style="color:var(--accent-primary);font-weight:bold;">${op.cup_level}</div>
        <div class="col col-rank">${op.totalRank}</div>
        <div class="col col-avatar">
          <div class="avatar-wrapper"><img src="${avatarUrl}" alt="${op.name}"></div>
        </div>
        <div class="col col-name op-name">${op.name}</div>
        <div class="col col-prof op-prof">${op.profession}</div>
        <div class="col col-rank">${op.idleRank}</div>
        <div class="col col-rank">${op.burstRank}</div>
      `;
    } else {
      const rank = state.currentTab === 'idle' ? op.idleRank : op.burstRank;
      const dps = state.currentTab === 'idle' ? Math.round(op.idle_score) : Math.round(op.best_dps);
      const total = state.currentTab === 'idle' ? Math.round(op.best_total_dmg) : Math.round(op.burst_score);
      
      div.innerHTML = `
        <div class="col col-rank">${rank}</div>
        <div class="col col-avatar">
          <div class="avatar-wrapper"><img src="${avatarUrl}" alt="${op.name}"></div>
        </div>
        <div class="col col-name op-name">${op.name}</div>
        <div class="col col-prof op-prof">${op.profession}</div>
        <div class="col col-num op-num">${dps}</div>
        <div class="col col-num op-num">${total}</div>
      `;
    }
    
    operatorListEl.appendChild(div);
  });
}

document.addEventListener('DOMContentLoaded', init);

// --- Search Logic ---
const searchBarBtn = document.getElementById('search-bar-btn');
const searchBackBtn = document.getElementById('search-back-btn');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchResults = document.getElementById('search-results');

searchBarBtn.addEventListener('click', () => {
  switchView('search');
});

searchBackBtn.addEventListener('click', () => {
  switchView('leaderboard');
});

searchBtn.addEventListener('click', async () => {
  const query = searchInput.value.trim();
  if (!query) return;
  
  searchResults.innerHTML = '<div class="loading-state">搜索中...</div>';
  
  try {
    const res = await fetch(`${API_BASE}/operators`);
    const data = await res.json();
    if (data.status === 'success') {
      const filtered = data.data.filter(op => op.name.includes(query));
      searchResults.innerHTML = '';
      if (filtered.length === 0) {
        searchResults.innerHTML = '<div class="loading-state">未找到结果</div>';
        return;
      }
      
      filtered.forEach(op => {
        const div = document.createElement('div');
        div.className = 'op-card';
        div.innerHTML = `
          <div class="col col-avatar">
            <div class="avatar-wrapper"><img src="https://dummyimage.com/100x100/333/fff&text=${op.name[0]}" alt="${op.name}"></div>
          </div>
          <div class="col col-name op-name">${op.name}</div>
          <div class="col col-prof op-prof">${op.character_type}</div>
        `;
        div.addEventListener('click', () => openDetail(op.name));
        searchResults.appendChild(div);
      });
    }
  } catch (err) {
    console.error(err);
  }
});

// --- Detail Logic ---
const detailBackBtn = document.getElementById('detail-back-btn');
const detailContent = document.getElementById('detail-content');

detailBackBtn.addEventListener('click', () => {
  switchView('leaderboard');
});

async function openDetail(opName) {
  switchView('detail');
  detailContent.innerHTML = '<div class="loading-state">加载中...</div>';
  
  try {
    const res = await fetch(`${API_BASE}/operator/${encodeURIComponent(opName)}`);
    const data = await res.json();
    
    if (data.status === 'success') {
      const op = data.data;
      
      let skillsHtml = '';
      if (op.skills && op.skills.length > 0) {
        skillsHtml = op.skills.map((sk, idx) => `
          <div class="skill-card">
            <div class="skill-name">技能 ${idx + 1}: ${sk.name || 'N/A'}</div>
            <div class="skill-stats">
              <div class="stat-box">SP消耗<div class="stat-val">${sk.sp_cost || 0}</div></div>
              <div class="stat-box">持续时间<div class="stat-val">${sk.duration || 0}s</div></div>
            </div>
          </div>
        `).join('');
      }
      
      detailContent.innerHTML = `
        <div class="detail-header">
          <div class="detail-avatar"><img src="https://dummyimage.com/120x120/333/fff&text=${op.name[0]}" alt="${op.name}" style="width:100%;height:100%;border-radius:16px;"></div>
          <div class="detail-info">
            <div class="detail-name">${op.name}</div>
            <div class="op-prof" style="font-size:16px;">${op.character_type || '未知'} | ★${op.rarity || 6}</div>
          </div>
        </div>
        <div class="detail-skills">
          ${skillsHtml}
        </div>
      `;
    }
  } catch (err) {
    console.error(err);
    detailContent.innerHTML = '<div class="loading-state" style="color:red;">获取数据失败</div>';
  }
}

const observer = new MutationObserver(() => {
  const cards = operatorListEl.querySelectorAll('.op-card');
  cards.forEach(card => {
    card.addEventListener('click', (e) => {
      const nameEl = e.currentTarget.querySelector('.op-name');
      if (nameEl) openDetail(nameEl.innerText.trim());
    });
  });
});
observer.observe(operatorListEl, { childList: true });

// --- Sandbox Logic ---
const sbSubmit = document.getElementById('sb-submit');
const sbResult = document.getElementById('sandbox-result');

sbSubmit.addEventListener('click', async () => {
  const opName = document.getElementById('sb-op-name').value.trim();
  const skillIdx = parseInt(document.getElementById('sb-skill-idx').value || 0);
  const def = parseInt(document.getElementById('sb-def').value || 0);
  const res = parseInt(document.getElementById('sb-res').value || 0);
  
  if (!opName) return alert('请输入干员名称');
  
  sbResult.innerHTML = '<div class="loading-state">演算中...</div>';
  
  try {
    const payload = {
      operator_name: opName,
      skill_index: skillIdx,
      enemy_def: def,
      enemy_res: res
    };
    
    const response = await fetch(`${API_BASE}/sandbox/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    
    if (data.status === 'success') {
      const r = data.data;
      sbResult.innerHTML = `
        <div class="skill-card">
          <div class="skill-name">演算完成</div>
          <div class="skill-stats" style="margin-top:15px;">
            <div class="stat-box">DPS<div class="stat-val">${r.dps}</div></div>
            <div class="stat-box">总伤<div class="stat-val">${r.total_damage}</div></div>
          </div>
          <div class="skill-stats" style="margin-top:15px;">
            <div class="stat-box" style="flex:none;width:50%;">周期DPS<div class="stat-val">${r.cycle_dps}</div></div>
          </div>
        </div>
      `;
    } else {
      sbResult.innerHTML = `<div class="loading-state" style="color:red;">计算失败</div>`;
    }
  } catch (err) {
    console.error(err);
    sbResult.innerHTML = `<div class="loading-state" style="color:red;">请求出错</div>`;
  }
});
