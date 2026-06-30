import os

base_dir = "frontend"

def write_file(path, content):
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Update Index Page (index.wxml, index.wxss, index.js)
write_file("pages/index/index.wxml", """
<view class="container">
  
  <!-- 自定义头部区域 (使用户提供的图片作为背景) -->
  <view class="custom-header">
    <image class="header-bg" src="../../image/Background.png" mode="aspectFill"></image>
    <view class="header-content" style="padding-top: {{statusBarHeight}}px;">
      
      <!-- 标题 -->
      <view class="title-container">
        <image class="header-title" src="../../image/Text_Title.png" mode="heightFix"></image>
      </view>
      
      <!-- 搜索栏 -->
      <view class="search-bar" bindtap="goToSearch">
        <icon type="search" size="18" color="#AAAAAA"></icon>
        <text class="search-text">搜索干员名或外号(如42)</text>
      </view>
      
      <!-- 导航栏 (Tabs) -->
      <view class="tabs">
        <view class="tab-item {{currentTab === 'total' ? 'active' : ''}}" bindtap="switchTab" data-tab="total">
          <image class="tab-icon" src="../../image/Navi_Bar_Cup.png" mode="aspectFit"></image>
          <text>总杯级</text>
        </view>
        <view class="tab-item {{currentTab === 'idle' ? 'active' : ''}}" bindtap="switchTab" data-tab="idle">
          <image class="tab-icon" src="../../image/Navi_Bar_Auto.png" mode="aspectFit"></image>
          <text>挂机</text>
        </view>
        <view class="tab-item {{currentTab === 'burst' ? 'active' : ''}}" bindtap="switchTab" data-tab="burst">
          <image class="tab-icon" src="../../image/Navi_Bar_Manual.png" mode="aspectFit"></image>
          <text>决战</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 视图切换与内容区 -->
  <view class="view-switch-bar">
    <text class="title">{{currentTabName}} TOP 10</text>
    <view class="switch-btn" bindtap="toggleViewMode">
      <text>{{viewMode === 'list' ? '📊 图表模式' : '📋 列表模式'}}</text>
    </view>
  </view>

  <scroll-view scroll-y class="content-scroll">
    <block wx:if="{{viewMode === 'list'}}">
      <view class="list-container">
        <block wx:for="{{operators}}" wx:key="rank">
          <operator-card item="{{item}}" scoreLabel="{{scoreLabel}}"></operator-card>
        </block>
      </view>
    </block>
    <block wx:else>
      <view class="chart-wrapper">
        <bar-chart chartData="{{chartData}}"></bar-chart>
      </view>
    </block>
  </scroll-view>

</view>
""")

write_file("pages/index/index.wxss", """
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* Custom Header */
.custom-header {
  position: relative;
  width: 100%;
}
.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  opacity: 0.8;
}
.header-content {
  display: flex;
  flex-direction: column;
  padding-bottom: 20rpx;
}
.title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 88rpx; /* 胶囊区域高度近似 */
  margin-bottom: 30rpx;
}
.header-title {
  height: 60rpx;
}

/* Search Bar */
.search-bar {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1rpx solid rgba(255,255,255,0.2);
  margin: 0 30rpx 40rpx 30rpx;
  padding: 16rpx 30rpx;
  border-radius: 40rpx;
}
.search-text {
  color: #AAAAAA;
  font-size: 28rpx;
  margin-left: 20rpx;
}

/* Tabs */
.tabs {
  display: flex;
  justify-content: space-around;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明以透出背景 */
  border-bottom: 2rpx solid var(--divider-color);
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
  color: var(--text-color-secondary);
  font-size: 26rpx;
  font-weight: 500;
  transition: all 0.2s;
  opacity: 0.6;
}
.tab-item.active {
  color: var(--text-color-primary);
  opacity: 1;
  border-bottom: 4rpx solid var(--accent-color);
}
.tab-icon {
  width: 60rpx;
  height: 60rpx;
  margin-bottom: 8rpx;
}

/* 视图切换栏与列表 */
.view-switch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: var(--bg-color-primary);
}
.view-switch-bar .title {
  font-size: 28rpx;
  color: var(--text-color-secondary);
  font-weight: bold;
}
.switch-btn {
  padding: 8rpx 20rpx;
  background-color: var(--bg-color-tertiary);
  border-radius: 30rpx;
  font-size: 24rpx;
  color: var(--text-color-primary);
  border: 1rpx solid var(--divider-color);
}
.content-scroll {
  flex: 1;
  height: 100%;
}
.list-container {
  padding: 20rpx 30rpx 40rpx 30rpx;
}
.chart-wrapper {
  padding: 20rpx;
  background-color: var(--bg-color-secondary);
  margin: 0 30rpx;
  border-radius: 16rpx;
}
""")

write_file("pages/index/index.js", """
Page({
  data: {
    statusBarHeight: 20,
    currentTab: 'burst',
    currentTabName: '决战榜',
    viewMode: 'list',
    scoreLabel: '1000甲总伤',
    operators: [],
    chartData: null
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
    this.loadMockData();
  },

  goToSearch() {
    wx.navigateTo({
      url: '/pages/search/search'
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    const tabNames = { 'total': '总杯级', 'idle': '挂机榜', 'burst': '决战榜' };
    this.setData({ 
      currentTab: tab, 
      currentTabName: tabNames[tab],
      scoreLabel: tab === 'burst' ? '1000甲总伤' : '平均DPS'
    });
    this.loadMockData(); 
  },

  toggleViewMode() {
    this.setData({ viewMode: this.data.viewMode === 'list' ? 'chart' : 'list' });
  },

  loadMockData() {
    const mockOperators = [
      { rank: 1, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '玛恩纳', profession: '解放者', tag: 'NEW', score: 125430, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_325_mlynar_1.png' },
      { rank: 2, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '史尔特尔', profession: '阵法术师', tag: '↑1', score: 112000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_350_surtr_1.png' },
      { rank: 3, cup_level: '超大杯·中', cup_level_code: 'high', name: '水陈', profession: '散射手', tag: '', score: 108500, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_1013_chen2_1.png' },
      { rank: 4, cup_level: '超大杯·中', cup_level_code: 'high', name: '银灰', profession: '领主', tag: '', score: 95400, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_172_svrash_1.png' },
      { rank: 5, cup_level: '大杯', cup_level_code: 'mid', name: '艾雅法拉', profession: '中坚术师', tag: '↓2', score: 87000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_180_amiy2_1.png' }
    ];

    const categories = mockOperators.map(o => o.name).reverse();
    const values = mockOperators.map(o => o.score).reverse();

    this.setData({
      operators: mockOperators,
      chartData: { categories, values }
    });
  }
});
""")

write_file("pages/index/index.json", """
{
  "usingComponents": {
    "operator-card": "../../components/operator-card/operator-card",
    "bar-chart": "../../components/bar-chart/bar-chart"
  }
}
""")

# 2. Update Search Page (search.wxml, search.wxss, search.js)
write_file("pages/search/search.json", """
{
  "usingComponents": {
    "navigation-bar": "../../components/navigation-bar/navigation-bar",
    "operator-card": "../../components/operator-card/operator-card"
  }
}
""")
write_file("pages/search/search.wxml", """
<navigation-bar title="搜索干员" back="{{true}}"></navigation-bar>
<view class="container">
  
  <view class="search-box">
    <icon type="search" size="18" color="#AAAAAA" class="search-icon"></icon>
    <input placeholder="输入干员名或外号(如42、水陈)" placeholder-class="ph-color" focus="{{true}}" bindinput="onInput" value="{{keyword}}"/>
    <icon type="clear" size="18" color="#AAAAAA" class="clear-icon" wx:if="{{keyword}}" bindtap="clearInput"></icon>
  </view>

  <!-- 搜索建议/历史区 -->
  <view class="suggest-area" wx:if="{{!keyword}}">
    <!-- 热门推荐 -->
    <view class="section">
      <view class="section-title">热门推荐</view>
      <view class="tag-list">
        <view class="tag" wx:for="{{hotTags}}" wx:key="*this" bindtap="useTag" data-tag="{{item}}">{{item}}</view>
      </view>
    </view>
    
    <!-- 历史记录 -->
    <view class="section" wx:if="{{history.length > 0}}">
      <view class="section-title">
        <text>搜索历史</text>
        <icon type="cancel" size="16" color="#666" bindtap="clearHistory"></icon>
      </view>
      <view class="tag-list">
        <view class="tag" wx:for="{{history}}" wx:key="*this" bindtap="useTag" data-tag="{{item}}">{{item}}</view>
      </view>
    </view>
  </view>

  <!-- 搜索结果区 -->
  <scroll-view scroll-y class="result-area" wx:if="{{keyword}}">
    <block wx:if="{{results.length > 0}}">
      <view class="list-container">
        <block wx:for="{{results}}" wx:key="rank">
          <view bindtap="goToDetail" data-id="{{item.name}}">
            <operator-card item="{{item}}" scoreLabel="参考DPS"></operator-card>
          </view>
        </block>
      </view>
    </block>
    <view class="empty-state" wx:else>
      <text>暂无找到该干员，试试搜别名？</text>
    </view>
  </scroll-view>

</view>
""")
write_file("pages/search/search.wxss", """
.search-box {
  display: flex;
  align-items: center;
  padding: 16rpx 20rpx;
  background-color: var(--bg-color-secondary);
  margin: 20rpx 30rpx;
  border-radius: 40rpx;
}
.search-icon {
  margin-right: 16rpx;
}
.clear-icon {
  margin-left: 16rpx;
}
.search-box input {
  flex: 1;
  color: var(--text-color-primary);
  font-size: 28rpx;
}
.ph-color {
  color: var(--text-color-secondary);
}

.suggest-area {
  padding: 20rpx 30rpx;
}
.section {
  margin-bottom: 40rpx;
}
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 28rpx;
  color: var(--text-color-secondary);
  margin-bottom: 20rpx;
  font-weight: bold;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
}
.tag {
  background-color: var(--bg-color-secondary);
  color: var(--text-color-primary);
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
  margin-right: 20rpx;
  margin-bottom: 20rpx;
  border: 1rpx solid var(--divider-color);
}

.result-area {
  flex: 1;
  height: 100%;
}
.list-container {
  padding: 20rpx 30rpx;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40vh;
  color: var(--text-color-secondary);
  font-size: 28rpx;
}
""")
write_file("pages/search/search.js", """
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
""")

# 3. Create Detail Page Stub
write_file("pages/detail/detail.json", """
{
  "usingComponents": {
    "navigation-bar": "../../components/navigation-bar/navigation-bar"
  }
}
""")
write_file("pages/detail/detail.wxml", """
<navigation-bar title="干员详情 (建设中)" back="{{true}}"></navigation-bar>
<view class="container">
  <view class="msg">
    <text>干员 {{name}} 的详情页将在阶段 4 完成建设</text>
  </view>
</view>
""")
write_file("pages/detail/detail.wxss", """
.msg {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  color: var(--accent-color);
  font-size: 32rpx;
  font-weight: bold;
}
""")
write_file("pages/detail/detail.js", """
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
""")

# Add detail page to app.json
import json
app_json_path = os.path.join(base_dir, "app.json")
with open(app_json_path, "r", encoding="utf-8") as f:
    app_data = json.load(f)
if "pages/detail/detail" not in app_data["pages"]:
    app_data["pages"].append("pages/detail/detail")
with open(app_json_path, "w", encoding="utf-8") as f:
    json.dump(app_data, f, indent=2, ensure_ascii=False)

print("Phase 3 Refactoring completed successfully.")
