# 后端系统重设计与重构实施计划

基于您提供的 `后端设计逻辑.md`，本项目将从原本“脚本式的一次性计算模型”转型为“基于面向对象与服务化的战斗模拟引擎”。本次重构动作较大，我整理了以下实施方案和待确认的开放性问题。

## User Review Required

> [!WARNING]
> **运行方式变更**
> 原本是通过命令行运行 `python pipeline.py` 来离线输出 JSON。由于改为了前后端交互模式，我们需要引入 Web 框架（推荐 **FastAPI**）来搭建 API Server。测试期间，它将作为本地 Server 监听请求，并返回战报。请确认是否接受引入 FastAPI。

## Open Questions

> [!IMPORTANT]
> 1. **关于战斗空间模拟精度**
> 目前旧版本是纯公式直接乘算DPS。设计文档提到了“运行战斗空间的代码进行模拟”。请问我们需要做到类似“时间轴帧率模拟器 (Tick-based)”（如每 0.033s 计算一次攻击、判定 buff 和 debuff），还是只需要面向对象的宏观回合制/公式计算器即可？（建议先从宏观对象公式结算开始，以防过度复杂）。
> 2. **文件结构拼写确认**
> 设计文档中存在拼写 `Operaters`，在重组 `data/` 目录时，是否需要帮您自动修正为标准的英语单词 `Operators`？
> 3. **关于 Python 代码包结构**
> 按照文档规划，爬虫、解析和逻辑都直接放在 `backend/` 第一级。然而在 Python 规范中，通常会统一放在 `backend/src/` 中避免导包混乱。如果您非常希望扁平化结构，我会直接遵守；或者我可以将它们作为标准的 package 处理？

## Proposed Changes

根据文档，系统将被划分如下模块，并进行目录结构的物理迁移和代码重构。

---

### 1. 数据存储层 (Data Layer)

重构原本杂乱的 `data/` 文件夹。

#### [NEW] `data/Operators` (干员基础数据存放处)
#### [NEW] `data/Enemies` (敌人模版及数值存放处)
#### [NEW] `data/raw_data` (原生的爬虫 HTML/纯文本存档)
#### [NEW] `data/parsed_data` (经过清洗的结构化缓存数据)
#### [DELETE] 清理旧的 `data/processed` 和 `data/output`，并迁移数据

---

### 2. 爬虫与解析层 (Data Ingestion)

#### [MODIFY] `backend/crawler/`
将现有的 `src/crawler` 重命名和迁移，爬取到的数据统一储存到 `data/raw_data`。

#### [MODIFY] `backend/parser/`
将现有的 `src/parser` 重命名和迁移，清洗后的数据统一储存到 `data/parsed_data`。

---

### 3. 面向对象逻辑层 (Object Logic)

这是本次重构的核心。

#### [NEW] `backend/logic/base_operator.py`
定义所有干员的基础抽象类 `Operator`。

#### [NEW] `backend/logic/professions.py`
按照特性定义各职业父类。例如 `HeavyShooter(Operator)`（重射手），在此预设攻击间隔 1.6s、阻挡数 1、再部署 70s 等共享属性。

#### [NEW] `backend/logic/enemy.py`
定义敌人对象的抽象模型（包含防御力、法抗、生命值等状态），供战斗环境调度。

#### [NEW] `backend/logic/operators/`
所有的干员将实例化为具体的类文件。例如 `char_103_angel.py` (银灰)，他将继承对应的职业父类，并且实现自己特定的天赋逻辑、技能开启时的数值修正。

---

### 4. 战斗空间模拟层 (Battle Environment)

代替旧的 `calculator` 计算器。

#### [NEW] `backend/battle/engine.py`
- 创建 `BattleEnvironment` 类。
- 实现 `add_operator(operator)` 和 `add_enemy(enemy)`。
- 实现 `simulate()` 方法：调度双方数值进行交互运算。返回伤害构成、总伤、DPS。

#### [DELETE] 清理废弃的旧计算脚本
- `backend/src/calculator/` 及旧版 `pipeline.py`

---

### 5. API 与应用启动 (API & Serving)

#### [NEW] `backend/main.py`
作为 Serverless Function 的本地调试入口。通过 FastAPI 构建后端接口：
- `POST /api/simulate`
  - Input: `{"operator_id": "...", "enemy_id": "...", "skill_level": "..."}`
  - Output: `{"total_damage": 278900, "dps": 4648, "details": "..."}`

## Verification Plan

### Automated Tests
- 为新设计的继承体系（如职业基类的默认数值）建立单元测试。
- 用经典的银灰、玛恩纳进行模拟调用，比对 `BattleEnvironment` 跑出的数据是否与 Phase 1.5 验证的理论伤害（玛恩纳27W）吻合。

### Manual Verification
- 启动 `backend/main.py`，使用 Curl 或 Postman (或者利用已有前端) 尝试对本地 API 发起 HTTP 调用，确认成功返回战报数据。
