# 🎯 前端开发执行计划：阶段 3 优化与重构方案

根据《前端Phase3优化方案.md》，我们需要对刚刚完成的 Phase 3 页面进行大幅度的 UI 与布局重构，主要涉及色彩体系、卡片表格化、以及头部定位的优化。本计划旨在确保修改精确还原您的最新设计意图。

## 1. 整体架构与开发目标

### 主题UI调整

- **背景色调**：修改 `frontend/app.wxss` 中的 CSS Variables (`--bg-color-primary` 等)，使其从纯黑 `#121212` 调整为偏灰的色调，使其与 `Background.png` 的底色完美融合。
- **返回按键**：在左上角追加一个标准尺寸的“返回键”图标。
- **导航图标改造**：弃用之前的横向撑满布局，将 Tabs（总杯级、挂机、决战）改造成分离的、独立的圆形或方形按钮容器。

### 页面布局优化

- **背景图下移**：修改 `index.wxml/wxss`，将 `Background.png` 的定位从 `top: 0` 改为受 `statusBarHeight` 约束，确保它不侵入手机顶部的时间/电池信息栏，其下的其他组件一并下移。
- **属性下拉框**：在排行榜标题（如“决战榜 TOP 10”）右侧或紧邻位置，增加微信原生的 `<picker>` 组件。提供 6 种预设敌人属性（默认：1000甲20抗）。
- **底端备注说明**：在表格最下方增加一个 `view`，用暗色系小字体展示关于敌人三抗、理论最大值声明及计算公式的免责说明。

### 组件设计重构 (表格化)

当前的 `<operator-card>` 是高度定制的单行卡片，现在需要将其改写成**严格的表格行列对齐 (Table Row) 形式**。
因为不同的榜单（总榜 vs 细分榜）具有完全不同的字段列数，我们将给 `operator-card` 组件增加 `mode` 属性，让其能智能切换渲染形态：

- **总杯榜 (`mode="total"`)**: Cup | Rank | 方形头像 | 干员名称 | 干员职业 | 挂机排行 | 决战排行
- **细分榜 (`mode="skill"`)**: Rank | 方形头像 | 干员名称 | 干员职业 | DPS | 总伤

---

## ⚠️ User Review Required

> [!IMPORTANT]
> **卡片重构与数据源 (Mock Data)**
> 因为新的表格增加了“挂机排行”、“决战排行”、“DPS”、“总伤”等多列并发数据，而原来的 Mock 数据比较单薄，本阶段在重构组件时，我将同步强化 `index.js` 里的 Mock Data 结构（例如补充 `idleRank`, `burstRank`, `dps`, `totalDmg` 字段），以确保前端能在表格中完整渲染出这些列的数据。

## ❓ Open Questions

> [!NOTE]
>
> 1. **背景颜色 (Hex)**：为了完美契合，您能否目测或提供一下 `Background.png` 大概的 Hex 颜色值？（若无，我将默认调配一个类似 `#1C1C1E` 的中性深灰）。
> 2. **左上角返回键**：由于当前是小程序默认首页，点击返回键预期是直接退出小程序，还是先弹个 Toast 占位？

## 🛠️ Proposed Changes

### [MODIFY] frontend/app.wxss (更改主题颜色变量)

### [MODIFY] frontend/pages/index/index.wxml & wxss (下移背景图、重构导航栏为独立按钮、增加左上角返回键、添加 Picker 下拉框和底部文字说明)

### [MODIFY] frontend/pages/index/index.js (扩展 Mock 数据结构，处理 Picker 逻辑)

#### [MODIFY] frontend/components/operator-card/ (大重构：将卡片布局转变为多列表格布局，支持 total/skill 两种渲染模式，更换为方形头像占位图)

## 🧪 Verification Plan

### Manual Verification

- 编译小程序后，核对顶栏是否低于手机状态栏。
- 切换上方圆角 Tab 时，观察下方表格结构能否在“总杯榜”和“挂机/决战榜”格式间无缝切换。
- 点击标题旁边的下拉框，测试能否唤起底部弹出的敌人属性选择器。
