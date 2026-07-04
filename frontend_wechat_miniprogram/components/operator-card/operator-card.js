Component({
  properties: {
    item: { type: Object, value: {} },
    mode: { type: String, value: 'total' }, // 'total' 或 'skill'
    isLast: { type: Boolean, value: false } // 用于去掉最后一行底部边框
  },
  methods: {
    goToDetail(e) {
      const name = e.currentTarget.dataset.name;
      if (name) {
        wx.navigateTo({
          url: `/pages/detail/detail?name=${encodeURIComponent(name)}`
        });
      }
    }
  }
});
