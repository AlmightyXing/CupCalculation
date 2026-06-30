# 🏆 前端开发执行计划：阶段 3（搜索与发现模块）

根据《前端设计与开发任务单》，当前进入阶段 3。我将指派 **“交互流 Agent”** 接管此阶段。该阶段旨在补全用户主动查找干员的链路，建立完善的搜索交互体系。

## 🎯 整体架构与开发目标

本阶段聚焦于入口联动与 `frontend/pages/search/search` 搜索页面的开发。

### 阶段 3 核心任务清单

1. **全局搜索入口改造**：
   - 在已封装的 `navigation-bar` (自定义导航栏) 中，增加一个“右侧功能区 (Slot)”，并在首页 (`pages/index/index`) 顶部导航栏右侧放入一个 🔍 搜索图标。
   - 点击该图标无缝跳转至 `pages/search/search`。
2. **搜索页核心布局 (`pages/search/search`)**：
   - **顶部搜索栏**：带有清除按钮的输入框，支持实时输入。
   - **搜索辅助面板**：包含“历史搜索”（使用 `wx.getStorageSync` 存入本地）和“热门推荐”（预设几个如“玛恩纳”、“史尔特尔”的 Tag）。
   - **搜索结果面板**：复用阶段 2 开发好的 `<operator-card>` 组件来展示搜索命中的干员，确保设计语言的一致性。
3. **模糊搜索与事件流 (Mock)**：
   - 输入框的输入事件 (`bindinput`) 会触发本地数据的过滤（模拟后端或前端内存的模糊搜索，支持名称拼音或外号如“42”、“水陈”的映射）。
   - 点击搜索结果中的干员，触发跳转至详情页（由于详情页在阶段 4 建设，这里暂用 `wx.navigateTo` 跳往一个占位页面或弹出 Toast）。

---

## ⚠️ User Review Required

> [!IMPORTANT]
> **本地与远程搜索权衡**：考虑到干员总数只有 129 个（加上后续扩展不到 200 个），在实际业务中我们可以在小程序启动时一次性把精简后的“全干员搜索词典（含外号）”拉取到前端本地内存，从而实现**无延迟、零网络请求的极速本地模糊搜索**。在此阶段，我们是否先以**全本地 Mock 过滤**来构建交互？

## ❓ Open Questions

> [!NOTE]
>
> 1. 首页的搜索入口位置：您更倾向于是放在**头部导航栏的右侧**（与“杯级排行榜”标题同行），还是在**榜单列表和 Tabs 之间**插入一个常驻的长条形搜索框？（默认提案为前者，更节省垂直屏幕空间）。
> 2. 点击搜索结果后，是否允许将当前的查询词自动加入本地的“历史搜索”记录中？

## 🛠️ Proposed Changes

### Components & Pages

#### [MODIFY] frontend/components/navigation-bar/ (开放右侧插槽 slot)

#### [MODIFY] frontend/pages/index/index.wxml (插入搜索图标跳转逻辑)

#### [MODIFY] frontend/pages/search/search.wxml & wxss (重构页面，加入历史/热门区域，及复用 operator-card)

#### [MODIFY] frontend/pages/search/search.js (实现历史记录存储、搜索词过滤与外号字典逻辑)

#### [NEW] frontend/pages/detail/detail (创建阶段 4 所需的详情页骨架，以便支持搜索结果点击跳转)

## 🧪 Verification Plan

### Manual Verification

- **Artifact 交付**：交互流 Agent 将提交本阶段的 `delivery_frontend_phase3.md`。
- **视图功能验证**：在开发者工具中，验证首页点击搜索能否正确跳转；验证输入“42”或“水陈”能否过滤出对应干员卡片；验证搜索历史是否会在清除后消失或重新进入小程序后依旧保留（本地缓存）。
