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
            skill.mockDps = '演算中';
            skill.mockDpsRank = '-';
            skill.mockTotalDmg = '演算中';
            skill.mockTotalRank = '-';
            skill.mockOverallRank = '-';
          });
        }
        
        // 同时请求排行榜数据以填充真实DPS
        try {
          const rankRes = await request.get(`/api/rankings?enemy_def=0&enemy_res=0`);
          if (rankRes && rankRes.data && rankRes.data.operators) {
            const myRankData = rankRes.data.operators.find(o => o.name === name);
            if (myRankData) {
              opData.ranks.total = myRankData.totalRank || '-';
              opData.ranks.idle = myRankData.idleRank || '-';
              opData.ranks.burst = myRankData.burstRank || '-';
              
              if (myRankData.skills && opData.skills) {
                myRankData.skills.forEach(sk => {
                  if (opData.skills[sk.skill_idx]) {
                    opData.skills[sk.skill_idx].mockDps = Math.round(sk.dps);
                    opData.skills[sk.skill_idx].mockTotalDmg = Math.round(sk.total_dmg);
                  }
                });
              }
            }
          }
        } catch(err) {
          console.error("加载排位数据失败", err);
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
