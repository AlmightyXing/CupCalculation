// Mock Data (Fallback if JSON cannot be fetched)
const MOCK_DATA = [
  {
    "character_id": "char_325_mlynar",
    "name": "玛恩纳",
    "cup_level": "超大杯·上",
    "rank": 1,
    "auto_dps": null,
    "manual_damage_total": 278932,
    "avatar": "https://prts.wiki/images/6/6b/%E5%A4%B4%E5%83%8F_%E7%8E%9B%E6%81%A9%E7%BA%B3.png"
  },
  {
    "character_id": "char_103_angel",
    "name": "银灰",
    "cup_level": "超大杯·中",
    "rank": 2,
    "auto_dps": 650,
    "manual_damage_total": 20590,
    "avatar": "https://prts.wiki/images/9/90/%E5%A4%B4%E5%83%8F_%E9%93%B6%E7%81%B0.png"
  },
  {
    "character_id": "char_140_anguis",
    "name": "能天使",
    "cup_level": "大杯",
    "rank": 3,
    "auto_dps": 263,
    "manual_damage_total": 2804,
    "avatar": "https://prts.wiki/images/9/9a/%E5%A4%B4%E5%83%8F_%E8%83%BD%E5%A4%A9%E4%BD%BF.png"
  }
];

// Map character names to their wiki avatars for demo purposes
const AVATAR_MAP = {
    "玛恩纳": "https://prts.wiki/images/6/6b/%E5%A4%B4%E5%83%8F_%E7%8E%9B%E6%81%A9%E7%BA%B3.png",
    "银灰": "https://prts.wiki/images/9/90/%E5%A4%B4%E5%83%8F_%E9%93%B6%E7%81%B0.png",
    "能天使": "https://prts.wiki/images/9/9a/%E5%A4%B4%E5%83%8F_%E8%83%BD%E5%A4%A9%E4%BD%BF.png"
};

let currentData = [];
let currentTab = 'manual'; // 'manual', 'auto', 'total'

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch('../data/output/result.json');
        if (response.ok) {
            currentData = await response.json();
            // Assign dummy avatars if not present
            currentData.forEach(item => {
                item.avatar = AVATAR_MAP[item.name] || `https://dummyimage.com/100x100/e0e0e0/ffffff&text=${item.name.charAt(0)}`;
            });
        } else {
            currentData = MOCK_DATA;
        }
    } catch (e) {
        console.log("Fetch failed, using mock data.", e);
        currentData = MOCK_DATA;
    }

    bindEvents();
    renderList();
}

function bindEvents() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            tabs.forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentTab = e.target.dataset.tab;
            renderList();
        });
    });

    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {
        renderList(e.target.value.trim().toLowerCase());
    });
}

function renderList(query = '') {
    const container = document.getElementById('list-container');
    container.innerHTML = '';

    // Filter by query
    let filteredData = currentData.filter(item => 
        item.name.toLowerCase().includes(query) || 
        (item.cup_level && item.cup_level.toLowerCase().includes(query))
    );

    // Sort according to current tab
    filteredData.sort((a, b) => {
        if (currentTab === 'manual') {
            return (b.manual_damage_total || 0) - (a.manual_damage_total || 0);
        } else if (currentTab === 'auto') {
            return (b.auto_dps || 0) - (a.auto_dps || 0);
        }
        return (a.rank || 999) - (b.rank || 999);
    });

    if (filteredData.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding: 40px; color: #8f959e;">未找到干员</div>';
        return;
    }

    filteredData.forEach((item, index) => {
        let cupClass = 'cup-low';
        if (item.cup_level) {
            if (item.cup_level.includes('超大杯')) {
                cupClass = 'cup-top';
            } else if (item.cup_level.includes('大杯')) {
                cupClass = 'cup-mid';
            }
        }

        let scoreLabel = '决战总伤';
        let scoreValue = item.manual_damage_total || '-';
        if (currentTab === 'auto') {
            scoreLabel = '挂机DPS';
            scoreValue = item.auto_dps || '-';
        } else if (currentTab === 'total') {
            scoreLabel = '综合排位';
            scoreValue = item.rank || '-';
        }

        const rankDisplay = index + 1;

        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.rank = rankDisplay;
        // Animation stagger
        card.style.animationDelay = `${index * 0.05}s`;
        
        card.innerHTML = `
            <div class="card-rank">${rankDisplay}</div>
            <div class="card-avatar">
                <img src="${item.avatar}" alt="${item.name}" onerror="this.src='https://dummyimage.com/100x100/e0e0e0/ffffff&text=O'"/>
            </div>
            <div class="card-info">
                <div class="card-name">${item.name}</div>
                <div class="card-stats">ID: ${item.character_id.split('_').pop()}</div>
            </div>
            <div class="card-score">
                ${item.cup_level ? `<div class="cup-badge ${cupClass}">${item.cup_level}</div>` : ''}
                <div class="score-value">${scoreValue}</div>
                <div style="font-size: 11px; color: var(--text-sub); margin-top:2px;">${scoreLabel}</div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            card.style.transform = 'scale(0.96)';
            setTimeout(() => card.style.transform = '', 150);
        });

        container.appendChild(card);
    });
}
