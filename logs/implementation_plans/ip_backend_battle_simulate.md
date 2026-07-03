# 方案 Phase 6：核心计算引擎接入与全局跑分演算

## 🎯 目标
完成战斗模拟逻辑（`engine.py` 及各类 `operator.py`）的最终调试，连通全量 130 名干员的技能伤害运算；同时在后端新增批量“跑分排位”接口，并在前端首页榜单及详情页中动态呈现基于真实计算产生的 DPS、总伤与杯级排名！

## 🔍 问题诊断与修复 (Research Results)
在测试全量干员并发跑分时，我发现了一小部分代码历史遗留的崩溃点（Python 并发模拟仅需不到 0.05 秒，速度极快！但存在异常抛出）：
1. **基类面板缺失**：`base_operator.py` 未统一初始化 `self.final_base_atk`，导致部分未重写 `__init__` 的子干员脚本报错。
2. **公式参数不匹配**：如 `锏` 脚本里传入了未在 `formulas.py` 声明的 `vulnerability_ratio`（脆弱乘区本应由环境全局接管），`圣聆初雪` 脚本使用了错误的 `res_ignore` 参数名。
3. **Null 型 Duration 崩溃**：部分弹药/瞬发技能 `duration` 为 `None`，在除法计算时抛出 `NoneType` 异常。

## 🛠️ 拟定执行步骤 (Proposed Changes)

### 1. 修复底层引擎与子类兼容性
- **[MODIFY] `backend/function/logic/base_operator.py`**
  - 在 `__init__` 统一注入信赖面板并初始化 `self.final_base_atk` 等终态面板属性。
  - 增强 `duration` 的防空 (None) 处理，避免计算时间周期时发生除零或 NoneType 异常。
- **[MODIFY] `backend/function/logic/operators/*.py`**
  - 写一个批量修复脚本，通过正则或 AST 修正 `vulnerability_ratio` 和 `res_ignore` 等传参错误，确保 130 位干员全部顺利通过单元测试计算。

### 2. 增设“排行榜”全量演算 API
- **[MODIFY] `backend/main/api_server.py`**
  - 新增 `GET /api/rankings?enemy_level={level}` 端点。
  - 逻辑：对 130 名干员进行遍历，获取每个技能在对应敌人（0抗、高抗等）下的 `dps` 和 `total_damage`。
  - 排位判定：
    - **挂机榜 (Idle)**：选取 `skill_type == "auto"` 技能的最高 `cycle_dps` 参与排名。
    - **决战榜 (Burst)**：选取 `skill_type == "manual"` 技能的最高 `total_damage` 参与排名。
    - **总杯 (Total Cup)**：结合决战与挂机排名，划定“超大杯(Top 10%)”、“大杯(Next 20%)”、“中杯”等头衔。

### 3. 前后端的终极结合
- **[MODIFY] `frontend/pages/index/index.js`**
  - 去除 `mockData`。在 `onLoad` 和切换敌人的事件 `onEnemyChange` 中，发起对 `/api/rankings?enemy_level=X` 的真实请求。
  - 获取排名后动态渲染 WXML。
- **[MODIFY] `frontend/pages/detail/detail.js`**
  - 获取干员详情时，同步向后端请求该干员的排名结果，将原本填写的 `演算中` 和占位符替换为真实的排行榜数字！

## ❓ User Review Required
> [!IMPORTANT]
> 1. 全局杯级评分标准（“总杯榜”）：目前计划直接基于 **[挂机DPS排位 + 决战总伤排位]** 的综合名次来按百分比分发“超大杯、大杯、中杯”的荣誉，您是否认同这种粗略算法？（因为复杂的实战环境难以用纯粹一维数值定义，这种权重的近似计算最能直观反映纸面实力）。
> 2. 由于 130 个干员全部是您或前置流程利用大模型自动生成的代码，我会用脚本自动抹平接口不兼容的地方，请允许我执行自动化批处理修复。

## 🧪 验证计划
1. 在后端运行一次全面的 `scratchpad.py` 测试，确保 130 份代码均不会抛出异常。
2. 重启 `api_server.py`。
3. 观察小程序首页，确认能根据右上角的敌人下拉框（比如切到 2000甲 40抗）实时刷新全服大榜，且水陈、玛恩纳等真实大杯干员能够正确登顶！
