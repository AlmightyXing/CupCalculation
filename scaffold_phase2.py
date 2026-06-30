import os

base_dir = "frontend"

def write_file(path, content):
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. Operator Card Component
write_file("components/operator-card/operator-card.json", """
{
  "component": true
}
""")
write_file("components/operator-card/operator-card.wxml", """
<view class="card">
  <view class="card-left">
    <view class="rank">#{{item.rank}}</view>
    <view class="avatar-container">
      <image class="avatar" src="{{item.avatar}}" mode="aspectFill"></image>
      <view class="cup-tag cup-{{item.cup_level_code}}">{{item.cup_level}}</view>
    </view>
  </view>
  <view class="card-middle">
    <view class="name-row">
      <text class="name">{{item.name}}</text>
      <text class="profession">{{item.profession}}</text>
    </view>
    <view class="tags-row" wx:if="{{item.tag}}">
      <text class="tag">{{item.tag}}</text>
    </view>
  </view>
  <view class="card-right">
    <view class="score-label">{{scoreLabel}}</view>
    <view class="score-value">{{item.score}}</view>
  </view>
</view>
""")
write_file("components/operator-card/operator-card.wxss", """
.card {
  display: flex;
  background-color: var(--bg-color-secondary);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.2);
}
.card-left {
  display: flex;
  align-items: center;
  margin-right: 24rpx;
}
.rank {
  font-size: 36rpx;
  font-weight: bold;
  color: var(--text-color-secondary);
  width: 60rpx;
  text-align: center;
  margin-right: 16rpx;
}
.avatar-container {
  position: relative;
}
.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 48rpx;
  border: 4rpx solid var(--divider-color);
}
.cup-tag {
  position: absolute;
  bottom: -10rpx;
  left: 50%;
  transform: translateX(-50%);
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  background-color: #555;
  color: #fff;
  white-space: nowrap;
  font-weight: bold;
}
.cup-super-high { background-color: #ff9800; }
.cup-high { background-color: #9c27b0; }
.cup-mid { background-color: #2196f3; }

.card-middle {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.name-row {
  display: flex;
  align-items: center;
  margin-bottom: 8rpx;
}
.name {
  font-size: 32rpx;
  font-weight: bold;
  color: var(--text-color-primary);
  margin-right: 16rpx;
}
.profession {
  font-size: 20rpx;
  color: var(--text-color-secondary);
  background-color: var(--bg-color-tertiary);
  padding: 2rpx 8rpx;
  border-radius: 8rpx;
}
.tags-row {
  display: flex;
}
.tag {
  font-size: 20rpx;
  color: var(--accent-color);
  border: 1rpx solid var(--accent-color);
  padding: 2rpx 8rpx;
  border-radius: 8rpx;
}
.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.score-label {
  font-size: 20rpx;
  color: var(--text-color-secondary);
  margin-bottom: 8rpx;
}
.score-value {
  font-size: 36rpx;
  font-weight: bold;
  color: var(--accent-color);
}
""")
write_file("components/operator-card/operator-card.js", """
Component({
  properties: {
    item: { type: Object, value: {} },
    scoreLabel: { type: String, value: '总伤' }
  }
});
""")

# 2. Bar Chart Component
write_file("components/bar-chart/bar-chart.json", """
{
  "component": true,
  "usingComponents": {
    "ec-canvas": "../../ec-canvas/ec-canvas"
  }
}
""")
write_file("components/bar-chart/bar-chart.wxml", """
<view class="chart-container">
  <ec-canvas id="mychart-dom-bar" canvas-id="mychart-bar" ec="{{ ec }}"></ec-canvas>
</view>
""")
write_file("components/bar-chart/bar-chart.wxss", """
.chart-container {
  width: 100%;
  height: 800rpx;
  position: relative;
}
ec-canvas {
  width: 100%;
  height: 100%;
}
""")
write_file("components/bar-chart/bar-chart.js", """
import * as echarts from '../../ec-canvas/echarts';

Component({
  properties: {
    chartData: {
      type: Object,
      value: null,
      observer(newVal) {
        if (newVal && this.chart) {
          this.initChart(this.chart, newVal);
        }
      }
    }
  },
  data: {
    ec: {
      lazyLoad: true
    }
  },
  ready() {
    this.ecComponent = this.selectComponent('#mychart-dom-bar');
    if (this.data.chartData) {
      this.init();
    }
  },
  methods: {
    init() {
      this.ecComponent.init((canvas, width, height, dpr) => {
        const chart = echarts.init(canvas, null, {
          width: width,
          height: height,
          devicePixelRatio: dpr
        });
        this.chart = chart;
        this.initChart(chart, this.data.chartData);
        return chart;
      });
    },
    initChart(chart, data) {
      if(!data || !data.categories) return;
      const option = {
        backgroundColor: '#121212',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        grid: {
          left: '3%',
          right: '8%',
          bottom: '3%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          axisLabel: { color: '#AAAAAA' },
          splitLine: { lineStyle: { color: '#333333' } }
        },
        yAxis: {
          type: 'category',
          data: data.categories,
          axisLabel: { color: '#FFFFFF', fontWeight: 'bold' }
        },
        series: [
          {
            type: 'bar',
            data: data.values,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#D32F2F' },
                { offset: 1, color: '#FF7043' }
              ]),
              borderRadius: [0, 4, 4, 0]
            },
            label: {
              show: true,
              position: 'right',
              color: '#FFFFFF'
            }
          }
        ]
      };
      chart.setOption(option);
    }
  }
});
""")

# 3. Update Index Page
write_file("pages/index/index.json", """
{
  "usingComponents": {
    "navigation-bar": "../../components/navigation-bar/navigation-bar",
    "operator-card": "../../components/operator-card/operator-card",
    "bar-chart": "../../components/bar-chart/bar-chart"
  }
}
""")
write_file("pages/index/index.wxml", """
<navigation-bar title="杯级排行榜" back="{{false}}"></navigation-bar>
<view class="container">
  
  <!-- Tabs -->
  <view class="tabs">
    <view class="tab-item {{currentTab === 'total' ? 'active' : ''}}" bindtap="switchTab" data-tab="total">总杯级</view>
    <view class="tab-item {{currentTab === 'idle' ? 'active' : ''}}" bindtap="switchTab" data-tab="idle">挂机</view>
    <view class="tab-item {{currentTab === 'burst' ? 'active' : ''}}" bindtap="switchTab" data-tab="burst">决战</view>
  </view>

  <!-- View Mode Switch -->
  <view class="view-switch-bar">
    <text class="title">{{currentTabName}} TOP 10</text>
    <view class="switch-btn" bindtap="toggleViewMode">
      <text>{{viewMode === 'list' ? '📊 图表模式' : '📋 列表模式'}}</text>
    </view>
  </view>

  <scroll-view scroll-y class="content-scroll">
    <!-- List Mode -->
    <block wx:if="{{viewMode === 'list'}}">
      <view class="list-container">
        <block wx:for="{{operators}}" wx:key="rank">
          <operator-card item="{{item}}" scoreLabel="{{scoreLabel}}"></operator-card>
        </block>
      </view>
    </block>

    <!-- Chart Mode -->
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
.tabs {
  display: flex;
  background-color: var(--bg-color-secondary);
  border-bottom: 2rpx solid var(--divider-color);
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  color: var(--text-color-secondary);
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.2s;
}
.tab-item.active {
  color: var(--text-color-primary);
  border-bottom: 4rpx solid var(--accent-color);
}
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
  padding: 0 30rpx 40rpx 30rpx;
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
    currentTab: 'burst',
    currentTabName: '决战榜',
    viewMode: 'list', // 'list' or 'chart'
    scoreLabel: '1000甲总伤',
    operators: [],
    chartData: null
  },

  onLoad() {
    this.loadMockData();
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    const tabNames = { 'total': '总杯级', 'idle': '挂机榜', 'burst': '决战榜' };
    this.setData({ 
      currentTab: tab, 
      currentTabName: tabNames[tab],
      scoreLabel: tab === 'burst' ? '1000甲总伤' : '平均DPS'
    });
    this.loadMockData(); // 模拟刷新数据
  },

  toggleViewMode() {
    this.setData({ viewMode: this.data.viewMode === 'list' ? 'chart' : 'list' });
  },

  loadMockData() {
    // 高仿真 Mock 数据
    const mockOperators = [
      { rank: 1, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '玛恩纳', profession: '解放者', tag: 'NEW', score: 125430, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_325_mlynar_1.png' },
      { rank: 2, cup_level: '超大杯·上', cup_level_code: 'super-high', name: '史尔特尔', profession: '阵法术师', tag: '↑1', score: 112000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_350_surtr_1.png' },
      { rank: 3, cup_level: '超大杯·中', cup_level_code: 'high', name: '水陈', profession: '散射手', tag: '', score: 108500, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_1013_chen2_1.png' },
      { rank: 4, cup_level: '超大杯·中', cup_level_code: 'high', name: '银灰', profession: '领主', tag: '', score: 95400, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_172_svrash_1.png' },
      { rank: 5, cup_level: '大杯', cup_level_code: 'mid', name: '艾雅法拉', profession: '中坚术师', tag: '↓2', score: 87000, avatar: 'https://cdn.jsdelivr.net/gh/Aceship/Arknight-Images/characters/char_180_amiy2_1.png' }
    ];

    // 翻转数组给图表使用（图表Y轴自下而上画）
    const categories = mockOperators.map(o => o.name).reverse();
    const values = mockOperators.map(o => o.score).reverse();

    this.setData({
      operators: mockOperators,
      chartData: { categories, values }
    });
  }
});
""")

print("Phase 2 scaffolding created successfully.")
