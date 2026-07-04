import request from '../../utils/request.js';

Page({
  data: {
    statusBarHeight: 20,
    operatorName: '',
    skillIndex: '',
    enemyDef: '',
    enemyRes: '',
    result: null
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
  },

  goBack() {
    wx.navigateBack();
  },

  onOpInput(e) {
    this.setData({ operatorName: e.detail.value });
  },

  onSkillInput(e) {
    this.setData({ skillIndex: e.detail.value });
  },

  onDefInput(e) {
    this.setData({ enemyDef: e.detail.value });
  },

  onResInput(e) {
    this.setData({ enemyRes: e.detail.value });
  },

  startSimulation() {
    const { operatorName, skillIndex, enemyDef, enemyRes } = this.data;
    
    if (!operatorName) {
      wx.showToast({ title: '请输入干员名称', icon: 'none' });
      return;
    }

    const payload = {
      operator_name: operatorName,
      skill_index: parseInt(skillIndex || '0', 10),
      enemy_def: parseInt(enemyDef || '0', 10),
      enemy_res: parseInt(enemyRes || '0', 10)
    };

    wx.showLoading({ title: '演算中...' });
    
    request.post('/api/sandbox/simulate', payload)
      .then(res => {
        wx.hideLoading();
        if (res.status === 'success') {
          this.setData({
            result: res.data
          });
        } else {
          wx.showToast({ title: '计算失败', icon: 'none' });
        }
      })
      .catch(err => {
        wx.hideLoading();
        wx.showToast({ title: '请求出错', icon: 'none' });
        console.error(err);
      });
  }
});
