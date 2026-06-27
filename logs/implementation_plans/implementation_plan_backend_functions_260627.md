# Arknights Operator Logic Implementation Plan

本计划旨在依据解析好的 JSON 数据，系统性地丰满干员和职业的业务逻辑（填充血肉），并给出具体的架构规范和实施范例。

## 目标概述
通过解析 JSON 数据中的天赋、技能描述和职业特性，为后端提供准确的干员 DPS 演算能力。我们将以“剑豪”职业和干员“艾丽妮”作为首个完整实现的基准案例，待您审核通过后，可将其作为标准模式推广至其余干员。

## User Review Required

> [!WARNING]
> **基类扩展限制**
> 您的要求中提到“不要轻易改动 `base_operator.py`”。为了保持代码整洁并支持复杂的乘区计算（如攻击乘算、无视防御等），我计划在 `base_operator.py` 的 `Operator` 类中添加一些非破坏性的辅助方法（例如 `calculate_physical_damage(atk, enemy_def)`），或者完全将这些通用公式放入 `professions.py` 中。请确认是否允许在 `base_operator.py` 中新增纯工具性质的方法。

## Open Questions

> [!IMPORTANT]
> **关于缺少 SP（技力）与循环周期数据的问题**
> 目前 JSON 数据的 `skills` 列表中缺少技能的“消耗SP”、“初始SP”以及具体的动作帧（动画时间）。
> 1. **爆发类技能（duration 为 null）**：如艾丽妮 S2、S3，这类技能是瞬间造成伤害。在缺少技能周期的情况下，它们的 `dps` 字段应如何计算？是仅返回 `total_damage` 并令 `dps = total_damage / 1`，还是仅在 `total_damage` 中体现，`dps` 保持为 0？
> 2. **群攻目标数**：技能计算通常假设对单体（1个敌人）计算 DPS/总伤。对于明确提及“周围小范围内所有敌人”或“最多6名”的技能，演算器默认只针对传入的单个 `Enemy` 对象计算对其造成的单体期望伤害，这样可以吗？

## Proposed Changes

### 1. 完善职业体系 (professions.py)
我们将根据干员类型动态扩展职业父类，并在其中实现职业特性。

#### [MODIFY] [professions.py](file:///e:/Local_AI_Station/CupCalculation/backend/function/logic/professions.py)
- **新增 `Swordmaster(Operator)` (剑豪)**
  - 属性初始化：`attack_interval = 1.3`，`block_count = 2`。
  - 特性实现：重写基础的普通攻击逻辑。剑豪的普攻造成两次伤害，因此在其基础 `calculate_dps`（`skill_index == -1`）中，单次攻击的伤害将计算两遍。

### 2. 实现干员具体逻辑 (ii07_艾丽妮.py)
以艾丽妮为例，展示如何将 JSON 中的文本和数值转化为乘区逻辑。

#### [MODIFY] [ii07_艾丽妮.py](file:///e:/Local_AI_Station/CupCalculation/backend/function/logic/operators/ii07_艾丽妮.py)
- **继承与初始化**：将继承自 `UnknownProfession` 改为继承 `Swordmaster`。
- **`apply_talents()` 实现**：
  - **天赋 1（审判之火）**：物理伤害有50%概率无视50%防御（对空100%）。我们将在对象中新增 `self.prob_ignore_def = 0.5` 和 `self.ignore_def_ratio = 0.5`。在伤害计算时基于期望计算无视防御的收益（由于目标是否对空未在 `Enemy` 中直接体现，暂按普通敌人 50% 概率计算）。
  - **天赋 2（净化之剑）**：攻速 +18。我们在初始化时 `self.attack_speed += 18`。
- **`calculate_dps(enemy, skill_index)` 实现**：
  - **普攻 (`skill_index == -1`)**：调用 `super().calculate_dps(enemy, -1)`（在剑豪父类中处理双击）。
  - **技能 1 (`skill_index == 0`)**：计算“200%物理伤害追加一次200%物理伤害”，计算单次施放的总伤害。
  - **技能 2 (`skill_index == 1`)**：计算“400%物理伤害”，总伤害 = 计算结果。
  - **技能 3 (`skill_index == 2`)**：计算“300%物理伤害” + 12次“250%物理伤害”，合计总伤害。由于是瞬间爆发，提供总伤数据。

### 3. 日志规范 (logs/log-260627.md)
按照要求，在开发日志末尾追加修改记录，附带精确到分钟的时间戳（中文）。

## Verification Plan

### Manual Verification
- 实例化艾丽妮对象，并创建一个测试用的 `Enemy` 对象。
- 调用其 `calculate_dps` 计算普攻和不同技能（S1, S2, S3）在当前防御下的期望伤害，并在终端打印，确保符合方舟的伤害计算公式（考虑保底伤害 5% 的情况）。
