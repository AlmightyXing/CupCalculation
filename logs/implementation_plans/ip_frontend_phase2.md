# 🏆 前端开发执行计划：阶段 2（首页排行榜单流开发）

根据《前端设计与开发任务单》，当前进入阶段 2。我将指派 **“UI 与数据 Agent”** 接管此阶段。该 Agent 将专注于小程序首页的完整视觉还原与交互逻辑。

## 🎯 整体架构与开发目标

本阶段聚焦于 `frontend/pages/index/index` 页面，核心是完成**单行卡片列表**与**ECharts数据可视化**。

### 阶段 2 核心任务清单

1. **顶部导航与分类切换栏 (Tabs)**：
   - 包含：“总杯级”、“挂机(DPS/HPS)”、“决战(总伤/DPS)”等 Tab 切换。
   - 增加一个“列表/图表”的视图模式切换开关。
2. **干员数据卡片组件 (`components/operator-card`)**：
   - 实现高质感深色卡片 UI。
   - 数据展示包括：当前排名 (Rank)、杯级徽章 (超大杯/大杯等)、干员头像、干员名称、干员职业图标、关键考核数值（如 1000甲DPS 12000）。
   - 动态标签支持：如 `NEW` (新干员) 或 `↑2` (排名上升)。
3. **ECharts for WeiXin 图表集成 (`components/bar-chart`)**：
   - 引入微信小程序版 ECharts。
   - 在“图表模式”下，抽取当前榜单 Top 10 的干员数据，渲染横向条形图，直观体现杯级之间的数值“断层”。
4. **Mock 数据注入**：
   - 为了在此阶段独立验证前端效果，UI Agent 将在 `pages/index/index.js` 中注入一组高仿真的 Mock 数据（暂不强依赖后端的 `/api/operators`，确保前端页面能直接看到效果和联调组件）。

---

## ⚠️ User Review Required

> [!IMPORTANT]
> **ECharts 库体积问题**：引入 `echarts-for-weixin` 会占据约近 1MB 的小程序包体积。由于是项目初期，为了保证开发速度和高质感图表，我们将直接全量引入。后期如有需要可以优化包体积。请确认是否接受。

## ❓ Open Questions

> [!NOTE]
>
> 1. 原型中展现的 ECharts 柱状图，您更倾向于是**横向柱状图**（适合展示长名字，自上而下排位），还是**纵向柱状图**（传统高低对比）？（考虑到手机屏幕宽度受限，默认我将使用横向排版，以便于放置干员名称）。
> 2. 干员头像等静态资源图片，在此阶段我将暂时使用网络上开源图床的占位图（Placeholder URL），后续最后联调阶段再替换为云存储中您上传的真实立绘/头像，这样可以吗？

## 🛠️ Proposed Changes

### Components & Pages

#### [MODIFY] frontend/pages/index/index.wxml (实现 Tab 与双视图容器)

#### [MODIFY] frontend/pages/index/index.wxss (实现深色主题样式布局)

#### [MODIFY] frontend/pages/index/index.js (注入 Mock 数据与交互逻辑)

#### [NEW] frontend/components/operator-card/ (单行干员信息卡片组件，含 wxml, wxss, js, json)

#### [NEW] frontend/components/bar-chart/ (封装的 ECharts 渲染组件)

#### [NEW] frontend/ec-canvas/ (ECharts 微信小程序官方组件目录)

## 🧪 Verification Plan

### Manual Verification

- **Artifact 交付**：UI Agent 将向您呈现本阶段的专项交付 Artifact，并在里面展示代码路径。
- **视图功能验证**：所有的 Mock 数据将在微信开发者工具中正确响应卡片滚动和 Tab 切换，切换到图表时能顺利渲染 ECharts 实例，且无 UI 溢出和报错。
