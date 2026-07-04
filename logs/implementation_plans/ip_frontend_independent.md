# 迁移前端架构为独立 App (Standalone App Migration Plan)

您希望将现有的前端架构从微信小程序中脱离出来，成为一个可以直接打开的独立应用程序。这是一个涉及到整个前端重写与架构更替的重大调整。

## 背景与现状
当前前端代码位于 `frontend/` 目录下，使用的是微信小程序的原生框架（包含 `.wxml`, `.wxss`, `.js`, `.json` 文件）。目前实现了以下主要页面和组件：
1. **首页 (Index)**：全干员榜单（总杯、挂机、决战）
2. **搜索页 (Search)**：搜索干员
3. **详情页 (Detail)**：干员面板与伤害详情
4. **沙盒测试页 (Sandbox)**：自定义战斗演算
5. **公用组件**：`operator-card` 卡片组件以及图表库 `ec-canvas`

## User Review Required

> [!WARNING]
> **技术栈的选择**
> 由于微信小程序的代码无法直接在桌面操作系统或浏览器中运行，我们需要选择一个新的跨平台或桌面开发框架。根据目前的业界最佳实践，我建议使用 **Electron + Vite + 原生 HTML/JS/CSS** (或使用 React/Vue，取决于您的偏好) 来构建。Electron 可以将 Web 技术打包成可以直接双击运行的独立 `.exe` 桌面程序，同时与后端的 Python FastAPI 完美契合。
> **请问您是否同意使用 Electron 作为独立 App 的容器框架？**

> [!IMPORTANT]
> **重构范围**
> 1. 原有的 `wxml` 将被翻译为标准的 `HTML`。
> 2. 原有的 `wxss` 将被翻译为标准的 `CSS`。
> 3. 小程序特有的 API（如 `wx.request`, `wx.navigateTo`, `wx.showToast` 等）将替换为标准 Web API（如 `fetch`, `window.location`, 自定义提示组件）。
> 这意味着现有的 `frontend` 文件夹将进行大规模重写。

## Open Questions

> [!NOTE]
> 1. **前端框架偏好**：您希望使用原生的 **Vanilla JS (原生 HTML+JS)** 进行重写，还是引入现代前端框架如 **Vue** 或 **React**？（如果不指定，我将默认使用 Vite 初始化原生的 Vanilla JS 项目，遵循极致纯粹的 Web 标准）。
> 2. **后端捆绑**：作为独立 App，您是希望：
>    - A: 仅打包前端为客户端，用户自己运行 Python 后端 API？
>    - B: 在 Electron 启动时，自动在后台拉起 `api_server.py`，实现纯粹的“一键启动双端”体验？
> 3. **目录结构**：我建议将现有的 `frontend` 目录重命名为 `frontend_miniprogram_backup` 作为备份，然后创建一个新的 `app_client` 目录来初始化新的桌面端工程。您觉得如何？

## Proposed Changes

如果达成一致，接下来的执行步骤如下：

### 1. 备份旧工程
#### [RENAME] `frontend/` -> `frontend_miniprogram_backup/`

### 2. 初始化桌面应用工程
#### [NEW] `desktop_app/` (或您指定的目录)
- 使用 `npm create vite@latest` 初始化前端工程。
- 安装并配置 `electron` 和 `electron-builder` 以支持打包。

### 3. 重写核心页面与组件
#### [NEW] `desktop_app/src/index.html` (首页及路由骨架)
#### [NEW] `desktop_app/src/pages/...` (分别实现 Index, Search, Detail, Sandbox 逻辑)
#### [NEW] `desktop_app/src/styles/...` (重写全局主题和样式)
#### [NEW] `desktop_app/src/components/...` (实现 OperatorCard 等公用组件)
- 移除对 `wx.*` API 的依赖。
- 将网络请求 `request.js` 适配为 `fetch` API，指向后端的 FastAPI 地址（如 `http://localhost:8000`）。
- 替换 ECharts 的微信小程序版本为标准的 ECharts Web 版本。

### 4. 主进程配置 (Electron)
#### [NEW] `desktop_app/main.js` (Electron 主进程文件)
- 配置窗口创建、生命周期管理。
- (可选) 配置自动启动 Python 子进程的逻辑。

## Verification Plan

### Manual Verification
- 运行 `npm run dev` 确保前端页面在开发模式下正确渲染。
- 运行 Electron 启动命令，确保桌面窗口成功打开，且能正常请求 FastAPI 接口。
- 验证所有页面（首页排位、搜索、详情页面板、沙盒环境）的数据流动与视觉展现均与原先的体验一致（甚至更加精美）。
