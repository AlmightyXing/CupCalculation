Component({
  properties: {
    item: { type: Object, value: {} },
    mode: { type: String, value: 'total' }, // 'total' 或 'skill'
    isLast: { type: Boolean, value: false } // 用于去掉最后一行底部边框
  }
});
