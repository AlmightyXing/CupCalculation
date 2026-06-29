# 战斗环境与团队增益架构实现计划

> **针对您 Comment 的回复：**
> 您的顾虑非常敏锐。**我的方案是完全泛用的，具备普适性，绝对不需要在运行时调用大模型，也不针对特定阵容硬编码。**
>
> 它的工作原理是建立一套**“标准化全局 Buff 协议”**：
> 1. **统一的环境基座**：在 `Enemy` 基类中，永久新增 `is_cced`（是否被控制）、`global_fragile`（脆弱）、`global_flat_arts`（法术附加）等属性。
> 2. **泛用的底层拦截**：`BattleEnvironment` 会在任何一场战斗开始前，将 `formulas.py` 里的计算公式自动对接给 `Enemy` 的这些新属性。这意味着**任何干员**只要打出了伤害，底层公式就会自动帮他计算环境里的脆弱和附加伤害。
> 3. **接口标准化**：为了让系统知道谁提供了 Buff，我们在 `Operator` 基类中加一个通用的接口 `get_team_buffs()`。虽然之前生成的 129 个干员的内部变量名千奇百怪（有的叫 `self.talent_res_down`，有的叫 `self.fragile_ratio`），但我们只需要在组队时，**人工（或一次性用脚本）将这些核心拐的 Buff 暴露给 `get_team_buffs()` 即可**。
>
> **结论**：这套环境代码本身是 100% 泛用和参数化的。日后只要把新干员的 Buff 填进通用接口，他就能立刻作为“拐”去增益任意其他干员，全程无需大模型干预。

---

## Proposed Changes

### 1. 敌人实体与基础模型扩展
#### [MODIFY] `backend/function/battle/enemy.py`
实现预设的 6 种标准木桩敌人，属性从 0防0抗 到 5000防100抗。
- `Enemy.get_dummy_target(level)`: 静态方法，快速获取对应级别的木桩。
- 增加标准状态字典或属性：`is_cced`、`global_fragile`、`global_arts_flat_dmg` 等，以支持标准化协议。

#### [MODIFY] `backend/function/logic/base_operator.py`
- 新增 `get_team_buffs(self, skill_index: int)` 虚方法，供特殊辅助干员（如铃兰、逻各斯）重写，向环境暴露自己提供的全队增益。

### 2. 战斗环境 (Battle Environment) 与 全局面板注入
#### [MODIFY] `backend/function/battle/engine.py`
重写 `BattleEnvironment` 类，引入泛用性的“环境上下文拦截”与“全局常数面板注入”机制。

- **阶段一：Buff 聚合 (Buff Aggregation)**
  遍历 `self.operators`，调用通用的 `op.get_team_buffs()` 接口。将所有干员提供的脆弱（取最大值）、减抗（叠加）、控制状态（只要有一个人提供就为 True）汇总写入 `Enemy` 实例中。
- **阶段二：动态劫持底层公式 (Formula Monkey Patching)**
  动态替换 `formulas.calculate_arts_damage` 和 `formulas.calculate_physical_damage`。劫持后的公式会统一读取当前 `Enemy` 实例身上的 `global_fragile` 和 `global_arts_flat_dmg`，使得场上**所有**在进行公式运算的干员，都能享受到同等的面板增益。
- **阶段三：伤害计算 (Simulation)**
  调用各干员的常规 DPS 公式，获得融入了团队 Buff 的总伤数据。
- **阶段四：现场恢复 (Teardown)**
  解除公式劫持，恢复原始干净的 `formulas.py`，保证对后续其他模拟不产生副作用。

### 3. 三人小队实战样例脚本
#### [NEW] `backend/main/run_team_synergy.py`
创建一个专门的入口脚本：
- 实例化【仇白】(YD20)、【逻各斯】(RE03)、【铃兰】(R172) 并加载它们的三技能数据。
- 为这三位干员**实现通用的 `get_team_buffs()` 接口**，并在仇白的判定中引入对 `enemy.is_cced` 的识别。
- 实例化 2000防 40抗 的重甲敌人。
- 对比展示：三人“单打独斗”时的总伤 VS 放入“协同战斗环境”后的实际总伤变化。

## Verification Plan
1. 运行 `run_team_synergy.py`。
2. 验证：
   - 仇白的伤害是否因为铃兰的停顿（泛用的 `is_cced` 标志）和 40% 脆弱、逻各斯的减抗和附加伤害而获得显著提升。
   - 团队总伤是否正确计算，并且全过程未调用任何 LLM 接口。
   - 终端能够清晰打印团队增益下的各干员 DPS 对比报告。

> 请确认是否解答了您的疑惑？同意后我将直接进行代码层面的改造！
