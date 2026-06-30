Component({
  properties: {
    title: { type: String, value: '' },
    back: { type: Boolean, value: false }
  },
  data: {
    statusBarHeight: 20,
    navHeight: 64,
    menuHeight: 44
  },
  attached() {
    const sysInfo = wx.getSystemInfoSync();
    const rect = wx.getMenuButtonBoundingClientRect ? wx.getMenuButtonBoundingClientRect() : null;
    let statusBarHeight = sysInfo.statusBarHeight;
    let navHeight, menuHeight;
    
    if (rect) {
      navHeight = rect.bottom + (rect.top - statusBarHeight);
      menuHeight = rect.height + (rect.top - statusBarHeight) * 2;
    } else {
      navHeight = statusBarHeight + 44;
      menuHeight = 44;
    }
    
    this.setData({
      statusBarHeight,
      navHeight,
      menuHeight
    });
  },
  methods: {
    onBack() {
      wx.navigateBack();
    }
  }
});
