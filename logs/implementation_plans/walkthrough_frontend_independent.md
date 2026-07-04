# 前端架构迁移：独立桌面应用 (Python WebView)

我们已经成功将《杯级计算器》从微信小程序脱离，重构为了一个完整的独立桌面应用（Standalone App）。

## 架构演进

由于系统环境中没有安装 Node.js，我们没有采用最初计划的 Electron + Vite 方案。而是巧妙地转用了 **Python 的 `pywebview` 库**，这完美契合了您“一键双端”与“绑定 Python 后台”的需求。

### 新的工作流：
1. **统一入口 (`main_app.py`)**：在启动时，Python 脚本会在后台开启子线程拉起 FastAPI 服务器，并在主线程创建原生的桌面窗口。
2. **前后端合并**：FastAPI 被配置为静态文件服务器，直接将 `frontend/` 目录挂载到 `/app/` 路由下。
3. **彻底抛弃微信依赖**：所有的网络请求都从 `wx.request` 替换成了原生的 `Fetch API`，并且自动指向本地启动的后台进程（`127.0.0.1:8000`）。这消除了任何网络波动，达到了“离线本地可用”的效果。

## 视觉与组件升级

为了符合《高级 Web 开发规范》，我对 UI 进行了深度定制：

- **Premium Dark Theme**：应用了原生的深色模式（深渊灰底色 + 蓝色光效发光强调色）。
- **微动画与 Glassmorphism**：顶部导航栏和数据表格应用了毛玻璃质感滤镜，按钮切换增加了缓动与反馈动画（Micro-animations）。
- **原生 JS 极简重构**：完全抛弃 `.wxml` 和 `.wxss`，在 `frontend/` 下实现了标准的 Web 堆栈：
  - [index.html](file:///e:/Local_AI_Station/CupCalculation/frontend/index.html) (骨架与路由容器)
  - [style.css](file:///e:/Local_AI_Station/CupCalculation/frontend/style.css) (现代化设计系统)
  - [app.js](file:///e:/Local_AI_Station/CupCalculation/frontend/app.js) (逻辑控制，包含首页排位、干员详情、沙盒测算、搜索模块的单页面路由渲染)。

## 验证与使用

> [!TIP]
> **如何启动新版应用？**
> 我已经在后台为您拉起了 `main_app.py`，此时应该已经弹出了原生的桌面窗口。
> 未来您随时可以双击或在终端中运行：
> ```bash
> .\.venv\Scripts\python.exe main_app.py
> ```
> 即可一键启动完整计算器桌面版。

## 记录

本次架构的大规模变动已记录入 [log-260704.md](file:///e:/Local_AI_Station/CupCalculation/logs/log-260704.md) 文件中。
