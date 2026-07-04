import request from '../../utils/request.js';

Page({
  data: {
    statusBarHeight: 20,
    currentTab: 'total',
    currentTabName: '总杯榜',
    enemyOptions: [
      '0甲 0抗',
      '1000甲 20抗',
      '2000甲 40抗',
      '3000甲 60抗',
      '4000甲 80抗',
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
    this.loadRealData();
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
  
  goToSandbox() {
    wx.navigateTo({
      url: '/pages/sandbox/sandbox'
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    const tabNames = { 'total': '总杯榜', 'idle': '挂机榜', 'burst': '决战榜' };
    this.setData({
      currentTab: tab,
      currentTabName: tabNames[tab]
    });
    this.processListData(); // 重新处理并渲染
  },

  onEnemyChange(e) {
    this.setData({
      enemyIndex: e.detail.value
    });
    this.loadRealData();
  },

  // 保存请求回来的所有全服干员排位
  allOperators: [],

  loadRealData() {
    const enemyOptionsStr = this.data.enemyOptions[this.data.enemyIndex];
    // 解析 '1000甲 20抗'
    const defMatch = enemyOptionsStr.match(/(\d+)甲/);
    const resMatch = enemyOptionsStr.match(/(\d+)抗/);
    const enemyDef = defMatch ? parseInt(defMatch[1]) : 0;
    const enemyRes = resMatch ? parseInt(resMatch[1]) : 0;

    request.get(`/api/rankings?enemy_def=${enemyDef}&enemy_res=${enemyRes}`)
      .then(res => {
        if (res.status === 'success') {
          this.allOperators = res.data.operators;
          this.processListData();
        }
      })
      .catch(err => {
        console.error('获取榜单失败', err);
        wx.showToast({ title: '加载失败', icon: 'none' });
      });
  },

  processListData() {
    let list = [...this.allOperators];

    // 根据当前的 Tab 重置 rank
    if (this.data.currentTab === 'idle') {
      list.sort((a, b) => a.idleRank - b.idleRank);
      list.forEach(op => {
        op.rank = op.idleRank;
        op.dps = Math.round(op.idle_score);
        op.totalDmg = Math.round(op.best_total_dmg);
      });
    } else if (this.data.currentTab === 'burst') {
      list.sort((a, b) => a.burstRank - b.burstRank);
      list.forEach(op => {
        op.rank = op.burstRank;
        op.dps = Math.round(op.best_dps);
        op.totalDmg = Math.round(op.burst_score);
      });
    } else {
      // Total Cup
      list.sort((a, b) => a.totalRank - b.totalRank);
      list.forEach(op => {
        op.rank = op.totalRank;
        op.dps = Math.round(op.best_dps);
        op.totalDmg = Math.round(op.best_total_dmg);
      });
    }

    // 依照用户要求：三个排行榜均应出现所有角色，而非只显示前10名
    const allOps = list;

    // 分组逻辑
    let grouped = [];
    let currentGroup = null;
    allOps.forEach(op => {
      if (!currentGroup || currentGroup.cup_level !== op.cup_level) {
        currentGroup = { cup_level: op.cup_level, list: [] };
        grouped.push(currentGroup);
      }
      currentGroup.list.push(op);
    });

    this.setData({
      operators: allOps,
      groupedOperators: grouped
    });
  }
});
