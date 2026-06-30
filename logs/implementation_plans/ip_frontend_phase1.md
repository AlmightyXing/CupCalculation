# 🏆 前端开发流水线与阶段一执行计划

根据 Manager Agent 的工作流原则，我将严格把控项目进度，协调不同“专职 Agent”推进《前端设计与开发任务单》的各个阶段。每个阶段完成后，我将提呈专项 Artifact 供您审阅，确保绝对符合您的预期后再推进下一阶段。

## 🎯 整体调度蓝图

项目前端共分为 5 大阶段。针对目前的 **阶段 1：工程初始化与全局设置**，我将指派 **“前端架构 Agent”** 进行执行。

### 阶段 1：前端架构 Agent 任务清单

1. **微信小程序原生框架初始化**：在 `frontend/` 目录下初始化标准的微信小程序目录结构（`app.js`, `app.json`, `app.wxss`, `pages/` 等）。
2. **全局 UI 规范确立**：依据《现代Web设计指南》与您的原型风格（如暗黑模式、高质感卡片），建立全局 CSS 变量与主色调配置。
3. **网络通信基建 (HTTP Request)**：封装 `utils/request.js`，无缝对接我们在后端的 `FastAPI` ( `/api/simulate` 等接口)。
4. **公共组件建设**：搭建自定义顶栏 (NavigationBar)、通用的加载骨架屏 (Skeleton) 及空状态 (Empty State) 反馈组件。

---

## ⚠️ User Review Required

> [!IMPORTANT]
> **技术栈确认**：PRD 中指定了使用“微信小程序原生框架”。为了保证代码结构的纯正，Agent 将直接使用 WXML, WXSS, 和纯 JS (不使用 TypeScript，除非您另有要求) 进行构建。
> 如果您希望使用 Taro 或 UniApp 以兼容多端及 H5 预览，请在此阶段提出。否则我们将按照原生微信小程序结构进行初始化。

## ❓ Open Questions

> [!NOTE]
>
> 1. 您是否已经准备好了小程序的 `AppID`？如果没有，初期我们将使用无 AppID 的测试模式（或者您提供测试号 AppID）进行开发。
> 2. 原型中展现的UI风格是偏向暗色系的高级质感。我们是否将默认全局设定为“深色主题 (Dark Mode)”？

## 🛠️ Proposed Changes

### Frontend Architecture

#### [NEW] frontend/app.js (应用入口与全局生命周期)

#### [NEW] frontend/app.json (全局路由与窗口/底栏配置)

#### [NEW] frontend/app.wxss (全局 CSS 变量、主色调、重置样式)

#### [NEW] frontend/utils/request.js (网络请求与拦截器封装)

#### [NEW] frontend/components/navigation-bar/ (自定义头部导航)

#### [NEW] frontend/pages/index/ (首页排行榜占位)

#### [NEW] frontend/pages/search/ (搜索页占位)

## 🧪 Verification Plan

### Automated Tests

- 不涉及自动化测试，将主要通过静态代码检查和格式化确保小程序规范。

### Manual Verification

- **Artifact 交付**：架构 Agent 将生成一份详尽的 `frontend_stage1_delivery.md` Artifact，内含搭建好的目录结构说明、全局样式配置方案，以及网络封装模块的核心代码。
- **审阅节点**：等待您对该 Artifact 做出批示，或进行必要的修改。通过后即进入“阶段 2：首页排行榜开发”。
