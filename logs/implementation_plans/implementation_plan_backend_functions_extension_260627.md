# 算法全局推广与基类重构计划 (Cycle DPS Promotion)

根据您的要求，为了将包含“攻回/自回”的**周期 DPS (Cycle DPS) 演算算法**推广到全部 130 位干员，我们需要从底层架构上进行一次解耦和重构。

如果每个干员的 `.py` 文件都像 `ii07_艾丽妮.py` 那样重复写一遍充能时间的 if-else 判断，代码将极度冗余且难以维护。因此，我计划在 `base_operator.py` 引入**模板方法模式 (Template Method Pattern)**。

## 目标概述
将周期 DPS 的计算逻辑完全下沉至 `base_operator.py`，使所有干员和职业自动继承该能力；具体的干员类只需专注于实现**“自己的普攻特殊逻辑”**和**“自己每个技能的倍率”**即可。

## User Review Required

> [!WARNING]
> **基类改动预警**
> 本次重构需要对 `base_operator.py` 中的 `calculate_dps` 接口进行实质性改写，并引入两个新的生命周期方法供子类覆写。虽然这违背了早期“不要轻易改动基类”的原则，但这是将算法推广到全局的**唯一优雅路径**。

## Proposed Changes

### 1. 重构基类设计 (base_operator.py)

#### [MODIFY] [base_operator.py](file:///e:/Local_AI_Station/CupCalculation/backend/function/logic/base_operator.py)
在 `Operator` 类中：
- **新增属性**：`self.damage_type = "physical"`（默认普攻伤害类型，术师等职业可在父类改为 `"arts"`）。
- **新增模板接口 1**：`calculate_normal_hit(self, enemy, target_count=1) -> float`。提供默认的普攻伤害期望计算（基础攻击力去减敌人防御/法抗）。干员如果像艾丽妮一样拥有“无视防御”的概率天赋，只需重写此方法。
- **新增模板接口 2**：`calculate_skill_damage(self, enemy, skill_index, target_count=1) -> float`。由具体干员重写，专门返回对应技能爆发期间的总伤。
- **重写 `calculate_dps`**：在这个主入口中，集中实现我们上一版讨论定稿的**回转周期演算算法**（读取 JSON 的 SP 消耗、判定攻回/自回、根据攻速折算充能时长、叠加充能期普攻伤害）。

### 2. 重构艾丽妮以适配新架构 (ii07_艾丽妮.py)

#### [MODIFY] [ii07_艾丽妮.py](file:///e:/Local_AI_Station/CupCalculation/backend/function/logic/operators/ii07_艾丽妮.py)
- 删除原先冗长的 `calculate_dps` 和底部的周期计算模板代码。
- 实现 `calculate_normal_hit`，将天赋 1 (审判之火破甲) 封装在内。
- 实现 `calculate_skill_damage`，单纯地利用 if-else 返回 S1、S2、S3 的技能总伤 `skill_dmg`。
- **不再重写 `calculate_dps`**，直接享受基类提供的全自动周期回转服务。

## Verification Plan

### Automated Tests
重构完成后，我将再次运行 `python test_irene.py`。
由于仅仅是设计模式上的解耦，重构前后的伤害期望数据、充能时间、周期 DPS 数据应当**100%完全一致**。这标志着新架构的平滑过渡，随后此模式即可直接覆盖其余 129 名干员。
