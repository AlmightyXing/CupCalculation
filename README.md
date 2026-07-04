# 《杯级计算器》(Whats Your Cup)

> 《明日方舟》六星干员数值量化分析与桌面可视化工具。

## 1. 项目简介

本应用旨在统一的基准（如：1000物理防御 / 20法术抗性）下，对《明日方舟》干员的伤害与治疗能力进行加权评分与**杯级评定**。通过独立封装的桌面端界面，提供直观的干员DPS排行榜、单干员全技能伤害测算沙盒（Sandbox）功能以及图表数据可视化。

## 2. 技术架构

- **前端层 (Frontend)**：基于 `HTML + Vanilla CSS + Vanilla JS` 构建的现代暗黑风格界面，通过原生技术栈实现高性能渲染，并利用 ECharts 提供数据可视化图表。
- **本地计算服务 (Backend)**：基于 `FastAPI` 搭建轻量级本地引擎，提供 `/api/operators` 和 `/api/sandbox/simulate` 等核心 RESTful 接口。
- **运算逻辑层 (Engine)**：完全面向对象建模的 Python 后端（四大属性修饰器和五大伤害类型），支持动态拦截与群体协同Buff演算机制。
- **跨平台桌面封装**：利用 `pywebview` 框架拉起客户端 Web 窗口与 FastAPI 进程双边守护，最后通过 `PyInstaller` 构建可直接独立运行的 `.exe` 应用。

## 3. 目录结构说明

```
CupCalculation/
├── backend/                  # 后端引擎目录
│   ├── function/             # 战斗演算引擎与干员机制逻辑
│   │   ├── battle/           # 沙盒仿真战场模型
│   │   └── logic/            # 干员对象与抽象基类 (operators/)
│   ├── main/                 # FastAPI路由及干员仓库动态加载
│   └── utils/                # 动态路径解析等工具类
├── data/                     # 数据与资源资产
│   ├── parsed_data/          # 干员属性/技能核心 JSON 数据
│   └── avatars_head_portrait/# 前端加载的干员头像图片库
├── frontend/                 # 原生前端 UI 源码
│   ├── index.html            # 布局入口
│   ├── style.css             # 样式库
│   └── app.js                # 交互与 API 对接
├── documents/                # 项目架构文档、PRD设计与进度报告
├── dist/                     # (编译后生成) 独立可执行程序路径
├── CupCalculation.spec       # PyInstaller 构建配置
├── build_app.py              # 一键自动化打包脚本
└── main_app.py               # 开发环境程序入口 (pywebview启动)
```

## 4. 环境配置与开发

本项目推荐使用 Python 3.12+。

### 4.1 运行开发环境

```powershell
# 1. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main_app.py
```

### 4.2 编译可执行程序 (.exe)

利用自动化打包脚本将所有资产封装为单体文件：

```powershell
python build_app.py
```

编译完成后，双击运行 `dist/CupCalculation/CupCalculation.exe` 即可启动应用。

## 5. 计算基准 (沙盒系统)

系统提供的沙盒仿真模型基于以下核心法则：

- **物理防御与法术抗性**：用户可在沙盒UI面板实时调节敌人的初始抗性（提供六大阶段预设）。
- **干员状态控制**：全员默认处于 **精二满级、0潜能、技能专三、模组满级（如适用）** 状态。
- **伤害统计方式**：
  - 挂机榜：评估全周期的平摊 DPS / HPS。
  - 决战榜：评估高压技能开启期间的总伤害极限 / HPS。

## 6. 免责声明与日志

> ⚠️ **声明**：本系统依赖于大模型对干员百科（PRTS）原始描述进行抽象提纯，干员技能逻辑代码实现暂未进行全部的人工精确校对，实际数据结果可能存在少数机制偏差，仅供交流学习参考！
