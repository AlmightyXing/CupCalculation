const API_BASE = '/api';

const state = {
  currentTab: 'total', // 'total', 'idle', 'burst', 'sandbox'
  enemyDef: 0,
  enemyRes: 0,
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
  
  operatorListEl.innerHTML = '';
  
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
    
    // Group by cup_level
    const groups = [];
    let currentCup = null;
    let currentGroup = [];
    list.forEach(op => {
      if (op.cup_level !== currentCup) {
        if (currentGroup.length > 0) {
          groups.push({ cup: currentCup, ops: currentGroup });
        }
        currentCup = op.cup_level;
        currentGroup = [];
      }
      currentGroup.push(op);
    });
    if (currentGroup.length > 0) {
      groups.push({ cup: currentCup, ops: currentGroup });
    }

    groups.forEach(group => {
      const groupDiv = document.createElement('div');
      groupDiv.style.display = 'flex';
      groupDiv.style.alignItems = 'stretch';
      groupDiv.style.marginBottom = '10px';
      groupDiv.style.gap = '10px'; // Space between cup label and cards

      const cupLabel = document.createElement('div');
      cupLabel.className = 'col-cup';
      cupLabel.style.display = 'flex';
      cupLabel.style.alignItems = 'center';
      cupLabel.style.justifyContent = 'center';
      cupLabel.style.fontWeight = 'bold';
      cupLabel.style.color = 'var(--accent-primary)';
      cupLabel.style.backgroundColor = 'var(--bg-tertiary)';
      cupLabel.style.borderRadius = '12px';
      cupLabel.style.border = '1px solid var(--border-color)';
      cupLabel.style.writingMode = 'vertical-rl';
      cupLabel.style.textOrientation = 'upright';
      cupLabel.style.letterSpacing = '4px';
      cupLabel.style.padding = '10px 0';
      // Override width to match col-cup in table-columns roughly, accounting for gap and padding
      cupLabel.style.flex = 'none';
      cupLabel.style.width = '70px'; 
      cupLabel.innerText = group.cup;

      const rowsDiv = document.createElement('div');
      rowsDiv.style.flex = '1';
      rowsDiv.style.display = 'flex';
      rowsDiv.style.flexDirection = 'column';
      rowsDiv.style.gap = '10px';

      group.ops.forEach(op => {
        const div = document.createElement('div');
        div.className = 'op-card';
        div.style.marginBottom = '0'; // override default margin since we use gap
        
        const avatarUrl = `/avatars/头像_${op.name}.png`;
        const fallbackUrl = `https://dummyimage.com/100x100/333/fff&text=${op.name[0]}`;
        const imgHtml = `<img src="${avatarUrl}" alt="${op.name}" onerror="this.onerror=null; this.src='${fallbackUrl}'">`;
        
        div.innerHTML = `
          <div class="col col-rank">${op.totalRank}</div>
          <div class="col col-avatar">
            <div class="avatar-wrapper">${imgHtml}</div>
          </div>
          <div class="col col-name op-name">${op.name}</div>
          <div class="col col-prof op-prof">${op.profession}</div>
          <div class="col col-rank">${op.idleRank}</div>
          <div class="col col-rank">${op.burstRank}</div>
        `;
        div.addEventListener('click', () => openDetail(op.name));
        rowsDiv.appendChild(div);
      });

      groupDiv.appendChild(cupLabel);
      groupDiv.appendChild(rowsDiv);
      operatorListEl.appendChild(groupDiv);
    });

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
    
    // Render normal cards
    list.forEach(op => {
      const div = document.createElement('div');
      div.className = 'op-card';
      
      const avatarUrl = `/avatars/头像_${op.name}.png`;
      const fallbackUrl = `https://dummyimage.com/100x100/333/fff&text=${op.name[0]}`;
      const imgHtml = `<img src="${avatarUrl}" alt="${op.name}" onerror="this.onerror=null; this.src='${fallbackUrl}'">`;
      
      const rank = state.currentTab === 'idle' ? op.idleRank : op.burstRank;
      const dps = state.currentTab === 'idle' ? Math.round(op.idle_score) : Math.round(op.best_dps);
      const total = state.currentTab === 'idle' ? Math.round(op.best_total_dmg) : Math.round(op.burst_score);
      
      div.innerHTML = `
        <div class="col col-rank">${rank}</div>
        <div class="col col-avatar">
          <div class="avatar-wrapper">${imgHtml}</div>
        </div>
        <div class="col col-name op-name">${op.name}</div>
        <div class="col col-prof op-prof">${op.profession}</div>
        <div class="col col-num op-num">${dps}</div>
        <div class="col col-num op-num">${total}</div>
      `;
      div.addEventListener('click', () => openDetail(op.name));
      operatorListEl.appendChild(div);
    });
  }
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
            <div class="avatar-wrapper"><img src="/avatars/头像_${op.name}.png" alt="${op.name}" onerror="this.onerror=null; this.src='https://dummyimage.com/100x100/333/fff&text=${op.name[0]}'"></div>
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
      
      let ranks = { total: '-', idle: '-', burst: '-' };
      let perfSkills = [];
      if (state.allOperators) {
        const found = state.allOperators.find(o => o.name === op.name);
        if (found) {
          ranks = {
            total: found.totalRank || '-',
            idle: found.idleRank || '-',
            burst: found.burstRank || '-'
          };
          perfSkills = found.skills || [];
        }
      }
      
      let skillsHtml = '';
      if (op.skills && op.skills.length > 0) {
        skillsHtml = op.skills.map((sk, idx) => {
          let dpsText = 'N/A';
          let totalDmgText = 'N/A';
          if (perfSkills && perfSkills.length > idx) {
            const perf = perfSkills[idx];
            if (perf && perf.dps > 0) dpsText = Math.round(perf.dps);
            if (perf && perf.total_dmg > 0) totalDmgText = Math.round(perf.total_dmg);
          }
          return `
          <div class="h4-title">技能 ${idx + 1}</div>
          <div class="flex-table skill-base-table">
            <div class="ft-row">
              <div class="ft-cell bg-20 center-content" style="flex: 7; font-weight:bold;">${sk.skill_name || 'N/A'}</div>
              <div class="ft-cell bg-20 center-content" style="flex: 3;">${sk.skill_type === 'auto' ? '自动' : '手动'}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">等级</div>
              <div class="ft-cell bg-60" style="flex: 5;">描述</div>
              <div class="ft-cell bg-60" style="flex: 1;">初始</div>
              <div class="ft-cell bg-60" style="flex: 1;">消耗</div>
              <div class="ft-cell bg-60" style="flex: 1;">持续</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-20" style="flex: 2;">RANK III</div>
              <div class="ft-cell bg-20 align-left" style="flex: 5; font-size: 11px;">${sk.description || '-'}</div>
              <div class="ft-cell bg-20" style="flex: 1;">${sk.start_sp || 0}</div>
              <div class="ft-cell bg-20" style="flex: 1;">${sk.consume_sp || 0}</div>
              <div class="ft-cell bg-20" style="flex: 1;">${sk.duration || '-'}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">DPS结论</div>
              <div class="ft-cell bg-20" style="flex: 3; font-weight:bold; color:var(--accent-primary);">${dpsText}</div>
              <div class="ft-cell bg-60" style="flex: 2;">总伤结论</div>
              <div class="ft-cell bg-20" style="flex: 3; font-weight:bold; color:var(--accent-primary);">${totalDmgText}</div>
            </div>
          </div>
        `}).join('');
      }

      let talentsHtml = '';
      if (op.talents && op.talents.length > 0) {
        talentsHtml = op.talents.map((t, idx) => `
          <div class="ft-row">
            <div class="ft-cell bg-60" style="flex: 2;">${idx === 0 ? '第一天赋' : '第二天赋'}</div>
            <div class="ft-cell bg-20" style="flex: 3;">${t.talent_name || '-'}</div>
            <div class="ft-cell bg-20 align-left" style="flex: 5;">${t.talent_description || t.talent_decription || '-'}</div>
          </div>
        `).join('');
      }
      
      detailContent.innerHTML = `
        <div class="detail-header">
          <div class="detail-avatar"><img src="/avatars/头像_${op.name}.png" alt="${op.name}" style="width:100%;height:100%;border-radius:16px;object-fit:cover;" onerror="this.onerror=null; this.src='https://dummyimage.com/120x120/333/fff&text=${op.name[0]}'"></div>
          <div class="detail-info">
            <div class="detail-name">${op.name}</div>
            <div class="op-prof" style="font-size:16px;">${(op.character && op.character.character_type) ? op.character.character_type : '未知'} | ★${op.rarity || 6}</div>
          </div>
        </div>
        
        <div class="section">
          <div class="h2-title">干员能力排名</div>
          <div class="rank-board">
            <div class="rank-item">
              <div class="rank-label">总榜排名</div>
              <div class="rank-value">#${ranks.total}</div>
            </div>
            <div class="rank-item">
              <div class="rank-label">挂机排名</div>
              <div class="rank-value">#${ranks.idle}</div>
            </div>
            <div class="rank-item">
              <div class="rank-label">决战排名</div>
              <div class="rank-value">#${ranks.burst}</div>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="h2-title">干员详细信息</div>
          
          <div class="h3-title">特性</div>
          <div class="flex-table trait-table">
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">分支</div>
              <div class="ft-cell bg-60 center-content" style="flex: 8;">描述</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-20 no-border-bottom" style="flex: 2;">${(op.character && op.character.character_type) ? op.character.character_type : '-'}</div>
              <div class="ft-cell bg-20 center-content" style="flex: 8; font-size: 12px; padding: 10px;">${(op.character && op.character.character_description) ? op.character.character_description : '-'}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-20" style="flex: 2;"></div>
              <div class="ft-cell bg-60" style="flex: 2;">攻击间隔</div>
              <div class="ft-cell bg-20" style="flex: 6;">${op.atk_time || '-'}</div>
            </div>
          </div>

          <div class="h3-title">属性</div>
          <div class="flex-table attr-table">
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;"></div>
              <div class="ft-cell bg-60" style="flex: 4;">精英2 满级</div>
              <div class="ft-cell bg-60" style="flex: 4;">信赖加成上限</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">生命上限</div>
              <div class="ft-cell bg-20" style="flex: 4;">${op.base_hp || 0}</div>
              <div class="ft-cell bg-20" style="flex: 4;">+${op.confidence_hp || 0}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">攻击</div>
              <div class="ft-cell bg-20" style="flex: 4;">${op.base_atk || 0}</div>
              <div class="ft-cell bg-20" style="flex: 4;">+${op.confidence_atk || 0}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">防御</div>
              <div class="ft-cell bg-20" style="flex: 4;">${op.base_def || 0}</div>
              <div class="ft-cell bg-20" style="flex: 4;">+${op.confidence_def || 0}</div>
            </div>
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">法术抗性</div>
              <div class="ft-cell bg-20" style="flex: 4;">${op.base_res || 0}</div>
              <div class="ft-cell bg-20" style="flex: 4;">+${op.confidence_res || 0}</div>
            </div>
          </div>

          <div class="h3-title">天赋</div>
          <div class="flex-table talent-table">
            <div class="ft-row">
              <div class="ft-cell bg-60" style="flex: 2;">天赋</div>
              <div class="ft-cell bg-60" style="flex: 3;">名称</div>
              <div class="ft-cell bg-60" style="flex: 5;">描述</div>
            </div>
            ${talentsHtml}
          </div>

          <div class="h3-title">技能</div>
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
