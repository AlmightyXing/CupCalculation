# Phase 7 交互与图表化功能实现计划

## 目标说明

完成 `前端设计与开发任务单.md` 中 Phase 7 的以下两项核心需求：
1. **图表化分析**：在榜单引入 ECharts 柱状图对比，直观展示 DPS/总伤差距断层。
2. **交互补充**：实现公式详解弹窗，加入长列表无限滚动加载（Virtual List / Infinite Scroll），优化大量干员的渲染性能。

## User Review Required

> [!IMPORTANT]
> **图表展示逻辑设计确认**
> 我计划在总杯榜/挂机榜/决战榜的顶部（或悬浮按钮）新增一个“图表视图”的切换按钮。点击后，会将当前的列表视图切换为 ECharts 柱状图，横轴为排名前 20 位的干员，纵轴为 DPS 或总伤（总杯榜则为综合评分）。请问您是否同意这种切换视图的方式？

> [!IMPORTANT]
> **长列表无限滚动设计确认**
> 为了优化渲染，我计划采用 **分批懒加载 (Infinite Scrolling)** 的方式。初始加载 20 名干员，当用户滚动到底部时自动加载后续 20 名干员。这种方式在 Vanilla JS 中最为轻量且能完美满足性能需求，您是否接受这种方案替代极其复杂的绝对定位 Virtual List？

## Open Questions

- 公式详解弹窗的内容需要写哪些公式？目前我计划填入最基础的《明日方舟》伤害计算公式（如：`物理伤害 = 最终攻击力 - 最终防御力`，`法术伤害 = 最终攻击力 * (1 - 最终法抗/100)`）。您是否有特殊的文本要求？

## Proposed Changes

### 1. ECharts 引入与视图开发
- **[MODIFY] `frontend/index.html`**
  - 在 `<head>` 中引入 ECharts CDN：`<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>`。
  - 在榜单区域的表头 (`table-header-bar`) 新增“图表视图 / 列表视图”切换按钮。
  - 新增图表容器 `<div id="chart-container" style="display: none; width: 100%; height: 500px;"></div>`。

- **[MODIFY] `frontend/app.js`**
  - 增加对 ECharts 实例的初始化。
  - 根据当前停留的榜单（挂机榜/决战榜），提取前20名干员的数据（名称与对应DPS/总伤），并调用 ECharts 渲染柱状图，直观展现数值断层。

### 2. 长列表无限滚动加载 (Infinite Scroll)
- **[MODIFY] `frontend/app.js`**
  - 重构 `renderList()` 逻辑，增加 `page` 和 `pageSize = 20` 的控制。
  - 为 `operator-list` 容器增加 `scroll` 事件监听：当 `scrollTop + clientHeight >= scrollHeight - 50` 时，触发 `loadMore()`，将下一批次干员的 DOM 节点 Append 进列表。

### 3. 公式详解弹窗 (Formula Modal)
- **[MODIFY] `frontend/index.html`**
  - 新增一个隐藏的 Modal 弹窗组件，内部包含基础伤害公式、DPS 计算原则和总杯计算权重的解释。
  - 在总榜标题旁或侧边栏新增一个“？”图标按钮，用于触发弹窗。

- **[MODIFY] `frontend/style.css`**
  - 补充 Modal 弹窗的遮罩层、居中显示面板、动画过渡以及关闭按钮的样式。

## Verification Plan

### Manual Verification
1. 启动桌面应用，切换到“挂机榜”，点击“图表视图”，验证是否出现 ECharts 柱状图并正确展现排名前列的 DPS 断层。
2. 迅速向下滚动榜单，验证到底部时是否平滑加载出后续排名的干员，不出现卡顿。
3. 点击“？”图标，验证公式弹窗是否顺利弹出，且样式美观。
