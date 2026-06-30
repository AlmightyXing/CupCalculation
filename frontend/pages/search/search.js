Page({
  data: {
    keyword: '',
    hotTags: ['玛恩纳', '水陈', '42', '叔叔', '翼德'],
    history: [],
    results: [],
    
    // 本地 mock 全字典
    dictionary: [
      { rank: 1, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '玛恩纳', alias: ['叔叔', 'mlynar'], profession: '解放者', score: 125430, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_325_mlynar_1.png' },
      { rank: 2, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '史尔特尔', alias: ['42', '奶奶', 'surtr'], profession: '阵法术师', score: 112000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_350_surtr_1.png' },
      { rank: 3, cup_level: '超大杯·中', cup_level_code: 'high', name: '假日威龙陈', alias: ['水陈', 'chen2'], profession: '散射手', score: 108500, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_1013_chen2_1.png' },
      { rank: 7, cup_level: '超大杯·下', cup_level_code: 'high', name: '缄默德克萨斯', alias: ['翼德', '德狗', 'texas2'], profession: '处决者', score: 92000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_1028_texas2_1.png' }
    ]
  },

  onLoad() {
    const history = wx.getStorageSync('search_history') || [];
    this.setData({ history });
  },

  onInput(e) {
    const keyword = e.detail.value.trim();
    this.setData({ keyword });
    this.doSearch(keyword);
  },

  clearInput() {
    this.setData({ keyword: '', results: [] });
  },

  useTag(e) {
    const tag = e.currentTarget.dataset.tag;
    this.setData({ keyword: tag });
    this.doSearch(tag);
  },

  doSearch(keyword) {
    if (!keyword) {
      this.setData({ results: [] });
      return;
    }
    const kw = keyword.toLowerCase();
    const res = this.data.dictionary.filter(item => {
      if (item.name.includes(kw)) return true;
      if (item.alias && item.alias.some(a => a.toLowerCase().includes(kw))) return true;
      return false;
    });
    this.setData({ results: res });
  },

  goToDetail(e) {
    const name = e.currentTarget.dataset.id;
    // 存入历史记录
    let history = this.data.history;
    const kw = this.data.keyword;
    if (kw && !history.includes(kw)) {
      history.unshift(kw);
      if (history.length > 10) history.pop();
      wx.setStorageSync('search_history', history);
      this.setData({ history });
    }
    
    // 跳转至详情占位
    wx.navigateTo({
      url: `/pages/detail/detail?name=${encodeURIComponent(name)}`,
      fail: () => {
        wx.showToast({ title: '详情页开发中', icon: 'none' });
      }
    });
  },

  clearHistory() {
    wx.removeStorageSync('search_history');
    this.setData({ history: [] });
  }
});
