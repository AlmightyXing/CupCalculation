import os
import json

base_dir = "frontend"

def write_file(path, content):
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# project.config.json
write_file("project.config.json", """
{
  "description": "项目配置文件",
  "packOptions": {
    "ignore": []
  },
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "minified": true
  },
  "compileType": "miniprogram",
  "libVersion": "3.0.0",
  "appid": "",
  "projectname": "WhatsYourCup",
  "condition": {}
}
""")

# app.json
write_file("app.json", """
{
  "pages": [
    "pages/index/index",
    "pages/search/search"
  ],
  "window": {
    "navigationBarTextStyle": "@navTxtStyle",
    "navigationBarTitleText": "杯级计算器",
    "navigationBarBackgroundColor": "@navBgColor",
    "backgroundColor": "@bgColor",
    "navigationStyle": "custom"
  },
  "darkmode": true,
  "themeLocation": "theme.json",
  "sitemapLocation": "sitemap.json"
}
""")

# theme.json
write_file("theme.json", """
{
  "light": {
    "navBgColor": "#121212",
    "navTxtStyle": "white",
    "bgColor": "#121212"
  },
  "dark": {
    "navBgColor": "#121212",
    "navTxtStyle": "white",
    "bgColor": "#121212"
  }
}
""")

# sitemap.json
write_file("sitemap.json", """
{
  "desc": "关于本文件的更多信息，请参考文档 https://developers.weixin.qq.com/miniprogram/dev/framework/sitemap.html",
  "rules": [{
    "action": "allow",
    "page": "*"
  }]
}
""")

# app.js
write_file("app.js", """
App({
  onLaunch() {
    console.log('App Launch');
  },
  globalData: {
    theme: 'dark'
  }
})
""")

# app.wxss
write_file("app.wxss", """
/* 强制使用暗色主题作为主基调，模拟高级质感 */
page {
  --bg-color-primary: #121212;
  --bg-color-secondary: #1E1E1E;
  --bg-color-tertiary: #2C2C2C;
  --text-color-primary: #FFFFFF;
  --text-color-secondary: #AAAAAA;
  --accent-color: #D32F2F; /* 示例突出版红色 */
  --divider-color: #333333;

  background-color: var(--bg-color-primary);
  color: var(--text-color-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
  box-sizing: border-box;
}

view, text, scroll-view, image {
  box-sizing: border-box;
}

.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
""")

# utils/request.js
write_file("utils/request.js", """
const BASE_URL = 'http://127.0.0.1:8000'; // 暂定本地FastAPI地址

/**
 * 封装微信小程序的网络请求
 */
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          // 可以在此统一处理错误提示
          wx.showToast({
            title: res.data.message || '请求失败',
            icon: 'none'
          });
          reject(res);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络异常',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

export default {
  get(url, data, header) {
    return request(url, { method: 'GET', data, header });
  },
  post(url, data, header) {
    return request(url, { method: 'POST', data, header });
  }
}
""")

# pages/index
write_file("pages/index/index.json", """
{
  "usingComponents": {
    "navigation-bar": "../../components/navigation-bar/navigation-bar"
  }
}
""")
write_file("pages/index/index.wxml", """
<navigation-bar title="杯级排行榜" back="{{false}}"></navigation-bar>
<view class="container">
  <!-- 占位，后续实现榜单流 -->
  <view class="loading-state">
    <text>正在加载榜单数据...</text>
  </view>
</view>
""")
write_file("pages/index/index.wxss", """
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  color: var(--text-color-secondary);
  font-size: 28rpx;
}
""")
write_file("pages/index/index.js", """
const api = require('../../utils/request.js').default;

Page({
  data: {
    operators: []
  },
  onLoad() {
    this.fetchData();
  },
  async fetchData() {
    try {
      // 预留对接后端接口
      // const res = await api.get('/api/operators');
      // this.setData({ operators: res });
    } catch (err) {
      console.error(err);
    }
  }
});
""")

# pages/search
write_file("pages/search/search.json", """
{
  "usingComponents": {
    "navigation-bar": "../../components/navigation-bar/navigation-bar"
  }
}
""")
write_file("pages/search/search.wxml", """
<navigation-bar title="搜索干员" back="{{true}}"></navigation-bar>
<view class="container">
  <view class="search-box">
    <input placeholder="输入干员名或外号(如42)" placeholder-class="ph-color"/>
  </view>
  <view class="empty-state">
    <text>暂无搜索结果</text>
  </view>
</view>
""")
write_file("pages/search/search.wxss", """
.search-box {
  padding: 20rpx;
  background-color: var(--bg-color-secondary);
  margin: 20rpx;
  border-radius: 12rpx;
}

.search-box input {
  color: var(--text-color-primary);
  font-size: 28rpx;
}

.ph-color {
  color: var(--text-color-secondary);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  color: var(--text-color-secondary);
}
""")
write_file("pages/search/search.js", """
Page({
  data: {
  },
  onLoad() {
  }
});
""")

# components/navigation-bar
write_file("components/navigation-bar/navigation-bar.json", """
{
  "component": true
}
""")
write_file("components/navigation-bar/navigation-bar.wxml", """
<view class="nav-bar" style="height: {{navHeight}}px; padding-top: {{statusBarHeight}}px;">
  <view class="nav-bar-inner" style="height: {{menuHeight}}px;">
    <view class="back-btn" bindtap="onBack" wx:if="{{back}}">
      <text class="back-icon">←</text>
    </view>
    <view class="title">{{title}}</view>
  </view>
</view>
""")
write_file("components/navigation-bar/navigation-bar.wxss", """
.nav-bar {
  width: 100%;
  background-color: var(--bg-color-primary);
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  border-bottom: 1rpx solid var(--divider-color);
}
.nav-bar-inner {
  display: flex;
  align-items: center;
  position: relative;
  width: 100%;
}
.back-btn {
  position: absolute;
  left: 30rpx;
  padding: 10rpx;
}
.back-icon {
  color: var(--text-color-primary);
  font-size: 40rpx;
}
.title {
  width: 100%;
  text-align: center;
  font-size: 32rpx;
  font-weight: 500;
  color: var(--text-color-primary);
}
""")
write_file("components/navigation-bar/navigation-bar.js", """
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
""")

print("Frontend scaffolding generated successfully.")
