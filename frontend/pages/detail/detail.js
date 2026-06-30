Page({
  data: {
    name: ''
  },
  onLoad(options) {
    if(options.name) {
      this.setData({ name: decodeURIComponent(options.name) });
    }
  }
});
