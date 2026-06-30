Page({
  data: {
    statusBarHeight: 20,
    currentTab: 'burst',
    currentTabName: '决战榜',
    viewMode: 'list',
    scoreLabel: '1000甲总伤',
    operators: [],
    chartData: null
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
    this.loadMockData();
  },

  goToSearch() {
    wx.navigateTo({
      url: '/pages/search/search'
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    const tabNames = { 'total': '总杯级', 'idle': '挂机榜', 'burst': '决战榜' };
    this.setData({ 
      currentTab: tab, 
      currentTabName: tabNames[tab],
      scoreLabel: tab === 'burst' ? '1000甲总伤' : '平均DPS'
    });
    this.loadMockData(); 
  },

  toggleViewMode() {
    this.setData({ viewMode: this.data.viewMode === 'list' ? 'chart' : 'list' });
  },

  loadMockData() {
    const mockOperators = [
      { rank: 1, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '玛恩纳', profession: '解放者', tag: 'NEW', score: 125430, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_325_mlynar_1.png' },
      { rank: 2, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '史尔特尔', profession: '阵法术师', tag: '↑1', score: 112000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_350_surtr_1.png' },
      { rank: 3, cup_level: '超大杯·中', cup_level_code: 'high', name: '水陈', profession: '散射手', tag: '', score: 108500, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_1013_chen2_1.png' },
      { rank: 4, cup_level: '超大杯·中', cup_level_code: 'high', name: '银灰', profession: '领主', tag: '', score: 95400, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_172_svrash_1.png' },
      { rank: 5, cup_level: '大杯', cup_level_code: 'mid', name: '艾雅法拉', profession: '中坚术师', tag: '↓2', score: 87000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_180_amiy2_1.png' }
    ];

    const categories = mockOperators.map(o => o.name).reverse();
    const values = mockOperators.map(o => o.score).reverse();

    this.setData({
      operators: mockOperators,
      chartData: { categories, values }
    });
  }
});
