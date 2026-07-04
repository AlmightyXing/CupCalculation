import sys
with open('e:/Local_AI_Station/CupCalculation/frontend/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add word-wrap to talent description
old_talent = '<div class="ft-cell bg-20 align-left" style="flex: 5;">${t.talent_description || t.talent_decription || \'-\'}</div>'
new_talent = '<div class="ft-cell bg-20 align-left" style="flex: 5; white-space: pre-wrap; word-break: break-word; line-height: 1.4;">${t.talent_description || t.talent_decription || \'-\'}</div>'
if old_talent in code: code = code.replace(old_talent, new_talent)

# 2. Add switchView hook for Sandbox
old_switch = '''    if (viewId === 'sandbox') {
      // nothing for now
    }'''
new_switch = '''    if (viewId === 'sandbox') {
      initSandboxForm();
    }'''
if old_switch in code: code = code.replace(old_switch, new_switch)

# 3. Add chart init to renderList success
old_renderList = '''      if (typeof isChartView !== 'undefined' && isChartView) {
        // We will call renderChart() when implementing chart
      }'''
new_renderList = '''      if (typeof isChartView !== 'undefined' && isChartView) {
        if (typeof renderChart !== 'undefined') renderChart();
      }'''
if old_renderList in code: code = code.replace(old_renderList, new_renderList)

# 4. Replace Sandbox logic
sandbox_start = code.find('// --- Sandbox Logic ---')
sandbox_end = code.find('let chartInstance = null;')
if sandbox_end == -1:
    sandbox_end = len(code)

new_sandbox = '''// --- Sandbox Logic ---
const majorClassMap = {
  '先锋': ['先锋', '尖兵', '冲锋手', '战术家', '执旗手', '情报官'],
  '近卫': ['近卫', '强攻手', '教官', '领主', '术战者', '剑豪', '武者', '无畏者', '收割者', '解放者', '重剑手', '撼地者'],
  '重装': ['重装', '铁卫', '守护者', '不屈者', '驭法铁卫', '决战者', '要塞', '哨戒铁卫'],
  '狙击': ['狙击', '速射手', '神射手', '炮手', '攻城射手', '散射手', '重射手', '投掷手', '猎手'],
  '术师': ['术师', '中坚术师', '阵法术师', '秘术师', '链术师', '轰击术师', '扩散术师', '本源术师'],
  '医疗': ['医疗', '医师', '群愈师', '疗养师', '行医', '咒愈师', '链愈师'],
  '辅助': ['辅助', '吟游者', '召唤师', '凝滞师', '削弱者', '护佑者', '巫役'],
  '特种': ['特种', '处决者', '推击手', '伏击客', '钩索师', '陷阱师', '行商', '傀儡师', '炼金师']
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
      filteredOps.sort((a,b) => a.name.localeCompare(b.name)).forEach(op => {
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
      let logsHtml = rep.combat_log.map(l => `<div>${l}</div>`).join('');
      
      sbResult.innerHTML = `
        <div class="detail-section" style="margin-top: 20px;">
          <h3 style="color: var(--accent-primary); border-bottom: 1px solid var(--accent-primary); padding-bottom: 5px; margin-bottom: 15px;">演算结果</h3>
          <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div class="glass-panel" style="flex: 1; text-align: center; padding: 15px;">
              <div style="font-size: 14px; color: #9ca3af;">最佳 DPS</div>
              <div style="font-size: 24px; font-weight: bold; color: #10b981;">${rep.dps}</div>
            </div>
            <div class="glass-panel" style="flex: 1; text-align: center; padding: 15px;">
              <div style="font-size: 14px; color: #9ca3af;">技能总伤</div>
              <div style="font-size: 24px; font-weight: bold; color: #f59e0b;">${rep.total_damage}</div>
            </div>
          </div>
          <h4 style="margin-bottom: 10px; color: #e5e7eb;">战斗日志</h4>
          <div class="glass-panel" style="max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 13px; color: #d1d5db; line-height: 1.6;">
            ${logsHtml}
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
'''

code = code[:sandbox_start] + new_sandbox
with open('e:/Local_AI_Station/CupCalculation/frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(code)
print('Patched app.js successfully!')
