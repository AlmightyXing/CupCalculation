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

      navBtns.forEach(b => b.classList.remove('active'));
      btnEl.classList.add('active');

      if (tab === 'sandbox') {
        switchView('sandbox');
      } else {
        switchView('leaderboard');
        state.currentTab = tab;

        let title = "总杯榜";
        if (tab === "idle") title = "挂机榜";
        if (tab === "burst") title = "决战榜";

        const titleEl = document.getElementById('leaderboard-title-text');
        if (titleEl) {
          titleEl.innerText = title;
        } else {
          document.getElementById('leaderboard-title').innerText = title;
        }

        renderList();
        if (typeof isChartView !== 'undefined' && isChartView) {
          if (typeof renderChart !== 'undefined') renderChart();
        }
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
  if (viewId === 'sandbox') {
    initSandboxForm();
  }
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
            <div class="ft-cell bg-20 align-left" style="flex: 5; white-space: pre-wrap; word-break: break-word; line-height: 1.4;">${t.talent_description || t.talent_decription || '-'}</div>
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
const majorClassMap = {
  '先锋': ['先锋', '尖兵', '冲锋手', '战术家', '执旗手', '情报官', '策士'],
  '近卫': ['近卫', '强攻手', '斗士', '教官', '领主', '术战者', '剑豪', '武者', '无畏者', '收割者', '解放者', '重剑手', '撼地者', '本源近卫', '佣兵'],
  '重装': ['重装', '铁卫', '守护者', '不屈者', '驭法铁卫', '决战者', '要塞', '哨戒铁卫', '本源铁卫'],
  '狙击': ['狙击', '速射手', '神射手', '炮手', '攻城射手', '散射手', '重射手', '投掷手', '猎手', '回环射手', '裂空炮手'],
  '术师': ['术师', '中坚术师', '御械术师', '阵法术师', '秘术师', '链术师', '轰击术师', '扩散术师', '本源术师', '塑灵术师'],
  '医疗': ['医疗', '医师', '群愈师', '疗养师', '行医', '咒愈师', '链愈师', '守望者'],
  '辅助': ['辅助', '吟游者', '召唤师', '凝滞师', '削弱者', '护佑者', '巫役', '工匠'],
  '特种': ['特种', '处决者', '推击手', '伏击客', '钩索师', '陷阱师', '行商', '傀儡师', '炼金师', '怪杰', '巡空者']
};

function getMajorClass(subProf) {
  for (let major in majorClassMap) {
    if (majorClassMap[major].includes(subProf) || subProf.includes(major)) return major;
  }
  return '其他';
}

const sbMajorProf = document.getElementById('sb-major-prof');
const sbSubProf = document.getElementById('sb-sub-prof');
const sbOpName = document.getElementById('sb-op-name');
const sbEnemyPreset = document.getElementById('sb-enemy-preset');
const sbSubmit = document.getElementById('sb-submit');
const sbResult = document.getElementById('sandbox-result');
const sbSkillGroup = document.getElementById('sb-skill-group');
const sbSkillIdx = document.getElementById('sb-skill-idx');

let isSandboxInitialized = false;

function initSandboxForm() {
  if (isSandboxInitialized) return;
  const ops = state.allOperators || [];
  if (ops.length === 0) return;

  sbMajorProf.addEventListener('change', () => {
    const major = sbMajorProf.value;
    sbSubProf.innerHTML = '<option value="">全部小职业</option>';

    let availableSubs = new Set();
    ops.forEach(op => {
      const opMajor = getMajorClass(op.profession);
      if (!major || opMajor === major) {
        availableSubs.add(op.profession);
      }
    });

    Array.from(availableSubs).sort().forEach(sub => {
      sbSubProf.innerHTML += `<option value="${sub}">${sub}</option>`;
    });

    sbSubProf.dispatchEvent(new Event('change'));
  });

  sbSubProf.addEventListener('change', () => {
    const major = sbMajorProf.value;
    const sub = sbSubProf.value;
    sbOpName.innerHTML = '';

    const filteredOps = ops.filter(op => {
      const opMajor = getMajorClass(op.profession);
      if (major && opMajor !== major) return false;
      if (sub && op.profession !== sub) return false;
      return true;
    });

    if (filteredOps.length === 0) {
      sbOpName.innerHTML = '<option value="">无符合条件的干员</option>';
    } else {
      filteredOps.sort((a, b) => a.name.localeCompare(b.name)).forEach(op => {
        sbOpName.innerHTML += `<option value="${op.name}">${op.name}</option>`;
      });
    }
  });

  if (sbSkillGroup) {
    const btns = sbSkillGroup.querySelectorAll('.skill-btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active', 'btn-primary'));
        btn.classList.add('active', 'btn-primary');
        sbSkillIdx.value = btn.dataset.skill;
      });
    });
    // Set default selected
    const defaultBtn = sbSkillGroup.querySelector('[data-skill="0"]');
    if (defaultBtn) defaultBtn.classList.add('btn-primary');
  }

  sbMajorProf.dispatchEvent(new Event('change'));
  isSandboxInitialized = true;
}

sbSubmit.addEventListener('click', async () => {
  const opName = sbOpName.value;
  const skillIdx = parseInt(sbSkillIdx.value || 0);
  const presetVal = parseInt(sbEnemyPreset.value || 0);

  const mapping = [
    [0, 0], [1000, 20], [2000, 40], [3000, 60], [4000, 80], [5000, 100]
  ];
  const def = mapping[presetVal][0];
  const res = mapping[presetVal][1];

  if (!opName) return alert('请选择干员！');

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
      const rep = data.data;
      let logsHtml = (rep.combat_log || []).map(l => `<div>${l}</div>`).join('');
      if (logsHtml) {
        logsHtml = `
          <h4 style="margin-top: 15px; color: #e5e7eb;">战斗日志：</h4>
          <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 4px; font-family: monospace; font-size: 0.85em; color: #d1d5db; max-height: 200px; overflow-y: auto;">
            ${logsHtml}
          </div>
        `;
      }

      sbResult.innerHTML = `
        <div class="detail-section" style="margin-top: 20px;">
          <h3 style="color: var(--accent-primary); border-bottom: 1px solid var(--accent-primary); padding-bottom: 5px; margin-bottom: 15px;">演算结果</h3>
          <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div class="glass-panel" style="flex: 1; text-align: center; padding: 15px;">
              <div style="font-size: 14px; color: #9ca3af;">最终DPS</div>
              <div style="font-size: 24px; font-weight: bold; color: #10b981;">${rep.dps}</div>
            </div>
            <div class="glass-panel" style="flex: 1; text-align: center; padding: 15px;">
              <div style="font-size: 14px; color: #9ca3af;">技能总伤</div>
              <div style="font-size: 24px; font-weight: bold; color: #f59e0b;">${rep.total_damage}</div>
            </div>
          </div>
          ${logsHtml}
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

let chartInstance = null;
function renderChart() {
  if (!state.allOperators || state.allOperators.length === 0) return;
  const container = document.getElementById('chart-container');
  if (!container) return;
  if (!chartInstance) {
    chartInstance = echarts.init(container);
  }

  let list = [...state.allOperators];
  let titleText = '';
  let yAxisName = '';
  let dataKey = '';

  if (state.currentTab === 'total') {
    list.sort((a, b) => a.totalRank - b.totalRank);
    titleText = '总杯榜 综合排位分布';
    yAxisName = '综合排名 (越小越强)';
    dataKey = 'totalRank';
  } else if (state.currentTab === 'idle') {
    list.sort((a, b) => a.idleRank - b.idleRank);
    titleText = '挂机榜 前20名DPS分布';
    yAxisName = '最佳挂机DPS';
    dataKey = 'idle_score';
  } else {
    list.sort((a, b) => a.burstRank - b.burstRank);
    titleText = '决战榜 前20名总伤分布';
    yAxisName = '最佳决战总伤';
    dataKey = 'burst_score';
  }

  const top20 = list.slice(0, 20);
  const xData = top20.map(op => op.name);
  let yData = top20.map(op => Math.round(op[dataKey] || 0));

  const option = {
    title: { text: titleText, left: 'center', textStyle: { color: '#e5e7eb' } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { color: '#9ca3af', interval: 0, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      nameTextStyle: { color: '#9ca3af' },
      axisLabel: { color: '#9ca3af' },
      inverse: state.currentTab === 'total'
    },
    series: [
      {
        data: yData,
        type: 'bar',
        itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] },
        label: { show: true, position: 'top', color: '#e5e7eb' }
      }
    ]
  };

  chartInstance.setOption(option, true);
}
