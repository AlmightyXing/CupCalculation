Page({
  data: {
    statusBarHeight: 20,
    currentTab: 'total',
    currentTabName: '总杯榜 TOP 10',
    enemyOptions: [
      '0甲 0抗',
      '500甲 20抗',
      '1000甲 20抗',
      '2000甲 50抗',
      '3000甲 70抗',
      '5000甲 100抗'
    ],
    enemyIndex: 2, 
    operators: [],
    groupedOperators: [] // 用于总杯榜的合并视图
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
    this.loadMockData();
  },
  
  exitMiniProgram() {
    wx.exitMiniProgram({
      success: () => console.log('已退出小程序'),
      fail: (err) => console.error(err)
    });
  },

  goToSearch() {
    wx.navigateTo({
      url: '/pages/search/search'
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    const tabNames = { 'total': '总杯榜', 'idle': '挂机榜', 'burst': '决战榜' };
    this.setData({ 
      currentTab: tab, 
      currentTabName: tabNames[tab] + ' TOP 10'
    });
    this.loadMockData(); 
  },

  onEnemyChange(e) {
    this.setData({
      enemyIndex: e.detail.value
    });
    this.loadMockData();
  },

  loadMockData() {
    const mockData = [
      { rank: 1, cup_level: '超大杯', name: '玛恩纳', profession: '解放者', idleRank: 10, burstRank: 1, dps: 3450, totalDmg: 125430 },
      { rank: 2, cup_level: '超大杯', name: '史尔特尔', profession: '阵法术师', idleRank: 15, burstRank: 2, dps: 3100, totalDmg: 112000 },
      { rank: 3, cup_level: '超大杯', name: '假日威龙陈', profession: '散射手', idleRank: 5, burstRank: 3, dps: 2800, totalDmg: 108500 },
      { rank: 4, cup_level: '大杯', name: '凛御银灰', profession: '领主', idleRank: 20, burstRank: 4, dps: 2500, totalDmg: 95400 },
      { rank: 5, cup_level: '大杯', name: '艾雅法拉', profession: '中坚术师', idleRank: 4, burstRank: 7, dps: 2200, totalDmg: 87000 }
    ];

    // 分组逻辑
    let grouped = [];
    let currentGroup = null;
    mockData.forEach(op => {
      if (!currentGroup || currentGroup.cup_level !== op.cup_level) {
        currentGroup = { cup_level: op.cup_level, list: [] };
        grouped.push(currentGroup);
      }
      currentGroup.list.push(op);
    });

    this.setData({
      operators: mockData,
      groupedOperators: grouped
    });
  }
});
