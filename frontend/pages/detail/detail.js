import request from '../../utils/request';

Page({
  data: {
    statusBarHeight: 20,
    showE2: false,
    operator: {}
  },

  onLoad(options) {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
    
    // 使用 decodeURIComponent 还原从路由参数传来的中文字符串，避免后续请求被双重 encode
    const rawName = options.name || "乌尔比安"; 
    const name = decodeURIComponent(rawName);
    this.loadOperatorData(name);
  },

  goBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  togglePortrait() {
    this.setData({ showE2: !this.data.showE2 });
  },

  async loadOperatorData(name) {
    try {
      wx.showLoading({ title: '加载中' });
      const res = await request.get(`/api/operator/${encodeURIComponent(name)}`);
      if (res && res.data) {
        const opData = res.data;
        
        // 兼容性占位符填充，避免前端报错
        opData.enName = opData.enName || 'UNKNOWN';
        opData.position = opData.position || (opData.character && opData.character.character_type) || '暂无位置';
        opData.tags = opData.tags || '暂无标签';
        
        opData.ranks = opData.ranks || {
          total: '-',
          idle: '-',
          burst: '-'
        };

        // 技能占位排名与伤害
        if (opData.skills && opData.skills.length > 0) {
          opData.skills.forEach((skill, index) => {
            skill.mockDps = skill.mockDps || '演算中';
            skill.mockDpsRank = skill.mockDpsRank || '-';
            skill.mockTotalDmg = skill.mockTotalDmg || '演算中';
            skill.mockTotalRank = skill.mockTotalRank || '-';
            skill.mockOverallRank = skill.mockOverallRank || '-';
          });
        }

        this.setData({ operator: opData });
      }
    } catch (e) {
      console.error('Failed to load operator', e);
      wx.showToast({ title: '获取数据失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  }
});
